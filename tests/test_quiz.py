from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_quiz():

    response = client.post(
        "/quiz/",
        json={
            "topic": "Python",
            "num_questions": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(data["quiz"]) > 0