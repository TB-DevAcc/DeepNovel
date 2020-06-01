# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, TextField
from wtforms.validators import DataRequired, Email, InputRequired, Optional

## login and registration


class LoginForm(FlaskForm):
    username = TextField("Username", id="username_login", validators=[DataRequired()])
    password = PasswordField("Password", id="pwd_login", validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    firstname = TextField(
        "Firstname", id="firstname_create", validators=[DataRequired(), Optional()]
    )
    lastname = TextField("Lastname", id="lastname_create", validators=[DataRequired(), Optional()])
    username = TextField("Username", id="username_create", validators=[DataRequired()])
    email = TextField("Email", id="email_create", validators=[DataRequired(), Email()])
    password = PasswordField("Password", id="pwd_create", validators=[DataRequired()])
    phone = TextField("Phonenumber", id="phone_create", validators=[DataRequired(), Optional()])
    newsletter = BooleanField(
        "Newsletter", id="pwd_create", validators=[DataRequired(), Optional()]
    )


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")
