from flask import current_app
from app import db
from app.models import WaterReading
from sqlalchemy import desc, func

def add_reading_service(date, value):
    existing = WaterReading.query.filter_by(date=date).first()
    if existing:
        raise ValueError(f"Reading for date {date} already exists.")
    
    prev_reading = WaterReading.query.filter(WaterReading.date < date).order_by(desc(WaterReading.date)).first()
    
    consumption = 0.0
    if prev_reading:
        if value < prev_reading.reading_value:
             # Basic validation: meter shouldn't go back unless reset (not handled here simplistically)
             # But for now, we'll assume it's an error or just warn.
             raise ValueError("New reading value is less than previous reading.")
        
        consumption = value - prev_reading.reading_value
    
    window = current_app.config['SPIKE_DETECTION_WINDOW']
    last_n_readings = WaterReading.query.filter(WaterReading.date < date).order_by(desc(WaterReading.date)).limit(window).all()
    
    is_spike = False
    if last_n_readings:
        consumptions = [r.consumption for r in last_n_readings if r.consumption is not None]
        if consumptions:
            avg_consumption = sum(consumptions) / len(consumptions)
            threshold = current_app.config['SPIKE_DETECTION_THRESHOLD']
            if avg_consumption > 0 and consumption > (avg_consumption * threshold):
                is_spike = True
    
    new_reading = WaterReading(date=date, reading_value=value, consumption=consumption, is_spike=is_spike)
    db.session.add(new_reading)
    
    next_reading = WaterReading.query.filter(WaterReading.date > date).order_by(WaterReading.date).first()
    if next_reading:
         if next_reading.reading_value >= value:
            next_reading.consumption = next_reading.reading_value - value
         else:
             db.session.rollback()
             raise ValueError("New reading value is greater than the subsequent reading.")

    db.session.commit()
    return new_reading

def get_dashboard_stats():
    total_consumption = db.session.query(func.sum(WaterReading.consumption)).scalar() or 0
    total_readings = db.session.query(func.count(WaterReading.id)).scalar() or 0
    
    avg_daily = 0
    if total_readings > 0:
        first = WaterReading.query.order_by(WaterReading.date).first()
        last = WaterReading.query.order_by(desc(WaterReading.date)).first()
        if first and last and first.date != last.date:
            days = (last.date - first.date).days
            if days > 0:
                avg_daily = total_consumption / days
        else:
             avg_daily = total_consumption

    recent_readings = WaterReading.query.order_by(desc(WaterReading.date)).limit(10).all()
    
    return {
        "total_consumption": round(total_consumption, 2),
        "avg_daily": round(avg_daily, 2),
        "recent_readings": recent_readings
    }

def get_all_readings():
    return WaterReading.query.order_by(desc(WaterReading.date)).all()

def delete_reading_service(id):
    reading = WaterReading.query.get(id)
    if reading:
        prev = WaterReading.query.filter(WaterReading.date < reading.date).order_by(desc(WaterReading.date)).first()
        next_r = WaterReading.query.filter(WaterReading.date > reading.date).order_by(WaterReading.date).first()
        
        if next_r:
            if prev:
                next_r.consumption = next_r.reading_value - prev.reading_value
            else:
                 next_r.consumption = 0
                 
        db.session.delete(reading)
        db.session.commit()
