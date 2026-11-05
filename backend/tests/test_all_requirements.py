import pytest
from fastapi.testclient import TestClient


def test_1_user_registration(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Traveler",
            "email": "traveler@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "traveler@example.com"
    assert "hashed_password" not in data["data"]


def test_2_duplicate_email_rejection(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate Traveler",
            "email": "traveler@example.com",
            "password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!",
        },
    )
    assert response.status_code == 409
    assert response.json()["success"] is False


def test_3_login_successful(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "traveler@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["email"] == "traveler@example.com"


def test_4_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "traveler@example.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_5_and_6_jwt_authentication_and_get_current_user(client: TestClient):
    # Login first
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "traveler@example.com",
            "password": "SecurePassword123!",
        },
    )
    token = login_res.json()["data"]["access_token"]

    # Call /auth/me with Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["data"]["email"] == "traveler@example.com"


def test_7_destination_listing(client: TestClient):
    response = client.get("/api/v1/destinations")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert data["meta"]["total"] >= 9


def test_8_destination_details(client: TestClient):
    response = client.get("/api/v1/destinations/dest_1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Bali"
    assert data["data"]["country"] == "Indonesia"


def test_9_search_destinations(client: TestClient):
    response = client.get("/api/v1/destinations?search=Bali")
    assert response.status_code == 200
    data = response.json()
    assert any(d["name"] == "Bali" for d in data["data"])

    # Search endpoint
    search_res = client.get("/api/v1/destinations/search?q=Alps")
    assert search_res.status_code == 200
    assert any("Alps" in d["name"] for d in search_res.json()["data"])


def test_10_category_filtering(client: TestClient):
    response = client.get("/api/v1/destinations?category=Beaches")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) > 0
    assert all(d["category"] == "Beaches" for d in data["data"])


def test_11_rating_filtering(client: TestClient):
    response = client.get("/api/v1/destinations?min_rating=4.9")
    assert response.status_code == 200
    data = response.json()
    assert all(d["rating"] >= 4.9 for d in data["data"])


def test_12_and_13_add_favorite_and_duplicate_prevention(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add favorite
    add_res = client.post("/api/v1/favorites/dest_2", headers=headers)
    assert add_res.status_code in [200, 201]

    # Duplicate add returns safely without error
    dup_res = client.post("/api/v1/favorites/dest_2", headers=headers)
    assert dup_res.status_code in [200, 201]

    # Check favorite
    check_res = client.get("/api/v1/favorites/check/dest_2", headers=headers)
    assert check_res.status_code == 200
    assert check_res.json()["data"]["is_saved"] is True


def test_14_remove_favorite(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    del_res = client.delete("/api/v1/favorites/dest_2", headers=headers)
    assert del_res.status_code == 200

    check_res = client.get("/api/v1/favorites/check/dest_2", headers=headers)
    assert check_res.json()["data"]["is_saved"] is False


def test_15_user_specific_favorites(client: TestClient):
    # Register user 2
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "User Two",
            "email": "user2@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    login2 = client.post(
        "/api/v1/auth/login",
        json={"email": "user2@example.com", "password": "Password123!"},
    )
    token2 = login2.json()["data"]["access_token"]

    # User 2 saves dest_3
    client.post("/api/v1/favorites/dest_3", headers={"Authorization": f"Bearer {token2}"})

    # User 2 favorites list
    favs_res = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {token2}"})
    assert favs_res.status_code == 200
    dest_ids = [d["id"] for d in favs_res.json()["data"]]
    assert "dest_3" in dest_ids

    # User 1 should not see dest_3
    login1 = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token1 = login1.json()["data"]["access_token"]
    favs1_res = client.get("/api/v1/favorites", headers={"Authorization": f"Bearer {token1}"})
    assert "dest_3" not in [d["id"] for d in favs1_res.json()["data"]]


def test_16_profile_update(client: TestClient):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update full name
    update_res = client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Updated Traveler Name"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["full_name"] == "Updated Traveler Name"


def test_17_review_creation_and_validation(client: TestClient):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid rating (> 5)
    invalid_res = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={"destination_id": "dest_1", "rating": 6.0, "comment": "Too high!"},
    )
    assert invalid_res.status_code == 422

    # Valid review
    valid_res = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={"destination_id": "dest_1", "rating": 5.0, "comment": "Breathtaking experience!"},
    )
    assert valid_res.status_code == 201
    assert valid_res.json()["data"]["rating"] == 5.0


def test_18_notification_functionality(client: TestClient):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "traveler@example.com", "password": "SecurePassword123!"},
    )
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    notices_res = client.get("/api/v1/notifications", headers=headers)
    assert notices_res.status_code == 200
    assert len(notices_res.json()["data"]) >= 1

    unread_res = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_res.status_code == 200
    assert unread_res.json()["data"]["unread_count"] >= 1

    # Mark all read
    read_all = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert read_all.status_code == 200

    unread_res2 = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_res2.json()["data"]["unread_count"] == 0


def test_19_unauthorized_api_access(client: TestClient):
    # Without token
    no_token = client.get("/api/v1/users/me")
    assert no_token.status_code == 401

    # Invalid token
    bad_token = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token_xyz"},
    )
    assert bad_token.status_code == 401
