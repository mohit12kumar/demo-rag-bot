from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_endpoint_exists():

    response = client.get("/")

    assert response.status_code == 200