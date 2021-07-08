import os, sys, tempfile, pytest
from web.config import TestingConfig, config
from web import app, db, User
from web.insights import to_list_str, to_list_int, profile, instagram_login, instagram

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


# starting the tests after setting up the testing environment

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config.from_object(config[os.getenv('FLASK_ENV')])
    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_insights(client):
    # test: if the insights page is working and handling errors properly
    req1 = registration(client, 'test6', 'username-insights@test.com', '12345678', '12345678', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'username-insights@test.com', '12345678')
    req = client.get('/insights', follow_redirects=True)
    assert req.status_code == 200

def test_to_list():
    assert to_list_int('[1, 2, 3]') == [1, 2, 3]
    assert to_list_int('[]') == None
    assert to_list_int('None') == None
    assert to_list_str('["hello", "halo", "hi"]') == ['hello', 'halo', 'hi']
    assert to_list_str('[]') == None
    assert to_list_str('None') == None
