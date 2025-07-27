from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(100), nullable=False)
    name_kz = db.Column(db.String(100), nullable=False)
    description_ru = db.Column(db.Text)
    description_kz = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with FAQ
    faqs = db.relationship('FAQ', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name_ru}>'

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question_ru = db.Column(db.Text, nullable=False)
    question_kz = db.Column(db.Text, nullable=False)
    answer_ru = db.Column(db.Text, nullable=False)
    answer_kz = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ {self.question_ru[:50]}...>'

class UserQuery(db.Model):
    __tablename__ = 'user_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), nullable=False, default='ru')
    response_time = db.Column(db.Float)  # Response time in seconds
    session_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserQuery {self.user_message[:30]}...>'

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
