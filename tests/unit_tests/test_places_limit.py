from flask import get_flashed_messages


def test_max_places_limit(
        mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test that a user cannot book more than maxPlaces"""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data

    # Login first to initialize session
    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    # First booking
    client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '10'
    })

    # Try to exceed limit
    response = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '3'  # Would exceed maxPlaces (10 + 3 > 12)
    })
    assert response.status_code == 200

    flashed_messages = get_flashed_messages()
    assert "Clubs are limited to 12 places for one competition." in flashed_messages


def test_competition_full(
        mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test handling when the competition has no available places"""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data

    client.post('/showSummary', data={'email': 'john@simplylift.co'})

    response = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[3]['name'],
        'places': '12'
    })
    assert response.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'This competition is full.' in flashed_messages


def test_not_enough_places(
        mocked_client, mocked_clubs_data, mocked_competitions_data):
    """Test handling when requesting more competition places than available"""
    client = mocked_client
    clubs = mocked_clubs_data  # Load mock club data
    competitions = mocked_competitions_data  # Load mock competition data

    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    competitions[1]['numberOfPlaces'] = '11'

    response = client.post('/purchasePlaces', data={
        'club': clubs[0]['name'],
        'competition': competitions[1]['name'],
        'places': '12'
    })
    assert response.status_code == 200

    flashed_messages = get_flashed_messages()
    assert 'This competition does not have this amount available.' in flashed_messages
