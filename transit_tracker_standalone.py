#!/usr/bin/env python3
"""
NYC Transit & Weather Tracker - Standalone Version
Raspberry Pi app with GUI for morning commute tracking
All-in-one file with no dependencies on other modules
"""

import pygame
import sys
import time
import threading
import requests
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2

# Force IPv4 to avoid network issues
def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family

# Configuration
BUS_API_KEY = "d098c010-5dd0-48f8-b7f8-33834298cf76"
SUBWAY_API_KEY = None  # Register at https://api.mta.info/ for subway data
WEATHER_API_KEY = "a087255cb25394fc4d92ed46fdfe4364"

# API URLs
BUS_API_BASE = "https://bustime.mta.info/api/siri/stop-monitoring.json"
SUBWAY_FEEDS = {
    "nqrw": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw"
}
ALTERNATIVE_FEEDS = {
    "mtapi": "https://api.nyct.io/gtfs-nqrw",
    "transitland": "https://transit.land/api/v2/rest/feeds/f-dr5r-nyct~rt"
}
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Stop IDs and coordinates
Q_TRAIN_STATIONS = {
    "86th_street_uptown": "Q05N",
    "86th_street_downtown": "Q05S"
}
BUS_STOP_IDS = {
    "M101": "405652",
    "M102": "402694",
    "M103": "402694"
}
SUBWAY_TIME_OFFSET_MINUTES = {
    "uptown": 0,
    "downtown": -5
}
WEATHER_CITY = "Manhattan,US"

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
DARK_BG = (20, 25, 30)
CARD_BG = (30, 35, 40)
WHITE = (255, 255, 255)
BLUE = (0, 123, 191)
LIGHT_BLUE = (100, 181, 246)
ORANGE = (255, 108, 0)
LIGHT_ORANGE = (255, 183, 77)
GREEN = (0, 147, 60)
LIGHT_GREEN = (129, 199, 132)
RED = (238, 53, 36)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 235, 59)

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900

class SubwayTracker:
    def __init__(self):
        self.api_key = SUBWAY_API_KEY
        
    def get_q_train_arrivals(self):
        """Get Q train arrival times for both uptown and downtown"""
        arrivals = self._try_mta_api()
        if arrivals:
            return arrivals
            
        arrivals = self._try_alternative_apis()
        if arrivals:
            return arrivals
            
        return self._get_mock_data()
    
    def _try_mta_api(self):
        """Try the official MTA API"""
        try:
            feed_url = SUBWAY_FEEDS['nqrw']
            
            if self.api_key:
                headers = {"x-api-key": self.api_key}
                response = requests.get(feed_url, headers=headers, timeout=(10, 30))
                
                if response.status_code == 200:
                    result = self._parse_gtfs_data(response.content)
                    if result:
                        print("✅ Using REAL subway data from MTA API (authenticated)")
                        return result
                elif response.status_code == 403:
                    print("Subway API key failed, trying without authentication...")
            
            print("Trying subway feed without authentication...")
            response = requests.get(feed_url, timeout=(10, 30))
            response.raise_for_status()
            result = self._parse_gtfs_data(response.content)
            if result:
                print("✅ Using REAL subway data from MTA API (public access)")
                return result
            
        except Exception as e:
            print(f"MTA subway API failed: {e}")
            return None
    
    def _try_alternative_apis(self):
        """Try alternative API endpoints"""
        for name, url in ALTERNATIVE_FEEDS.items():
            try:
                print(f"Trying alternative API: {name}")
                response = requests.get(url, timeout=(10, 35))
                response.raise_for_status()
                result = self._parse_gtfs_data(response.content)
                if result:
                    print(f"✅ Using REAL subway data from {name} API")
                    return result
            except Exception as e:
                print(f"Alternative API {name} failed: {e}")
                continue
        return None
    
    def _parse_gtfs_data(self, content):
        """Parse GTFS realtime data"""
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(content)
            
            arrivals = {"uptown": [], "downtown": []}
            
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip = entity.trip_update
                    
                    if hasattr(trip.trip, 'schedule_relationship'):
                        if trip.trip.schedule_relationship != 0:
                            continue
                    
                    if trip.trip.route_id == 'Q':
                        for stop_update in trip.stop_time_update:
                            if stop_update.stop_id in ['Q05N', 'Q05S']:
                                arrival_time = None
                                if stop_update.HasField('arrival'):
                                    arrival_time = datetime.fromtimestamp(stop_update.arrival.time)
                                elif stop_update.HasField('departure'):
                                    arrival_time = datetime.fromtimestamp(stop_update.departure.time)
                                
                                if arrival_time:
                                    direction = "uptown" if stop_update.stop_id.endswith('N') else "downtown"
                                    
                                    corrected_arrival_time = arrival_time
                                    offset = SUBWAY_TIME_OFFSET_MINUTES.get(direction, 0)
                                    corrected_arrival_time = arrival_time + timedelta(minutes=offset)
                                    
                                    now = datetime.now()
                                    
                                    if corrected_arrival_time < now:
                                        continue
                                    
                                    time_diff = (corrected_arrival_time - now).total_seconds()
                                    minutes_away = round(time_diff / 60)
                                    
                                    if minutes_away > 0:
                                        minutes_away = minutes_away - 1
                                    
                                    if direction == "uptown" and minutes_away > 0:
                                        minutes_away = minutes_away - 1
                                    
                                    if minutes_away >= 0:
                                        arrivals[direction].append({
                                            "minutes": minutes_away,
                                            "time": corrected_arrival_time.strftime("%H:%M")
                                        })
            
            for direction in arrivals:
                arrivals[direction] = sorted(arrivals[direction], key=lambda x: x["minutes"])[:3]
                
            return arrivals
            
        except Exception as e:
            print(f"Error parsing GTFS data: {e}")
            return None
    
    def _get_mock_data(self):
        """Return mock data when APIs are unavailable"""
        print("🔸 Using MOCK subway data (APIs unavailable)")
        import random
        
        mock_arrivals = {"uptown": [], "downtown": []}
        
        for direction in ["uptown", "downtown"]:
            for i in range(3):
                minutes = random.randint(2, 15) + (i * 5)
                arrival_time = datetime.now().replace(second=0, microsecond=0)
                arrival_time = arrival_time.replace(minute=arrival_time.minute + minutes)
                
                mock_arrivals[direction].append({
                    "minutes": minutes,
                    "time": arrival_time.strftime("%H:%M")
                })
        
        return mock_arrivals

