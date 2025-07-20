# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Raspberry Pi MTA transit tracker that displays real-time arrival information for Q train (uptown/downtown) at 86th Street and M101/M102/M103 buses at 83rd Street & 2nd Avenue. The app refreshes every 30 seconds and is designed for a morning commute dashboard.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py

# Test individual components (for development)
python -c "from subway_tracker import SubwayTracker; s=SubwayTracker(); print(s.get_q_train_arrivals())"
python -c "from bus_tracker import BusTracker; b=BusTracker(); print(b.get_bus_arrivals())"
```

## Architecture

The application follows a modular design with clear separation of concerns:

- **main.py**: Application orchestrator with display loop and terminal UI
- **subway_tracker.py**: Handles Q train GTFS-RT data from MTA subway feeds  
- **bus_tracker.py**: Manages M101/M102/M103 bus data via MTA Bus Time SIRI API
- **config.py**: Centralized configuration for API keys, endpoints, and stop mappings

## MTA API Integration

### Subway Data (GTFS-RT)
- Uses Google Protocol Buffers format via `gtfs-realtime-bindings`
- Fetches from MTA NQRW feed: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct/gtfs-nqrw`
- Filters for Q train route and specific stop IDs (Q05N/Q05S for 86th Street)
- Parses binary protobuf data and converts timestamps to arrival predictions

### Bus Data (SIRI API)
- Uses MTA Bus Time JSON API with coordinate-based stop discovery
- Primary endpoint: `/stop-monitoring.json` with stop ID and route filters
- Fallback stop discovery via `/stops-for-location.json` using lat/lon coordinates
- Filters out M101 LIMITED buses (shows non-limited only)

## Key Patterns

### Configuration Management
All API endpoints, stop IDs, and coordinates are centralized in `config.py`. Station mappings use descriptive names (`86th_street_uptown`) rather than raw stop IDs.

### Error Handling
Each API call is wrapped in try/catch blocks with graceful degradation. Individual component failures don't crash the main application.

### Data Processing
- Subway: Separates uptown/downtown by stop ID suffix (N=uptown, S=downtown)
- Bus: Dynamic stop ID discovery with hard-coded fallback (stop ID 308214)
- Both limit results to 3 upcoming arrivals and filter out past times

### Display Loop
30-second refresh cycle with cross-platform screen clearing and real-time timestamp display. Uses emoji indicators for visual clarity on terminal interfaces.

## Important Notes

- API key is currently hard-coded in `config.py` but should be moved to environment variable
- Bus stop coordinates for 83rd & 2nd Avenue may need adjustment based on actual MTA stop locations
- Application designed for continuous operation on Raspberry Pi with terminal output