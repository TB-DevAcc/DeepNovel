# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Binary, Boolean, Column, Integer, String

from app import db, login_manager
from app.base.util import hash_pass


class User(db.Model, UserMixin):

    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    firstname = Column(String, unique=False)
    lastname = Column(String, unique=False)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    phone = Column(String, unique=False)
    profile_picture = Column(
        String(20), nullable=False, default="/static/assets/images/faces/face1.jpg"
    )
    newsletter = Column(Boolean)
    posts = db.relationship("Post", backref="author", lazy=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == "password":
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")
    user = User.query.filter_by(username=username).first()
    return user if user else None


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
