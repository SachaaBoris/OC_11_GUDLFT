import pytest


def test_purchase_places_updates_points(mocked_client, mocked_clubs_data):
    """Test that club points are updated after purchasing places."""
    client = mocked_client
    clubs = mocked_clubs_data

    # Base club data
    initial_points = int(clubs[0]['points'])  # Simply Lift points = 133
    places_to_purchase = 2
    expected_remaining_points = initial_points - places_to_purchase

    # Sending POST request to purchase places
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': str(places_to_purchase)
        }
    )

    # Verifying response status and updated club points
    assert response.status_code == 200

    # Points should be updated in the mocked_clubs_data
    updated_points = int(clubs[0]['points'])
    assert updated_points == expected_remaining_points  # 133 - 2 = 131
