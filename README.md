# Energy-System

# Energy Intelligence Platform

A comprehensive smart energy management platform that provides real-time monitoring, AI-powered analytics, and predictive insights for energy consumption and production systems.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Hardware Integration](#hardware-integration)
- [API Documentation](#api-documentation)
- [Usage Guide](#usage-guide)
- [Machine Learning Components](#machine-learning-components)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The Energy Intelligence Platform is a full-stack web application designed to help homes and businesses optimize their energy consumption through real-time monitoring, historical analysis, and AI-powered predictions. The platform integrates with IoT sensors and energy monitoring hardware to collect data and provide actionable insights.

### Key Capabilities

- **Real-time Energy Monitoring**: Track energy production and consumption in real-time
- **Hardware Integration**: Connect with IoT sensors and energy monitoring devices
- **AI-Powered Analytics**: Machine learning algorithms for consumption prediction
- **Voltage Monitoring**: Advanced electrical parameter monitoring with alert systems
- **Historical Analysis**: Trend analysis and pattern recognition
- **Smart Recommendations**: AI-generated optimization suggestions
- **User Management**: Secure authentication and profile management

## Features

### Dashboard & Monitoring
- Real-time energy data visualization
- Interactive charts and graphs
- Live hardware status monitoring
- Alert system for critical conditions
- Energy efficiency tracking

### Analytics & Predictions
- Machine learning-based consumption forecasting
- Historical trend analysis
- Peak usage pattern identification
- Efficiency optimization recommendations
- Cost-saving opportunity identification

### Hardware Integration
- RESTful API for sensor data ingestion
- Support for multiple electrical parameters
- Real-time voltage monitoring with alerts
- Configurable threshold settings
- Hardware connectivity status tracking

### User Features
- Secure user authentication
- Profile management with image upload
- Customizable dashboard themes
- Notification preferences
- Password reset functionality

## Technology Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with session management
- **Scheduling**: APScheduler for background tasks
- **Machine Learning**: NumPy for predictive analytics

### Frontend
- **UI Framework**: Bootstrap 5.3
- **Charts**: Chart.js for data visualization
- **Icons**: Feather Icons
- **Fonts**: Google Fonts (Inter)
- **Animations**: Animate.css

### Infrastructure
- **Web Server**: Flask development server / Gunicorn (production)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Security**: Werkzeug security utilities
- **File Handling**: Werkzeug file utilities

### Development Tools
- **Package Management**: uv (Python package manager)
- **Environment**: Replit-compatible setup
- **Configuration**: Environment variables for settings

## Architecture

### Application Structure
```
Energy Intelligence Platform
├── Web Interface (Flask + Bootstrap)
├── API Layer (RESTful endpoints)
├── Data Processing (Python + SQLAlchemy)
├── Machine Learning (Custom predictor)
├── Hardware Integration (IoT API)
└── Database (SQLite/PostgreSQL)
```

### Data Flow
1. **Hardware Sensors** → Send data via HTTP POST to `/api/hardware/data`
2. **API Layer** → Validates and processes incoming sensor data
3. **Database** → Stores energy data with electrical parameters
4. **Analytics Engine** → Processes data for insights and predictions
5. **Web Interface** → Displays real-time and historical data to users

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Internet connection for CDN resources

### Quick Start on Replit

1. **Fork the Project**: Click "Use Template" or fork this repl
2. **Install Dependencies**: Dependencies are automatically installed via `pyproject.toml`
3. **Run the Application**: Click the "Run" button or use the terminal

### Manual Setup

1. **Clone the Repository**:
   ```bash
   git clone [repository-url]
   cd energy-intelligence-platform
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Initialize Database**:
   ```bash
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

5. **Access the Platform**: Open your browser to `http://localhost:5000`

### Default Credentials
- **Username**: demo
- **Password**: password

## Hardware Integration

The platform supports integration with IoT sensors and energy monitoring devices through RESTful API endpoints.

### API Endpoints

#### Data Submission
```http
POST /api/hardware/data
Headers:
  X-API-Key: your-api-key
  Content-Type: application/json

{
  "energy_produced": 75.5,
  "energy_consumed": 62.3,
  "current_load": 35.8,
  "voltage": 220.5,
  "current": 15.2,
  "current1": 5.1,
  "current2": 5.0,
  "current3": 5.1,
  "frequency": 50.0,
  "power_factor": 0.95,
  "facility_id": 1
}
```

#### Hardware Status Check
```http
GET /api/hardware/status
Headers:
  X-API-Key: your-api-key
```

#### Configuration Retrieval
```http
GET /api/hardware/config
Headers:
  X-API-Key: your-api-key
```

### Supported Parameters

#### Required Fields
- `energy_produced`: Energy production in kWh
- `energy_consumed`: Energy consumption in kWh
- `current_load`: Current system load percentage

#### Optional Electrical Parameters
- `voltage`: System voltage in Volts
- `current`: Total current in Amperes
- `current1`, `current2`, `current3`: Three-phase currents
- `frequency`: System frequency in Hz
- `power_factor`: Power factor (0.0 - 1.0)

### Example Integration Code

**Python Client Example** (`examples/python_sensor_client.py`):
```python
import requests
import time
import random

API_URL = "https://your-repl-url.com/api/hardware/data"
API_KEY = "your-api-key"

while True:
    data = {
        "energy_produced": round(random.uniform(50, 100), 2),
        "energy_consumed": round(random.uniform(40, 80), 2),
        "current_load": round(random.uniform(20, 60), 2),
        "voltage": round(random.uniform(215, 225), 1),
        "current": round(random.uniform(10, 20), 1),
        "frequency": round(random.uniform(49.8, 50.2), 1),
        "power_factor": round(random.uniform(0.85, 0.98), 2)
    }
    
    response = requests.post(API_URL, json=data, headers={"X-API-Key": API_KEY})
    print(f"Response: {response.status_code}")
    time.sleep(300)  # Send data every 5 minutes
```

## API Documentation

### Authentication
All hardware API endpoints require an API key in the header:
```
X-API-Key: your-api-key
```

### Web API Endpoints (Authenticated Users)

#### Get Latest Data
```http
GET /api/latest-hardware-data
```
Returns the most recent sensor data (within last 60 seconds).

#### Check Hardware Status
```http
GET /api/hardware-status-check
```
Returns whether hardware has sent recent data.

#### Get Predictions
```http
GET /api/predictions
```
Returns 24-hour energy consumption predictions.

### Debug Endpoints (Development Only)

#### Test Hardware Data
```http
GET /api/debug/test-hardware
```
Creates test sensor data for development.

#### Voltage Demo
```http
GET /api/debug/voltage-demo?condition=normal
```
Demonstrates voltage monitoring with different conditions:
- `normal`: Standard voltage levels
- `high_warning`: High voltage warning
- `high_critical`: Critical high voltage
- `low_warning`: Low voltage warning
- `low_critical`: Critical low voltage
- `fluctuating`: Variable voltage levels

## Usage Guide

### Getting Started

1. **Login**: Use the default credentials (demo/password) or create a new account
2. **Dashboard**: View real-time energy data and system status
3. **Settings**: Configure facility details and hardware integration
4. **Historical**: Analyze energy trends and patterns
5. **ML Dashboard**: View consumption predictions and insights

### Dashboard Features

#### Real-time Monitoring
- **Energy Production**: Current solar/renewable energy generation
- **Energy Consumption**: Real-time consumption levels
- **System Efficiency**: Overall system performance
- **Hardware Status**: Live connection status with sensors

#### Charts and Visualization
- **Energy Chart**: 24-hour production vs consumption
- **Efficiency Trends**: System efficiency over time
- **Load Monitoring**: Current system load levels
- **Voltage Monitoring**: Real-time voltage levels with alerts

#### AI Recommendations
The system provides intelligent suggestions based on current data:
- High consumption warnings
- Efficiency optimization tips
- Load balancing recommendations
- Maintenance alerts

### Historical Analysis

Access detailed historical data analysis:
- **Timeframe Selection**: Choose 7, 30, or custom day ranges
- **Trend Analysis**: Identify consumption patterns
- **Peak Usage**: Find high-consumption periods
- **Efficiency Tracking**: Monitor performance improvements

### Machine Learning Dashboard

View AI-powered insights:
- **Consumption Predictions**: 24-hour forecasts
- **Model Accuracy**: Prediction reliability scores
- **Savings Opportunities**: Optimization recommendations
- **Pattern Recognition**: Usage pattern identification

## Machine Learning Components

### EnergyPredictor Class

The platform includes a custom machine learning predictor (`ml_predictor.py`) that:

#### Training Process
1. **Data Collection**: Gathers historical energy consumption data
2. **Pattern Recognition**: Identifies hourly and daily usage patterns
3. **Baseline Calculation**: Establishes average consumption levels
4. **Model Validation**: Tests prediction accuracy on historical data

#### Prediction Features
- **Hourly Patterns**: How consumption varies by hour of day
- **Daily Patterns**: How consumption varies by day of week
- **Trend Analysis**: Long-term consumption trends
- **Seasonal Adjustments**: Account for weather and seasonal changes

#### Accuracy Metrics
- **MAPE**: Mean Absolute Percentage Error
- **Validation Score**: Model reliability percentage
- **Confidence Intervals**: Prediction uncertainty ranges

## File Structure

```
energy-intelligence-platform/
├── app.py                      # Main Flask application
├── main.py                     # Application entry point
├── models.py                   # Database models
├── ml_predictor.py             # Machine learning predictor
├── utils.py                    # Utility functions
├── test_hardware_connection.py # Hardware testing utility
├── pyproject.toml              # Python dependencies
├── replit.nix                  # Replit configuration
├── .replit                     # Replit run configuration
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── dashboard.html         # Main dashboard
│   ├── historical.html        # Historical analysis
│   ├── landing.html           # Landing page
│   ├── login.html             # Authentication
│   ├── ml_dashboard.html      # ML insights
│   ├── profile.html           # User profile
│   ├── settings.html          # Configuration
│   └── voltage_demo.html      # Voltage monitoring demo
├── static/                     # Static assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   ├── img/                   # Images
│   └── uploads/               # User uploads
├── examples/                   # Integration examples
│   ├── HARDWARE_INTEGRATION.md
│   ├── python_sensor_client.py
│   └── esp8266_sensor_client.ino
└── instance/                   # Database files
    └── energy_intelligence.db
```

## Configuration

### Environment Variables

Set these environment variables for production:

```bash
# Database Configuration
DATABASE_URL="postgresql://user:password@host:port/database"

# Security
SESSION_SECRET="your-secret-key-here"

# Hardware Integration
HARDWARE_API_KEY="your-hardware-api-key"

# Application Settings
FLASK_ENV="production"
```

### Database Configuration

#### Development (SQLite)
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/energy_intelligence.db"
```

#### Production (PostgreSQL)
```python
SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host:port/database"
```

### Hardware Settings

Configure hardware integration in the settings panel:
- **API Key**: Generate secure keys for device authentication
- **Reporting Interval**: Set data collection frequency
- **Voltage Thresholds**: Configure alert levels
- **Facility Details**: Set location and capacity information

## Troubleshooting

### Common Issues

#### Database Errors
```bash
# Reset database
rm -f instance/energy_intelligence.db
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
```

#### Hardware Connection Issues
1. Check API key configuration
2. Verify network connectivity
3. Review endpoint URLs
4. Check data format compliance

#### Missing Dependencies
```bash
# Reinstall dependencies
uv sync --reinstall
```

#### Port Conflicts
Change the port in `main.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Debug Mode

Enable debug endpoints for development:
```bash
export FLASK_ENV=development
```

Access debug features:
- `/api/debug/test-hardware` - Generate test data
- `/api/debug/voltage-demo` - Voltage monitoring demo

### Logs and Monitoring

Check application logs for detailed error information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support and Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Reporting Issues
When reporting issues, include:
- Error messages
- Steps to reproduce
- Hardware configuration
- Browser and system information

### Feature Requests
For new features, provide:
- Use case description
- Expected behavior
- Integration requirements
- Performance considerations

---

**Energy Intelligence Platform** - Smart energy management for the future.

For technical support or questions, refer to the examples directory or consult the API documentation.
