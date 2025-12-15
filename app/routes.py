from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import add_reading_service, get_dashboard_stats, get_all_readings, delete_reading_service
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    stats = get_dashboard_stats()
    history = get_all_readings()
    return render_template('index.html', stats=stats, history=history)

@bp.route('/add', methods=['GET', 'POST'])
def add_reading():
    if request.method == 'POST':
        date_str = request.form.get('date')
        value_str = request.form.get('value')
        
        if not date_str or not value_str:
            flash('Please provide both date and reading value.', 'error')
            return redirect(url_for('main.add_reading'))
            
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            value = float(value_str)
            
            add_reading_service(date_obj, value)
            flash('Reading added successfully!', 'success')
            return redirect(url_for('main.index'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An unexpected error occurred.', 'error')
            
    return render_template('add.html')

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_reading(id):
    try:
        delete_reading_service(id)
        flash('Reading deleted successfully.', 'success')
    except Exception as e:
        flash('Error deleting reading.', 'error')
    
    return redirect(url_for('main.index'))
