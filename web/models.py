from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Boolean, String, DateTime, Integer, Numeric, ForeignKey, Text
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

# ORM mapping
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    reset_token = db.Column(db.String(1000))
    instagram_username = db.Column(db.String(200), nullable=False)
    instagram_password = db.Column(db.String(10000), nullable=False)
    instagram_key = db.Column(db.String(200), nullable=False)
    analyze_posts = db.Column(db.Boolean, unique=False, default=True)
    media = db.Column(db.Integer(), default=None)
    followers = db.Column(db.Integer(), default=None)
    posts_update = db.Column(db.Integer(), default=None)
    likes_update = db.Column(db.Integer(), default=None)
    avg_likes_update = db.Column(db.Integer(), default=None)
    comments_update = db.Column(db.Integer(), default=None)
    hasht = db.Column(db.String(300), default=None)
    count_res = db.Column(db.String(300), default=None)
    likes_res = db.Column(db.String(300), default=None)
    comments_res = db.Column(db.String(300), default=None)
    likes = db.Column(db.String(300), default=None)
    dates = db.Column(db.String(300), default=None)
    captions = db.Column(db.String(300), default=None)
    comments = db.Column(db.String(300), default=None)
    links = db.Column(db.String(300), default=None)
    time = db.Column(db.Integer())

    def __repr__(self):
        return "<User(id={}, username={}, email={}, instagram_username={})".format(self.id, self.username, self.email, self.instagram_username)
 
 #table for keeping track of categories for each user
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keyword = db.Column(db.String(80))
