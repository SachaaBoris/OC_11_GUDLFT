# tests/test_server.py
from flask import get_flashed_messages


# HTTP method restrictions
def test_protected_summary_access(unknown_client):
    """Test protected summary route with unauthentified user."""
    response = unknown_client.get('/showSummary')
    assert response.status_code == 405  # Not allowed


def test_protected_purchase_access(unknown_client):
    """Test protected purchase route with unauthentified user."""
    response = unknown_client.get('/purchasePlaces')
    assert response.status_code == 405  # Not allowed

# Mail authentication


def test_show_summary_with_valid_email(mocked_client):
    """Test summary route with valid email."""
    response = mocked_client.post(
        '/showSummary',
        data={
            'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b'Welcome, john@simplylift.co' in response.data


def test_show_summary_with_invalid_email(mocked_client):
    """Test summary route with invalid email."""
    response = mocked_client.post(
        '/showSummary',
        data={
            'email': 'invalid@email.com'})
    assert response.status_code == 302  # Redirect
    flashed_messages = get_flashed_messages()
    assert 'Sorry, that email wasn\'t found.' in flashed_messages


def test_show_summary_with_empty_email(mocked_client):
    """Test summary route with empty email."""
    response = mocked_client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302  # Redirect
