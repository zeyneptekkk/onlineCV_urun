from flask import render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Resume, Payment, db
from middleware import login_required, subscription_required
from services import AuthService
from .blueprints import dashboard_bp


@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """Dashboard home"""
    user = User.query.get(session['user_id'])
    resumes = Resume.query.filter_by(user_id=user.id).all()
    subscription_status = user.check_subscription_status()
    
    return render_template('dashboard/index.html',
                          user=user,
                          resumes=resumes,
                          subscription_status=subscription_status)


@dashboard_bp.route('/plan', methods=['GET', 'POST'])
@login_required
def choose_plan():
    """Choose subscription plan"""
    user = User.query.get(session['user_id'])
    
    # If already active, redirect to dashboard
    if user.check_subscription_status():
        flash('Zaten aktif bir aboneliğiniz var.', 'info')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        plan_type = request.form.get('plan', 'monthly')
        
        result = AuthService.choose_plan(user.id, plan_type)
        
        if result['success']:
            payment = result['payment']
            flash(f'Plan seçildi: {plan_type}. Ödeme sayfasına yönlendiriliyorsunuz...', 'info')
            return redirect(url_for('dashboard.payment', payment_id=payment.id))
        else:
            flash(result['error'], 'danger')
    
    return render_template('dashboard/choose_plan.html', user=user)


@dashboard_bp.route('/payment/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def payment(payment_id):
    """Payment processing (dummy for MVP)"""
    user = User.query.get(session['user_id'])
    payment = Payment.query.get(payment_id)
    
    if not payment or payment.user_id != user.id:
        flash('Ödeme bulunamadı.', 'danger')
        return redirect(url_for('dashboard.choose_plan'))
    
    if request.method == 'POST':
        # Dummy payment processing
        result = AuthService.process_dummy_payment(payment_id)
        
        if result['success']:
            flash(f'Ödeme başarılı! Abonelik aktif edildi.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['error'], 'danger')
    
    return render_template('dashboard/payment.html', payment=payment, user=user)


@dashboard_bp.route('/renew', methods=['GET', 'POST'])
@login_required
def renew_subscription():
    """Renew expired subscription"""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        plan_type = request.form.get('plan', 'monthly')
        
        result = AuthService.renew_subscription(user.id, plan_type)
        
        if result['success']:
            payment = result['payment']
            return redirect(url_for('dashboard.payment', payment_id=payment.id))
        else:
            flash(result['error'], 'danger')
    
    return render_template('dashboard/renew.html', user=user)


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings"""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        db.session.commit()
        flash('Profil güncellendi.', 'success')
        return redirect(url_for('dashboard.settings'))
    
    return render_template('dashboard/settings.html', user=user)
