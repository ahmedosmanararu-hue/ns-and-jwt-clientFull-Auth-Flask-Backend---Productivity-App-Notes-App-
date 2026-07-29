import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user, login_user


def generate_jwt_token(user_id):
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    secret = current_app.config.get('SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def decode_jwt_token(token):
    """Decode a JWT token and return the payload"""
    secret = current_app.config.get('SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            # Fall back to session check
            from flask_login import current_user
            if current_user.is_authenticated:
                return f(*args, **kwargs)
            return jsonify({'errors': ['Authentication required']}), 401
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'errors': ['Invalid or expired token']}), 401
        
        from app.models.user import User
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'errors': ['User not found']}), 401
        
        # Set user as current user for the request context
        from flask_login import login_user
        login_user(user)
        
        return f(*args, **kwargs)
    
    return decorated


def get_token_from_request():
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

