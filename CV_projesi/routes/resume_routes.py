import os
import io
import base64
from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from models import User, Resume, Achievement, Reference, db
from middleware import subscription_required, login_required
from .blueprints import resume_bp

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _save_photo(file, resume_id, subfolder=''):
    """Save an uploaded photo for a resume, namespaced by resume id (and optional subfolder)."""
    if not file or not file.filename:
        return None

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        return None

    parts = ['resumes', str(resume_id)] + ([subfolder] if subfolder else [])
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], *parts)
    os.makedirs(folder, exist_ok=True)

    filename = secure_filename(file.filename)
    file.save(os.path.join(folder, filename))
    return '/'.join(parts + [filename])


@resume_bp.route('/new', methods=['GET', 'POST'])
@subscription_required
def create_resume():
    """Create new resume"""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        resume = Resume(
            user_id=user.id,
            title=request.form.get('title', 'Benim CV\'m').strip(),
            full_name=request.form.get('full_name', '').strip(),
            job_title=request.form.get('job_title', '').strip(),
            email=request.form.get('email', '').strip(),
            phone=request.form.get('phone', '').strip(),
            city=request.form.get('city', '').strip(),
        )
        
        db.session.add(resume)
        db.session.commit()
        
        flash('CV oluşturuldu!', 'success')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))
    
    return render_template('resume/create.html', user=user)


@resume_bp.route('/<int:resume_id>/edit', methods=['GET', 'POST'])
@subscription_required
def edit_resume(resume_id):
    """Edit resume"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)
    
    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        resume.title = request.form.get('title', '').strip()
        resume.full_name = request.form.get('full_name', '').strip()
        resume.job_title = request.form.get('job_title', '').strip()
        resume.summary = request.form.get('summary', '').strip()
        resume.email = request.form.get('email', '').strip()
        resume.phone = request.form.get('phone', '').strip()
        resume.city = request.form.get('city', '').strip()
        resume.linkedin = request.form.get('linkedin', '').strip()
        resume.github = request.form.get('github', '').strip()
        resume.website = request.form.get('website', '').strip()

        photo_path = _save_photo(request.files.get('profile_photo'), resume.id)
        if photo_path:
            resume.profile_photo = photo_path

        db.session.commit()
        flash('CV güncellendi!', 'success')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))

    return render_template('resume/edit.html', resume=resume, user=user)


@resume_bp.route('/<int:resume_id>/achievements/add', methods=['POST'])
@subscription_required
def add_achievement(resume_id):
    """Add a certificate / bootcamp / event / competition entry"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    title = request.form.get('title', '').strip()
    if not title:
        flash('Başlık gerekli.', 'danger')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))

    achievement = Achievement(
        resume_id=resume.id,
        category=request.form.get('category', 'sertifika'),
        title=title,
        organization=request.form.get('organization', '').strip(),
        date=request.form.get('date', '').strip(),
        description=request.form.get('description', '').strip(),
        order=len(resume.achievements),
    )
    db.session.add(achievement)
    db.session.flush()

    photo_path = _save_photo(request.files.get('photo'), resume.id, 'achievements')
    if photo_path:
        achievement.photo = photo_path

    db.session.commit()
    flash('Eklendi!', 'success')
    return redirect(url_for('resume.edit_resume', resume_id=resume.id))


@resume_bp.route('/<int:resume_id>/achievements/<int:achievement_id>/delete', methods=['POST'])
@subscription_required
def delete_achievement(resume_id, achievement_id):
    """Delete a certificate / bootcamp / event / competition entry"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    achievement = Achievement.query.get(achievement_id)
    if achievement and achievement.resume_id == resume.id:
        db.session.delete(achievement)
        db.session.commit()
        flash('Silindi.', 'info')

    return redirect(url_for('resume.edit_resume', resume_id=resume.id))


@resume_bp.route('/<int:resume_id>/references/add', methods=['POST'])
@subscription_required
def add_reference(resume_id):
    """Add a reference person"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    full_name = request.form.get('full_name', '').strip()
    if not full_name:
        flash('İsim gerekli.', 'danger')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))

    reference = Reference(
        resume_id=resume.id,
        full_name=full_name,
        company=request.form.get('company', '').strip(),
        position=request.form.get('position', '').strip(),
        relation=request.form.get('relation', '').strip(),
        description=request.form.get('description', '').strip(),
        linkedin=request.form.get('linkedin', '').strip(),
        order=len(resume.references),
    )
    db.session.add(reference)
    db.session.flush()

    photo_path = _save_photo(request.files.get('photo'), resume.id, 'references')
    if photo_path:
        reference.photo = photo_path

    db.session.commit()
    flash('Referans eklendi!', 'success')
    return redirect(url_for('resume.edit_resume', resume_id=resume.id))


