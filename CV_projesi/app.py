import os
import io
import base64
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cv-projesi-gizli-anahtar-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── MODELLER ─────────────────────────────────────────────────────────────────

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(256), nullable=False)

    def sifre_kontrol(self, sifre):
        return check_password_hash(self.sifre_hash, sifre)


class KisiselBilgi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(100), default='')
    unvan = db.Column(db.String(200), default='')
    email = db.Column(db.String(100), default='')
    telefon = db.Column(db.String(20), default='')
    sehir = db.Column(db.String(100), default='')
    linkedin = db.Column(db.String(300), default='')
    github = db.Column(db.String(300), default='')
    leetcode = db.Column(db.String(300), default='')
    website = db.Column(db.String(300), default='')
    ozet = db.Column(db.Text, default='')
    profil_foto = db.Column(db.String(300), default='')
    cv_dosya = db.Column(db.String(300), default='')


class Proje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, default='')
    teknolojiler = db.Column(db.String(500), default='')
    github_link = db.Column(db.String(300), default='')
    demo_link = db.Column(db.String(300), default='')
    resim = db.Column(db.String(300), default='')
    tarih = db.Column(db.String(50), default='')
    sira = db.Column(db.Integer, default=0)
    fotograflar = db.relationship('ProjeFoto', backref='proje', lazy=True,
                                  cascade='all, delete-orphan', order_by='ProjeFoto.sira')


class ProjeFoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proje_id = db.Column(db.Integer, db.ForeignKey('proje.id'), nullable=False)
    dosya = db.Column(db.String(300), nullable=False)
    sira = db.Column(db.Integer, default=0)


class Sertifika(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    kurum = db.Column(db.String(200), default='')
    tarih = db.Column(db.String(50), default='')
    dosya = db.Column(db.String(300), default='')
    aciklama = db.Column(db.Text, default='')
    kategori = db.Column(db.String(50), nullable=False)
    sira = db.Column(db.Integer, default=0)
    fotograflar = db.relationship('SertifikaFoto', backref='sertifika', lazy=True,
                                  cascade='all, delete-orphan', order_by='SertifikaFoto.sira')


class SertifikaFoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sertifika_id = db.Column(db.Integer, db.ForeignKey('sertifika.id'), nullable=False)
    dosya = db.Column(db.String(300), nullable=False)
    sira = db.Column(db.Integer, default=0)


class Referans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(100), nullable=False)
    sirket = db.Column(db.String(200), default='')
    pozisyon = db.Column(db.String(200), default='')
    iliski = db.Column(db.String(200), default='')
    telefon = db.Column(db.String(20), default='')
    email = db.Column(db.String(100), default='')
    aciklama = db.Column(db.Text, default='')
    linkedin = db.Column(db.String(300), default='')
    profil_foto = db.Column(db.String(300), default='')
    sirket_logo = db.Column(db.String(300), default='')
    sira = db.Column(db.Integer, default=0)


class VideoMulakat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    youtube_link = db.Column(db.String(300), default='')
    sirket = db.Column(db.String(200), default='')
    sirket_logo = db.Column(db.String(300), default='')
    tarih = db.Column(db.String(50), default='')
    aciklama = db.Column(db.Text, default='')
    sira = db.Column(db.Integer, default=0)


class Yetenek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kategori = db.Column(db.String(100), default='Programlama Dilleri')
    isim = db.Column(db.String(100), nullable=False)
    seviye = db.Column(db.String(50), default='')
    sira = db.Column(db.Integer, default=0)


class Staj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sirket_adi = db.Column(db.String(200), nullable=False)
    sirket_logo = db.Column(db.String(300), default='')
    alan = db.Column(db.String(200), default='')
    baslangic = db.Column(db.String(50), default='')
    bitis = db.Column(db.String(50), default='')
    aciklama = db.Column(db.Text, default='')
    rapor_link = db.Column(db.String(500), default='')
    sira = db.Column(db.Integer, default=0)
    ekip = db.relationship('StajEkip', backref='staj', lazy=True,
                           cascade='all, delete-orphan', order_by='StajEkip.sira')


