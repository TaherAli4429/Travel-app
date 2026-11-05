import pytest
from fastapi.testclient import TestClient


def test_auth_full_lifecycle(client: TestClient):
    # 1. Register valid User A
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice Traveler",
            "email": "alice@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["success"] is True
    assert reg_res.json()["data"]["email"] == "alice@example.com"

    # 2. Duplicate registration rejection
    dup_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice Duplicate",
            "email": "alice@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert dup_res.status_code == 409

    # 3. Invalid email format
    invalid_email_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Bad Email",
            "email": "not-an-email",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert invalid_email_res.status_code == 422

    # 4. Short password
    short_pw_res = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Short Password",
            "email": "short@example.com",
            "password": "123",
            "confirm_password": "123",
        },
    )
    assert short_pw_res.status_code == 422

    # 5. Login User A
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 6. Wrong password rejection
    bad_pw_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "WrongPassword!"},
    )
    assert bad_pw_res.status_code == 401

    # 7. Nonexistent email rejection
    no_user_res = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "Password123!"},
    )
    assert no_user_res.status_code == 401

    # 8. /auth/me verification
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "alice@example.com"

    # 9. Refresh token verification
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()["data"]

    # 10. Forgot password and reset password flow
    forgot_res = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "alice@example.com"},
    )
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["data"]["dev_reset_token"]

    reset_res = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "NewSecretPassword123!",
            "confirm_password": "NewSecretPassword123!",
        },
    )
    assert reset_res.status_code == 200

    # Login with new password
    new_login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "NewSecretPassword123!"},
    )
    assert new_login_res.status_code == 200
    new_token = new_login_res.json()["data"]["access_token"]

    # 11. Logout endpoint
    logout_res = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert logout_res.status_code == 200


def test_destinations_all_nine_and_filters(client: TestClient):
    # 1. Verify all 9 seeded destinations are present
    res = client.get("/api/v1/destinations?limit=50")
    assert res.status_code == 200
    data = res.json()["data"]
    names = [d["name"] for d in data]

    expected = [
        "Bali",
        "Swiss Alps",
        "Santorini",
        "Kyoto",
        "Maldives",
        "Dubai",
        "Banff National Park",
        "Queenstown",
        "Amalfi Coast",
    ]
    for exp in expected:
        assert exp in names, f"Destination {exp} missing from seeded list"

    # 2. Search by name
    search_bali = client.get("/api/v1/destinations/search?q=Bali")
    assert search_bali.status_code == 200
    assert any(d["name"] == "Bali" for d in search_bali.json()["data"])

    # 3. Search by country
    search_japan = client.get("/api/v1/destinations/search?q=Japan")
    assert search_japan.status_code == 200
    assert any(d["name"] == "Kyoto" for d in search_japan.json()["data"])

    # 4. Filter by category
    beaches = client.get("/api/v1/destinations?category=Beaches")
    assert beaches.status_code == 200
    for d in beaches.json()["data"]:
        assert d["category"] == "Beaches"

    # 5. Filter by rating
    high_rating = client.get("/api/v1/destinations?min_rating=4.9")
    assert high_rating.status_code == 200
    for d in high_rating.json()["data"]:
        assert d["rating"] >= 4.9

    # 6. Combined filter
    combined = client.get("/api/v1/destinations?category=Beaches&min_rating=4.9")
    assert combined.status_code == 200
    for d in combined.json()["data"]:
        assert d["category"] == "Beaches" and d["rating"] >= 4.9

    # 7. Empty search result
    empty_res = client.get("/api/v1/destinations/search?q=NonExistentCityXYZ999")
    assert empty_res.status_code == 200
    assert len(empty_res.json()["data"]) == 0

    # 8. Single destination details
    detail_res = client.get("/api/v1/destinations/dest_1")
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["name"] == "Bali"

    # 9. Nonexistent destination
    not_found = client.get("/api/v1/destinations/dest_999999")
    assert not_found.status_code == 404

    # 10. Featured destination
    feat_res = client.get("/api/v1/destinations/featured")
    assert feat_res.status_code == 200
    assert feat_res.json()["data"] is not None

    # 11. Categories listing
    cats_res = client.get("/api/v1/destinations/categories")
    assert cats_res.status_code == 200
    cats = cats_res.json()["data"]
    assert "Beaches" in cats
    assert "Mountains" in cats


