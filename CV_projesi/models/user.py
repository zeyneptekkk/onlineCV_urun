from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), default='')
    
    # Subscription fields
    plan_type = db.Column(db.String(20), default='free')  # free, monthly, yearly
    status = db.Column(db.String(20), default='inactive')  # inactive, active, expired
    subscribed_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def activate_subscription(self, plan_type='monthly'):
        """Activate subscription"""
        self.plan_type = plan_type
        self.status = 'active'
        self.subscribed_at = datetime.utcnow()
        
        # Set expiry date
        if plan_type == 'monthly':
            self.expires_at = datetime.utcnow() + timedelta(days=30)
        elif plan_type == 'yearly':
            self.expires_at = datetime.utcnow() + timedelta(days=365)
        
        return self
    
    def renew_subscription(self):
        """Renew expired subscription"""
        if self.plan_type in ['monthly', 'yearly']:
            self.status = 'active'
            self.subscribed_at = datetime.utcnow()
            
            if self.plan_type == 'monthly':
                self.expires_at = datetime.utcnow() + timedelta(days=30)
            elif self.plan_type == 'yearly':
                self.expires_at = datetime.utcnow() + timedelta(days=365)
        
        return self
    
    def check_subscription_status(self):
        """Check if subscription is active"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            self.status = 'expired'
            return False
        
        return True
    
    def can_edit_resume(self):
        """Can user edit resumes?"""
        return self.check_subscription_status()
    
    def can_use_ai(self):
        """Can user use AI features?"""
        return self.check_subscription_status()
    
    def get_public_resumes(self):
        """Get all published resumes"""
        return Resume.query.filter_by(user_id=self.id, is_published=True).all()
    
    def __repr__(self):
        return f'<User {self.email}>'
