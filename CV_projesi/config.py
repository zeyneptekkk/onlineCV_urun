import os
from datetime import timedelta

class Config:
    """Base config"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cv-saas-dev-key-2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4'
    
    # Subscription
    PLAN_PRICES = {
        'monthly': 99,      # TL
        'yearly': 899,      # TL
    }
    
    # AI Tones
    AI_TONES = {
        'professional': 'Bunu profesyonel bir CV\'ye uygun hale getir:',
        'technical': 'Bunu teknik ve uzman tonu ile yeniden yaz:',
        'short': 'Bunu 50 kelime içine sıkıştır, etkileyici yap:',
        'modern': 'Bunu modern ve dinamik tonu ile yaz:',
    }


class DevelopmentConfig(Config):
    """Development config - SQLite"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cv_saas.db'


class ProductionConfig(Config):
    """Production config - PostgreSQL"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/cv_saas'
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing config"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Config selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get appropriate config based on FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
