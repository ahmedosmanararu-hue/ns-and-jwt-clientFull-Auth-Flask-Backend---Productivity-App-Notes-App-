from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, bcrypt

class User(UserMixin, db.Model):
    """User model with secure password handling"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationship with notes
    notes = db.relationship(
        'Note', 
        backref='user', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    
    @property
    def password(self):
        """Prevent password from being accessed"""
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Hash password before storing"""
        if not password or len(password) < 8:
            raise ValueError('Password must be at least 8 characters')
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excludes sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
