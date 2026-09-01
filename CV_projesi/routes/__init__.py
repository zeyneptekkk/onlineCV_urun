from .blueprints import auth_bp, dashboard_bp, resume_bp, api_bp, public_bp

# Import routes to register them
from . import auth_routes
from . import dashboard_routes
from . import resume_routes
from . import api_routes
from . import public_routes

__all__ = ['auth_bp', 'dashboard_bp', 'resume_bp', 'api_bp', 'public_bp']
