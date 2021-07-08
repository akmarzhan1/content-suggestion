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

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config.from_object(config[os.getenv('FLASK_ENV')])
    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_valid_registration(client):
    # test: if the registration is working
    req = registration(client, 'test0', 'username-reg-valid@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    assert b'Congrats on successful account creation' in req.data


def test_invalid_registration_username(client):
    # test: the registration shouldn't work for duplicate usernames
    req1 = registration(client, 'test2', 'username-reg-invalid1@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = registration(client, 'test2', 'username-reg-invalid2@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    assert b'This username already exists. Please choose another one or log in.' in req2.data


def test_invalid_registration_email(client):
    # test: the registration shouldn't work for duplicate emails
    req1 = registration(client, 'test1', 'username-reg-invalid@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = registration(client, 'test12', 'username-reg-invalid@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    assert b'There is a SuggestMe account associated with that email. Please use another email or log in.' in req2.data

def test_invalid_email_address(client):
    """Testing sign up with invalid email"""
    req1 = registration(client, 'test1', 'notemail', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    assert (b'Invalid email address.' in req1.data)

def test_short_registration_password(client):
    # test: the registration shouldn't work if password is too short
    req = registration(client, 'test3', 'username-reg-invalid1@test.com', '123', '123', 'cs162_content_suggestion3', 'akma123')
    assert b'Field must be between 8 and 200 characters long.' in req.data

def test_invalid_registration_password(client):
    # test: the registration shouldn't work if there is no password
    req = registration(client, 'test3', 'username-reg-invalid1@test.com', '', '', 'cs162_content_suggestion3', 'akma123')
    assert b'Sign up' in req.data

def test_wrong_password_confirmation(client):
    """Testing sign up with wrong set of passwords"""
    req = registration(client, 'test3', 'username-reg-invalid1@test.com', 'password1', 'password2', 'cs162_content_suggestion3', 'akma123')
    assert (b'Field must be equal to password.' in req.data)

def test_invalid_registration_confirm_password(client):
    # test: the registration shouldn't work if the confirmation password doesn't match the actual password
    req = registration(client, 'test4', 'username-reg-invalid1@test.com', '12345678', '123456789', 'cs162_content_suggestion3', 'akma123')
    assert b'Field must be equal to password.' in req.data

def test_wrong_email_and_password(client):
    """Testing with wrong email and wrong password confirmation"""
    req = registration(client, 'test4', 'notemail', 'password1', 'password2', 'cs162_content_suggestion3', 'akma123')
    assert (b'Invalid email address.' in req.data and b'Field must be equal to password.' in req.data)

def test_short_email_and_password(client):
    """Testing with short email and wrong password confirmation"""
    req = registration(client, 'test4', 'asdf', 'password1', 'password2', 'cs162_content_suggestion3', 'akma123')
    assert (b'Invalid email address.' in req.data and b'Field must be equal to password.' in req.data)

def test_long_email_and_wrong_password(client):
    """Testing with long email and wrong password confirmation"""
    req = registration(client, 'test4', 'verylongemailshouldntbeaccepted@verylongemail.com', 'password1', 'password2', 'cs162_content_suggestion3', 'akma123')
    assert (b'Field must be between 6 and 35 characters long.' in req.data and b'Field must be equal to password.' in req.data)
