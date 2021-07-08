import os, sys, tempfile, pytest
from web.config import TestingConfig, config
from web import app, db

sys.path.append(os.path.dirname(__file__))

def registration(client, username, email, password, password_confirm, instagram_username, instagram_password):
    # action: registration used for the tests
    return client.post(
        '/register',
        data=dict(
                username=username, 
                email=email,
                password=password, 
                password_confirm=password_confirm, 
                instagram_username=instagram_username,
                instagram_password=instagram_password
        ),
        follow_redirects=True)

def login(client, email, password):
    # action: login used for the tests
    return client.post(
        '/login',
        data=dict(email=email, password=password),
        follow_redirects=True)

def update_username(client, new_username):
    return client.post(
        '/update_username',
        data=dict(new_username=new_username),
        follow_redirects=True
    )

def update_email(client, new_email):
    return client.post(
        '/update_email',
        data=dict(new_email=new_email),
        follow_redirects=True
    )

def update_password(client, new_password, new_password_confirm):
    return client.post(
        '/update_password',
        data=dict(
            new_password=new_password,
            new_password_confirm=new_password_confirm
        ),
        follow_redirects=True
    )

def update_instagram_username(client, new_instagram_username):
    return client.post(
        '/update_instagram_username',
        data=dict(
            new_instagram_username=new_instagram_username,
        ),
        follow_redirects=True
    )

def update_instagram_password(client, new_instagram_password):
    return client.post(
        '/update_instagram_password',
        data=dict(
            new_instagram_password=new_instagram_password,
        ),
        follow_redirects=True
    )

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config.from_object(config[os.getenv('FLASK_ENV')])
    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_update_username(client):
    # test: if the login is working
    req1 = registration(client, 'old_username', 'update_username@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'update_username@email.com', 'password1')
    req3 = update_username(client, 'new_username')
    assert b'Username updated to:' in req3.data

def test_update_email(client):
    # test: if the login is working
    req1 = registration(client, 'user1', 'old_email@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'old_email@email.com', 'password1')
    req3 = update_email(client, 'new_email@email.com')
    assert b'Email updated to:' in req3.data

def test_update_password(client):
    # test: if the login is working
    req1 = registration(client, 'user2', 'email2@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'email2@email.com', 'password1')
    req3 = update_password(client, 'password2', 'password2')
    assert b'Password updated' in req3.data

def test_update_instagram_username(client):
    # test: if the login is working
    req1 = registration(client, 'user3', 'email3@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'email3@email.com', 'password1')
    req3 = update_instagram_username(client, 'new_instagram_username')
    assert b'Instagram username updated to:' in req3.data

def test_update_instagram_password(client):
    # test: if the login is working
    req1 = registration(client, 'user4', 'email4@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'email4@email.com', 'password1')
    req3 = update_instagram_password(client, 'new_instagram_password')
    assert b'Instagram password updated.' in req3.data
