from flask import Blueprint

# Create all blueprints (no imports from routes to avoid circular imports)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
resume_bp = Blueprint('resume', __name__, url_prefix='/resume')
api_bp = Blueprint('api', __name__, url_prefix='/api')
public_bp = Blueprint('public', __name__)
