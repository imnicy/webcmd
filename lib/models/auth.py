import datetime
import random
import string

from . import Model
from functools import wraps
from providers.db import database as db
from providers.jwt import jwt
from flask import g
from ..capsule.exceptions import TokenDiscarded
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims
from werkzeug.security import generate_password_hash, check_password_hash


class User(Model):
    __tablename__ = 'iy_terminal_user_auth'

    hidden = ['password', 'remember_token']

    __status_enum__ = {
        '-1': 'off',
        '0': 'normal',
        '1': 's1',
        '2': 's2',
        '3': 's3'
    }

    supper_user = 1
    normal_user = 2

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(64), unique=True)

    password = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('iy_terminal_user_groups.id'), default=normal_user)
    gender = db.Column(db.Enum('m', 'f', '*'), default='*')
    state = db.Column(db.Enum(*__status_enum__.keys()), default='0')

    avatar = db.Column(db.String(16), nullable=True)
    fullname = db.Column(db.String(32), unique=True)
    webpage = db.Column(db.String(191), nullable=True)
    github_username = db.Column(db.String(191), nullable=True)
    remember_token = db.Column(db.String(32), nullable=True)

    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @property
    def password_source(self):
        raise AttributeError('password is not a readable attribute')

    @password_source.setter
    def password_source(self, password):
        self.password = generate_password_hash(password)

    @staticmethod
    def create(**kwargs):
        """
        create user
        :param kwargs: dict
        :return: User
        """
        if 'password' in kwargs:
            raise AttributeError('password is not a settable attribute')

        email = kwargs.get('email')
        username = kwargs.get('username')

        if email is None or username is None:
            raise AttributeError('username and email is required for create account.')

        user = User(**kwargs)

        db.session.add(user)
        db.session.commit()

        user.refresh_remember_token()

        return user

    @staticmethod
    def check_email(email):
        count = User.query.filter_by(email=email).count()
        if isinstance(count, int) and count > 0:
            return False

        return True

    @staticmethod
    def check_username(username):
        count = User.query.filter_by(username=username).count()
        if isinstance(count, int) and count > 0:
            return False

        return True

    @staticmethod
    def check_email_or_username(email, username):
        count = User.query.filter((User.email == email) | (User.username == username)).count()
        if isinstance(count, int) and count > 0:
            return False

        return True

    def update_profile(self, updates):
        """
        update user profile
        :param updates: dict
        :return: User
        """
        for k, v in updates:
            if v is not None:
                self[k] = v

        db.session.add(self)
        db.session.commit()

        if 'password' in updates:
            self.refresh_remember_token()

        return self

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def available_user(self):
        return self.state > 0

    @staticmethod
    def authenticate(email_or_username, password):
        found_user = User.query.filter_by((User.email == email_or_username) | (User.username == email_or_username))\
            .first()

        if found_user and found_user.verify_password(password):
            found_user.refresh_remember_token()
            return found_user

    def refresh_remember_token(self):
        remember = ''.join(random.sample(string.ascii_letters + string.digits, 8))

        @jwt.user_identity_loader
        def payload_identify_lookup(identify):
            return identify

        @jwt.user_claims_loader
        def add_claims_to_access_token(identify):
            return {'identify': identify, 'remember': remember}

        # update user remember token
        self.remember_token = remember

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def identify(identify, remember):
        if identify is None or remember is None:
            return None

        user_id = identify
        return User.query.filter_by(id=user_id, remember_token=remember).first()

    def __repr__(self):
        return '<User %s>' % self.username


class Group(Model):
    __tablename__ = 'iy_terminal_user_groups'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(256))
    level = db.Column(db.SmallInteger)

    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    users = db.relationship('User', backref='group', lazy='dynamic')

    def __repr__(self):
        return '<Group %s>' % self.name


def auth_required(fn):
    """
    A decorator to protect a Flask endpoint.

    If you decorate an endpoint with this, it will ensure that the requester
    has a valid access token before allowing the endpoint to be called. This
    does not check the freshness of the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = User.identify(**get_jwt_claims())

        """
        Verify the 'identify' and 'Remember' fields in the carrier 
        and authenticate the user through it
        
        If the authentication fails, the user will be notified that the session has been discarded
        """
        if user is None:
            raise TokenDiscarded('Access token has been discarded')

        """
        Put authenticated users into local proxy locals
        """
        g.user = user

        return fn(*args, **kwargs)

    return wrapper
