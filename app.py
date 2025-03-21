import os
import secrets
from datetime import datetime, timedelta
import logging

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from itsdangerous import URLSafeTimedSerializer

from models import db, User, Facility, EnergyData
from utils import generate_mock_data, get_ai_recommendations, analyze_trends, get_trend_insights
from ml_predictor import EnergyPredictor

# Initialize the ML predictor
predictor = EnergyPredictor()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))

# Configure the SQLAlchemy database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///energy_intelligence.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create URL safe serializer for password reset tokens
serializer = URLSafeTimedSerializer(app.secret_key)

# Add context processor for templates
@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow
    }

# Initialize scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.start()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def update_mock_data():
    """Update mock data and store in database"""
    with app.app_context():
        facility = Facility.query.first()
        if facility:
            mock_data = generate_mock_data()
            
            # Create a new energy data record
            energy_data = EnergyData(
                timestamp=datetime.utcnow(),
                energy_produced=mock_data['energy_produced'],
                energy_consumed=mock_data['energy_consumed'],
                efficiency=mock_data['efficiency'],
                current_load=mock_data['current_load'],
                facility_id=facility.id
            )
            
            db.session.add(energy_data)
            db.session.commit()
            logger.debug("Updated mock data")


def create_default_facility():
    """Create a default facility if none exists"""
    with app.app_context():
        if Facility.query.count() == 0:
            default_facility = Facility(
                name="Main Facility",
                location="123 Energy Way, Powertown",
                capacity=100.0,
                solar_panels=48
            )
            db.session.add(default_facility)
            db.session.commit()
            logger.info("Created default facility")


# Initialize the app with data
with app.app_context():
    # Create database tables if they don't exist
    db.create_all()
    
    # Create a default user if none exists
    if User.query.count() == 0:
        default_user = User(
            username="demo",
            email="demo@example.com"
        )
        default_user.set_password("password")
        db.session.add(default_user)
        db.session.commit()
        logger.info("Created default user")
    
    # Create a default facility if none exists
    create_default_facility()
    
    # Schedule the mock data update task
    if not scheduler.get_job('update_mock_data'):
        scheduler.add_job(
            update_mock_data,
            'interval',
            minutes=5,
            id='update_mock_data',
            replace_existing=True
        )
        logger.info("Scheduled mock data updates")


@app.route('/')
def index():
    """Render the landing page"""
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        # Check if identifier is username or email
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username/email or password')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        user_check = User.query.filter((User.username == username) | (User.email == email)).first()
        
        if user_check:
            flash('Username or email already exists')
        else:
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgotten password requests"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate password reset token
            token = serializer.dumps(user.email, salt='password-reset-salt')
            
            # Store token and expiry in database
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            # In a real application, send an email with reset link
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f'Password reset link: {reset_url}')
            
            # For demo purposes, display the token
            flash(f'Reset token: {token}')
            flash('A password reset link has been sent to your email')
        else:
            # Don't reveal if email exists or not
            flash('If your email is registered, you will receive a password reset link')
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset using token"""
    try:
        # Find user with this token
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or user.reset_token_expiry < datetime.utcnow():
            flash('The password reset link is invalid or has expired')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            new_password = request.form.get('password')
            
            # Update user's password
            user.set_password(new_password)
            
            # Clear reset token
            user.reset_token = None
            user.reset_token_expiry = None
            
            db.session.commit()
            
            flash('Your password has been updated. You can now log in with your new password')
            return redirect(url_for('login'))
        
        return render_template('reset_password.html', token=token)
        
    except Exception as e:
        flash('An error occurred. Please try again.')
        logger.error(f"Password reset error: {str(e)}")
        return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Render the main dashboard"""
    facility = Facility.query.first()
    
    # Get the latest energy data
    latest_data = EnergyData.query.order_by(EnergyData.timestamp.desc()).first()
    
    # Get AI recommendations based on latest data
    recommendations = []
    if latest_data:
        data_dict = {
            'energy_produced': latest_data.energy_produced,
            'energy_consumed': latest_data.energy_consumed,
            'efficiency': latest_data.efficiency,
            'current_load': latest_data.current_load
        }
        recommendations = get_ai_recommendations(data_dict)
    
    # Get data for the last 24 hours for the charts
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    historical_data = EnergyData.query.filter(EnergyData.timestamp >= one_day_ago).order_by(EnergyData.timestamp).all()
    
    # Format data for the chart
    timestamps = [data.timestamp.strftime('%H:%M') for data in historical_data]
    production = [data.energy_produced for data in historical_data]
    consumption = [data.energy_consumed for data in historical_data]
    efficiency = [data.efficiency for data in historical_data]
    load = [data.current_load for data in historical_data]
    
    return render_template(
        'dashboard.html',
        facility=facility,
        latest_data=latest_data,
        recommendations=recommendations,
        timestamps=timestamps,
        production=production,
        consumption=consumption,
        efficiency=efficiency,
        load=load
    )


