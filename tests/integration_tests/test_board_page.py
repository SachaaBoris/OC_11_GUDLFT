import pytest

def test_board_page(unknown_client, mocked_client, mocked_clubs_data):
    clubs = mocked_clubs_data  # Load mock club data
    
    # Not connected guest
    client = unknown_client
    response = client.get('/board')
    assert response.status_code == 200
    assert b'<h2>Club Points Board</h2>' in response.data
    assert b'Simply Lift' in response.data
    assert b'Return to Login Page' in response.data

    # Connected guest
    client = mocked_client
    with client.session_transaction() as sess:
        sess['email'] = 'john@simplylift.co'
    response = client.get('/board')
    assert response.status_code == 200
    assert b'<h2>Club Points Board</h2>' in response.data
    assert b'Simply Lift' in response.data
    assert b'Return to Login Page' in response.data