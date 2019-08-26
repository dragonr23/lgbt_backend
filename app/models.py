from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from time import time
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    zipcode = db.Column(db.String(20))
    sexuality= db.Column(db.String(50))
    gender = db.Column(db.String(50))
    religion = db.Column(db.String(50))


    def set_password(self, password):
        self.password_hash =generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


    # create a method for generating a token and verifying that token

    def get_token(self, expires_in=86400):
        return jwt.encode(
            { 'user_id': self.id, 'exp': time() + expires_in },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms =['HS256']
            )['user_id']

        except:
            return

        return User.query.get(id)

class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    date_sent = db.Column(db.DateTime, default=datetime.now().date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reciever_id = db.Column(db.Integer)
    message = db.Column(db.String(500))