@app.route('/historical')
@login_required
def historical_analysis():
    """Render historical data analysis"""
    # Get timeframe from request, default to 7 days
    days = int(request.args.get('days', 7))
    
    # Get historical data for the specified timeframe
    time_ago = datetime.utcnow() - timedelta(days=days)
    historical_data = EnergyData.query.filter(EnergyData.timestamp >= time_ago).order_by(EnergyData.timestamp).all()
    
    # Convert to list of dictionaries for analysis
    data_points = []
    for data in historical_data:
        data_points.append({
            'timestamp': data.timestamp,
            'energy_produced': data.energy_produced,
            'energy_consumed': data.energy_consumed,
            'efficiency': data.efficiency,
            'current_load': data.current_load
        })
    
    # Analyze data to find trends
    trend_analysis = analyze_trends(data_points)
    
    # Get recommendations based on trends
    insights = get_trend_insights(trend_analysis)
    
    # Format data for charts
    timestamps = [data.timestamp.strftime('%m-%d %H:%M') for data in historical_data]
    production = [data.energy_produced for data in historical_data]
    consumption = [data.energy_consumed for data in historical_data]
    efficiency = [data.efficiency for data in historical_data]
    load = [data.current_load for data in historical_data]
    
    return render_template(
        'historical.html',
        days=days,
        trend_analysis=trend_analysis,
        insights=insights,
        timestamps=timestamps,
        production=production,
        consumption=consumption,
        efficiency=efficiency,
        load=load
    )


