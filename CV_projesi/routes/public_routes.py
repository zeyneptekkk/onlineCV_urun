from flask import render_template, abort, session
from models import User, Resume
from .blueprints import public_bp


@public_bp.route('/')
def index():
    """Landing page"""
    return render_template('public/index.html')


@public_bp.route('/u/<public_slug>')
def view_public_profile(public_slug):
    """View published resume (public profile) - works even with expired subscription"""
    resume = Resume.query.filter_by(
        public_slug=public_slug,
        is_published=True
    ).first()
    
    if not resume:
        abort(404)
    
    user = resume.user
    
    # This page is READ-ONLY, always accessible
    # Even if subscription expired
    return render_template('public/profile.html', resume=resume, user=user)


@public_bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('public/pricing.html')


@public_bp.route('/features')
def features():
    """Features page"""
    return render_template('public/features.html')
