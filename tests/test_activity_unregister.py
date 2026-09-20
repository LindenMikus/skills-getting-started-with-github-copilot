from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    test_email = "newstudent@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert signup_response.status_code == 200

    unregister_response = client.delete(f"/activities/{activity_name}/participants?email={test_email}")
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {test_email} from {activity_name}"

    activities = client.get("/activities").json()
    assert test_email not in activities[activity_name]["participants"]


def test_unregister_participant_returns_404_when_not_found():
    activity_name = "Soccer Club"
    missing_email = "ghost@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
