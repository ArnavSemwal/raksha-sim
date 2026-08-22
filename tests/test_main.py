from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_patients():
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert "vitals" in data
    assert "triage_results" in data
