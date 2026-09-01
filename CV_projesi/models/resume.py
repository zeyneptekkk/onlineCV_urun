import re
from datetime import datetime
from . import db

_TR_ASCII_MAP = str.maketrans({
    'ç': 'c', 'Ç': 'C',
    'ğ': 'g', 'Ğ': 'G',
    'ı': 'i', 'İ': 'I',
    'ö': 'o', 'Ö': 'O',
    'ş': 's', 'Ş': 'S',
    'ü': 'u', 'Ü': 'U',
})


class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Basic info
    title = db.Column(db.String(200), default='Benim CV\'m')
    full_name = db.Column(db.String(120), default='')
    job_title = db.Column(db.String(200), default='')
    summary = db.Column(db.Text, default='')
    profile_photo = db.Column(db.String(300), default='')
    
    # Contact
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(20), default='')
    city = db.Column(db.String(100), default='')
    linkedin = db.Column(db.String(300), default='')
    github = db.Column(db.String(300), default='')
    website = db.Column(db.String(300), default='')
    
    # Content (stored as JSON)
    experience = db.Column(db.JSON, default=list)
    education = db.Column(db.JSON, default=list)
    skills = db.Column(db.JSON, default=list)
    
    # Publishing
    public_slug = db.Column(db.String(120), unique=True, index=True, nullable=True)
    template_id = db.Column(db.String(50), default='modern')
    is_published = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    achievements = db.relationship('Achievement', backref='resume', lazy=True,
                                    cascade='all, delete-orphan', order_by='Achievement.order')
    references = db.relationship('Reference', backref='resume', lazy=True,
                                  cascade='all, delete-orphan', order_by='Reference.order')

    def generate_slug(self):
        """Generate a public slug like 'ad_soyad_CV'"""
        name = (self.full_name or '').translate(_TR_ASCII_MAP).lower()
        name = re.sub(r'[^a-z0-9]+', '_', name).strip('_')
        base_slug = f'{name}_CV' if name else 'cv_CV'

        slug = base_slug
        suffix = 2
        while Resume.query.filter(
            Resume.public_slug == slug,
            Resume.id != (self.id or -1)
        ).first():
            slug = f'{base_slug}{suffix}'
            suffix += 1

        self.public_slug = slug
        return self.public_slug
    
    def publish(self):
        """Publish resume"""
        if not self.public_slug:
            self.generate_slug()
        
        self.is_published = True
        return self
    
    def unpublish(self):
        """Unpublish resume"""
        self.is_published = False
        return self
    
    def get_public_url(self):
        """Get public viewing URL"""
        if self.is_published and self.public_slug:
            return f'/u/{self.public_slug}'
        return None
    
    def add_experience(self, company, position, start_date, end_date, description=''):
        """Add work experience"""
        if not self.experience:
            self.experience = []
        
        self.experience.append({
            'company': company,
            'position': position,
            'start_date': start_date,
            'end_date': end_date,
            'description': description,
        })
        return self
    
    def add_education(self, school, degree, field, graduation_year, description=''):
        """Add education"""
        if not self.education:
            self.education = []
        
        self.education.append({
            'school': school,
            'degree': degree,
            'field': field,
            'graduation_year': graduation_year,
            'description': description,
        })
        return self
    
    def add_skill(self, skill_name, category='Technical', level='Intermediate'):
        """Add skill"""
        if not self.skills:
            self.skills = []
        
        self.skills.append({
            'name': skill_name,
            'category': category,
            'level': level,
        })
        return self
    
    def __repr__(self):
        return f'<Resume {self.title}>'


ACHIEVEMENT_CATEGORIES = {
    'sertifika': 'Sertifika',
    'bootcamp': 'Bootcamp',
    'etkinlik': 'Etkinlik',
    'yarisma': 'Yarışma',
}


class Achievement(db.Model):
    """Sertifika, bootcamp, etkinlik veya yarışma kaydı"""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)

    category = db.Column(db.String(20), default='sertifika')  # sertifika, bootcamp, etkinlik, yarisma
    title = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), default='')
    date = db.Column(db.String(50), default='')
    description = db.Column(db.Text, default='')
    photo = db.Column(db.String(300), default='')
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Achievement {self.title}>'


class Reference(db.Model):
    """Referans kişisi"""
    __tablename__ = 'resume_references'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)

    full_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(200), default='')
    position = db.Column(db.String(200), default='')
    relation = db.Column(db.String(200), default='')
    description = db.Column(db.Text, default='')
    linkedin = db.Column(db.String(300), default='')
    photo = db.Column(db.String(300), default='')
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Reference {self.full_name}>'
