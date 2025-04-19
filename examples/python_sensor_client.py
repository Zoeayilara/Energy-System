#!/usr/bin/env python3
"""
Python Test Client for Energy Intelligence Hardware API

This script demonstrates how to send energy data to the
Energy Intelligence application using Python requests library.
It can be used for testing or as a basis for integration with
other Python-based energy monitoring systems.
"""

import requests
import json
import time
import random
from datetime import datetime

# API Configuration
SERVER_URL = "http://localhost:5000"  # Change to your server URL
API_KEY = "dev_hardware_key"  # Change to your API key

# Reporting configuration
REPORT_INTERVAL = 300  # seconds (5 minutes)

def get_server_config():
    """Get configuration from the server"""
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(f"{SERVER_URL}/api/hardware/config", headers=headers)
        
        if response.status_code == 200:
            config = response.json()
            print("Server configuration received:")
            print(json.dumps(config, indent=2))
            return config
        else:
            print(f"Error getting config: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def check_server_status():
    """Check if the server is online"""
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(f"{SERVER_URL}/api/hardware/status", headers=headers)
        
        if response.status_code == 200:
            status = response.json()
            print("Server status:")
            print(json.dumps(status, indent=2))
            return True
        else:
            print(f"Error checking status: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def send_sensor_data(energy_produced, energy_consumed, current_load):
    """Send energy data to the server"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "energy_produced": energy_produced,
        "energy_consumed": energy_consumed,
        "current_load": current_load
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/hardware/data", 
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Data sent successfully. Response: {result}")
            return True
        else:
            print(f"Error sending data: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def simulate_energy_readings():
    """Simulate energy sensor readings"""
    # Get the current hour to simulate day/night solar production
    current_hour = datetime.now().hour
    
    # Simulate solar energy production (more during day, less at night)
    if 6 <= current_hour <= 18:
        # Daytime production
        energy_produced = random.uniform(50.0, 100.0)
    else:
        # Nighttime production
        energy_produced = random.uniform(0.0, 10.0)
    
    # Simulate energy consumption
    energy_consumed = random.uniform(30.0, 80.0)
    
    # Simulate current load
    current_load = random.uniform(20.0, 60.0)
    
    return energy_produced, energy_consumed, current_load

def main():
    """Main function to run the test client"""
    print("Energy Intelligence Python Test Client")
    print("=====================================")
    
    # Check if server is online
    if not check_server_status():
        print("Cannot connect to server. Exiting.")
        return
    
    # Get initial configuration
    config = get_server_config()
    
    # If config was received successfully, we can use its values
    if config and "config" in config and "reporting_interval" in config["config"]:
        report_interval = config["config"]["reporting_interval"]
    else:
        report_interval = REPORT_INTERVAL
    
    print(f"\nSending simulated data every {report_interval} seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Get simulated energy readings
            energy_produced, energy_consumed, current_load = simulate_energy_readings()
            
            print(f"\nTime: {datetime.now().isoformat()}")
            print(f"Energy Produced: {energy_produced:.2f} kWh")
            print(f"Energy Consumed: {energy_consumed:.2f} kWh")
            print(f"Current Load: {current_load:.2f} kW")
            
            # Send data to server
            send_sensor_data(energy_produced, energy_consumed, current_load)
            
            # Wait for the next reporting interval
            time.sleep(report_interval)
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()