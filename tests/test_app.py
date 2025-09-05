"""Basic application tests for QR Info Portal."""
import pytest
from app import create_app
from app.database import init_database


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })
    
    with app.app_context():
        init_database()
    
    yield app


@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()


def test_app_creation(app):
    """Test app creation."""
    assert app is not None
    assert app.config["TESTING"] is True


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["service"] == "qr-info-portal"


def test_homepage_loads(client):
    """Test that homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    # Check for some expected content
    assert b"QR" in response.data or b"Portal" in response.data


def test_admin_requires_auth(client):
    """Test that admin pages require authentication."""
    response = client.get("/admin")
    assert response.status_code == 401


def test_qr_endpoint(client):
    """Test QR code generation endpoint."""
    response = client.get("/qr")
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_week_view(client):
    """Test week view loads."""
    response = client.get("/week")
    assert response.status_code == 200


def test_month_view(client):
    """Test month view loads."""
    response = client.get("/month")
    assert response.status_code == 200


def test_404_error(client):
    """Test 404 error handling."""
    response = client.get("/nonexistent-page")
    assert response.status_code == 404


def test_language_switching(client):
    """Test language switching functionality."""
    response = client.get("/set-language/en", follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get("/set-language/th", follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get("/set-language/de", follow_redirects=True) 
    assert response.status_code == 200