import pytest
from datetime import datetime, timedelta


def test_booking_deadline_client(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test that expired competitions do not show a booking button."""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data
    
    # Login
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # Ensure "Book Places" link is not present in the response for competition[4]
    assert response.status_code == 200
    assert f'<a href="/book/{competitions[4]["name"]}/Simply Lift">' not in response.data.decode('utf-8')