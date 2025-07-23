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

# Modern UI Colors with Gradients
BLACK = (0, 0, 0)
BG_DARK = (10, 10, 15)  # Deep space black with blue tint
BG_GRADIENT_TOP = (15, 15, 25)  # Slightly lighter for gradient
BG_GRADIENT_BOTTOM = (5, 5, 10)  # Darker for depth

# Primary Colors - Vibrant and Modern
PRIMARY_BLUE = (0, 122, 255)  # iOS blue
PRIMARY_GREEN = (52, 199, 89)  # Success green
PRIMARY_ORANGE = (255, 149, 0)  # Warning orange
PRIMARY_RED = (255, 59, 48)  # Danger red
PRIMARY_PURPLE = (175, 82, 222)  # Accent purple
PRIMARY_CYAN = (50, 173, 230)  # Info cyan

# Glass/Card Colors with Transparency
CARD_BG = (255, 255, 255, 10)  # White with low opacity
CARD_BORDER = (255, 255, 255, 30)  # White border with opacity
TEXT_PRIMARY = (255, 255, 255)  # Pure white
TEXT_SECONDARY = (200, 200, 210)  # Slightly muted
TEXT_MUTED = (150, 150, 170)  # Muted text

# Accent Colors
ACCENT_GOLD = (255, 215, 0)  # Premium gold
ACCENT_SILVER = (192, 192, 192)  # Metallic silver
SHADOW = (0, 0, 0, 50)  # Shadow color

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 680

