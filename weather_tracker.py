import requests
from datetime import datetime
import config
import socket
import requests.packages.urllib3.util.connection as urllib3_cn

# Force IPv4 to avoid network issues
def allowed_gai_family():
    return socket.AF_INET  # Only allow IPv4

urllib3_cn.allowed_gai_family = allowed_gai_family

class WeatherTracker:
    def __init__(self):
        self.api_key = config.WEATHER_API_KEY
        self.city = config.WEATHER_CITY
        self.base_url = config.WEATHER_API_URL
        self.forecast_url = config.WEATHER_FORECAST_URL
        
    def get_weather_data(self):
        """Get current weather data from OpenWeatherMap"""
        # Try with progressively longer timeouts
        for timeout in [20, 30, 45]:
            try:
                url = f"{self.base_url}?q={self.city}&appid={self.api_key}&units=imperial"
                response = requests.get(url, timeout=(10, timeout))
                
                if response.status_code == 200:
                    print("=" * 60)
                    print("RAW CURRENT WEATHER JSON RESPONSE:")
                    print("=" * 60)
                    print(response.text)
                    print("=" * 60)
                    
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
                    
                    # Add sunrise/sunset times
                    if 'sys' in data:
                        weather_info['sunrise'] = datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")
                        weather_info['sunset'] = datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
                    
                    # Get hourly forecast
                    weather_info['hourly'] = self.get_hourly_forecast()
                    
                    return weather_info
                else:
                    print(f"Weather API error: {response.status_code}")
                    if response.status_code == 401:
                        print("Invalid API key for OpenWeatherMap")
                    return self._get_mock_weather()
                    
            except requests.exceptions.Timeout:
                print(f"Weather API timeout (tried {timeout}s)")
                continue
            except requests.exceptions.ConnectionError:
                print("Weather API connection error - network may be down")
                return self._get_mock_weather()
            except Exception as e:
                print(f"Error fetching weather data: {type(e).__name__}: {str(e)[:100]}")
                return self._get_mock_weather()
        
        # If all retries failed
        print("Weather API failed after all retries")
        return self._get_mock_weather()
    
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
    
    def display_weather_info(self):
        """Display weather information in terminal"""
        weather = self.get_weather_data()
        
        print("\n🌤️  WEATHER - Manhattan")
        print("=" * 30)
        print(f"Conditions: {weather['description']}")
        print(f"Temperature: {weather['temp']}°F (feels like {weather['feels_like']}°F)")
        print(f"Humidity: {weather['humidity']}%")
        print(f"Wind: {weather['wind_speed']} mph")
        
        if 'sunrise' in weather and 'sunset' in weather:
            print(f"Sunrise: {weather['sunrise']} | Sunset: {weather['sunset']}")
    
    def get_weather_icon_emoji(self, icon_code):
        """Convert OpenWeatherMap icon code to emoji"""
        icon_map = {
            "01d": "☀️", "01n": "🌙",  # Clear sky
            "02d": "⛅", "02n": "☁️",   # Few clouds
            "03d": "☁️", "03n": "☁️",   # Scattered clouds
            "04d": "☁️", "04n": "☁️",   # Broken clouds
            "09d": "🌦️", "09n": "🌦️",  # Shower rain
            "10d": "🌧️", "10n": "🌧️",  # Rain
            "11d": "⛈️", "11n": "⛈️",   # Thunderstorm
            "13d": "❄️", "13n": "❄️",   # Snow
            "50d": "🌫️", "50n": "🌫️"   # Mist
        }
        return icon_map.get(icon_code, "🌡️")
    
    def get_hourly_forecast(self):
        """Get 5 hour forecast from OpenWeatherMap"""
        # Try with progressively longer timeouts for forecast
        for connect_timeout in [15, 25, 40]:
            try:
                url = f"{self.forecast_url}?q={self.city}&appid={self.api_key}&units=imperial&cnt=8"
                
                # Create a session to handle potential network issues
                session = requests.Session()
                response = session.get(url, timeout=(connect_timeout, 45))
                
                if response.status_code == 200:
                    print("=" * 60)
                    print("RAW FORECAST JSON RESPONSE:")
                    print("=" * 60)
                    print(response.text)
                    print("=" * 60)
                    
                    data = response.json()
                    hourly = []
                    
                    for item in data['list'][:5]:  # Get next 5 3-hour blocks
                        forecast_time = datetime.fromtimestamp(item['dt'])
                        hourly.append({
                            "hour": forecast_time.strftime("%I%p").lstrip('0'),
                            "temp": round(item['main']['temp']),
                            "feels_like": round(item['main'].get('feels_like', item['main']['temp'])),
                            "icon": item['weather'][0]['icon'],
                            "description": item['weather'][0]['description'].title(),
                            "pop": item.get('pop', 0),  # Precipitation probability
                            "humidity": item['main'].get('humidity', 0),
                            "wind_speed": round(item.get('wind', {}).get('speed', 0))
                        })
                    
                    print("✅ Using REAL hourly forecast data")
                    return hourly
                else:
                    print(f"Forecast API error: {response.status_code}")
                    return self._get_mock_hourly()
                    
            except requests.exceptions.Timeout:
                print(f"Forecast API timeout (tried {connect_timeout}s connect)")
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"Forecast API connection error: {str(e)[:100]}")
                continue
            except Exception as e:
                print(f"Error fetching hourly forecast: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        # If all retries failed, try manual fallback
        print("Forecast API failed after all retries - trying manual fallback")
        return self._try_manual_forecast_fallback()
    
    def _get_mock_hourly(self):
        """Return mock hourly data"""
        import random
        
        hourly = []
        base_temp = 72
        current_hour = datetime.now().hour
        
        for i in range(5):
            hour = (current_hour + i * 3) % 24
            temp_variation = random.randint(-5, 5)
            actual_temp = base_temp + temp_variation
            feels_like_temp = actual_temp + random.randint(-3, 5)  # Feels like can be different
            hourly.append({
                "hour": f"{hour % 12 or 12}{'PM' if hour >= 12 else 'AM'}",
                "temp": actual_temp,
                "feels_like": feels_like_temp,
                "icon": "01d" if 6 <= hour < 18 else "01n",
                "description": "Clear Sky",
                "pop": random.randint(0, 30) / 100,  # 0-30% chance of rain
                "humidity": random.randint(40, 80),
                "wind_speed": random.randint(3, 12)
            })
        
        return hourly
    
    def _try_manual_forecast_fallback(self):
        """Manual fallback - try alternate methods to get forecast data"""
        print("🔄 Trying manual forecast fallback methods...")
        
        # Method 1: Try with different user agent
        try:
            url = f"{self.forecast_url}?q={self.city}&appid={self.api_key}&units=imperial&cnt=8"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=(20, 40))
            
            if response.status_code == 200:
                data = response.json()
                hourly = []
                
                for item in data['list'][:5]:
                    forecast_time = datetime.fromtimestamp(item['dt'])
                    hourly.append({
                        "hour": forecast_time.strftime("%I%p").lstrip('0'),
                        "temp": round(item['main']['temp']),
                        "feels_like": round(item['main'].get('feels_like', item['main']['temp'])),
                        "icon": item['weather'][0]['icon'],
                        "description": item['weather'][0]['description'].title(),
                        "pop": item.get('pop', 0),  # Precipitation probability
                        "humidity": item['main'].get('humidity', 0),
                        "wind_speed": round(item.get('wind', {}).get('speed', 0))
                    })
                
                print("✅ Using REAL hourly forecast data (fallback method)")
                return hourly
                
        except Exception as e:
            print(f"Manual fallback failed: {e}")
        
        # If all else fails, return mock data
        print("🔸 All forecast methods failed - using mock hourly data")
        return self._get_mock_hourly()