def test_favorites_lifecycle_and_multiuser_isolation(client: TestClient):
    # Setup User A
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "User Alpha", "email": "alpha@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token_a = client.post("/api/v1/auth/login", json={"email": "alpha@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "User Beta", "email": "beta@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token_b = client.post("/api/v1/auth/login", json={"email": "beta@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A saves Bali (dest_1)
    add_a = client.post("/api/v1/favorites/dest_1", headers=headers_a)
    assert add_a.status_code in [200, 201]

    # Duplicate add returns safely (idempotent)
    dup_a = client.post("/api/v1/favorites/dest_1", headers=headers_a)
    assert dup_a.status_code in [200, 201]

    # User A checks favorite
    check_a = client.get("/api/v1/favorites/check/dest_1", headers=headers_a)
    assert check_a.json()["data"]["is_saved"] is True

    # User A lists favorites -> contains Bali
    list_a = client.get("/api/v1/favorites", headers=headers_a)
    assert any(d["id"] == "dest_1" for d in list_a.json()["data"])

    # User B checks Bali -> is_saved must be False! (Multi-user isolation)
    check_b = client.get("/api/v1/favorites/check/dest_1", headers=headers_b)
    assert check_b.json()["data"]["is_saved"] is False

    # User B lists favorites -> Bali must not be there!
    list_b = client.get("/api/v1/favorites", headers=headers_b)
    assert not any(d["id"] == "dest_1" for d in list_b.json()["data"])

    # User B saves Maldives (dest_5)
    client.post("/api/v1/favorites/dest_5", headers=headers_b)

    # User A lists favorites -> Bali exists, Maldives does not!
    list_a_after = client.get("/api/v1/favorites", headers=headers_a)
    a_ids = [d["id"] for d in list_a_after.json()["data"]]
    assert "dest_1" in a_ids
    assert "dest_5" not in a_ids

    # User A deletes Bali
    del_a = client.delete("/api/v1/favorites/dest_1", headers=headers_a)
    assert del_a.status_code == 200

    # Check Bali is unsaved
    check_a_del = client.get("/api/v1/favorites/check/dest_1", headers=headers_a)
    assert check_a_del.json()["data"]["is_saved"] is False


