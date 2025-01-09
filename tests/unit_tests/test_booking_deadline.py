from flask import get_flashed_messages
from datetime import datetime, timedelta
from unittest.mock import patch


def test_purchase_places_after_deadline(
        mocked_client, mocked_clubs_data, mocked_competitions_data):
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


def test_purchase_places_deadline_edge_cases(
        mocked_client, mocked_competitions_data):
    """Test booking exactly at, just before, and just after deadline."""
    client = mocked_client
    competitions = mocked_competitions_data

    # Fixed competition date
    competition = competitions[0]
    # Date fixe de la compétition
    competition_date = datetime(2025, 1, 10, 12, 0, 0)
    competition['date'] = competition_date.strftime("%Y-%m-%d %H:%M:%S")

    # Test case 1: Just before deadline (should ok)
    test_time = competition_date - timedelta(days=1, seconds=1)
    with patch('server.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.strptime = datetime.strptime

        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': competition['name'],
            'places': '1'
        })
        assert response.status_code == 200
        flashed_messages = get_flashed_messages()
        print(f"\nTest case 1 - Current time: {test_time}")
        print(f"Flashed messages: {flashed_messages}")
        assert "Great-booking complete!" in flashed_messages

    # Test case 2: Exactly at deadline (should ko)
    test_time = competition_date - timedelta(days=1)
    with patch('server.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.strptime = datetime.strptime

        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': competition['name'],
            'places': '1'
        })
        assert response.status_code == 200
        flashed_messages = get_flashed_messages()
        assert "This competition is no longer bookable." in flashed_messages

    # Test case 3: Just after deadline (should ko)
    test_time = competition_date - timedelta(days=1) + timedelta(seconds=1)
    with patch('server.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.strptime = datetime.strptime

        response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': competition['name'],
            'places': '1'
        })
        assert response.status_code == 200
        flashed_messages = get_flashed_messages()
        print(f"\nTest case 3 - Current time: {test_time}")
        print(f"Flashed messages: {flashed_messages}")
        assert "This competition is no longer bookable." in flashed_messages
