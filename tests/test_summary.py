from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_summary():

    response = client.post(
        "/summary/",
        json={
            "topic": "FastAPI"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True