# CV SaaS - Profesyonel CV Oluşturma Platformu

Multi-user subscription-based SaaS uygulaması AI destekli CV optimizasyonu ile.

## Özellikler

- ✅ Kullanıcı kaydı ve girişi
- ✅ Aylık/Yıllık abonelik sistemi
- ✅ CV düzenleyici (form-based)
- ✅ 4 farklı tonda AI metni optimize etme (OpenAI)
- ✅ Paylaşılabilir public link (`/u/<slug>`)
- ✅ Read-only profil (süresi dolsa bile çalışır)
- ✅ Dummy ödeme sistemi (MVP)
- ✅ Subscription middleware ve decorators

## Proje Yapısı

```
CV_projesi/
├── app.py                    # Eski portfolio app (arka planda kalacak)
├── app_new.py                # YENİ - Blueprint-based Flask app
├── config.py                 # Configuration (SQLite, PostgreSQL, OpenAI)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
│
├── models/
│   ├── __init__.py           # Database initialization
│   ├── user.py               # User model (subscription)
│   ├── resume.py             # Resume/CV model
│   └── payment.py            # Payment model
│
├── middleware/
│   └── __init__.py           # @login_required, @subscription_required
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py         # OpenAI integration
│   └── auth_service.py       # Authentication logic
│
├── routes/
│   ├── __init__.py           # Blueprints registration
│   ├── auth_routes.py        # /auth/register, /auth/login
│   ├── dashboard_routes.py   # /dashboard, /plan, /payment
│   ├── resume_routes.py      # /resume/new, /resume/<id>/edit
│   ├── api_routes.py         # /api/optimize, /api/optimize-all
│   └── public_routes.py      # /, /u/<slug>, /pricing
│
└── templates/
    ├── base.html             # Base template
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── dashboard/
    │   ├── index.html
    │   ├── choose_plan.html
    │   ├── payment.html
    │   └── renew.html
    ├── resume/
    │   ├── create.html
    │   ├── edit.html        # AI optimizer dahil
    │   └── preview.html
    ├── public/
    │   ├── index.html       # Landing page
    │   ├── profile.html     # Read-only CV view
    │   └── pricing.html
    └── errors/
        └── 404.html
```

## Setup & Kurulum

### 1. Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edit .env ve OPENAI_API_KEY'i ayarlayın
```

### 4. Database

```bash
# Models otomatik create_all() ile oluşturulacak
# app.py çalıştırırken veya:
python
from app_new import app, db
with app.app_context():
    db.create_all()
```

### 5. Run the App

```bash
python app_new.py
# veya
flask --app app_new run
```

Erişim: `http://localhost:5000`

## Route Haritası

### Public Routes
- `GET /` - Landing page
- `GET /u/<slug>` - Public CV viewing (read-only, always accessible)
- `GET /pricing` - Fiyatlandırma
- `GET /features` - Özellikler

### Auth Routes
- `GET/POST /auth/register` - Kayıt
- `GET/POST /auth/login` - Giriş
- `GET /auth/logout` - Çıkış

### Dashboard Routes (login_required)
- `GET /dashboard/` - Dashboard home
- `GET/POST /dashboard/plan` - Plan seçimi
- `GET/POST /dashboard/payment/<id>` - Ödeme
- `GET/POST /dashboard/renew` - Abonelik yenileme
- `GET/POST /dashboard/settings` - Profil ayarları

### Resume Routes (subscription_required)
- `GET/POST /resume/new` - CV oluştur
- `GET/POST /resume/<id>/edit` - CV düzenle
- `GET /resume/<id>/preview` - Önizle
- `POST /resume/<id>/publish` - Yayınla
- `POST /resume/<id>/delete` - Sil

### API Routes (api_subscription_required)
- `POST /api/optimize` - Metin optimize etme (1 tone)
- `POST /api/optimize-all` - Tüm tonlarda optimize
- `GET /api/tones` - Mevcut tonları listele

## Subscription Logic

### Kullanıcı Durumları
- **inactive**: Plan seçmedi → edit kapalı
- **active**: Ödeme tamamlandı → edit açık
- **expired**: Abonelik bitmiş → edit kapalı

### Read-Only Davranışı
```
Dashboard (edit kapalı) ← Süresi doldu
Public Profile (/u/<slug>) ← HALA ÇALIŞIR ✓
```

## AI Integration

### Tones
- `professional` - Profesyonel ton
- `technical` - Teknik/uzman ton
- `short` - Kısa ve etkili (50-80 kelime)
- `modern` - Modern/girişimci ton

### API Endpoint
```bash
POST /api/optimize
Content-Type: application/json

{
  "text": "Benim metnim...",
  "tone": "professional"
}
```

## Database Schema

### Users Table
- id, email, password_hash, full_name
- plan_type (free/monthly/yearly)
- status (inactive/active/expired)
- subscribed_at, expires_at, created_at

### Resumes Table
- id, user_id, title, full_name, job_title, summary
- email, phone, city, linkedin, github, website
- experience (JSON), education (JSON), skills (JSON)
- public_slug, template_id, is_published
- created_at, updated_at

### Payments Table
- id, user_id, amount, currency, plan_type
- status (pending/completed/failed)
- transaction_id, payment_method, created_at

## MVP Checklist

- [x] User authentication (register, login, logout)
- [x] Subscription system (monthly, yearly)
- [x] Resume CRUD operations
- [x] Public profile link
- [x] AI text optimization
- [x] Dummy payment flow
- [x] Middleware & decorators
- [ ] Email notifications
- [ ] PDF export
- [ ] Premium templates
- [ ] Stripe integration
- [ ] Analytics dashboard

## Development Notes

### Mevcut Eski Kod
`app.py` dosyası önceki portfolio uygulamasıdır ve şimdi kullanılmıyor.
Yeni sistem `app_new.py` ile başlıyor.

### Geçiş Planı
1. MVP'de yeni sistem tam olarak test et
2. Eski verileri migrate et (gerekirse)
3. Production'a taşı
4. Stripe entegrasyonu ekle

### OpenAI API Alternatifleri
- `openai>=1.3.0` - Resmi Python client
- Fallback: Ollama (self-hosted)
- Fallback: Hugging Face API

## License

MIT License
