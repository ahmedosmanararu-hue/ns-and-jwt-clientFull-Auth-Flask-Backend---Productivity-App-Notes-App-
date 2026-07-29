from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models.user import User
from ..extensions import db
from ..utils import generate_jwt_token, get_token_from_request, decode_jwt_token

auth_bp = Blueprint('auth', __name__)


def _make_auth_response(user, status_code=200):
    """Create auth response with token and user data (compatible with both clients)"""
    user_dict = user.to_dict()
    token = generate_jwt_token(user.id)
    return jsonify({'token': token, 'user': user_dict}), status_code


def _error_response(messages, status_code=400):
    """Create error response in array format expected by clients"""
    if isinstance(messages, str):
        messages = [messages]
    return jsonify({'errors': messages}), status_code


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['username', 'email', 'password']
        if not all(field in data for field in required):
            return _error_response('Missing required fields', 400)
        
        # Check for existing user
        if User.query.filter_by(username=data['username']).first():
            return _error_response('Username already exists', 409)
        if User.query.filter_by(email=data['email']).first():
            return _error_response('Email already exists', 409)
        
        # Create user
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
        except ValueError as e:
            return _error_response(str(e), 400)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user in via session
        login_user(user)
        session['user_id'] = user.id
        
        return _make_auth_response(user, 201)
        
    except Exception as e:
        db.session.rollback()
        return _error_response('Registration failed', 500)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user (alias used by both clients)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', f"{username}@example.com")
        
        if not username or not password:
            return _error_response('Username and password are required', 400)
        
        # Check for existing user
        if User.query.filter_by(username=username).first():
            return _error_response('Username already exists', 409)
        
        # Create user
        try:
            user = User(
                username=username,
                email=email,
                password=password
            )
        except ValueError as e:
            return _error_response(str(e), 400)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user in via session
        login_user(user)
        session['user_id'] = user.id
        
        return _make_auth_response(user, 201)
        
    except Exception as e:
        db.session.rollback()
        return _error_response('Registration failed', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login existing user"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return _error_response('Username and password required', 400)
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return _error_response('Invalid credentials', 401)
        
        login_user(user)
        session['user_id'] = user.id
        
        return _make_auth_response(user, 200)
        
    except Exception as e:
        return _error_response('Login failed', 500)


@auth_bp.route('/logout', methods=['POST', 'DELETE'])
@login_required
def logout():
    """Logout current user (supports POST and DELETE)"""
    try:
        session.clear()
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return _error_response('Logout failed', 500)


@auth_bp.route('/check_session', methods=['GET'])
def check_session():
    """Check if user is logged in via session"""
    try:
        if current_user.is_authenticated:
            return jsonify(current_user.to_dict()), 200
        else:
            return jsonify(None), 200
    except Exception as e:
        return _error_response('Session check failed', 500)


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user via JWT token (used by JWT client)"""
    try:
        # Try JWT auth first
        token = get_token_from_request()
        if token:
            payload = decode_jwt_token(token)
            if payload:
                from ..models.user import User
                user = User.query.get(payload['user_id'])
                if user:
                    return jsonify(user.to_dict()), 200
            return _error_response('Invalid or expired token', 401)
        
        # Fall back to session
        if current_user.is_authenticated:
            return jsonify(current_user.to_dict()), 200
        
        return _error_response('Authentication required', 401)
        
    except Exception as e:
        return _error_response('Authentication check failed', 500)
