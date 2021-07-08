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

def logout(client):
    # action: logout used
    return client.get(
        '/logout',
        follow_redirects=True)

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config.from_object(config[os.getenv('FLASK_ENV')])
    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_login_valid(client):
    # test: if the login is working
    req1 = registration(client, 'test5', 'username-login-valid@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'username-login-valid@test.com', '12345678')
    assert b'Here are your latest suggestions' in req2.data

def test_login_invalid(client):
    # test: the login shouldn't work if the person isn't registered
    req = login(client, 'username-login-invalid@test.com', '12345678')
    assert b'Please try logging in again!' in req.data

def test_login_invalid_email(client):
    # test: the login shouldn't work if the person doesn't enter an email
    req = login(client, '', 'test123')
    assert b'Login' in req.data

def test_login_short_password(client):
    # test: the login shouldn't work if the person enter a short password
    req = login(client, 'username-login-invalid@test.com', '123')
    assert b'Login' in req.data

def test_login_invalid_password(client):
    # test: the login shouldn't work if the person doesn't enter a password
    req1 = registration(client, 'test5', 'username-login-invalid@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'username-login-invalid@test.com', '')
    assert b'Login' in req2.data

def test_logout(client):
    # test: if the logout is working
    req1 = registration(client, 'test6', 'username-logout@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'username-logout@test.com', '12345678')
    req3 = logout(client)
    assert b'Login' in req3.data