import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
import config
import os

class SubwayTracker:
    def __init__(self):
        self.api_key = config.SUBWAY_API_KEY
        
    def get_q_train_arrivals(self):
        """Get Q train arrival times for both uptown and downtown"""
        # Check if we should use mock data (for testing)
        if os.environ.get('USE_MOCK_DATA', '').lower() in ['1', 'true', 'yes']:
            print("🧪 Using MOCK subway data for testing")
            return self._get_mock_data()
            
        # Try main MTA API first
        arrivals = self._try_mta_api()
        if arrivals:
            return arrivals
            
        # Try alternative APIs
        arrivals = self._try_alternative_apis()
        if arrivals:
            return arrivals
            
        # Return mock data as fallback
        return self._get_mock_data()
    
    def _try_mta_api(self):
        """Try the official MTA API"""
        try:
            feed_url = config.SUBWAY_FEEDS['nqrw']
            
            # Try with API key first (if available)
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
            
            # Try without API key (some feeds are now public)
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
        for name, url in config.ALTERNATIVE_FEEDS.items():
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
                    
                    # Skip if this is static/scheduled data (not real-time)
                    if hasattr(trip.trip, 'schedule_relationship'):
                        if trip.trip.schedule_relationship != 0:  # 0 = SCHEDULED (real-time tracked)
                            continue
                    
                    if trip.trip.route_id == 'Q':
                        for stop_update in trip.stop_time_update:
                            # 86th St station stop IDs
                            if stop_update.stop_id in ['Q05N', 'Q05S']:
                                arrival_time = None
                                if stop_update.HasField('arrival'):
                                    arrival_time = datetime.fromtimestamp(stop_update.arrival.time)
                                elif stop_update.HasField('departure'):
                                    arrival_time = datetime.fromtimestamp(stop_update.departure.time)
                                
                                if arrival_time:
                                    # Determine direction first
                                    direction = "uptown" if stop_update.stop_id.endswith('N') else "downtown"
                                    
                                    # Apply direction-specific time offset correction
                                    corrected_arrival_time = arrival_time
                                    if hasattr(config, 'SUBWAY_TIME_OFFSET_MINUTES'):
                                        from datetime import timedelta
                                        if isinstance(config.SUBWAY_TIME_OFFSET_MINUTES, dict):
                                            offset = config.SUBWAY_TIME_OFFSET_MINUTES.get(direction, 0)
                                        else:
                                            offset = config.SUBWAY_TIME_OFFSET_MINUTES
                                        corrected_arrival_time = arrival_time + timedelta(minutes=offset)
                                    
                                    # Calculate minutes away from corrected time
                                    now = datetime.now()
                                    
                                    # Skip if the corrected arrival time is in the past
                                    if corrected_arrival_time < now:
                                        continue
                                    
                                    # Calculate minutes from corrected arrival time
                                    time_diff = (corrected_arrival_time - now).total_seconds()
                                    minutes_away = round(time_diff / 60)
                                    
                                    # Don't show if time would be negative
                                    if minutes_away >= 0:
                                        arrivals[direction].append({
                                            "minutes": minutes_away,
                                            "time": corrected_arrival_time.strftime("%H:%M")
                                        })
            
            # Sort by minutes away and take first 3
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
        
        # Generate realistic mock arrival times
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
    
    def display_subway_info(self):
        """Display Q train arrival information"""
        arrivals = self.get_q_train_arrivals()
        
        print("\n🚇 Q TRAIN - 86th Street")
        print("=" * 30)
        
        print("UPTOWN (Queens/Astoria):")
        if arrivals["uptown"]:
            for arrival in arrivals["uptown"]:
                print(f"  {arrival['minutes']} min ({arrival['time']})")
        else:
            print("  No upcoming trains")
            
        print("\nDOWNTOWN (Brooklyn/Brighton Beach):")
        if arrivals["downtown"]:
            for arrival in arrivals["downtown"]:
                print(f"  {arrival['minutes']} min ({arrival['time']})")
        else:
            print("  No upcoming trains")