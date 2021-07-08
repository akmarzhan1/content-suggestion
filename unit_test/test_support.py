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


def send_support(client, topic, description):
    return client.post(
        '/support',
        data=dict(
            topic=topic,
            description=description
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

def test_send_support_ticket(client):
    # test: if the login is working
    req1 = registration(client, 'user_support1', 'user_support1@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'user_support1@email.com', 'password1')
    req3 = send_support(client, 'topic', 'description')
    assert b'Thanks for entering in contact with our Support, we will reply soon!' in req3.data

def test_invalid_support_ticket(client):
    # test: if the login is working
    req1 = registration(client, 'user_support2', 'user_support2@email.com', 'password1', 'password1', 'cs162_content_suggestion3', 'akma123')
    req2 = login(client, 'user_support2@email.com', 'password1')
    req3 = send_support(client, '', '')
    assert b'This field is required.' in req3.data