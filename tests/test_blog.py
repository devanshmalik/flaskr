import pytest
from flaskr.db import get_db


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'test title' in response.data


def test_create(app, client, blog):
    response = blog.create()
    assert response.headers['Location'] == 'http://localhost/'

    response = client.get('/')
    assert b'test_title 2' in response.data
    assert b'test_body 2' in response.data

    with app.app_context():
        post = get_db().execute(
            "SELECT * FROM post WHERE title = 'test_title 2'"
        ).fetchone()
        assert post is not None
        assert post['body'] == 'test_body 2'


@pytest.mark.parametrize(
    ('title', 'body', 'message'),
    (
        ('', '', b'Title is required.'),
        ('', 'test_body', b'Title is required.'),
    )
)
def test_create_validate_inputs(blog, title, body, message):
    response = blog.create(title, body)
    assert message in response.data


def test_update(app, client, blog):
    response = blog.update()
    assert response.headers['Location'] == 'http://localhost/'

    response = client.get('/')
    assert b'updated_title_1' in response.data
    assert b'updated_body_1' in response.data

    with app.app_context():
        post = get_db().execute(
            "SELECT * FROM post WHERE id = 1"
        ).fetchone()
        assert post is not None
        assert post['title'] == 'updated_title_1'


@pytest.mark.parametrize(
    ('title', 'body', 'message'),
    (
        ('', '', b'Title is required.'),
        ('', 'test_body', b'Title is required.'),
    )
)
def test_update_validate_inputs(blog, title, body, message):
    response = blog.update(title, body)
    assert message in response.data


def test_delete(app, client, blog):
    response = client.get('/')
    assert b'test title' in response.data

    response = blog.delete()
    assert response.headers['Location'] == 'http://localhost/'

    response = client.get('/')
    assert b'test title' not in response.data
