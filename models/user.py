from models.dbSettings import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    session_token = db.Column(db.String)
    active = db.Column(db.Integer)
