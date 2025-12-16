from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services import add_reading_service, get_dashboard_stats, get_all_readings, delete_reading_service, get_cost_analysis, set_tariff
from app.models import User
from app import db
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return redirect(url_for('main.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('main.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('main.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('main.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('main.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/')
@login_required
def index():
    stats = get_dashboard_stats(current_user.id)
    history = get_all_readings(current_user.id)
    return render_template('index.html', stats=stats, history=history)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
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
            
            add_reading_service(current_user.id, date_obj, value)
            flash('Reading added successfully!', 'success')
            return redirect(url_for('main.index'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An unexpected error occurred.', 'error')
            
    return render_template('add.html')

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_reading(id):
    try:
        delete_reading_service(id, current_user.id)
        flash('Reading deleted successfully.', 'success')
    except Exception as e:
        flash('Error deleting reading.', 'error')
    
    return redirect(url_for('main.index'))

@bp.route('/cost')
@login_required
def cost_analysis():
    data = get_cost_analysis(current_user.id)
    return render_template('cost.html', **data)

@bp.route('/cost/update', methods=['POST'])
@login_required
def update_tariff():
    try:
        cost_str = request.form.get('cost')
        if not cost_str:
            flash('Please provide a valid cost.', 'error')
            return redirect(url_for('main.cost_analysis'))
        
        cost = float(cost_str)
        if cost < 0:
             flash('Cost cannot be negative.', 'error')
             return redirect(url_for('main.cost_analysis'))
             
        set_tariff(cost)
        flash('Tariff updated successfully.', 'success')
    except ValueError:
        flash('Invalid cost value.', 'error')
    except Exception as e:
        flash('Error updating tariff.', 'error')
        
    return redirect(url_for('main.cost_analysis'))

