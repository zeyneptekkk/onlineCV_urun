from flask import render_template, request, redirect, url_for, flash, session
from services import AuthService
from models import User
from .blueprints import auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not email or not password:
            flash('Email ve şifre gerekli.', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Şifreler eşleşmiyor.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalı.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Register
        result = AuthService.register(email, password, full_name)
        
        if result['success']:
            flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['error'], 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        result = AuthService.login(email, password)
        
        if result['success']:
            flash('Hoş geldiniz!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(result['error'], 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    AuthService.logout()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('public.index'))
