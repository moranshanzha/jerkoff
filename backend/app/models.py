from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    
    journals = db.relationship('Journal', backref='author', lazy='dynamic')
    resources = db.relationship('Resource', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    tags = db.relationship('Tag', secondary='journal_tags', backref='journals')
    
    def __repr__(self):
        return '<Journal {}>'.format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    
    def __repr__(self):
        return '<Tag {}>'.format(self.name)

journal_tags = db.Table('journal_tags',
    db.Column('journal_id', db.Integer, db.ForeignKey('journal.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    description = db.Column(db.Text)
    file_type = db.Column(db.String(64))
    file_path = db.Column(db.String(256))
    uploaded_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<Resource {}>'.format(self.name)

class ResetPasswordRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reset_password_requests')
    
    def __repr__(self):
        return '<ResetPasswordRequest {}>'.format(self.token)

class ConfirmationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    user = db.relationship('User', backref='confirmation_tokens')
    
    def __repr__(self):
        return '<ConfirmationToken {}>'.format(self.token)
