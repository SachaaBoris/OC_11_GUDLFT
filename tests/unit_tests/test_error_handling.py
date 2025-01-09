import pytest
from flask import get_flashed_messages


def test_missing_post_data(mocked_client):
    """Test handling of missing POST data in purchasePlaces."""
    client = mocked_client
    
    # Login first
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    # Missing 'places' field
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival'
        }
    )
    
    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "An unexpected error occurred. Please try again." in flashed_messages

def test_invalid_club_competition_combination(mocked_client):
    """Test handling of invalid club/competition combination."""
    client = mocked_client
    
    # Login first
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    # Invalid club
    response = client.post(
        '/purchasePlaces', 
        data={
            'club': 'NonExistentClub',
            'competition': 'Spring Festival',
            'places': '1'
        }
    )
    
    # Check redirection
    assert response.status_code == 302
    flashed_messages = get_flashed_messages()
    assert "Competition or club not found!" in flashed_messages