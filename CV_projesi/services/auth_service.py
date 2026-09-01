from models import db, User, Payment
from datetime import datetime
from flask import session


class AuthService:
    """Authentication and user management"""
    
    @staticmethod
    def register(email, password, full_name=''):
        """Register new user"""
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return {'success': False, 'error': 'Bu email zaten kayıtlı.'}
        
        try:
            user = User(
                email=email,
                full_name=full_name,
                status='inactive'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {'success': True, 'user': user}
        
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def login(email, password):
        """Login user"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return {'success': False, 'error': 'Email veya şifre hatalı.'}
        
        # Set session
        session['user_id'] = user.id
        session['email'] = user.email
        session.permanent = True
        
        return {'success': True, 'user': user}
    
    @staticmethod
    def logout():
        """Logout user"""
        session.clear()
        return {'success': True}
    
    @staticmethod
    def get_current_user():
        """Get currently logged in user"""
        user_id = session.get('user_id')
        if user_id:
            return User.query.get(user_id)
        return None
    
    @staticmethod
    def choose_plan(user_id, plan_type):
        """User chooses a plan (pre-payment step)"""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Kullanıcı bulunamadı.'}
        
        if plan_type not in ['monthly', 'yearly']:
            return {'success': False, 'error': 'Geçersiz plan.'}
        
        # Create payment record (pending)
        from config import get_config
        config = get_config()
        
        payment = Payment(
            user_id=user_id,
            amount=config.PLAN_PRICES.get(plan_type, 0),
            currency='TRY',
            plan_type=plan_type,
            status='pending',
            payment_method='dummy'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return {'success': True, 'payment': payment}
    
    @staticmethod
    def process_dummy_payment(payment_id):
        """Process dummy payment (for MVP testing)"""
        payment = Payment.query.get(payment_id)
        if not payment:
            return {'success': False, 'error': 'Ödeme bulunamadı.'}
        
        # Complete payment
        payment.complete_payment()
        db.session.commit()
        
        return {'success': True, 'payment': payment, 'user': payment.user}
    
    @staticmethod
    def renew_subscription(user_id, plan_type):
        """Renew expired subscription"""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Kullanıcı bulunamadı.'}
        
        # Create payment record
        from config import get_config
        config = get_config()
        
        payment = Payment(
            user_id=user_id,
            amount=config.PLAN_PRICES.get(plan_type, 0),
            currency='TRY',
            plan_type=plan_type,
            status='pending',
            payment_method='dummy'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return {'success': True, 'payment': payment}