def test_profile_management_and_stats(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Charlie Traveler", "email": "charlie@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token = client.post("/api/v1/auth/login", json={"email": "charlie@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get profile
    prof_res = client.get("/api/v1/users/me", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()["data"]
    assert prof["full_name"] == "Charlie Traveler"
    assert "saved_count" in prof
    assert "reviews_count" in prof
    assert "trips_count" in prof

    # 2. PUT update full profile
    put_res = client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Charles Traveler Updated", "profile_image": "https://example.com/new_avatar.jpg"},
    )
    assert put_res.status_code == 200
    assert put_res.json()["data"]["full_name"] == "Charles Traveler Updated"

    # 3. PATCH update partial profile
    patch_res = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Charlie Final"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["full_name"] == "Charlie Final"

    # 4. Change password with correct current password
    cp_res = client.post(
        "/api/v1/users/me/change-password",
        headers=headers,
        json={
            "current_password": "Password123!",
            "new_password": "BrandNewPassword123!",
            "confirm_password": "BrandNewPassword123!",
        },
    )
    assert cp_res.status_code == 200

    # 5. Change password with wrong current password
    bad_cp_res = client.post(
        "/api/v1/users/me/change-password",
        headers=headers,
        json={
            "current_password": "WrongOldPassword",
            "new_password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!",
        },
    )
    assert bad_cp_res.status_code == 400


def test_reviews_lifecycle_and_recalculation(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Reviewer Dan", "email": "dan@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token_dan = client.post("/api/v1/auth/login", json={"email": "dan@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers_dan = {"Authorization": f"Bearer {token_dan}"}

    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Eve Sneaky", "email": "eve@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token_eve = client.post("/api/v1/auth/login", json={"email": "eve@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers_eve = {"Authorization": f"Bearer {token_eve}"}

    # 1. Invalid rating (> 5.0)
    inv_res = client.post(
        "/api/v1/reviews",
        headers=headers_dan,
        json={"destination_id": "dest_3", "rating": 5.5, "comment": "Too high!"},
    )
    assert inv_res.status_code == 422

    # 2. Empty comment
    empty_res = client.post(
        "/api/v1/reviews",
        headers=headers_dan,
        json={"destination_id": "dest_3", "rating": 4.5, "comment": ""},
    )
    assert empty_res.status_code == 422

    # 3. Valid review submission
    create_res = client.post(
        "/api/v1/reviews",
        headers=headers_dan,
        json={"destination_id": "dest_3", "rating": 5.0, "comment": "Santorini sunsets are unforgettable!"},
    )
    assert create_res.status_code == 201
    review_id = create_res.json()["data"]["id"]

    # 4. Fetch destination reviews
    dest_revs = client.get("/api/v1/reviews/destination/dest_3")
    assert dest_revs.status_code == 200
    revs = dest_revs.json()["data"]
    assert any(r["id"] == review_id for r in revs)

    # 5. Fetch user's own reviews
    my_revs = client.get("/api/v1/reviews/my-reviews", headers=headers_dan)
    assert my_revs.status_code == 200
    assert any(r["id"] == review_id for r in my_revs.json()["data"])

    # 6. Unauthorized edit by Eve
    eve_edit = client.put(
        f"/api/v1/reviews/{review_id}",
        headers=headers_eve,
        json={"rating": 1.0, "comment": "Hacked review"},
    )
    assert eve_edit.status_code == 403

    # 7. Authorized edit by Dan
    dan_edit = client.put(
        f"/api/v1/reviews/{review_id}",
        headers=headers_dan,
        json={"rating": 4.8, "comment": "Updated thoughts: still magnificent!"},
    )
    assert dan_edit.status_code == 200
    assert dan_edit.json()["data"]["rating"] == 4.8

    # 8. Unauthorized delete by Eve
    eve_del = client.delete(f"/api/v1/reviews/{review_id}", headers=headers_eve)
    assert eve_del.status_code == 403

    # 9. Authorized delete by Dan
    dan_del = client.delete(f"/api/v1/reviews/{review_id}", headers=headers_dan)
    assert dan_del.status_code == 200

    # 10. Nonexistent review operations
    not_found_edit = client.put(
        "/api/v1/reviews/fake_review_id_999",
        headers=headers_dan,
        json={"rating": 4.0},
    )
    assert not_found_edit.status_code == 404


def test_notifications_lifecycle(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Frank Notified", "email": "frank@example.com", "password": "Password123!", "confirm_password": "Password123!"},
    )
    token = client.post("/api/v1/auth/login", json={"email": "frank@example.com", "password": "Password123!"}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch notifications (seeded welcome notification exists)
    notices_res = client.get("/api/v1/notifications", headers=headers)
    assert notices_res.status_code == 200
    notices = notices_res.json()["data"]
    assert len(notices) >= 1
    first_id = notices[0]["id"]

    # 2. Check unread count
    unread_res = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_res.status_code == 200
    assert unread_res.json()["data"]["unread_count"] >= 1

    # 3. Mark single as read
    mark_res = client.patch(f"/api/v1/notifications/{first_id}/read", headers=headers)
    assert mark_res.status_code == 200
    assert mark_res.json()["data"]["is_read"] is True

    # 4. Mark all as read
    all_read = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert all_read.status_code == 200

    unread_zero = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_zero.json()["data"]["unread_count"] == 0

    # 5. Delete notification
    del_notice = client.delete(f"/api/v1/notifications/{first_id}", headers=headers)
    assert del_notice.status_code == 200

    # 6. Nonexistent notification
    fake_read = client.patch("/api/v1/notifications/fake_notif_999/read", headers=headers)
    assert fake_read.status_code == 404


def test_security_and_edge_cases(client: TestClient):
    # 1. Protected routes reject missing token
    protected_urls = [
        ("GET", "/api/v1/auth/me"),
        ("POST", "/api/v1/auth/logout"),
        ("GET", "/api/v1/users/me"),
        ("PUT", "/api/v1/users/me"),
        ("PATCH", "/api/v1/users/me"),
        ("POST", "/api/v1/users/me/change-password"),
        ("GET", "/api/v1/favorites"),
        ("POST", "/api/v1/favorites/dest_1"),
        ("DELETE", "/api/v1/favorites/dest_1"),
        ("GET", "/api/v1/favorites/check/dest_1"),
        ("POST", "/api/v1/reviews"),
        ("GET", "/api/v1/reviews/my-reviews"),
        ("GET", "/api/v1/notifications"),
        ("GET", "/api/v1/notifications/unread-count"),
        ("PATCH", "/api/v1/notifications/read-all"),
    ]

    for method, url in protected_urls:
        if method == "GET":
            r = client.get(url)
        elif method == "POST":
            r = client.post(url, json={})
        elif method == "PUT":
            r = client.put(url, json={})
        elif method == "PATCH":
            r = client.patch(url)
        elif method == "DELETE":
            r = client.delete(url)
        assert r.status_code in [401, 403], f"Expected 401/403 for unauthenticated {method} {url}, got {r.status_code}"

    # 2. Invalid JWT token
    bad_token = client.get("/api/v1/users/me", headers={"Authorization": "Bearer malformed.jwt.token"})
    assert bad_token.status_code == 401

    # 3. SQL Injection resistance in destination search
    sqli = client.get("/api/v1/destinations/search?q=' OR '1'='1")
    assert sqli.status_code == 200
    # SQL injection does not return all items; it matches literal search term safely
    assert len(sqli.json()["data"]) == 0
