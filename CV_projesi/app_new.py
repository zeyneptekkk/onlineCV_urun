import os
from flask import Flask, render_template, redirect, url_for
from config import get_config
from models import db
from routes import auth_bp, dashboard_bp, resume_bp, api_bp, public_bp


def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load config
    if config is None:
        config = get_config()
    
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(public_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()

        from sqlalchemy import text
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE resumes ADD COLUMN profile_photo VARCHAR(300) DEFAULT ''"))
                conn.commit()
            except Exception:
                pass
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    # Context processor
    @app.context_processor
    def inject_user():
        from flask import session
        from models import User
        
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        
        return {'current_user': user}
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
