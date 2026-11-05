import os
import sys
import time
from pathlib import Path
import httpx

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE_URL = "http://127.0.0.1:8001/api/v1"

def run_live_tests():
    print(f"=== Starting Live E2E Verification against {BASE_URL} ===")
    client = httpx.Client(timeout=10.0)

    # 1. Health check
    t0 = time.time()
    health_res = client.get(f"{BASE_URL}/health")
    health_ms = (time.time() - t0) * 1000
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    print(f"[PASS] Health Check ({health_ms:.1f}ms): {health_res.json()['message']}")

    # 2. Destinations listing from PostgreSQL wanderly_db
    t0 = time.time()
    dest_res = client.get(f"{BASE_URL}/destinations?limit=50")
    dest_ms = (time.time() - t0) * 1000
    assert dest_res.status_code == 200
    dest_data = dest_res.json()["data"]
    names = [d["name"] for d in dest_data]
    print(f"[PASS] Destinations Listing ({dest_ms:.1f}ms): {len(dest_data)} destinations loaded from wanderly_db")

    all_9 = [
        "Bali", "Swiss Alps", "Santorini", "Kyoto", "Maldives",
        "Dubai", "Banff National Park", "Queenstown", "Amalfi Coast"
    ]
    for n in all_9:
        assert n in names, f"Destination {n} missing from wanderly_db!"
    print(f"[PASS] All 9 Seeded Destinations verified present in PostgreSQL")

    # 3. Categories & Filters
    cat_res = client.get(f"{BASE_URL}/destinations/categories")
    assert cat_res.status_code == 200
    assert "Beaches" in cat_res.json()["data"]
    print(f"[PASS] Destination Categories: {cat_res.json()['data']}")

    # 4. Search query
    search_res = client.get(f"{BASE_URL}/destinations/search?q=Alps")
    assert search_res.status_code == 200
    assert any("Alps" in d["name"] for d in search_res.json()["data"])
    print(f"[PASS] Destination Search: Found 'Swiss Alps' matching query 'Alps'")

    # 5. User A Registration & Authentication Lifecycle
    ts = int(time.time())
    email_a = f"live_qa_a_{ts}@example.com"
    email_b = f"live_qa_b_{ts}@example.com"
    password = "LiveSecurePass123!"

    reg_a = client.post(f"{BASE_URL}/auth/register", json={
        "full_name": "QA Alice",
        "email": email_a,
        "password": password,
        "confirm_password": password
    })
    assert reg_a.status_code == 201, f"User A registration failed: {reg_a.text}"
    print(f"[PASS] Live User A registered: {email_a}")

    login_a = client.post(f"{BASE_URL}/auth/login", json={
        "email": email_a,
        "password": password
    })
    assert login_a.status_code == 200
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("[PASS] User A logged in and JWT Bearer token issued")

    # 6. Profile & Stats
    prof_a = client.get(f"{BASE_URL}/users/me", headers=headers_a)
    assert prof_a.status_code == 200
    assert prof_a.json()["data"]["email"] == email_a
    print(f"[PASS] Profile loaded for {email_a} (Saved: {prof_a.json()['data']['saved_count']})")

    # 7. Favorites Persistence
    add_fav = client.post(f"{BASE_URL}/favorites/dest_1", headers=headers_a)
    assert add_fav.status_code in [200, 201]
    print("[PASS] Added Bali (dest_1) to User A's favorites in PostgreSQL")

    fav_list = client.get(f"{BASE_URL}/favorites", headers=headers_a)
    assert any(d["id"] == "dest_1" for d in fav_list.json()["data"])
    print("[PASS] Verified Bali persists in User A's Saved bucket list")

    # 8. User B Multi-User Isolation
    reg_b = client.post(f"{BASE_URL}/auth/register", json={
        "full_name": "QA Bob",
        "email": email_b,
        "password": password,
        "confirm_password": password
    })
    assert reg_b.status_code == 201
    login_b = client.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": password})
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B should NOT see User A's Bali
    b_favs = client.get(f"{BASE_URL}/favorites", headers=headers_b)
    assert not any(d["id"] == "dest_1" for d in b_favs.json()["data"]), "Security leak: User B sees User A's favorites!"
    print("[PASS] Multi-User Isolation: User B cannot see User A's favorites")

    # User B adds Maldives (dest_5)
    client.post(f"{BASE_URL}/favorites/dest_5", headers=headers_b)
    # Check User A's list again
    a_favs_again = client.get(f"{BASE_URL}/favorites", headers=headers_a)
    a_ids = [d["id"] for d in a_favs_again.json()["data"]]
    assert "dest_1" in a_ids and "dest_5" not in a_ids
    print("[PASS] Multi-User Isolation: User A list isolated from User B changes")

    # 9. Reviews Lifecycle
    rev_res = client.post(f"{BASE_URL}/reviews", headers=headers_a, json={
        "destination_id": "dest_4",
        "rating": 5.0,
        "comment": "Kyoto temples were stunning!"
    })
    assert rev_res.status_code == 201
    rev_id = rev_res.json()["data"]["id"]
    print("[PASS] User A submitted review for Kyoto (dest_4)")

    dest_revs = client.get(f"{BASE_URL}/reviews/destination/dest_4")
    assert any(r["id"] == rev_id for r in dest_revs.json()["data"])
    print("[PASS] Destination reviews endpoint returned new review")

    # Eve (User B) cannot edit User A's review
    hacked = client.put(f"{BASE_URL}/reviews/{rev_id}", headers=headers_b, json={"rating": 1.0})
    assert hacked.status_code == 403
    print("[PASS] Authorization: User B forbidden from modifying User A's review (403)")

    # Clean up review
    del_rev = client.delete(f"{BASE_URL}/reviews/{rev_id}", headers=headers_a)
    assert del_rev.status_code == 200
    print("[PASS] Review deleted successfully by author")

    # 10. Notifications Lifecycle
    notices = client.get(f"{BASE_URL}/notifications", headers=headers_a)
    assert notices.status_code == 200
    unread = client.get(f"{BASE_URL}/notifications/unread-count", headers=headers_a)
    assert unread.status_code == 200
    print(f"[PASS] User A notifications loaded (Unread: {unread.json()['data']['unread_count']})")

    mark_all = client.patch(f"{BASE_URL}/notifications/read-all", headers=headers_a)
    assert mark_all.status_code == 200
    unread_zero = client.get(f"{BASE_URL}/notifications/unread-count", headers=headers_a)
    assert unread_zero.json()["data"]["unread_count"] == 0
    print("[PASS] Mark all notifications as read verified (Unread count = 0)")

    # 11. Cleanup test users
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.favorite import Favorite
    from app.models.notification import Notification

    db = SessionLocal()
    try:
        for em in [email_a, email_b]:
            u = db.query(User).filter(User.email == em).first()
            if u:
                db.query(Favorite).filter(Favorite.user_id == u.id).delete()
                db.query(Notification).filter(Notification.user_id == u.id).delete()
                db.delete(u)
        db.commit()
        print("[PASS] Live test artifacts cleanly purged from PostgreSQL wanderly_db")
    finally:
        db.close()

    print("\n=======================================================")
    print("ALL LIVE END-TO-END VERIFICATION CHECKS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    run_live_tests()
