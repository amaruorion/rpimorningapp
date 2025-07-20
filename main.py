#!/usr/bin/env python3
"""
MTA Morning Transit Tracker
Raspberry Pi app to track Q train and M101/M102/M103 bus arrivals
"""

import time
import os
from datetime import datetime
from subway_tracker import SubwayTracker
from bus_tracker import BusTracker
from weather_tracker import WeatherTracker

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_header():
    """Display the app header"""
    now = datetime.now()
    print("🏙️  MTA MORNING TRANSIT TRACKER")
    print("=" * 40)
    print(f"📅 {now.strftime('%A, %B %d, %Y')}")
    print(f"⏰ {now.strftime('%I:%M:%S %p')}")

def main():
    """Main application loop"""
    print("🚀 Starting MTA Morning Transit Tracker...")
    print("Press Ctrl+C to exit")
    
    subway_tracker = SubwayTracker()
    bus_tracker = BusTracker()
    weather_tracker = WeatherTracker()
    
    try:
        while True:
            clear_screen()
            display_header()
            
            # Display weather information
            weather_tracker.display_weather_info()
            
            # Display subway information
            subway_tracker.display_subway_info()
            
            # Display bus information
            bus_tracker.display_bus_info()
            
            print("\n🎉 ALL DATA LOADED SUCCESSFULLY!")
            print("=" * 40)
            print("🔄 Refreshing in 30 seconds... (Ctrl+C to exit)")
            
            # Wait 30 seconds before next update
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Have a great commute!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your internet connection and API key.")

if __name__ == "__main__":
    main()