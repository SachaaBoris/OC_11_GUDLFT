import pytest
from flask import get_flashed_messages
from datetime import datetime, timedelta


def test_purchase_places_after_deadline(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test that booking is disallowed after the competition's booking deadline."""
    client = mocked_client
    competitions = mocked_competitions_data

    # Mock a competition with a past booking deadline
    competition = competitions[0]
    competition_date = datetime.now() + timedelta(days=2)
    booking_deadline = competition_date - timedelta(days=2)
    competition['date'] = booking_deadline.strftime("%Y-%m-%d %H:%M:%S")
    
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': competition['name'],
            'places': '1'
        }
    )

    # Verify the booking is rejected
    assert response.status_code == 200
    flashed_messages = get_flashed_messages()
    assert "This competition is no longer bookable." in flashed_messages