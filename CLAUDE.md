# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Raspberry Pi MTA transit tracker that displays real-time arrival information for Q train (uptown/downtown) at 86th Street and M101/M102/M103 buses at 83rd Street & 2nd Avenue. The app features both terminal and GUI interfaces, with weather forecasting and auto-refreshing displays optimized for morning commute dashboard use.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the terminal application
python main.py

# Run the GUI application (recommended for display)
python gui.py

# Windows batch scripts (auto-install dependencies)
run.bat              # Terminal version
run_gui.bat          # GUI version (for Raspberry Pi)
run_gui_windows.bat  # Windows GUI version

# Test individual components
python -c "from subway_tracker import SubwayTracker; s=SubwayTracker(); print(s.get_q_train_arrivals())"
python -c "from bus_tracker import BusTracker; b=BusTracker(); print(b.get_bus_arrivals())"
python -c "from weather_tracker import WeatherTracker; w=WeatherTracker(); print(w.get_weather_data())"

# Test bus API specifically
python test_bus_api.py
```

## Architecture

The application uses a modular, multi-interface design with robust fallback systems:

### Core Components
- **main.py**: Terminal interface with display loop and cross-platform screen clearing
- **gui.py**: Pygame-based GUI optimized for 1200x680 displays with clean, modern design
- **subway_tracker.py**: Q train GTFS-RT data processor with multiple API fallbacks
- **bus_tracker.py**: MTA Bus Time SIRI API client with dynamic stop discovery
- **weather_tracker.py**: OpenWeatherMap integration with hourly forecasting
- **config.py**: Centralized configuration with API keys, endpoints, and coordinate mappings

### Interface Design Patterns
- **Terminal Mode**: Text-based with emoji indicators, 30-second refresh cycle
- **GUI Mode**: Modern glassmorphic design with real-time updates, clean typography
- **Responsive Layout**: GUI components positioned to fit exactly within screen bounds

## API Integration & Fallback Strategy

### Subway Data (GTFS-RT)
- **Primary**: MTA GTFS-RT protobuf feeds via `gtfs-realtime-bindings`
- **Endpoint**: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct/gtfs-nqrw`
- **Fallbacks**: Third-party proxies (api.nyct.io, transitland), mock data
- **Processing**: Filters Q train (route_id "Q") for stops Q05N/Q05S with time offset adjustments

### Bus Data (SIRI API) 
- **Primary**: MTA Bus Time JSON API with coordinate-based stop discovery
- **Endpoint**: `/stop-monitoring.json` with MonitoringRef and LineRef filters
- **Features**: Shows stops away, filters M101 LIMITED, dynamic stop ID resolution
- **Fallbacks**: Hard-coded stop IDs, realistic mock data with random stop distances

### Weather Data (OpenWeatherMap)
- **Current Conditions**: Temperature, feels-like, humidity, wind speed
- **Hourly Forecast**: 5 periods with detailed conditions and precipitation probability
- **Fallbacks**: Multiple timeout retries, IPv4-only connections, mock weather data

## Data Processing Patterns

### Error Handling & Resilience
- Each API component wrapped in try/catch with graceful degradation
- Individual failures don't crash the main application
- Mock data systems provide realistic fallback behavior
- Progressive timeout strategies for network requests

### Real-time Data Management
- **Subway**: Timestamp conversion from GTFS epoch to local time with directional separation
- **Bus**: Live vehicle tracking with arrival predictions and distance from stop
- **Weather**: Hourly forecast with temperature (actual + feels-like) and conditions
- **Filtering**: Removes past arrivals, limits to 3 upcoming per route

### Display Optimization
- **Terminal**: Compact text format with truncated destination names
- **GUI**: Clean glassmorphic cards with proper spacing, color-coded urgency
- **Refresh Strategy**: 30-second cycles with background data fetching threads

## GUI Interface Design

### Modern Clean Layout
- **Screen Resolution**: 1200x680 optimized for desktop/laptop displays
- **Design Language**: Glassmorphic cards with gradient backgrounds
- **Typography**: Clean, readable fonts with proper hierarchy
- **Color Coding**: Red ≤2min, Orange ≤5min, White >5min for urgency

### Layout Management
- **Header**: 60px - Simple title, current time, last update status
- **Weather**: 120px - 5 hourly forecast cards with temp and conditions
- **Subway**: 160px - Side-by-side uptown/downtown Q train arrivals  
- **Bus**: 120px - M102/M103 routes with arrival times and destinations
- **Footer**: 30px - Simple instruction text (Press R to refresh • ESC to exit)

### Dependencies & Installation
- Python 3.7+ with pygame for GUI rendering
- Network connectivity required for live data (graceful offline fallback)
- Auto-installation scripts for Windows/Linux deployment

## Configuration Management

### API Keys
- **Bus API**: Pre-configured working key for MTA Bus Time
- **Subway API**: Requires separate registration at api.mta.info (see api_setup_guide.md)
- **Weather API**: OpenWeatherMap key included for basic weather data

### Location Configuration
- **Q Train**: 86th Street station (Q05N northbound, Q05S southbound)
- **Buses**: 83rd Street & 2nd Avenue (coordinates: 40.777, -73.950)
- **Stop IDs**: Route-specific mappings (M102: 402694, M103: 402694)

### Timing Adjustments
- **Subway**: Configurable per-direction time offsets (uptown -2 min, downtown -5 min correction)
- **Bus**: 1-minute arrival adjustment for walking time to stop
- **Weather**: 3-hour forecast intervals from current time

## Important Notes

- GUI applications run as primary interface for desktop deployment
- Mock data systems ensure application works without internet connectivity
- All timestamps converted to local time zone for user display
- Bus tracking includes real-time vehicle position data when available
- Weather data includes both current conditions and 5-period hourly forecasts
- Clean, minimal design with no confusing indicators or clutter