from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models so they are registered with SQLAlchemy
from .user import User
from .resume import Resume, Achievement, Reference, ACHIEVEMENT_CATEGORIES
from .payment import Payment

__all__ = ['db', 'User', 'Resume', 'Payment', 'Achievement', 'Reference', 'ACHIEVEMENT_CATEGORIES']
