import pytest
from flask import get_flashed_messages


def test_booking_tracking_flow_cannot_exceed(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test the complete booking flow with tracking"""
    client = mocked_client
    clubs = mocked_clubs_data
    competitions = mocked_competitions_data

    # 1. Initialize tracker & login
    with client.session_transaction() as sess:
        sess.clear()
        sess['booking_tracker'] = [{"name": comp["name"], "alreadyBooked": "0"} for comp in competitions]
    login_response = client.post('/showSummary', data={
            'email': 'john@simplylift.co'
    }, follow_redirects=True)
    assert login_response.status_code == 200

    # 2. Make first booking
    first_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],  # Winter SkiLïft
        'places': '5'
    })
    assert first_booking.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'Great-booking complete!' in flashed_messages

    # 3. Try to exceed limit
    second_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'], # Winter SkiLïft
        'places': '8'
    })
    assert second_booking.status_code == 200
    
    flashed_messages = get_flashed_messages()
    assert "Clubs are limited to 12 places for one competition." in flashed_messages
    
    # Verify session data
    with client.session_transaction() as sess:
        tracker = sess['booking_tracker']
        spring_booking = next(b for b in tracker if b['name'] == 'Winter SkiLïft')
        assert spring_booking['alreadyBooked'] == '5'  # Should not have changed


def test_multiple_competitions_tracking(mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test tracking bookings across multiple competitions"""
    client = mocked_client
    clubs = mocked_clubs_data
    competitions = mocked_competitions_data

    # 1. Initialize tracker & login
    with client.session_transaction() as sess:
        sess.clear()
        sess['booking_tracker'] = [{"name": comp["name"], "alreadyBooked": "0"} for comp in competitions]
    login_response = client.post('/showSummary', data={
            'email': 'john@simplylift.co'
    }, follow_redirects=True)
    assert login_response.status_code == 200

    # 2. Make first booking
    first_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],  # Winter SkiLïft
        'places': '5'
    })
    assert first_booking.status_code == 200
    flashed_messages = get_flashed_messages()
    assert 'Great-booking complete!' in flashed_messages

    # Verify session data
    with client.session_transaction() as sess:
        tracker = sess.get('booking_tracker', [])
        spring_booking = next((b for b in tracker if b['name'] == 'Spring Festival'), None)
        winter_booking = next((b for b in tracker if b['name'] == 'Winter SkiLïft'), None)
        summer_booking = next((b for b in tracker if b['name'] == 'SummerIs Magic'), None)
        assert winter_booking['alreadyBooked'] == '5'
        assert spring_booking['alreadyBooked'] == '0'
        assert summer_booking['alreadyBooked'] == '0'

    # 3. Try to exceed limit
    second_booking = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[2]['name'], # Spring Festival
        'places': '10'
    })

    # Verify session data
    with client.session_transaction() as sess:
        tracker = sess.get('booking_tracker', [])
        spring_booking = next((b for b in tracker if b['name'] == 'Spring Festival'), None)
        winter_booking = next((b for b in tracker if b['name'] == 'Winter SkiLïft'), None)
        summer_booking = next((b for b in tracker if b['name'] == 'SummerIs Magic'), None)
        assert spring_booking['alreadyBooked'] == '10'
        assert winter_booking['alreadyBooked'] == '5'
        assert summer_booking['alreadyBooked'] == '0'