@resume_bp.route('/<int:resume_id>/references/<int:reference_id>/delete', methods=['POST'])
@subscription_required
def delete_reference(resume_id, reference_id):
    """Delete a reference person"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    reference = Reference.query.get(reference_id)
    if reference and reference.resume_id == resume.id:
        db.session.delete(reference)
        db.session.commit()
        flash('Silindi.', 'info')

    return redirect(url_for('resume.edit_resume', resume_id=resume.id))


@resume_bp.route('/<int:resume_id>/preview', methods=['GET'])
@login_required
def preview_resume(resume_id):
    """Preview resume before publishing"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)
    
    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('resume/preview.html', resume=resume, user=user)


@resume_bp.route('/<int:resume_id>/publish', methods=['POST'])
@subscription_required
def publish_resume(resume_id):
    """Publish resume to public link"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)
    
    if not resume or resume.user_id != user.id:
        return jsonify({'success': False, 'error': 'CV bulunamadı.'}), 404
    
    if not resume.public_slug:
        resume.generate_slug()
    
    resume.publish()
    db.session.commit()
    
    public_url = resume.get_public_url()
    flash(f'CV yayınlandı! Linki paylaş: {public_url}', 'success')
    
    return jsonify({
        'success': True,
        'public_url': public_url,
        'slug': resume.public_slug
    })


@resume_bp.route('/<int:resume_id>/unpublish', methods=['POST'])
@subscription_required
def unpublish_resume(resume_id):
    """Unpublish resume"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)
    
    if not resume or resume.user_id != user.id:
        return jsonify({'success': False, 'error': 'CV bulunamadı.'}), 404
    
    resume.unpublish()
    db.session.commit()
    
    flash('CV yayından kaldırıldı.', 'info')
    
    return jsonify({'success': True})


@resume_bp.route('/<int:resume_id>/delete', methods=['POST'])
@subscription_required
def delete_resume(resume_id):
    """Delete resume"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)
    
    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    db.session.delete(resume)
    db.session.commit()

    flash('CV silindi.', 'info')
    return redirect(url_for('dashboard.index'))


def _qr_png_bytes(url):
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#3d0512', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


@resume_bp.route('/<int:resume_id>/qr')
@login_required
def resume_qr(resume_id):
    """Show a QR code linking to the published public CV"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    if not resume.is_published or not resume.public_slug:
        flash('QR kod oluşturmak için önce CV\'nizi yayınlamalısınız.', 'warning')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))

    public_url = request.host_url.rstrip('/') + resume.get_public_url()

    try:
        buf = _qr_png_bytes(public_url)
        qr_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        flash(f'QR kod oluşturulamadı: {e}', 'danger')
        return redirect(url_for('resume.edit_resume', resume_id=resume.id))

    return render_template('resume/qr.html', resume=resume, public_url=public_url, qr_image=qr_image)


@resume_bp.route('/<int:resume_id>/qr/indir')
@login_required
def resume_qr_download(resume_id):
    """Download the QR code as a PNG file"""
    user = User.query.get(session['user_id'])
    resume = Resume.query.get(resume_id)

    if not resume or resume.user_id != user.id or not resume.is_published:
        flash('CV bulunamadı.', 'danger')
        return redirect(url_for('dashboard.index'))

    public_url = request.host_url.rstrip('/') + resume.get_public_url()
    buf = _qr_png_bytes(public_url)

    return send_file(buf, mimetype='image/png', as_attachment=True,
                      download_name=f'{resume.public_slug}-qr.png')
