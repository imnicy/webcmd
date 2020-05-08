from . import database as db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.Integer)
    city = db.Column(db.String)

    def __repr__(self):
        return '<User %s>' % self.name
