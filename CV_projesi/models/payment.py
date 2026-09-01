from datetime import datetime
from . import db


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='TRY')
    plan_type = db.Column(db.String(20), nullable=False)  # monthly, yearly
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    
    # Transaction
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    payment_method = db.Column(db.String(50), default='dummy')  # dummy, stripe, paypal
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def complete_payment(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
        # Activate user subscription
        self.user.activate_subscription(self.plan_type)
        
        return self
    
    def fail_payment(self):
        """Mark payment as failed"""
        self.status = 'failed'
        return self
    
    def __repr__(self):
        return f'<Payment {self.user_id} - {self.plan_type}>'