@app.route('/ml-dashboard')
@login_required
def ml_dashboard():
    """Render ML dashboard with predictions"""
    # Get historical data for training the model
    days_for_training = 30
    time_ago = datetime.utcnow() - timedelta(days=days_for_training)
    historical_data = EnergyData.query.filter(EnergyData.timestamp >= time_ago).order_by(EnergyData.timestamp).all()
    
    # Convert to list of dictionaries for the predictor
    data_points = []
    for data in historical_data:
        data_points.append({
            'timestamp': data.timestamp,
            'energy_produced': data.energy_produced,
            'energy_consumed': data.energy_consumed,
            'efficiency': data.efficiency,
            'current_load': data.current_load
        })
    
    # Train the predictor if we have enough data
    model_score = 0
    if len(data_points) > 24:
        model_score = predictor.train(data_points)
    
    # Get predictions for the next 24 hours
    predictions = predictor.predict(data_points, horizon=24)
    
    # Generate timestamps for predictions
    last_timestamp = datetime.utcnow()
    if data_points:
        last_timestamp = data_points[-1]['timestamp']
    
    prediction_timestamps = []
    for i in range(24):
        next_hour = last_timestamp + timedelta(hours=i+1)
        prediction_timestamps.append(next_hour.strftime('%m-%d %H:%M'))
    
    # Get recent actual data for comparison
    recent_hours = min(24, len(data_points))
    recent_data = data_points[-recent_hours:]
    recent_timestamps = [d['timestamp'].strftime('%m-%d %H:%M') for d in recent_data]
    recent_consumption = [d['energy_consumed'] for d in recent_data]
    
    return render_template(
        'ml_dashboard.html',
        model_score=model_score,
        prediction_timestamps=prediction_timestamps,
        predictions=predictions,
        recent_timestamps=recent_timestamps,
        recent_consumption=recent_consumption
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Render user profile page"""
    if request.method == 'POST':
        # Update profile details
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        
        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if current_password and new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password updated successfully')
            else:
                flash('Current password is incorrect')
        
        db.session.commit()
        flash('Profile updated successfully')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Render application settings page"""
    facility = Facility.query.first()
    
    if request.method == 'POST':
        setting_type = request.form.get('setting_type')
        
        if setting_type == 'facility':
            # Update facility settings
            facility.name = request.form.get('facility_name', facility.name)
            facility.location = request.form.get('facility_location', facility.location)
            facility.capacity = float(request.form.get('facility_capacity', facility.capacity))
            facility.solar_panels = int(request.form.get('facility_solar_panels', facility.solar_panels))
            
            db.session.commit()
            flash('Facility settings updated successfully')
            
        elif setting_type == 'notifications':
            # In a real app, you would save these preferences to a user settings table
            flash('Notification settings updated successfully')
            
        elif setting_type == 'display':
            # In a real app, you would save these preferences to a user settings table
            theme = request.form.get('theme')
            chart_color_scheme = request.form.get('chart_color_scheme')
            dashboard_layout = request.form.get('dashboard_layout')
            default_timeframe = request.form.get('default_timeframe')
            
            # Here we'd save these settings to the database
            # For demo purposes, we'll just acknowledge the change
            flash(f'Display settings updated successfully. Theme set to {theme}.')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', facility=facility)


@app.route('/api/data')
@login_required
def get_data():
    """API endpoint to get the latest energy data"""
    # Get the latest data point
    latest_data = EnergyData.query.order_by(EnergyData.timestamp.desc()).first()
    
    if not latest_data:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 404
    
    # Format data as JSON
    data = {
        'timestamp': latest_data.timestamp.isoformat(),
        'energy_produced': latest_data.energy_produced,
        'energy_consumed': latest_data.energy_consumed,
        'efficiency': latest_data.efficiency,
        'current_load': latest_data.current_load
    }
    
    return jsonify({
        'status': 'success',
        'data': data
    })


@app.route('/api/predictions')
@login_required
def get_predictions():
    """Get energy consumption predictions for the next 24 hours"""
    # Get historical data for training the model
    days_for_training = 30
    time_ago = datetime.utcnow() - timedelta(days=days_for_training)
    historical_data = EnergyData.query.filter(EnergyData.timestamp >= time_ago).order_by(EnergyData.timestamp).all()
    
    # Convert to list of dictionaries for the predictor
    data_points = []
    for data in historical_data:
        data_points.append({
            'timestamp': data.timestamp,
            'energy_produced': data.energy_produced,
            'energy_consumed': data.energy_consumed,
            'efficiency': data.efficiency,
            'current_load': data.current_load
        })
    
    # Train the predictor if we have enough data
    if len(data_points) > 24:
        predictor.train(data_points)
    
    # Get predictions for the next 24 hours
    predictions = predictor.predict(data_points, horizon=24)
    
    # Generate timestamps for predictions
    last_timestamp = datetime.utcnow()
    if data_points:
        last_timestamp = data_points[-1]['timestamp']
    
    prediction_data = []
    for i, value in enumerate(predictions):
        next_hour = last_timestamp + timedelta(hours=i+1)
        prediction_data.append({
            'timestamp': next_hour.isoformat(),
            'value': value
        })
    
    return jsonify({
        'status': 'success',
        'data': prediction_data
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)