class BusTracker:
    def __init__(self):
        self.api_key = BUS_API_KEY
        
    def get_bus_arrivals(self):
        """Get M102, M103 bus arrival times"""
        arrivals, error_msg = self._try_bus_api()
        if any(arrivals.values()):
            return arrivals
            
        if error_msg == "No buses found":
            print("ℹ️  No buses currently scheduled at this stop")
            return {"M102": [], "M103": []}
        else:
            return self._get_mock_bus_data(error_msg)
    
    def _try_bus_api(self):
        """Try to get real bus data from MTA API"""
        arrivals = {"M102": [], "M103": []}
        routes = ["MTA NYCT_M102", "MTA NYCT_M103"]
        real_data_found = False
        errors = []
        
        for route in routes:
            try:
                route_short = route.split("_")[-1]
                route_stop_id = BUS_STOP_IDS.get(route_short, "405652")
                
                params = {
                    "key": self.api_key,
                    "OperatorRef": "MTA",
                    "MonitoringRef": route_stop_id,
                    "LineRef": route
                }
                
                response = requests.get(BUS_API_BASE, params=params, timeout=(10, 30))
                response.raise_for_status()
                data = response.json()
                
                if (data.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery")):
                    delivery = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]
                    
                    if delivery.get("MonitoredStopVisit"):
                        for visit in delivery["MonitoredStopVisit"]:
                            journey = visit["MonitoredVehicleJourney"]
                            
                            if not journey.get("Monitored", True):
                                continue
                            
                            if route_short == "M101" and "LIMITED" in journey.get("DestinationName", ""):
                                continue
                                
                            call = journey.get("MonitoredCall", {})
                            if call.get("ExpectedArrivalTime"):
                                arrival_time = datetime.fromisoformat(
                                    call["ExpectedArrivalTime"].replace("Z", "+00:00")
                                ).replace(tzinfo=None)
                                
                                now = datetime.now()
                                if arrival_time < now:
                                    continue
                                
                                minutes_away = int((arrival_time - now).total_seconds() / 60)
                                
                                if minutes_away > 0:
                                    minutes_away = minutes_away - 1
                                
                                if minutes_away >= 0:
                                    arrivals[route_short].append({
                                        "minutes": minutes_away,
                                        "time": arrival_time.strftime("%H:%M"),
                                        "destination": journey.get("DestinationName", "")
                                    })
                                    real_data_found = True
                else:
                    pass
                
                arrivals[route_short] = sorted(arrivals[route_short], key=lambda x: x["minutes"])[:3]
                
            except Exception as e:
                error_msg = f"{route.split('_')[-1]}: {str(e)}"
                errors.append(error_msg)
                print(f"Error fetching {route} data: {e}")
        
        if real_data_found:
            print("✅ Using REAL bus data from MTA Bus Time API")
            return arrivals, None
        else:
            error_summary = "No buses found" if not errors else "; ".join(errors)
            return arrivals, error_summary
    
    def _get_mock_bus_data(self, error_msg=None):
        """Return mock bus data when API is unavailable"""
        if error_msg:
            print(f"🔸 Using MOCK bus data - Reason: {error_msg}")
        else:
            print("🔸 Using MOCK bus data (API unavailable)")
        import random
        
        arrivals = {"M102": [], "M103": []}
        destinations = {"M102": "125th St", "M103": "125th St"}
        
        for route in arrivals.keys():
            for i in range(3):
                minutes = random.randint(3, 20) + (i * 4)
                arrival_time = datetime.now().replace(second=0, microsecond=0)
                arrival_time = arrival_time.replace(minute=arrival_time.minute + minutes)
                
                arrivals[route].append({
                    "minutes": minutes,
                    "time": arrival_time.strftime("%H:%M"),
                    "destination": destinations[route]
                })
        
        return arrivals

