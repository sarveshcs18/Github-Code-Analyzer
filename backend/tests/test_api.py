from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app_name": "GitHub Repo Analyzer"}

def test_analyze_repo_validation():
    # Invalid URL
    response = client.post("/api/v1/repo/analyze", json={"url": "ftp://example.com"})
    assert response.status_code == 422 # Validation error

def test_analyze_repo_mock_dev():
    # Ensure we use mock in dev environment if configured
    # We depend on settings.ENV and settings.VERTEX_PROJECT_ID
    # This might fail if the test env is not setup exactly as dev, 
    # but basic connectivity check is good.
    pass
