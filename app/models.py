from app import db
from datetime import datetime

class WaterReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    reading_value = db.Column(db.Float, nullable=False)
    consumption = db.Column(db.Float, default=0.0)
    is_spike = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<WaterReading {self.date}: {self.reading_value}>'
