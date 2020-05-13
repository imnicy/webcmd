import datetime
from providers.db import database as db
from werkzeug.security import generate_password_hash, check_password_hash

Base = db.Model


class User(Base):
    __tablename__ = 'iy_terminal_user_auth'

    __status_enum__ = {
        '-1': 'off',
        '0': 'normal',
        '1': 's1',
        '2': 's2',
        '3': 's3'
    }

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(64), unique=True)

    password = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('iy_terminal_user_groups.id'))
    gender = db.Column(db.Enum('m', 'f', '*'))
    state = db.Column(db.Enum(*__status_enum__.keys()))

    avatar = db.Column(db.String(16), nullable=True)
    fullname = db.Column(db.String(32), unique=True)
    webpage = db.Column(db.String(191), nullable=True)
    github = db.Column(db.String(191), nullable=True)
    remember_token = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @property
    def password_source(self):
        raise AttributeError('password is not a readable attribute')

    @password_source.setter
    def password_source(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def available_user(self):
        return self.state > 0

    def __repr__(self):
        return '<User %s>' % self.username


class Group(Base):
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