class StajEkip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staj_id = db.Column(db.Integer, db.ForeignKey('staj.id'), nullable=False)
    ad_soyad = db.Column(db.String(100), nullable=False)
    unvan = db.Column(db.String(200), default='')
    resim = db.Column(db.String(300), default='')
    sira = db.Column(db.Integer, default=0)


# ─── YARDIMCI ─────────────────────────────────────────────────────────────────

def youtube_embed_url(link):
    if not link:
        return ''
    if 'youtu.be/' in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    elif 'watch?v=' in link:
        video_id = link.split('watch?v=')[-1].split('&')[0]
    elif 'embed/' in link:
        return link
    else:
        return link
    return f'https://www.youtube.com/embed/{video_id}'


app.jinja_env.globals['youtube_embed_url'] = youtube_embed_url


@app.context_processor
def inject_bilgi():
    bilgi = KisiselBilgi.query.first()
    return dict(bilgi=bilgi)


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def giris_gerekli(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_giris'))
        return f(*args, **kwargs)
    return decorated


def dosya_kaydet(dosya, klasor):
    if dosya and dosya.filename and allowed_file(dosya.filename):
        filename = secure_filename(dosya.filename)
        kayit_yolu = os.path.join(app.config['UPLOAD_FOLDER'], klasor, filename)
        dosya.save(kayit_yolu)
        return klasor + '/' + filename
    return None


# ─── PUBLIC ROTALAR ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    bilgi = KisiselBilgi.query.first()
    projeler = Proje.query.order_by(Proje.sira, Proje.id.desc()).limit(4).all()
    stajlar = Staj.query.order_by(Staj.sira, Staj.id.desc()).all()
    referanslar = Referans.query.order_by(Referans.sira, Referans.id.desc()).all()
    yetenekler_list = Yetenek.query.order_by(Yetenek.kategori, Yetenek.sira).all()
    etkinlikler = Sertifika.query.filter_by(kategori='etkinlik').order_by(Sertifika.sira, Sertifika.id.desc()).limit(6).all()
    sertifikalar = Sertifika.query.filter_by(kategori='sertifika').order_by(Sertifika.sira, Sertifika.id.desc()).limit(6).all()
    yarismalar = Sertifika.query.filter_by(kategori='yarısma').filter(Sertifika.fotograflar.any()).order_by(Sertifika.sira, Sertifika.id.desc()).all()
    videolar = VideoMulakat.query.order_by(VideoMulakat.sira, VideoMulakat.id.desc()).all()
    kategoriler = {}
    for y in yetenekler_list:
        kategoriler.setdefault(y.kategori, []).append(y)
    stats = {
        'proje': Proje.query.count(),
        'staj': Staj.query.count(),
        'sertifika': Sertifika.query.count(),
        'referans': Referans.query.count(),
    }
    return render_template('index.html',
        bilgi=bilgi,
        projeler=projeler,
        stajlar=stajlar,
        referanslar=referanslar,
        kategoriler=kategoriler,
        etkinlikler=etkinlikler,
        sertifikalar=sertifikalar,
        yarismalar=yarismalar,
        videolar=videolar,
        stats=stats
    )


@app.route('/projeler')
def projeler():
    tum_projeler = Proje.query.order_by(Proje.sira, Proje.id.desc()).all()
    return render_template('projeler.html', projeler=tum_projeler)


@app.route('/yetenekler')
def yetenekler():
    tum_yetenekler = Yetenek.query.order_by(Yetenek.sira, Yetenek.id).all()
    kategoriler = {}
    for y in tum_yetenekler:
        k = y.kategori or 'Diğer'
        if k not in kategoriler:
            kategoriler[k] = []
        kategoriler[k].append(y)
    return render_template('yetenekler.html', kategoriler=kategoriler)


@app.route('/staj')
def staj():
    stajlar = Staj.query.order_by(Staj.sira, Staj.id.desc()).all()
    return render_template('staj.html', stajlar=stajlar)


@app.route('/sertifikalar')
def sertifikalar():
    return render_template('sertifikalar/index.html')


@app.route('/sertifikalar/sertifikalar-listesi')
def sertifikalar_listesi():
    items = Sertifika.query.filter_by(kategori='sertifika').order_by(Sertifika.sira, Sertifika.id.desc()).all()
    return render_template('sertifikalar/sertifikalar_listesi.html', items=items)


@app.route('/sertifikalar/bootcamplar')
def bootcamplar():
    items = Sertifika.query.filter_by(kategori='bootcamp').order_by(Sertifika.sira, Sertifika.id.desc()).all()
    return render_template('sertifikalar/bootcamplar.html', items=items)


@app.route('/sertifikalar/etkinlikler')
def etkinlikler():
    items = Sertifika.query.filter_by(kategori='etkinlik').order_by(Sertifika.sira, Sertifika.id.desc()).all()
    return render_template('sertifikalar/etkinlikler.html', items=items)


@app.route('/sertifikalar/yarismalar')
def yarismalar():
    items = Sertifika.query.filter_by(kategori='yarısma').order_by(Sertifika.sira, Sertifika.id.desc()).all()
    return render_template('sertifikalar/yarismalar.html', items=items)


@app.route('/sertifikalar/video-mulakat')
def video_mulakat():
    videolar = VideoMulakat.query.order_by(VideoMulakat.sira, VideoMulakat.id.desc()).all()
    return render_template('sertifikalar/video_mulakat.html', videolar=videolar)


@app.route('/referanslar')
def referanslar():
    tum_referanslar = Referans.query.order_by(Referans.sira, Referans.id.desc()).all()
    return render_template('referanslar.html', referanslar=tum_referanslar)


# ─── ADMIN GİRİŞ ──────────────────────────────────────────────────────────────

@app.route('/admin/giris', methods=['GET', 'POST'])
def admin_giris():
    if 'admin_id' in session:
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi', '').strip()
        sifre = request.form.get('sifre', '')
        admin = Admin.query.filter_by(kullanici_adi=kullanici_adi).first()
        if admin and admin.sifre_kontrol(sifre):
            session['admin_id'] = admin.id
            session['admin_adi'] = admin.kullanici_adi
            flash('Hoş geldin!', 'success')
            return redirect(url_for('admin_panel'))
        flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    return render_template('admin/login.html')


@app.route('/admin/cikis')
def admin_cikis():
    session.clear()
    return redirect(url_for('index'))


# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

@app.route('/admin')
@giris_gerekli
def admin_panel():
    return render_template('admin/dashboard.html',
                           proje_sayisi=Proje.query.count(),
                           sertifika_sayisi=Sertifika.query.count(),
                           referans_sayisi=Referans.query.count(),
                           video_sayisi=VideoMulakat.query.count(),
                           yetenek_sayisi=Yetenek.query.count(),
                           staj_sayisi=Staj.query.count())


# ─── SİRALAMA (Sürükle-Bırak) ─────────────────────────────────────────────────

@app.route('/admin/siralama-guncelle', methods=['POST'])
@giris_gerekli
def admin_siralama_guncelle():
    data = request.get_json()
    model_adi = data.get('model')
    id_listesi = data.get('ids', [])
    model_map = {
        'proje': Proje, 'sertifika': Sertifika, 'referans': Referans,
        'video': VideoMulakat, 'yetenek': Yetenek, 'staj': Staj,
    }
    Model = model_map.get(model_adi)
    if not Model:
        return jsonify({'ok': False}), 400
    for i, item_id in enumerate(id_listesi):
        item = db.session.get(Model, item_id)
        if item:
            item.sira = i
    db.session.commit()
    return jsonify({'ok': True})


# ─── KİŞİSEL BİLGİ ────────────────────────────────────────────────────────────

@app.route('/admin/kisisel-bilgi', methods=['GET', 'POST'])
@giris_gerekli
def admin_kisisel_bilgi():
    bilgi = KisiselBilgi.query.first()
    if not bilgi:
        bilgi = KisiselBilgi()
        db.session.add(bilgi)
        db.session.commit()

    if request.method == 'POST':
        bilgi.ad_soyad = request.form.get('ad_soyad', '').strip()
        bilgi.unvan = request.form.get('unvan', '').strip()
        bilgi.email = request.form.get('email', '').strip()
        bilgi.telefon = request.form.get('telefon', '').strip()
        bilgi.sehir = request.form.get('sehir', '').strip()
        bilgi.linkedin = request.form.get('linkedin', '').strip()
        bilgi.github = request.form.get('github', '').strip()
        bilgi.leetcode = request.form.get('leetcode', '').strip()
        bilgi.website = request.form.get('website', '').strip()
        bilgi.ozet = request.form.get('ozet', '').strip()
        yol = dosya_kaydet(request.files.get('profil_foto'), 'profil')
        if yol:
            bilgi.profil_foto = yol
        yol = dosya_kaydet(request.files.get('cv_dosya'), 'profil')
        if yol:
            bilgi.cv_dosya = yol
        db.session.commit()
        flash('Kişisel bilgiler güncellendi!', 'success')
        return redirect(url_for('admin_kisisel_bilgi'))

    return render_template('admin/kisisel_bilgi.html', bilgi=bilgi)


# ─── PROJELER ─────────────────────────────────────────────────────────────────

@app.route('/admin/projeler')
@giris_gerekli
def admin_projeler():
    tum_projeler = Proje.query.order_by(Proje.sira, Proje.id.desc()).all()
    return render_template('admin/projeler.html', projeler=tum_projeler)


@app.route('/admin/proje/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_proje_ekle():
    if request.method == 'POST':
        proje = Proje(
            baslik=request.form.get('baslik', '').strip(),
            aciklama=request.form.get('aciklama', '').strip(),
            teknolojiler=request.form.get('teknolojiler', '').strip(),
            github_link=request.form.get('github_link', '').strip(),
            demo_link=request.form.get('demo_link', '').strip(),
            tarih=request.form.get('tarih', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        yol = dosya_kaydet(request.files.get('resim'), 'projeler')
        if yol:
            proje.resim = yol
        db.session.add(proje)
        db.session.flush()
        for f in request.files.getlist('fotograflar'):
            yol2 = dosya_kaydet(f, 'projeler')
            if yol2:
                db.session.add(ProjeFoto(proje_id=proje.id, dosya=yol2, sira=len(proje.fotograflar)))
        db.session.commit()
        flash('Proje eklendi!', 'success')
        return redirect(url_for('admin_projeler'))
    return render_template('admin/proje_form.html', proje=None, baslik='Proje Ekle')


@app.route('/admin/proje/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_proje_duzenle(id):
    proje = db.get_or_404(Proje, id)
    if request.method == 'POST':
        proje.baslik = request.form.get('baslik', '').strip()
        proje.aciklama = request.form.get('aciklama', '').strip()
        proje.teknolojiler = request.form.get('teknolojiler', '').strip()
        proje.github_link = request.form.get('github_link', '').strip()
        proje.demo_link = request.form.get('demo_link', '').strip()
        proje.tarih = request.form.get('tarih', '').strip()
        proje.sira = int(request.form.get('sira', 0) or 0)
        yol = dosya_kaydet(request.files.get('resim'), 'projeler')
        if yol:
            proje.resim = yol
        for f in request.files.getlist('fotograflar'):
            yol2 = dosya_kaydet(f, 'projeler')
            if yol2:
                db.session.add(ProjeFoto(proje_id=proje.id, dosya=yol2, sira=len(proje.fotograflar)))
        db.session.commit()
        flash('Proje güncellendi!', 'success')
        return redirect(url_for('admin_projeler'))
    return render_template('admin/proje_form.html', proje=proje, baslik='Proje Düzenle')


@app.route('/admin/proje/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_proje_sil(id):
    proje = db.get_or_404(Proje, id)
    db.session.delete(proje)
    db.session.commit()
    flash('Proje silindi.', 'info')
    return redirect(url_for('admin_projeler'))


@app.route('/admin/proje-foto/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_proje_foto_sil(id):
    foto = db.get_or_404(ProjeFoto, id)
    proje_id = foto.proje_id
    db.session.delete(foto)
    db.session.commit()
    flash('Fotoğraf silindi.', 'info')
    return redirect(url_for('admin_proje_duzenle', id=proje_id))


# ─── SERTİFİKALAR ─────────────────────────────────────────────────────────────

@app.route('/admin/sertifikalar')
@giris_gerekli
def admin_sertifikalar():
    tum_sertifikalar = Sertifika.query.order_by(Sertifika.kategori, Sertifika.sira, Sertifika.id.desc()).all()
    return render_template('admin/sertifikalar.html', sertifikalar=tum_sertifikalar)


@app.route('/admin/sertifika/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_sertifika_ekle():
    if request.method == 'POST':
        sertifika = Sertifika(
            baslik=request.form.get('baslik', '').strip(),
            kurum=request.form.get('kurum', '').strip(),
            tarih=request.form.get('tarih', '').strip(),
            aciklama=request.form.get('aciklama', '').strip(),
            kategori=request.form.get('kategori', 'bootcamp'),
            sira=int(request.form.get('sira', 0) or 0),
        )
        db.session.add(sertifika)
        db.session.flush()
        for f in request.files.getlist('fotograflar'):
            yol = dosya_kaydet(f, 'sertifikalar')
            if yol:
                db.session.add(SertifikaFoto(sertifika_id=sertifika.id, dosya=yol,
                                             sira=len(sertifika.fotograflar)))
        db.session.commit()
        flash('Sertifika eklendi!', 'success')
        return redirect(url_for('admin_sertifikalar'))
    return render_template('admin/sertifika_form.html', sertifika=None, baslik='Sertifika Ekle')


@app.route('/admin/sertifika/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_sertifika_duzenle(id):
    sertifika = db.get_or_404(Sertifika, id)
    if request.method == 'POST':
        sertifika.baslik = request.form.get('baslik', '').strip()
        sertifika.kurum = request.form.get('kurum', '').strip()
        sertifika.tarih = request.form.get('tarih', '').strip()
        sertifika.aciklama = request.form.get('aciklama', '').strip()
        sertifika.kategori = request.form.get('kategori', 'bootcamp')
        sertifika.sira = int(request.form.get('sira', 0) or 0)
        for f in request.files.getlist('fotograflar'):
            yol = dosya_kaydet(f, 'sertifikalar')
            if yol:
                db.session.add(SertifikaFoto(sertifika_id=sertifika.id, dosya=yol,
                                             sira=len(sertifika.fotograflar)))
        db.session.commit()
        flash('Sertifika güncellendi!', 'success')
        return redirect(url_for('admin_sertifikalar'))
    return render_template('admin/sertifika_form.html', sertifika=sertifika, baslik='Sertifika Düzenle')


@app.route('/admin/sertifika/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_sertifika_sil(id):
    sertifika = db.get_or_404(Sertifika, id)
    db.session.delete(sertifika)
    db.session.commit()
    flash('Sertifika silindi.', 'info')
    return redirect(url_for('admin_sertifikalar'))


@app.route('/admin/sertifika-foto/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_sertifika_foto_sil(id):
    foto = db.get_or_404(SertifikaFoto, id)
    sertifika_id = foto.sertifika_id
    db.session.delete(foto)
    db.session.commit()
    flash('Fotoğraf silindi.', 'info')
    return redirect(url_for('admin_sertifika_duzenle', id=sertifika_id))


# ─── REFERANSLAR ──────────────────────────────────────────────────────────────

@app.route('/admin/referanslar')
@giris_gerekli
def admin_referanslar():
    tum_referanslar = Referans.query.order_by(Referans.sira, Referans.id.desc()).all()
    return render_template('admin/referanslar.html', referanslar=tum_referanslar)


@app.route('/admin/referans/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_referans_ekle():
    if request.method == 'POST':
        referans = Referans(
            ad_soyad=request.form.get('ad_soyad', '').strip(),
            sirket=request.form.get('sirket', '').strip(),
            pozisyon=request.form.get('pozisyon', '').strip(),
            iliski=request.form.get('iliski', '').strip(),
            telefon=request.form.get('telefon', '').strip(),
            email=request.form.get('email', '').strip(),
            aciklama=request.form.get('aciklama', '').strip(),
            linkedin=request.form.get('linkedin', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        yol = dosya_kaydet(request.files.get('profil_foto'), 'referanslar')
        if yol:
            referans.profil_foto = yol
        yol2 = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol2:
            referans.sirket_logo = yol2
        db.session.add(referans)
        db.session.commit()
        flash('Referans eklendi!', 'success')
        return redirect(url_for('admin_referanslar'))
    return render_template('admin/referans_form.html', referans=None, baslik='Referans Ekle')


@app.route('/admin/referans/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_referans_duzenle(id):
    referans = db.get_or_404(Referans, id)
    if request.method == 'POST':
        referans.ad_soyad = request.form.get('ad_soyad', '').strip()
        referans.sirket = request.form.get('sirket', '').strip()
        referans.pozisyon = request.form.get('pozisyon', '').strip()
        referans.iliski = request.form.get('iliski', '').strip()
        referans.telefon = request.form.get('telefon', '').strip()
        referans.email = request.form.get('email', '').strip()
        referans.aciklama = request.form.get('aciklama', '').strip()
        referans.linkedin = request.form.get('linkedin', '').strip()
        referans.sira = int(request.form.get('sira', 0) or 0)
        yol = dosya_kaydet(request.files.get('profil_foto'), 'referanslar')
        if yol:
            referans.profil_foto = yol
        yol2 = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol2:
            referans.sirket_logo = yol2
        db.session.commit()
        flash('Referans güncellendi!', 'success')
        return redirect(url_for('admin_referanslar'))
    return render_template('admin/referans_form.html', referans=referans, baslik='Referans Düzenle')


@app.route('/admin/referans/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_referans_sil(id):
    referans = db.get_or_404(Referans, id)
    db.session.delete(referans)
    db.session.commit()
    flash('Referans silindi.', 'info')
    return redirect(url_for('admin_referanslar'))


# ─── VİDEO MÜLAKATLAR ─────────────────────────────────────────────────────────

@app.route('/admin/videolar')
@giris_gerekli
def admin_videolar():
    tum_videolar = VideoMulakat.query.order_by(VideoMulakat.sira, VideoMulakat.id.desc()).all()
    return render_template('admin/videolar.html', videolar=tum_videolar)


@app.route('/admin/video/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_video_ekle():
    if request.method == 'POST':
        video = VideoMulakat(
            baslik=request.form.get('baslik', '').strip(),
            youtube_link=request.form.get('youtube_link', '').strip(),
            sirket=request.form.get('sirket', '').strip(),
            tarih=request.form.get('tarih', '').strip(),
            aciklama=request.form.get('aciklama', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        yol = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol:
            video.sirket_logo = yol
        db.session.add(video)
        db.session.commit()
        flash('Video eklendi!', 'success')
        return redirect(url_for('admin_videolar'))
    return render_template('admin/video_form.html', video=None, baslik='Video Ekle')


@app.route('/admin/video/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_video_duzenle(id):
    video = db.get_or_404(VideoMulakat, id)
    if request.method == 'POST':
        video.baslik = request.form.get('baslik', '').strip()
        video.youtube_link = request.form.get('youtube_link', '').strip()
        video.sirket = request.form.get('sirket', '').strip()
        video.tarih = request.form.get('tarih', '').strip()
        video.aciklama = request.form.get('aciklama', '').strip()
        video.sira = int(request.form.get('sira', 0) or 0)
        yol = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol:
            video.sirket_logo = yol
        db.session.commit()
        flash('Video güncellendi!', 'success')
        return redirect(url_for('admin_videolar'))
    return render_template('admin/video_form.html', video=video, baslik='Video Düzenle')


@app.route('/admin/video/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_video_sil(id):
    video = db.get_or_404(VideoMulakat, id)
    db.session.delete(video)
    db.session.commit()
    flash('Video silindi.', 'info')
    return redirect(url_for('admin_videolar'))


# ─── YETENEKLER ───────────────────────────────────────────────────────────────

@app.route('/admin/yetenekler')
@giris_gerekli
def admin_yetenekler():
    tum_yetenekler = Yetenek.query.order_by(Yetenek.sira, Yetenek.id).all()
    return render_template('admin/yetenekler.html', yetenekler=tum_yetenekler)


@app.route('/admin/yetenek/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_yetenek_ekle():
    if request.method == 'POST':
        yetenek = Yetenek(
            kategori=request.form.get('kategori', '').strip(),
            isim=request.form.get('isim', '').strip(),
            seviye=request.form.get('seviye', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        db.session.add(yetenek)
        db.session.commit()
        flash('Yetenek eklendi!', 'success')
        return redirect(url_for('admin_yetenekler'))
    return render_template('admin/yetenek_form.html', yetenek=None, baslik='Yetenek Ekle')


@app.route('/admin/yetenek/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_yetenek_duzenle(id):
    yetenek = db.get_or_404(Yetenek, id)
    if request.method == 'POST':
        yetenek.kategori = request.form.get('kategori', '').strip()
        yetenek.isim = request.form.get('isim', '').strip()
        yetenek.seviye = request.form.get('seviye', '').strip()
        yetenek.sira = int(request.form.get('sira', 0) or 0)
        db.session.commit()
        flash('Yetenek güncellendi!', 'success')
        return redirect(url_for('admin_yetenekler'))
    return render_template('admin/yetenek_form.html', yetenek=yetenek, baslik='Yetenek Düzenle')


@app.route('/admin/yetenek/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_yetenek_sil(id):
    yetenek = db.get_or_404(Yetenek, id)
    db.session.delete(yetenek)
    db.session.commit()
    flash('Yetenek silindi.', 'info')
    return redirect(url_for('admin_yetenekler'))


# ─── STAJLAR ──────────────────────────────────────────────────────────────────

@app.route('/admin/stajlar')
@giris_gerekli
def admin_stajlar():
    tum_stajlar = Staj.query.order_by(Staj.sira, Staj.id.desc()).all()
    return render_template('admin/stajlar.html', stajlar=tum_stajlar)


@app.route('/admin/staj/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_staj_ekle():
    if request.method == 'POST':
        s = Staj(
            sirket_adi=request.form.get('sirket_adi', '').strip(),
            alan=request.form.get('alan', '').strip(),
            baslangic=request.form.get('baslangic', '').strip(),
            bitis=request.form.get('bitis', '').strip(),
            aciklama=request.form.get('aciklama', '').strip(),
            rapor_link=request.form.get('rapor_link', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        yol = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol:
            s.sirket_logo = yol
        db.session.add(s)
        db.session.commit()
        flash('Staj eklendi!', 'success')
        return redirect(url_for('admin_stajlar'))
    return render_template('admin/staj_form.html', staj=None, baslik='Staj Ekle')


@app.route('/admin/staj/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_staj_duzenle(id):
    s = db.get_or_404(Staj, id)
    if request.method == 'POST':
        s.sirket_adi = request.form.get('sirket_adi', '').strip()
        s.alan = request.form.get('alan', '').strip()
        s.baslangic = request.form.get('baslangic', '').strip()
        s.bitis = request.form.get('bitis', '').strip()
        s.aciklama = request.form.get('aciklama', '').strip()
        s.rapor_link = request.form.get('rapor_link', '').strip()
        s.sira = int(request.form.get('sira', 0) or 0)
        yol = dosya_kaydet(request.files.get('sirket_logo'), 'logolar')
        if yol:
            s.sirket_logo = yol
        db.session.commit()
        flash('Staj güncellendi!', 'success')
        return redirect(url_for('admin_stajlar'))
    return render_template('admin/staj_form.html', staj=s, baslik='Staj Düzenle')


@app.route('/admin/staj/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_staj_sil(id):
    s = db.get_or_404(Staj, id)
    db.session.delete(s)
    db.session.commit()
    flash('Staj silindi.', 'info')
    return redirect(url_for('admin_stajlar'))


# ─── STAJ EKİP ────────────────────────────────────────────────────────────────

@app.route('/admin/staj/<int:staj_id>/ekip')
@giris_gerekli
def admin_staj_ekip(staj_id):
    s = db.get_or_404(Staj, staj_id)
    return render_template('admin/staj_ekip.html', staj=s)


@app.route('/admin/staj/<int:staj_id>/ekip/ekle', methods=['GET', 'POST'])
@giris_gerekli
def admin_staj_ekip_ekle(staj_id):
    s = db.get_or_404(Staj, staj_id)
    if request.method == 'POST':
        uye = StajEkip(
            staj_id=staj_id,
            ad_soyad=request.form.get('ad_soyad', '').strip(),
            unvan=request.form.get('unvan', '').strip(),
            sira=int(request.form.get('sira', 0) or 0),
        )
        yol = dosya_kaydet(request.files.get('resim'), 'referanslar')
        if yol:
            uye.resim = yol
        db.session.add(uye)
        db.session.commit()
        flash('Ekip üyesi eklendi!', 'success')
        return redirect(url_for('admin_staj_ekip', staj_id=staj_id))
    return render_template('admin/staj_ekip_form.html', staj=s, uye=None, baslik='Ekip Üyesi Ekle')


@app.route('/admin/staj/ekip/duzenle/<int:id>', methods=['GET', 'POST'])
@giris_gerekli
def admin_staj_ekip_duzenle(id):
    uye = db.get_or_404(StajEkip, id)
    if request.method == 'POST':
        uye.ad_soyad = request.form.get('ad_soyad', '').strip()
        uye.unvan = request.form.get('unvan', '').strip()
        uye.sira = int(request.form.get('sira', 0) or 0)
        yol = dosya_kaydet(request.files.get('resim'), 'referanslar')
        if yol:
            uye.resim = yol
        db.session.commit()
        flash('Ekip üyesi güncellendi!', 'success')
        return redirect(url_for('admin_staj_ekip', staj_id=uye.staj_id))
    return render_template('admin/staj_ekip_form.html', staj=uye.staj, uye=uye, baslik='Ekip Üyesi Düzenle')


@app.route('/admin/staj/ekip/sil/<int:id>', methods=['POST'])
@giris_gerekli
def admin_staj_ekip_sil(id):
    uye = db.get_or_404(StajEkip, id)
    staj_id = uye.staj_id
    db.session.delete(uye)
    db.session.commit()
    flash('Ekip üyesi silindi.', 'info')
    return redirect(url_for('admin_staj_ekip', staj_id=staj_id))


# ─── QR KOD ───────────────────────────────────────────────────────────────────

def _qr_buf():
    import qrcode
    site_url = request.host_url.rstrip('/')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(site_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf, site_url

@app.route('/admin/qr')
@giris_gerekli
def admin_qr():
    try:
        buf, site_url = _qr_buf()
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return render_template('admin/qr.html', qr_image=img_b64, site_url=site_url)
    except Exception as e:
        flash(f'QR kod oluşturulamadı: {e}', 'danger')
        return redirect(url_for('admin_panel'))

@app.route('/admin/qr/indir')
@giris_gerekli
def admin_qr_indir():
    try:
        buf, _ = _qr_buf()
        return send_file(buf, mimetype='image/png',
                         as_attachment=True, download_name='cv-qr-kod.png')
    except Exception as e:
        flash(f'QR kod indirilemedi: {e}', 'danger')
        return redirect(url_for('admin_qr'))


# ─── BAŞLAT ───────────────────────────────────────────────────────────────────

def veritabani_olustur():
    with app.app_context():
        db.create_all()

        from sqlalchemy import text
        with db.engine.connect() as conn:
            for tablo, kolon, tip in [
                ('referans', 'profil_foto', "VARCHAR(300) DEFAULT ''"),
                ('referans', 'sirket_logo', "VARCHAR(300) DEFAULT ''"),
                ('video_mulakat', 'sirket_logo', "VARCHAR(300) DEFAULT ''"),
                ('staj', 'rapor_link', "VARCHAR(500) DEFAULT ''"),
                ('kisisel_bilgi', 'leetcode', "VARCHAR(300) DEFAULT ''"),
            ]:
                try:
                    conn.execute(text(f'ALTER TABLE {tablo} ADD COLUMN {kolon} {tip}'))
                    conn.commit()
                except Exception:
                    pass

        for klasor in ['profil', 'sertifikalar', 'projeler', 'referanslar', 'logolar']:
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], klasor), exist_ok=True)

        if not Admin.query.first():
            db.session.add_all([
                Admin(kullanici_adi='zeynep', sifre_hash=generate_password_hash('zeynep123')),
                Admin(kullanici_adi='mustafa', sifre_hash=generate_password_hash('mustafa123')),
            ])
            db.session.commit()

        if not KisiselBilgi.query.first():
            db.session.add(KisiselBilgi())
            db.session.commit()


if __name__ == '__main__':
    veritabani_olustur()
    app.run(debug=True)
