# MTA Morning Transit Tracker

A Raspberry Pi app that displays real-time arrival information for:
- Q Train (uptown and downtown) at 86th Street
- M101 (non-limited), M102, M103 buses at 83rd Street & 2nd Avenue

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Features

- Real-time Q train arrivals for both directions
- Real-time bus arrivals for M101/M102/M103 routes
- Auto-refreshing display every 30 seconds
- Clean terminal interface optimized for Raspberry Pi

## API Configuration

The app uses your MTA API key configured in `config.py`. The key is already set up for:
- Subway data from MTA GTFS-RT feeds
- Bus data from MTA Bus Time SIRI API

## Files

- `main.py` - Main application with display loop
- `subway_tracker.py` - Q train arrival tracking
- `bus_tracker.py` - Bus arrival tracking  
- `config.py` - API keys and configuration
- `requirements.txt` - Python dependencies