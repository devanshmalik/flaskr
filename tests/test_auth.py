# from flaskr.auth import
import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        user = get_db().execute(
            "SELECT * FROM user WHERE username = 'a'"
        ).fetchone()
        assert user['username'] == 'a'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', b'Username is required.'),
        ('admin', '', b'Password is required.'),
        ('test', 'test', b'already registered.'),
    )
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data
    # assert message in response.get_data(as_text=True)


def test_login_successful(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', b'Incorrect username'),
        ('admin', '', b'Incorrect username'),
        ('test', '', b'Incorrect password'),
        ('test', 'wrong_password', b'Incorrect password'),
    )
)
def test_login_validate_input(auth, username, password, message):
    # response = client.post(
    #     '/auth/login',
    #     data={'username': username, 'password': password}
    # )
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session