#!/usr/bin/env python3
"""
Test script to verify bus API is working
"""

import requests
import config

def test_bus_api():
    """Test the bus API with your key and stop ID"""
    
    url = "https://bustime.mta.info/api/siri/stop-monitoring.json"
    params = {
        "key": config.BUS_API_KEY,
        "MonitoringRef": config.BUS_STOP_ID
    }
    
    print(f"Testing bus API...")
    print(f"URL: {url}")
    print(f"Stop ID: {config.BUS_STOP_ID}")
    print(f"API Key: {config.BUS_API_KEY[:8]}...")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Bus API is working!")
            
            if data.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery"):
                delivery = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]
                if delivery.get("MonitoredStopVisit"):
                    print(f"Found {len(delivery['MonitoredStopVisit'])} bus arrivals")
                    
                    for visit in delivery["MonitoredStopVisit"][:5]:  # Show first 5
                        journey = visit["MonitoredVehicleJourney"]
                        route = journey.get("PublishedLineName", "Unknown")
                        destination = journey.get("DestinationName", "Unknown")
                        
                        call = journey.get("MonitoredCall", {})
                        arrival_time = call.get("ExpectedArrivalTime", "Unknown")
                        
                        print(f"  {route} → {destination} at {arrival_time}")
                else:
                    print("No buses currently scheduled at this stop")
            else:
                print("No monitoring data in response")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_bus_api()