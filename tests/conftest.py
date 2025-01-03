import sys
import os
import pytest

# Adding root project folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from server import app, loadClubs, loadCompetitions


# Fixtures
@pytest.fixture
def unknown_client():
    """Furnishes Flask unauthentified client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mocked_clubs_data():
    """Furnishes mocked clubs data."""
    return [
        {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "133"
        },
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "4"
        },
        {
            "name": "She Lifts",
            "email": "kate@shelifts.co.uk",
            "points": "12"
        }
    ]


@pytest.fixture
def mocked_competitions_data():
    """Furnishes mocked competitions data."""
    return [
        {
            "name": "Winter SkiLïft",
            "date": "2025-02-15 10:00:00",
            "numberOfPlaces": "13"
        },
        {
            "name": "Spring Festival",
            "date": "2024-03-27 10:00:00",
            "numberOfPlaces": "13"
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "0"
        }
    ]


@pytest.fixture
def mocked_client(monkeypatch, mocked_clubs_data, mocked_competitions_data):
    """Furnishes Flask client with mocked data."""
    def mock_load_clubs():
        return mocked_clubs_data

    def mock_load_competitions():
        return mocked_competitions_data

    # Mocking data
    monkeypatch.setattr('server.clubs', mocked_clubs_data)
    monkeypatch.setattr('server.competitions', mocked_competitions_data)
    monkeypatch.setattr('server.loadClubs', mock_load_clubs)
    monkeypatch.setattr('server.loadCompetitions', mock_load_competitions)

    # Tests app.config
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        yield client