class MTAGui:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Transit Command Center - NYC")
        
        # Clean, readable fonts - much smaller
        self.title_font = pygame.font.Font(None, 36)
        self.header_font = pygame.font.Font(None, 28)
        self.regular_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 32)
        self.time_font = pygame.font.Font(None, 48)  # For time display only
        
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
    
    def draw_gradient_background(self):
        """Draw a modern gradient background"""
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(BG_GRADIENT_TOP[0] * (1 - color_ratio) + BG_GRADIENT_BOTTOM[0] * color_ratio)
            g = int(BG_GRADIENT_TOP[1] * (1 - color_ratio) + BG_GRADIENT_BOTTOM[1] * color_ratio)
            b = int(BG_GRADIENT_TOP[2] * (1 - color_ratio) + BG_GRADIENT_BOTTOM[2] * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_glass_card(self, rect, color_tint=None, border_color=None, shadow=True):
        """Draw a modern glassmorphic card with blur effect"""
        # Shadow
        if shadow:
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 100), shadow_surface.get_rect(), border_radius=20)
            self.screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
        
        # Glass effect background
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        base_color = color_tint if color_tint else (255, 255, 255, 15)
        pygame.draw.rect(card_surface, base_color, card_surface.get_rect(), border_radius=20)
        
        # Border
        border = border_color if border_color else (255, 255, 255, 40)
        pygame.draw.rect(card_surface, border, card_surface.get_rect(), 2, border_radius=20)
        
        self.screen.blit(card_surface, (rect.x, rect.y))
        
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    # Removed complex data visualization
    
    # Removed confusing status indicator method
    
    # Removed overly complex time badge method
    
    def _get_weather_color(self, icon_code):
        """Get color based on weather condition"""
        if icon_code.startswith('01'):  # Clear
            return ACCENT_GOLD
        elif icon_code.startswith('02') or icon_code.startswith('03'):  # Clouds
            return ACCENT_SILVER
        elif icon_code.startswith('04'):  # Broken clouds
            return TEXT_MUTED
        elif icon_code.startswith('09') or icon_code.startswith('10'):  # Rain
            return PRIMARY_BLUE
        elif icon_code.startswith('11'):  # Thunderstorm
            return PRIMARY_RED
        elif icon_code.startswith('13'):  # Snow
            return TEXT_PRIMARY
        else:
            return PRIMARY_GREEN
    
    def draw_header(self):
        """Draw clean, simple header"""
        # Simple background card
        header_rect = pygame.Rect(20, 15, SCREEN_WIDTH - 40, 60)
        self.draw_glass_card(header_rect, shadow=False)
        
        # Title
        title = "NYC Transit Tracker"
        title_surface = self.title_font.render(title, True, TEXT_PRIMARY)
        self.screen.blit(title_surface, (40, 25))
        
        # Current time - simple and clean
        current_time = datetime.now()
        time_str = current_time.strftime("%I:%M %p")
        date_str = current_time.strftime("%A, %B %d")
        
        # Time display
        time_surface = self.time_font.render(time_str, True, TEXT_PRIMARY)
        time_rect = time_surface.get_rect(right=SCREEN_WIDTH - 40, centery=35)
        self.screen.blit(time_surface, time_rect)
        
        # Date below time
        date_surface = self.small_font.render(date_str, True, TEXT_SECONDARY)
        date_rect = date_surface.get_rect(right=SCREEN_WIDTH - 40, top=55)
        self.screen.blit(date_surface, date_rect)
        
        # Last update - simple text
        if not self.loading:
            update_text = f"Last updated: {self.last_update.strftime('%I:%M %p')}"
            update_surface = self.small_font.render(update_text, True, TEXT_MUTED)
            self.screen.blit(update_surface, (40, 55))
    
    def draw_weather_section(self):
        """Draw clean weather section"""
        if not self.weather_data:
            return
            
        # Section header
        header_y = 95
        weather_title = self.header_font.render("Weather - Next 5 Hours", True, TEXT_PRIMARY)
        self.screen.blit(weather_title, (20, header_y))
        
        # Weather cards with detailed information
        if 'hourly' in self.weather_data and self.weather_data['hourly']:
            card_width = 230
            card_height = 160  # Increased height for more info
            start_x = 20
            start_y = 125
            
            for i, hour_data in enumerate(self.weather_data['hourly'][:5]):
                card_x = start_x + (i * (card_width + 10))
                card_rect = pygame.Rect(card_x, start_y, card_width, card_height)
                
                # Card background
                self.draw_glass_card(card_rect)
                
                # Hour
                hour_surface = self.regular_font.render(hour_data['hour'], True, PRIMARY_CYAN)
                self.screen.blit(hour_surface, (card_x + 15, start_y + 10))
                
                # Temperature - main temp
                temp_text = f"{hour_data['temp']}°F"
                temp_surface = self.large_font.render(temp_text, True, TEXT_PRIMARY)
                self.screen.blit(temp_surface, (card_x + 15, start_y + 30))
                
                # Feels like temperature
                if 'feels_like' in hour_data:
                    feels_text = f"Feels: {hour_data['feels_like']}°F"
                    feels_surface = self.small_font.render(feels_text, True, TEXT_SECONDARY)
                    self.screen.blit(feels_surface, (card_x + 15, start_y + 60))
                
                # Weather description
                desc_text = hour_data['description'].title()
                if len(desc_text) > 18:
                    desc_text = desc_text[:15] + "..."
                desc_surface = self.small_font.render(desc_text, True, TEXT_SECONDARY)
                self.screen.blit(desc_surface, (card_x + 15, start_y + 80))
                
                # Rain chance
                if 'pop' in hour_data:
                    rain_text = f"Rain: {int(hour_data['pop'] * 100)}%"
                    rain_color = PRIMARY_BLUE if hour_data['pop'] > 0.3 else TEXT_MUTED
                    rain_surface = self.small_font.render(rain_text, True, rain_color)
                    self.screen.blit(rain_surface, (card_x + 15, start_y + 100))
                
                # Humidity
                if 'humidity' in hour_data:
                    humidity_text = f"Humidity: {hour_data['humidity']}%"
                    humidity_surface = self.small_font.render(humidity_text, True, TEXT_MUTED)
                    self.screen.blit(humidity_surface, (card_x + 15, start_y + 120))
                
                # Wind speed and direction
                if 'wind_speed' in hour_data:
                    wind_text = f"Wind: {hour_data['wind_speed']} mph"
                    if 'wind_deg' in hour_data:
                        # Convert wind degree to direction
                        wind_deg = hour_data['wind_deg']
                        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
                        direction = directions[int((wind_deg + 22.5) / 45) % 8]
                        wind_text = f"Wind: {direction} {hour_data['wind_speed']} mph"
                    wind_surface = self.small_font.render(wind_text, True, TEXT_MUTED)
                    self.screen.blit(wind_surface, (card_x + 15, start_y + 140))
    
    def draw_subway_section(self):
        """Draw clean subway section"""
        # Section header - moved down for taller weather cards
        header_y = 305
        subway_title = self.header_font.render("Q Train - 86th Street", True, TEXT_PRIMARY)
        self.screen.blit(subway_title, (20, header_y))
        
        # Simple side-by-side cards
        card_width = (SCREEN_WIDTH - 60) // 2
        card_height = 140  # Slightly smaller to fit
        uptown_x = 20
        downtown_x = 30 + card_width
        cards_y = 335
        
        # Uptown card
        uptown_rect = pygame.Rect(uptown_x, cards_y, card_width, card_height)
        self.draw_glass_card(uptown_rect)
        
        # Direction header
        direction_surface = self.header_font.render("Uptown (Queens)", True, PRIMARY_ORANGE)
        self.screen.blit(direction_surface, (uptown_x + 15, cards_y + 15))
        
        # Arrivals - simple list
        if self.subway_data["uptown"]:
            for i, arrival in enumerate(self.subway_data["uptown"][:3]):
                arrival_y = cards_y + 45 + (i * 30)
                
                # Simple time display
                time_text = f"{arrival['minutes']} min - {arrival['time']}"
                color = PRIMARY_RED if arrival['minutes'] <= 2 else PRIMARY_ORANGE if arrival['minutes'] <= 5 else TEXT_PRIMARY
                time_surface = self.regular_font.render(time_text, True, color)
                self.screen.blit(time_surface, (uptown_x + 15, arrival_y))
        else:
            no_data = self.regular_font.render("No trains", True, TEXT_MUTED)
            self.screen.blit(no_data, (uptown_x + 15, cards_y + 70))
        
        # Downtown card
        downtown_rect = pygame.Rect(downtown_x, cards_y, card_width, card_height)
        self.draw_glass_card(downtown_rect)
        
        # Direction header
        direction_surface = self.header_font.render("Downtown (Brooklyn)", True, PRIMARY_BLUE)
        self.screen.blit(direction_surface, (downtown_x + 15, cards_y + 15))
        
        # Arrivals - simple list
        if self.subway_data["downtown"]:
            for i, arrival in enumerate(self.subway_data["downtown"][:3]):
                arrival_y = cards_y + 45 + (i * 30)
                
                # Simple time display
                time_text = f"{arrival['minutes']} min - {arrival['time']}"
                color = PRIMARY_RED if arrival['minutes'] <= 2 else PRIMARY_ORANGE if arrival['minutes'] <= 5 else TEXT_PRIMARY
                time_surface = self.regular_font.render(time_text, True, color)
                self.screen.blit(time_surface, (downtown_x + 15, arrival_y))
        else:
            no_data = self.regular_font.render("No trains", True, TEXT_MUTED)
            self.screen.blit(no_data, (downtown_x + 15, cards_y + 70))
    
    def draw_bus_section(self):
        """Draw clean bus section"""
        # Section header - moved down
        header_y = 495
        bus_title = self.header_font.render("Buses - 83rd & 2nd Ave", True, TEXT_PRIMARY)
        self.screen.blit(bus_title, (20, header_y))
        
        # Simple bus cards
        routes = ["M102", "M103"]
        card_width = (SCREEN_WIDTH - 60) // 2
        card_height = 110  # Slightly smaller to fit
        cards_y = 525
        
        for i, route in enumerate(routes):
            card_x = 20 + (i * (card_width + 20))
            card_rect = pygame.Rect(card_x, cards_y, card_width, card_height)
            
            # Simple card
            self.draw_glass_card(card_rect)
            
            # Route header
            route_color = PRIMARY_GREEN if route == "M102" else PRIMARY_PURPLE
            route_surface = self.header_font.render(route, True, route_color)
            self.screen.blit(route_surface, (card_x + 15, cards_y + 15))
            
            # Arrivals - simple list
            if self.bus_data[route]:
                for j, arrival in enumerate(self.bus_data[route][:2]):
                    arrival_y = cards_y + 45 + (j * 30)
                    
                    # Simple time and destination
                    time_text = f"{arrival['minutes']} min - {arrival['destination'][:25]}"
                    color = PRIMARY_RED if arrival['minutes'] <= 2 else PRIMARY_ORANGE if arrival['minutes'] <= 5 else TEXT_PRIMARY
                    time_surface = self.regular_font.render(time_text, True, color)
                    self.screen.blit(time_surface, (card_x + 15, arrival_y))
            else:
                no_data = self.regular_font.render("No buses", True, TEXT_MUTED)
                self.screen.blit(no_data, (card_x + 15, cards_y + 60))
    
    def draw_loading(self):
        """Draw simple loading indicator"""
        if self.loading:
            # Simple loading panel
            load_panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
            self.draw_glass_card(load_panel)
            
            # Loading text
            loading_text = "Loading transit data..."
            loading_surface = self.header_font.render(loading_text, True, TEXT_PRIMARY)
            loading_rect = loading_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(loading_surface, loading_rect)
    
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
            
            # Draw gradient background
            self.draw_gradient_background()
            
            # Draw components
            self.draw_header()
            
            if self.loading:
                self.draw_loading()
            else:
                self.draw_weather_section()
                self.draw_subway_section()
                self.draw_bus_section()
            
            # Simple footer - positioned right after bus section
            footer_text = "Press R to refresh • ESC to exit"
            footer_surface = self.small_font.render(footer_text, True, TEXT_MUTED)
            footer_rect = footer_surface.get_rect(center=(SCREEN_WIDTH // 2, 655))
            self.screen.blit(footer_surface, footer_rect)
            
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