import os, sys, tempfile, pytest
from web.config import TestingConfig, config
from web import app, db
import requests
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import extract, func, text, cast, Date

sys.path.append(os.path.dirname(__file__))

APP_URL = "http://127.0.0.1:5000"

connStr = "mysql+pymysql://root:test_password@127.0.0.1:3306/main"
dbengine = create_engine(connStr)

Base = declarative_base()
metadata = MetaData()

Session = sessionmaker(bind=dbengine)
session = Session()

# Instantiating tables
Categories = Table("category", metadata, autoload=True, autoload_with=dbengine)
User = Table("user", metadata, autoload=True, autoload_with=dbengine)


@pytest.fixture
def client():
    pass

def test_reset(client):
    req = requests.post(APP_URL+"/register", data={
        'username': 'test2', 
        'email': 'test2@email.com', 
        'password': 'asdjfhaoisdfj', 
        'password_confirm': 'asdjfhaoisdfj', 
        'instagram_username': 'user_test',
        'instagram_password': 'user_password'
    })
    # should have user registered
    assert(req.status_code == 200)

    req = requests.post(APP_URL+"/reset", data={
        'email': 'test1@email.com', 
    })
    # should try to reset email
    assert(req.status_code == 200)


    # checking if user was added in DB
    user = session.query(User).filter_by(
        username="test2",
        email="test2@email.com",
    ).first()

    assert(user.reset_token!="")