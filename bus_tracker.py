import requests
from datetime import datetime
import config

class BusTracker:
    def __init__(self):
        self.api_key = config.BUS_API_KEY
        
    def find_bus_stop_id(self):
        """Find the stop ID for 83rd Street and 2nd Avenue area"""
        coords = config.BUS_STOP_COORDINATES["83rd_2nd_ave"]
        url = f"https://bustime.mta.info/api/where/stops-for-location.json"
        params = {
            "key": self.api_key,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "latSpan": 0.005,
            "lonSpan": 0.005
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and data["data"].get("stops"):
                for stop in data["data"]["stops"]:
                    # Look for stops that serve M101, M102, or M103
                    for route in stop.get("routeIds", []):
                        if route in ["MTA NYCT_M101", "MTA NYCT_M102", "MTA NYCT_M103"]:
                            return stop["id"]
            return None
            
        except Exception as e:
            print(f"Error finding bus stop: {e}")
            return None
    
    def get_bus_arrivals(self, stop_id=None):
        """Get M101, M102, M103 bus arrival times"""
        # Try real API first
        arrivals, error_msg = self._try_bus_api(stop_id)
        if any(arrivals.values()):  # If we got any real data
            return arrivals
            
        # Check if it's just no buses vs actual error
        if error_msg == "No buses found":
            print("ℹ️  No buses currently scheduled at this stop")
            return {"M102": [], "M103": []}
        else:
            # Return mock data for actual API errors
            return self._get_mock_bus_data(error_msg)
    
    def _try_bus_api(self, stop_id=None):
        """Try to get real bus data from MTA API"""
        arrivals = {"M102": [], "M103": []}
        routes = ["MTA NYCT_M102", "MTA NYCT_M103"]
        real_data_found = False
        errors = []
        
        for route in routes:
            try:
                route_short = route.split("_")[-1]  # Get M101, M102, or M103
                
                # Use route-specific stop ID
                route_stop_id = config.BUS_STOP_IDS.get(route_short, "405652")
                
                url = config.BUS_API_BASE
                params = {
                    "key": self.api_key,
                    "OperatorRef": "MTA",
                    "MonitoringRef": route_stop_id,
                    "LineRef": route
                }
                
                response = requests.get(url, params=params, timeout=(10, 30))
                response.raise_for_status()
                data = response.json()
                
                if (data.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery")):
                    delivery = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]
                    
                    if delivery.get("MonitoredStopVisit"):
                        for visit in delivery["MonitoredStopVisit"]:
                            journey = visit["MonitoredVehicleJourney"]
                            
                            # Skip if not monitored (not real-time tracked)
                            if not journey.get("Monitored", True):
                                continue
                            
                            # Skip limited buses for M101
                            if route_short == "M101" and "LIMITED" in journey.get("DestinationName", ""):
                                continue
                                
                            call = journey.get("MonitoredCall", {})
                            if call.get("ExpectedArrivalTime"):
                                arrival_time = datetime.fromisoformat(
                                    call["ExpectedArrivalTime"].replace("Z", "+00:00")
                                ).replace(tzinfo=None)
                                
                                # Skip if the arrival time is in the past
                                now = datetime.now()
                                if arrival_time < now:
                                    continue
                                
                                minutes_away = int((arrival_time - now).total_seconds() / 60)
                                
                                # Subtract one minute from the arrival time
                                if minutes_away > 0:
                                    minutes_away = minutes_away - 1
                                
                                # Don't show if adjusted time would be negative
                                if minutes_away >= 0:
                                    arrivals[route_short].append({
                                        "minutes": minutes_away,
                                        "time": arrival_time.strftime("%H:%M"),
                                        "destination": journey.get("DestinationName", "")
                                    })
                                    real_data_found = True
                    else:
                        # API worked but no buses at this stop for this route
                        pass
                else:
                    errors.append(f"{route_short}: No service delivery data")
                
                # Sort and limit to 3 arrivals
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
        destinations = {
            "M102": "125th St", 
            "M103": "125th St"
        }
        
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
    
    def display_bus_info(self):
        """Display bus arrival information"""
        arrivals = self.get_bus_arrivals()
        
        print("\n🚌 BUSES - 83rd Street & 2nd Avenue")
        print("=" * 35)
        
        for route in ["M102", "M103"]:
            print(f"\n{route}:")
            if arrivals[route]:
                for arrival in arrivals[route]:
                    dest = arrival["destination"][:20] + "..." if len(arrival["destination"]) > 20 else arrival["destination"]
                    print(f"  {arrival['minutes']} min ({arrival['time']}) → {dest}")
            else:
                print("  No upcoming buses")