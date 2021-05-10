import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'Log In' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    # User id 1 should be unable to update / delete now
    auth.login()
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(app, client, auth):
    auth.login()
    assert client.get('/create').status_code == 200

    client.post('/create', data={'title': 'created', 'body': ''})
    response = client.get('/')
    assert b'created' in response.data
    assert b'' in response.data

    with app.app_context():
        post = get_db().execute(
            "SELECT * FROM post WHERE title = 'created'"
        ).fetchone()
        assert post is not None
        assert post['body'] == ''


def test_update(app, client, auth):
    auth.login()
    assert client.get('/1/update').status_code == 200

    client.post('/1/update', data={'title': 'updated', 'body': ''})
    response = client.get('/')
    assert b'updated' in response.data
    assert b'' in response.data

    with app.app_context():
        post = get_db().execute(
            "SELECT * FROM post WHERE id = 1"
        ).fetchone()
        assert post is not None
        assert post['title'] == 'updated'
        assert post['body'] == ''


@pytest.mark.parametrize(
    ('title', 'body', 'message'),
    (
        ('', '', b'Title is required.'),
        ('', 'test_body', b'Title is required.'),
    )
)
def test_create_validate_inputs(client, auth, title, body, message):
    auth.login()
    response = client.post('/create', data={'title': title, 'body': body})
    assert message in response.data


@pytest.mark.parametrize(
    ('title', 'body', 'message'),
    (
        ('', '', b'Title is required.'),
        ('', 'test_body', b'Title is required.'),
    )
)
def test_update_validate_inputs(client, auth, title, body, message):
    auth.login()
    response = client.post('/1/update', data={'title': title, 'body': body})
    assert message in response.data


def test_delete(app, client, auth):
    auth.login()
    response = client.get('/')
    assert b'test title' in response.data

    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'
    response = client.get('/')
    assert b'test title' not in response.data

    with app.app_context():
        post = get_db().execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
