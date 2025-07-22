#!/usr/bin/env python3
"""
MTA Morning Transit Tracker - Pygame GUI
Raspberry Pi app with graphical interface
"""

import pygame
import sys
import time
import threading
from datetime import datetime
from subway_tracker import SubwayTracker
from bus_tracker import BusTracker
from weather_tracker import WeatherTracker

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
DARK_BG = (20, 25, 30)
CARD_BG = (30, 35, 40)
WHITE = (255, 255, 255)
BLUE = (0, 123, 191)  # MTA Blue
LIGHT_BLUE = (100, 181, 246)
ORANGE = (255, 108, 0)  # MTA Orange
LIGHT_ORANGE = (255, 183, 77)
GREEN = (0, 147, 60)  # MTA Green
LIGHT_GREEN = (129, 199, 132)
RED = (238, 53, 36)   # MTA Red
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 235, 59)

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900

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
                # Fetch subway data
                self.subway_data = self.subway_tracker.get_q_train_arrivals()
                
                # Fetch bus data
                self.bus_data = self.bus_tracker.get_bus_arrivals()
                
                # Fetch weather data
                self.weather_data = self.weather_tracker.get_weather_data()
                
                self.last_update = datetime.now()
                self.loading = False
                
                print("🎉 ALL DATA LOADED SUCCESSFULLY!")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error fetching data: {e}")
            
            time.sleep(30)  # Update every 30 seconds
    
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def _get_weather_color(self, icon_code):
        """Get color based on weather condition"""
        if icon_code.startswith('01'):  # Clear
            return YELLOW
        elif icon_code.startswith('02') or icon_code.startswith('03'):  # Clouds
            return LIGHT_GRAY
        elif icon_code.startswith('04'):  # Broken clouds
            return GRAY
        elif icon_code.startswith('09') or icon_code.startswith('10'):  # Rain
            return LIGHT_BLUE
        elif icon_code.startswith('11'):  # Thunderstorm
            return RED
        elif icon_code.startswith('13'):  # Snow
            return WHITE
        else:
            return LIGHT_GREEN
    
    def draw_header(self):
        """Draw the application header"""
        # Header background removed
        
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
            
        # Weather card background removed
        weather_card = pygame.Rect(30, 160, SCREEN_WIDTH - 60, 240)
        
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
                
                # Feels like temperature (smaller, below actual temp)
                if 'feels_like' in hour_data:
                    feels_text = f"Feels {hour_data['feels_like']}°F"
                    feels_surface = self.small_font.render(feels_text, True, LIGHT_GRAY)
                    self.screen.blit(feels_surface, (hour_x, hourly_y + 100))
                
                # Weather condition description (more prominent and clear)
                desc_text = hour_data['description'].title()[:12]  # Full description, capitalized
                desc_surface = self.regular_font.render(desc_text, True, WHITE)
                self.screen.blit(desc_surface, (hour_x, hourly_y + 125))
                
                # No weather symbol - just the description text is enough
                
                # Precipitation probability
                if 'pop' in hour_data:
                    pop_text = f"Rain: {int(hour_data['pop'] * 100)}%"
                    pop_surface = self.small_font.render(pop_text, True, LIGHT_BLUE)
                    self.screen.blit(pop_surface, (hour_x, hourly_y + 155))
                
                # Humidity
                if 'humidity' in hour_data:
                    humidity_text = f"Humidity: {hour_data['humidity']}%"
                    humidity_surface = self.small_font.render(humidity_text, True, LIGHT_GRAY)
                    self.screen.blit(humidity_surface, (hour_x, hourly_y + 180))
                
                # Wind speed
                if 'wind_speed' in hour_data:
                    wind_text = f"Wind: {hour_data['wind_speed']}mph"
                    wind_surface = self.small_font.render(wind_text, True, LIGHT_GRAY)
                    self.screen.blit(wind_surface, (hour_x, hourly_y + 205))
    
    def draw_subway_section(self):
        """Draw Q train information"""
        # Subway cards side by side - adjusted positioning
        card_width = (SCREEN_WIDTH - 80) // 2
        uptown_card = pygame.Rect(30, 420, card_width, 220)
        downtown_card = pygame.Rect(50 + card_width, 420, card_width, 220)
        
        # Card backgrounds removed
        
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
        # Bus card background removed
        bus_card = pygame.Rect(30, 660, SCREEN_WIDTH - 60, 180)
        
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
                    dest = arrival['destination'][:12] + "..." if len(arrival['destination']) > 12 else arrival['destination']
                    dest_surface = self.regular_font.render(dest, True, LIGHT_GRAY)
                    self.screen.blit(dest_surface, (arrival_x + 130, y_pos + 12))
                    
                    # Stops away information
                    stops = arrival.get('stops_away', 'Unknown')
                    stops_surface = self.small_font.render(stops, True, YELLOW)
                    self.screen.blit(stops_surface, (arrival_x + 280, y_pos + 12))
            else:
                no_buses = self.header_font.render("No buses", True, GRAY)
                self.screen.blit(no_buses, (arrival_x, route_y + 15))
    
    def draw_loading(self):
        """Draw loading indicator"""
        if self.loading:
            # Loading card background removed
            load_card = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 75, 500, 150)
            
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
            
            # Instructions background removed
            instruction_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
            
            instruction_text = "Press 'R' to refresh  •  'ESC' to exit"
            instruction_surface = self.regular_font.render(instruction_text, True, LIGHT_GRAY)
            text_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
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