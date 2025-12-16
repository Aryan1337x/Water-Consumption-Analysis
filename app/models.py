from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    water_readings = db.relationship('WaterReading', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class WaterReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    reading_value = db.Column(db.Float, nullable=False)
    consumption = db.Column(db.Float, default=0.0)
    is_spike = db.Column(db.Boolean, default=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
    
    @property
    def consumption_category(self):
        if self.consumption is None:
            return "N/A"
        if self.consumption < 120:
            return "Too low consumption"
        elif 120 <= self.consumption <= 140:
            return "Average"
        else:
            return "Too much consumption"

    def __repr__(self):
        return f'<WaterReading {self.date}: {self.reading_value}>'

class WaterTariff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<WaterTariff {self.cost_per_unit}>'
