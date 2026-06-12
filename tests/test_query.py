from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_query():

    response = client.post(
        "/query/",
        json={
            "user_id": 1,
            "question": "What is FastAPI?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True