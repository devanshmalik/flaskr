import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class BlogActions(object):
    def __init__(self, client, auth):
        self._client = client
        self._auth = auth
        self._auth.login()

    def create(self, title='test_title 2', body='test_body 2'):
        return self._client.post(
            '/create',
            data={'title': title, 'body': body}
        )

    def update(self, title='updated_title_1', body='updated_body_1'):
        return self._client.post(
            '/1/update',
            data={'title': title, 'body': body}
        )

    def delete(self):
        return self._client.post(
            '/1/delete'
        )


@pytest.fixture
def blog(client, auth):
    return BlogActions(client, auth)




class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)