class WeatherTracker:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.city = WEATHER_CITY
        self.base_url = WEATHER_API_URL
        self.forecast_url = WEATHER_FORECAST_URL
        
    def get_weather_data(self):
        """Get current weather data from OpenWeatherMap"""
        for timeout in [20, 30, 45]:
            try:
                url = f"{self.base_url}?q={self.city}&appid={self.api_key}&units=imperial"
                response = requests.get(url, timeout=(10, timeout))
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Using REAL weather data from OpenWeatherMap")
                    
                    weather_info = {
                        "description": data['weather'][0]['description'].title(),
                        "temp": round(data['main']['temp']),
                        "feels_like": round(data['main']['feels_like']),
                        "humidity": data['main']['humidity'],
                        "wind_speed": round(data['wind']['speed']),
                        "icon": data['weather'][0]['icon'],
                        "main": data['weather'][0]['main']
                    }
                    
                    if 'sys' in data:
                        weather_info['sunrise'] = datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")
                        weather_info['sunset'] = datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
                    
                    weather_info['hourly'] = self.get_hourly_forecast()
                    return weather_info
                else:
                    print(f"Weather API error: {response.status_code}")
                    return self._get_mock_weather()
                    
            except Exception as e:
                print(f"Error fetching weather data: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        print("Weather API failed after all retries")
        return self._get_mock_weather()
    
    def get_hourly_forecast(self):
        """Get 5 hour forecast from OpenWeatherMap"""
        for connect_timeout in [15, 25, 40]:
            try:
                url = f"{self.forecast_url}?q={self.city}&appid={self.api_key}&units=imperial&cnt=8"
                response = requests.get(url, timeout=(connect_timeout, 45))
                
                if response.status_code == 200:
                    data = response.json()
                    hourly = []
                    
                    for item in data['list'][:5]:
                        forecast_time = datetime.fromtimestamp(item['dt'])
                        hourly.append({
                            "hour": forecast_time.strftime("%I%p").lstrip('0'),
                            "temp": round(item['main']['temp']),
                            "icon": item['weather'][0]['icon'],
                            "description": item['weather'][0]['description'].title(),
                            "pop": item.get('pop', 0),
                            "humidity": item['main'].get('humidity', 0),
                            "wind_speed": round(item.get('wind', {}).get('speed', 0))
                        })
                    
                    print("✅ Using REAL hourly forecast data")
                    return hourly
                else:
                    return self._get_mock_hourly()
                    
            except Exception as e:
                continue
        
        return self._get_mock_hourly()
    
    def _get_mock_weather(self):
        """Return mock weather data when API is unavailable"""
        print("🔸 Using MOCK weather data (API unavailable)")
        return {
            "description": "Partly Cloudy",
            "temp": 72,
            "feels_like": 75,
            "humidity": 65,
            "wind_speed": 8,
            "icon": "02d",
            "main": "Clouds",
            "sunrise": "06:30",
            "sunset": "19:45",
            "hourly": self._get_mock_hourly()
        }
    
    def _get_mock_hourly(self):
        """Return mock hourly data"""
        import random
        hourly = []
        base_temp = 72
        current_hour = datetime.now().hour
        
        for i in range(5):
            hour = (current_hour + i * 3) % 24
            temp_variation = random.randint(-5, 5)
            hourly.append({
                "hour": f"{hour % 12 or 12}{'PM' if hour >= 12 else 'AM'}",
                "temp": base_temp + temp_variation,
                "icon": "01d" if 6 <= hour < 18 else "01n",
                "description": "Clear Sky",
                "pop": random.randint(0, 30) / 100,
                "humidity": random.randint(40, 80),
                "wind_speed": random.randint(3, 12)
            })
        
        return hourly

class MTAGui:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MTA Morning Transit Tracker")
        
        # Fonts - Reduced sizes
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.regular_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 56)
        self.xlarge_font = pygame.font.Font(None, 72)
        
        # Transit trackers
        self.subway_tracker = SubwayTracker()
        self.bus_tracker = BusTracker()
        self.weather_tracker = WeatherTracker()
        
        # Data storage
        self.subway_data = {"uptown": [], "downtown": []}
        self.bus_data = {"M102": [], "M103": []}
        self.weather_data = {}
        self.last_update = datetime.now()
        self.loading = True
        
        # Start data fetching thread
        self.data_thread = threading.Thread(target=self.fetch_data_loop, daemon=True)
        self.data_thread.start()
    
    def fetch_data_loop(self):
        """Background thread to fetch transit data"""
        while True:
            try:
                self.subway_data = self.subway_tracker.get_q_train_arrivals()
                self.bus_data = self.bus_tracker.get_bus_arrivals()
                self.weather_data = self.weather_tracker.get_weather_data()
                
                self.last_update = datetime.now()
                self.loading = False
                
                print("🎉 ALL DATA LOADED SUCCESSFULLY!")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error fetching data: {e}")
            
            time.sleep(30)
    
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_header(self):
        """Draw the application header"""
        # Header background - Taller for larger fonts
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 140)
        self.draw_rounded_rect(self.screen, CARD_BG, header_rect, 0)
        
        # Title
        title_text = self.title_font.render("NYC Transit & Weather", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 45))
        self.screen.blit(title_text, title_rect)
        
        # Current time
        current_time = datetime.now().strftime("%A, %B %d - %I:%M:%S %p")
        time_text = self.regular_font.render(current_time, True, LIGHT_GRAY)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(time_text, time_rect)
        
        # Last update
        if not self.loading:
            update_text = f"Updated: {self.last_update.strftime('%I:%M:%S %p')}"
            update_surface = self.small_font.render(update_text, True, GRAY)
            update_rect = update_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
            self.screen.blit(update_surface, update_rect)
    
    def draw_weather_section(self):
        """Draw hourly weather forecast only"""
        if not self.weather_data:
            return
            
        # Weather card for detailed hourly forecast - Much larger
        weather_card = pygame.Rect(30, 160, SCREEN_WIDTH - 60, 280)
        self.draw_rounded_rect(self.screen, CARD_BG, weather_card, 15)
        
        # Hourly forecast
        if 'hourly' in self.weather_data and self.weather_data['hourly']:
            hourly_y = weather_card.y + 30
            hourly_title = self.header_font.render("Hourly Forecast", True, LIGHT_GREEN)
            self.screen.blit(hourly_title, (weather_card.x + 30, hourly_y))
            
            for i, hour_data in enumerate(self.weather_data['hourly'][:5]):
                hour_x = weather_card.x + 40 + (i * 225)
                
                # Hour label
                hour_text = hour_data['hour']
                hour_surface = self.header_font.render(hour_text, True, YELLOW)
                self.screen.blit(hour_surface, (hour_x, hourly_y + 40))
                
                # Temperature (prominent but not overlapping)
                temp_text = f"{hour_data['temp']}°F"
                temp_surface = self.large_font.render(temp_text, True, WHITE)
                self.screen.blit(temp_surface, (hour_x, hourly_y + 70))
                
                # Weather condition description (more prominent and clear)
                desc_text = hour_data['description'].title()[:12]  # Full description, capitalized
                desc_surface = self.regular_font.render(desc_text, True, WHITE)
                self.screen.blit(desc_surface, (hour_x, hourly_y + 115))
                
                # No weather symbol - just the description text is enough
                
                # Precipitation probability
                if 'pop' in hour_data:
                    pop_text = f"Rain: {int(hour_data['pop'] * 100)}%"
                    pop_surface = self.small_font.render(pop_text, True, LIGHT_BLUE)
                    self.screen.blit(pop_surface, (hour_x, hourly_y + 170))
                
                # Humidity
                if 'humidity' in hour_data:
                    humidity_text = f"Humidity: {hour_data['humidity']}%"
                    humidity_surface = self.small_font.render(humidity_text, True, LIGHT_GRAY)
                    self.screen.blit(humidity_surface, (hour_x, hourly_y + 195))
                
                # Wind speed
                if 'wind_speed' in hour_data:
                    wind_text = f"Wind: {hour_data['wind_speed']}mph"
                    wind_surface = self.small_font.render(wind_text, True, LIGHT_GRAY)
                    self.screen.blit(wind_surface, (hour_x, hourly_y + 220))
    
    def draw_subway_section(self):
        """Draw Q train information"""
        # Subway cards side by side - adjusted for larger weather section and bigger cards
        card_width = (SCREEN_WIDTH - 80) // 2
        uptown_card = pygame.Rect(30, 460, card_width, 260)
        downtown_card = pygame.Rect(50 + card_width, 460, card_width, 260)
        
        # Draw cards
        self.draw_rounded_rect(self.screen, CARD_BG, uptown_card, 15)
        self.draw_rounded_rect(self.screen, CARD_BG, downtown_card, 15)
        
        # Uptown section
        # Draw Q in circle (larger)
        pygame.draw.circle(self.screen, YELLOW, (uptown_card.x + 50, uptown_card.y + 45), 35)
        q_text = self.header_font.render("Q", True, BLACK)
        q_rect = q_text.get_rect(center=(uptown_card.x + 50, uptown_card.y + 45))
        self.screen.blit(q_text, q_rect)
        
        uptown_header = self.header_font.render("Uptown", True, YELLOW)
        self.screen.blit(uptown_header, (uptown_card.x + 100, uptown_card.y + 20))
        
        dest_text = self.regular_font.render("Queens/Astoria", True, GRAY)
        self.screen.blit(dest_text, (uptown_card.x + 100, uptown_card.y + 60))
        
        # Uptown arrivals (larger spacing and fonts)
        if self.subway_data["uptown"]:
            for i, arrival in enumerate(self.subway_data["uptown"][:3]):
                y_pos = uptown_card.y + 110 + (i * 50)
                
                # Time in minutes (extra large)
                min_text = f"{arrival['minutes']}"
                color = LIGHT_GREEN if arrival['minutes'] <= 5 else WHITE
                min_surface = self.large_font.render(min_text, True, color)
                self.screen.blit(min_surface, (uptown_card.x + 35, y_pos))
                
                # "min" label (larger)
                min_label = self.regular_font.render("min", True, GRAY)
                self.screen.blit(min_label, (uptown_card.x + 100 + (15 if arrival['minutes'] < 10 else 0), y_pos + 15))
                
                # Clock time (larger)
                time_text = arrival['time']
                time_surface = self.header_font.render(time_text, True, LIGHT_GRAY)
                self.screen.blit(time_surface, (uptown_card.x + 200, y_pos + 10))
        else:
            no_trains = self.header_font.render("No trains", True, GRAY)
            no_trains_rect = no_trains.get_rect(center=(uptown_card.centerx, uptown_card.centery + 30))
            self.screen.blit(no_trains, no_trains_rect)
        
        # Downtown section
        # Draw Q in circle (larger)
        pygame.draw.circle(self.screen, YELLOW, (downtown_card.x + 50, downtown_card.y + 45), 35)
        q_text = self.header_font.render("Q", True, BLACK)
        q_rect = q_text.get_rect(center=(downtown_card.x + 50, downtown_card.y + 45))
        self.screen.blit(q_text, q_rect)
        
        downtown_header = self.header_font.render("Downtown", True, YELLOW)
        self.screen.blit(downtown_header, (downtown_card.x + 100, downtown_card.y + 20))
        
        dest_text = self.regular_font.render("Brooklyn/Brighton Beach", True, GRAY)
        self.screen.blit(dest_text, (downtown_card.x + 100, downtown_card.y + 60))
        
        # Downtown arrivals (larger spacing and fonts)
        if self.subway_data["downtown"]:
            for i, arrival in enumerate(self.subway_data["downtown"][:3]):
                y_pos = downtown_card.y + 110 + (i * 50)
                
                # Time in minutes (extra large)
                min_text = f"{arrival['minutes']}"
                color = LIGHT_GREEN if arrival['minutes'] <= 5 else WHITE
                min_surface = self.large_font.render(min_text, True, color)
                self.screen.blit(min_surface, (downtown_card.x + 35, y_pos))
                
                # "min" label (larger)
                min_label = self.regular_font.render("min", True, GRAY)
                self.screen.blit(min_label, (downtown_card.x + 100 + (15 if arrival['minutes'] < 10 else 0), y_pos + 15))
                
                # Clock time (larger)
                time_text = arrival['time']
                time_surface = self.header_font.render(time_text, True, LIGHT_GRAY)
                self.screen.blit(time_surface, (downtown_card.x + 200, y_pos + 10))
        else:
            no_trains = self.header_font.render("No trains", True, GRAY)
            no_trains_rect = no_trains.get_rect(center=(downtown_card.centerx, downtown_card.centery + 30))
            self.screen.blit(no_trains, no_trains_rect)
    
    def draw_bus_section(self):
        """Draw bus information"""
        # Bus card spanning full width (much larger)
        bus_card = pygame.Rect(30, 740, SCREEN_WIDTH - 60, 200)
        self.draw_rounded_rect(self.screen, CARD_BG, bus_card, 15)
        
        # Bus header (larger)
        bus_header = self.header_font.render("Buses - 83rd St & 2nd Ave", True, LIGHT_BLUE)
        self.screen.blit(bus_header, (bus_card.x + 30, bus_card.y + 20))
        
        # Bus routes side by side (larger spacing)
        routes = ["M102", "M103"]
        route_width = (bus_card.width - 60) // 2
        
        for i, route in enumerate(routes):
            route_x = bus_card.x + 30 + (i * route_width)
            route_y = bus_card.y + 70
            
            # Route number in circle (larger)
            circle_color = BLUE if route == "M102" else LIGHT_BLUE
            pygame.draw.circle(self.screen, circle_color, (route_x + 40, route_y + 30), 40)
            route_text = self.header_font.render(route[1:], True, WHITE)
            route_rect = route_text.get_rect(center=(route_x + 40, route_y + 30))
            self.screen.blit(route_text, route_rect)
            
            # Route arrivals (larger fonts and spacing)
            arrival_x = route_x + 100
            if self.bus_data[route]:
                for j, arrival in enumerate(self.bus_data[route][:3]):
                    y_pos = route_y + (j * 45)
                    
                    # Time in minutes (larger)
                    min_text = f"{arrival['minutes']}"
                    color = LIGHT_GREEN if arrival['minutes'] <= 5 else WHITE
                    min_surface = self.large_font.render(min_text, True, color)
                    self.screen.blit(min_surface, (arrival_x, y_pos))
                    
                    # "min" label (larger)
                    min_label = self.regular_font.render("min", True, GRAY)
                    self.screen.blit(min_label, (arrival_x + 60, y_pos + 15))
                    
                    # Destination (larger font, more space)
                    dest = arrival['destination'][:18] + "..." if len(arrival['destination']) > 18 else arrival['destination']
                    dest_surface = self.regular_font.render(dest, True, LIGHT_GRAY)
                    self.screen.blit(dest_surface, (arrival_x + 130, y_pos + 12))
            else:
                no_buses = self.header_font.render("No buses", True, GRAY)
                self.screen.blit(no_buses, (arrival_x, route_y + 15))
    
    def draw_loading(self):
        """Draw loading indicator"""
        if self.loading:
            # Loading card (larger)
            load_card = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 75, 500, 150)
            self.draw_rounded_rect(self.screen, CARD_BG, load_card, 15)
            
            loading_text = self.header_font.render("Loading transit data...", True, WHITE)
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(loading_text, loading_rect)
    
    def run(self):
        """Main application loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Manual refresh
                        self.loading = True
                        threading.Thread(target=self.fetch_data_loop, daemon=True).start()
            
            # Clear screen with dark background
            self.screen.fill(DARK_BG)
            
            # Draw components
            self.draw_header()
            
            if self.loading:
                self.draw_loading()
            else:
                self.draw_weather_section()
                self.draw_subway_section()
                self.draw_bus_section()
            
            # Instructions with background (larger)
            instruction_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
            self.draw_rounded_rect(self.screen, CARD_BG, instruction_rect, 0)
            
            instruction_text = "Press 'R' to refresh  •  'ESC' to exit"
            instruction_surface = self.regular_font.render(instruction_text, True, LIGHT_GRAY)
            text_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(instruction_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    try:
        app = MTAGui()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()