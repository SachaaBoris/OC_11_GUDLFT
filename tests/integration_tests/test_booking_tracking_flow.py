import pytest
from flask import get_flashed_messages


def test_booking_tracking_flow(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test the complete booking flow with tracking"""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data

    # 1. Login to initialize tracker
    login_response = client.post('/showSummary', data={
            'email': 'john@simplylift.co'
    })
    assert login_response.status_code == 200

    # 2. Make first booking
    first_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '5'
    })
    assert first_booking.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'Great-booking complete!' in flashed_messages

    # 3. Try to exceed limit
    second_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '8'
    })
    assert second_booking.status_code == 200

    flashed_messages = get_flashed_messages()
    assert "Clubs are limited to 12 places for one competition." in flashed_messages

    # Verify session data
    with client.session_transaction() as sess:
        tracker = sess['booking_tracker']
        spring_booking = next(b for b in tracker if b['name'] == 'Spring Festival')
        assert spring_booking['alreadyBooked'] == '5'  # Should not have changed


def test_multiple_competitions_tracking(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test tracking bookings across multiple competitions"""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data

    # 1. Login to initialize tracker
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # 2. Book places in first competition
    first_response = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '5'
    })
    assert first_response.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'Great-booking complete!' in flashed_messages
    
    # 3. Book places in second competition
    second_response = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[0]['name'],
        'places': '10'
    })
    assert second_response.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'Great-booking complete!' in flashed_messages

    # Verify tracking for both competitions
    with client.session_transaction() as sess:
        tracker = sess.get('booking_tracker', [])
        spring_booking = next((b for b in tracker if b['name'] == 'Spring Festival'), None)
        winter_booking = next((b for b in tracker if b['name'] == 'Winter SkiLïft'), None)

        assert spring_booking is not None and spring_booking['alreadyBooked'] == '5'
        assert winter_booking is not None and winter_booking['alreadyBooked'] == '10'
