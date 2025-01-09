#pytest tests/integration_tests/test_navigation_flow_and_redirection.py
import pytest
from flask import get_flashed_messages


def test_complete_navigation_flow(mocked_client):
    """Test all major navigation paths."""
    client = mocked_client
    
    # 1. Start at index
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the GUDLFT Registration Portal!' in response.data
    
    # 2. Login
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b'Welcome, john@simplylift.co' in response.data
    
    # 3. Navigate to booking page
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200
    assert b'How many places?' in response.data
    
    # 4. Check board access
    response = client.get('/board')
    assert response.status_code == 200
    assert b'Club Points Board' in response.data
    
    # 5. Logout
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location == '/'

def test_invalid_club_redirect(mocked_client):
    """Test invalid club redirection."""
    client = mocked_client

    # Login
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Access book URL with invalid club
    response = client.get('/book/SummerIs%20Magic/NonExistentClub', follow_redirects=True)

    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "Invalid club or competition. Please log in again." in flashed_messages
    assert b"Please enter your secretary email to continue:" in response.data  # Verify the login page is displayed


def test_invalid_competition_redirect(mocked_client):
    """Test invalid competition redirection."""
    client = mocked_client

    # Login
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Access book URL with invalid competition
    response = client.get('/book/NonExistentCompetition/Simply%20Lift', follow_redirects=True)

    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "Invalid club or competition. Please log in again." in flashed_messages
    assert b"Please enter your secretary email to continue:" in response.data  # Verify the login page is displayed
