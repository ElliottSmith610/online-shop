from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class Database:
    def __init__(self, app):
        self.db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(200), nullable=False)
    l_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.string(250, nullable=False))
    ## Any relationships ##
    # link to a cart db? #


class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)

