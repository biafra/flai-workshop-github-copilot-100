"""
Tests for the Mergington High School FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self, client: TestClient):
        response = client.get("/activities")
        assert response.status_code == 200

    def test_returns_dict(self, client: TestClient):
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_contains_expected_activities(self, client: TestClient):
        response = client.get("/activities")
        data = response.json()
        expected = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Art Club",
            "Drama Society",
            "Math Olympiad",
            "Debate Club",
        ]
        for name in expected:
            assert name in data, f"Expected activity '{name}' not found"

    def test_activity_has_required_fields(self, client: TestClient):
        response = client.get("/activities")
        data = response.json()
        for name, details in data.items():
            assert "description" in details, f"'{name}' missing 'description'"
            assert "schedule" in details, f"'{name}' missing 'schedule'"
            assert "max_participants" in details, f"'{name}' missing 'max_participants'"
            assert "participants" in details, f"'{name}' missing 'participants'"


# ---------------------------------------------------------------------------
# GET / (redirect)
# ---------------------------------------------------------------------------

class TestRoot:
    def test_redirects_to_static(self, client: TestClient):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (301, 302, 307, 308)
        assert response.headers["location"].endswith("/static/index.html")


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_successful_signup(self, client: TestClient):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "message" in body
        assert "newstudent@mergington.edu" in body["message"]

    def test_signup_adds_participant(self, client: TestClient):
        email = "newstudent@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert email in participants

    def test_signup_nonexistent_activity_returns_404(self, client: TestClient):
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404

    def test_signup_nonexistent_activity_error_detail(self, client: TestClient):
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_returns_400(self, client: TestClient):
        # michael@mergington.edu is already in Chess Club participants
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400

    def test_duplicate_signup_error_detail(self, client: TestClient):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.json()["detail"] == "Student already signed up"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_successful_unregister(self, client: TestClient):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "message" in body
        assert "michael@mergington.edu" in body["message"]

    def test_unregister_removes_participant(self, client: TestClient):
        email = "michael@mergington.edu"
        client.delete("/activities/Chess Club/signup", params={"email": email})
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert email not in participants

    def test_unregister_nonexistent_activity_returns_404(self, client: TestClient):
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_activity_error_detail(self, client: TestClient):
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_enrolled_returns_404(self, client: TestClient):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "noone@mergington.edu"},
        )
        assert response.status_code == 404

    def test_unregister_not_enrolled_error_detail(self, client: TestClient):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "noone@mergington.edu"},
        )
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_signup_then_unregister_roundtrip(self, client: TestClient):
        email = "roundtrip@mergington.edu"
        signup = client.post("/activities/Art Club/signup", params={"email": email})
        assert signup.status_code == 200

        unregister = client.delete("/activities/Art Club/signup", params={"email": email})
        assert unregister.status_code == 200

        activities_response = client.get("/activities")
        participants = activities_response.json()["Art Club"]["participants"]
        assert email not in participants
