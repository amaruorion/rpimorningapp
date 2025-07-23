# Bus API key (valid for MTA Bus Time)
BUS_API_KEY = "d098c010-5dd0-48f8-b7f8-33834298cf76"

# Subway API key (you need to register separately at api.mta.info)
SUBWAY_API_KEY = None  # Register at https://api.mta.info/ for subway data

# Primary MTA subway feeds (requires separate API key)
SUBWAY_FEEDS = {
    "nqrw": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw"
}

# Alternative subway endpoints (try if main API fails)
ALTERNATIVE_FEEDS = {
    "mtapi": "https://api.nyct.io/gtfs-nqrw",  # Third-party proxy
    "transitland": "https://transit.land/api/v2/rest/feeds/f-dr5r-nyct~rt"  # Transitland
}

BUS_API_BASE = "https://bustime.mta.info/api/siri/stop-monitoring.json"

Q_TRAIN_STATIONS = {
    "86th_street_uptown": "Q05N",
    "86th_street_downtown": "Q05S"
}

BUS_STOP_COORDINATES = {
    "83rd_2nd_ave": {
        "lat": 40.777,
        "lon": -73.950
    }
}

# Specific stop IDs for different bus routes
BUS_STOP_IDS = {
    "M101": "405652",  # 86th Street stop
    "M102": "402694",  # Different stop for M102
    "M103": "402694"   # Same stop as M102
}

# Time adjustment (in minutes) - positive number makes times later, negative makes them earlier
SUBWAY_TIME_OFFSET_MINUTES = {
    "uptown": -2,   # Subtract 2 minutes for uptown (currently 2 minutes fast)
    "downtown": -5  # Subtract 5 minutes for downtown (currently 5 minutes fast)
}

# OpenWeatherMap API configuration
WEATHER_API_KEY = "a087255cb25394fc4d92ed46fdfe4364"
WEATHER_CITY = "Manhattan,US"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"