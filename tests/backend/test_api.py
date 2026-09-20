import pytest
from fastapi.testclient import TestClient

from src.app import DEFAULT_ACTIVITIES, create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activity_details(client):
    # Arrange
    expected_activity = DEFAULT_ACTIVITIES["Chess Club"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"] == expected_activity


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = DEFAULT_ACTIVITIES[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity():
    # Arrange
    activity_name = "Full Club"
    activity_data = {
        activity_name: {"max_participants": 1, "participants": ["existing@example.com"]}
    }
    client = TestClient(create_app(activity_data))

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "new@example.com"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Soccer Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    test_email = "newstudent@mergington.edu"
    client = TestClient(create_app())

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    unregister_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": test_email}
    )

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {test_email} from {activity_name}"

    activities = client.get("/activities").json()
    assert test_email not in activities[activity_name]["participants"]


def test_unregister_participant_returns_404_when_not_found():
    # Arrange
    activity_name = "Soccer Club"
    missing_email = "ghost@mergington.edu"
    client = TestClient(create_app())

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_requires_email(client):
    # Arrange
    activity_name = "Soccer Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants")

    # Assert
    assert response.status_code == 422
