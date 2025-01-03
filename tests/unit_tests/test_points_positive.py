import pytest
from flask import get_flashed_messages


def test_purchase_places_positive_points(mocked_client, mocked_clubs_data):
    """Test that club points don't become negative."""
    client = mocked_client
    clubs = mocked_clubs_data

    # Initial club data
    initial_points = int(clubs[1]['points'])  # Iron Temple points = 4
    places_to_purchase = 6  # Attempt to purchase more places than the club can afford
    expected_remaining_points = initial_points  # Points should not change if the purchase fails

    # Simulate the purchase with more places than available points
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Iron Temple',
            'competition': 'Spring Festival',
            'places': str(places_to_purchase)
        }
    )

    # Verify that the request failed and points remain unchanged
    assert response.status_code == 200
    assert int(clubs[1]['points']) == expected_remaining_points  # 4 (initial) expected

    # Verify the flash message
    flashed_messages = get_flashed_messages()
    assert 'Not enough points!' in flashed_messages  # Flash message should indicate "Not enough points!"
