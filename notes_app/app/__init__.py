from flask import Flask
from .config import Config
from .extensions import (
    db, migrate, bcrypt, login_manager, 
    cors, session
)

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    
    # Configure CORS
    cors.init_app(app, 
                  origins=app.config['CORS_ORIGINS'].split(','),
                  supports_credentials=True)
    
    # Register blueprints (no prefix so clients can access /login, /signup, /me, /notes directly)
    from .routes.auth_routes import auth_bp
    from .routes.note_routes import note_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(note_bp, url_prefix='/notes')
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return {'error': 'Authentication required'}, 401
    
    return app
