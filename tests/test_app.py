import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import app

# Create a test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns the expected welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Feddit API"}


def test_health_check_endpoint():
    """Test the health check endpoint returns status ok"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_comments_router_included():
    """
    Test that the comments router is properly included
    This tests that the app has routes that would be defined in the comments module
    Note: This test assumes comments module at least defines some routes
    """
    # Get all routes in the application
    routes = [route.path for route in app.routes]

    # Check if any route contains "comments" which would indicate the router is included
    # This is a simple check and might need adjustment based on your actual route naming
    has_comments_routes = any("comments" in route for route in routes)
    assert has_comments_routes
