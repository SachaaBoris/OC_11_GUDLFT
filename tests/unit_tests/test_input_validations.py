import pytest
from flask import get_flashed_messages


def test_invalid_places_input_negative(mocked_client):
    """Test handling of negative number in places field."""
    client = mocked_client
    
    # Login first
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '-1'
    })
    
    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "Places to book must be a positive integer." in flashed_messages

def test_invalid_places_input_non_numeric(mocked_client):
    """Test handling of non-numeric input in places field."""
    client = mocked_client
    
    # Login first
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': 'abc'
    })
    
    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "Invalid number of places!" in flashed_messages

def test_invalid_email_format(mocked_client):
    """Test handling of malformed email addresses."""
    response = mocked_client.post('/showSummary', data={'email': 'invalid.email.com'})
    assert response.status_code == 302  # Redirect expected
    flashed_messages = get_flashed_messages()
    assert "Sorry, that email wasn't found." in flashed_messages
