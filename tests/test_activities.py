"""Backend tests for the Mergington High School activities API."""

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    # Arrange: snapshot participant lists so each test starts clean
    snapshot = {
        name: details["participants"][:] for name, details in activities.items()
    }
    test_client = TestClient(app)
    yield test_client
    for name, people in snapshot.items():
        activities[name]["participants"] = people


def test_list_activities(client):
    # Arrange
    expected_names = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for name in expected_names:
        assert name in data
        assert "description" in data[name]
        assert "participants" in data[name]
        assert "schedule" in data[name]
        assert "max_participants" in data[name]


def test_signup_for_activity(client):
    # Arrange
    activity = "Science Club"
    email = "newstudent@mergington.edu"
    before = len(activities[activity]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == before + 1


def test_duplicate_signup_rejected(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    before = activities[activity]["participants"][:]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert activities[activity]["participants"] == before


def test_unregister_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant(client):
    # Arrange
    activity = "Drama Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
