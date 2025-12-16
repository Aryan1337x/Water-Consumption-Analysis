from flask import current_app
from app import db
from app.models import WaterReading, WaterTariff
from sqlalchemy import desc, func
from datetime import datetime

def add_reading_service(user_id, date, value):
    existing = WaterReading.query.filter_by(user_id=user_id, date=date).first()
    if existing:
        raise ValueError(f"Reading for date {date} already exists.")
    
    if date > datetime.now().date():
        raise ValueError("Cannot add readings for future dates.")
    
    prev_reading = WaterReading.query.filter(
        WaterReading.user_id == user_id,
        WaterReading.date < date
    ).order_by(desc(WaterReading.date)).first()
    
    consumption = 0.0
    if prev_reading:
        if value < prev_reading.reading_value:
             raise ValueError("New reading value is less than previous reading.")
        
        consumption = value - prev_reading.reading_value
    
    window = current_app.config['SPIKE_DETECTION_WINDOW']
    last_n_readings = WaterReading.query.filter(
        WaterReading.user_id == user_id,
        WaterReading.date < date
    ).order_by(desc(WaterReading.date)).limit(window).all()
    
    is_spike = False
    if last_n_readings:
        consumptions = [r.consumption for r in last_n_readings if r.consumption is not None]
        if consumptions:
            avg_consumption = sum(consumptions) / len(consumptions)
            threshold = current_app.config['SPIKE_DETECTION_THRESHOLD']
            if avg_consumption > 0 and consumption > (avg_consumption * threshold):
                is_spike = True
    
    new_reading = WaterReading(user_id=user_id, date=date, reading_value=value, consumption=consumption, is_spike=is_spike)
    db.session.add(new_reading)
    
    next_reading = WaterReading.query.filter(
        WaterReading.user_id == user_id,
        WaterReading.date > date
    ).order_by(WaterReading.date).first()
    if next_reading:
         if next_reading.reading_value >= value:
            next_reading.consumption = next_reading.reading_value - value
         else:
             db.session.rollback()
             raise ValueError("New reading value is greater than the subsequent reading.")

    db.session.commit()
    return new_reading

def get_dashboard_stats(user_id):
    total_consumption = db.session.query(func.sum(WaterReading.consumption)).filter(
        WaterReading.user_id == user_id
    ).scalar() or 0
    total_readings = db.session.query(func.count(WaterReading.id)).filter(
        WaterReading.user_id == user_id
    ).scalar() or 0
    
    avg_daily = 0
    if total_readings > 0:
        first = WaterReading.query.filter_by(user_id=user_id).order_by(WaterReading.date).first()
        last = WaterReading.query.filter_by(user_id=user_id).order_by(desc(WaterReading.date)).first()
        if first and last and first.date != last.date:
            days = (last.date - first.date).days
            if days > 0:
                avg_daily = total_consumption / days
        else:
             avg_daily = total_consumption

    recent_readings = WaterReading.query.filter_by(user_id=user_id).order_by(desc(WaterReading.date)).limit(10).all()
    
    return {
        "total_consumption": round(total_consumption, 2),
        "avg_daily": round(avg_daily, 2),
        "recent_readings": recent_readings
    }

def get_all_readings(user_id):
    return WaterReading.query.filter_by(user_id=user_id).order_by(desc(WaterReading.date)).all()

def delete_reading_service(id, user_id):
    reading = WaterReading.query.filter_by(id=id, user_id=user_id).first()
    if reading:
        prev = WaterReading.query.filter(
            WaterReading.user_id == user_id,
            WaterReading.date < reading.date
        ).order_by(desc(WaterReading.date)).first()
        next_r = WaterReading.query.filter(
            WaterReading.user_id == user_id,
            WaterReading.date > reading.date
        ).order_by(WaterReading.date).first()
        
        if next_r:
            if prev:
                next_r.consumption = next_r.reading_value - prev.reading_value
            else:
                 next_r.consumption = 0
                 
        db.session.delete(reading)
        db.session.commit()

def get_current_tariff():
    tariff = WaterTariff.query.order_by(desc(WaterTariff.updated_at)).first()
    return tariff.cost_per_unit if tariff else 0.0

def set_tariff(value):
    new_tariff = WaterTariff(cost_per_unit=value)
    db.session.add(new_tariff)
    db.session.commit()
    return new_tariff

def get_cost_analysis(user_id):
    readings = WaterReading.query.filter_by(user_id=user_id).order_by(desc(WaterReading.date)).all()
    tariff = get_current_tariff()
    
    analysis_data = []
    total_monthly_cost = 0.0
    
    window = current_app.config.get('SPIKE_DETECTION_WINDOW', 5)

    for i, reading in enumerate(readings):
        daily_cost = reading.consumption * tariff
        wastage_cost = 0.0
        
        if reading.is_spike:
            prev_readings = readings[i+1 : i+1+window]
            valid_prev = [r.consumption for r in prev_readings if r.consumption is not None]
            
            if valid_prev:
                avg_consumption = sum(valid_prev) / len(valid_prev)
                excess = reading.consumption - avg_consumption
                if excess > 0:
                    wastage_cost = excess * tariff

        analysis_data.append({
            'date': reading.date,
            'consumption': reading.consumption,
            'cost': round(daily_cost, 2),
            'is_spike': reading.is_spike,
            'category': reading.consumption_category,
            'wastage_cost': round(wastage_cost, 2)
        })
        
        if reading.date.month == datetime.now().month and reading.date.year == datetime.now().year:
            total_monthly_cost += daily_cost

    return {
        'current_tariff': tariff,
        'total_monthly_cost': round(total_monthly_cost, 2),
        'analysis_data': analysis_data
    }
