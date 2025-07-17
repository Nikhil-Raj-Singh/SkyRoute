import requests
import polyline
from config import GOOGLE_MAPS_API_KEY

class MapService:
    """Service for interacting with Google Maps API"""
    
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        
    def get_route(self, origin, destination, waypoints=None):
        """Get a route between two points with optional waypoints"""
        url = "https://maps.googleapis.com/maps/api/directions/json"
        
        params = {
            "origin": self._format_location(origin),
            "destination": self._format_location(destination),
            "key": self.api_key,
            "mode": "driving"  # Using driving as flight path approximation
        }
        
        if waypoints:
            waypoints_str = "|".join([self._format_location(wp) for wp in waypoints])
            params["waypoints"] = waypoints_str
            
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK" and data["routes"]:
                return self._parse_route(data["routes"][0])
        
        return None
    
    def _format_location(self, location):
        """Format a location for the Google Maps API"""
        if isinstance(location, str):
            return location
        elif isinstance(location, tuple) and len(location) == 2:
            return f"{location[0]},{location[1]}"
        return ""
    
    def _parse_route(self, route):
        """Parse a route from the Google Maps Directions API"""
        if not route or "legs" not in route:
            return None
            
        path_points = []
        encoded_polyline = route.get("overview_polyline", {}).get("points", "")
        
        if encoded_polyline:
            # Decode the polyline to get the coordinates
            path_points = polyline.decode(encoded_polyline)
            
        # Get distance and duration
        total_distance = 0
        total_duration = 0
        
        for leg in route["legs"]:
            total_distance += leg.get("distance", {}).get("value", 0)  # in meters
            total_duration += leg.get("duration", {}).get("value", 0)  # in seconds
            
        return {
            "path": path_points,
            "distance": total_distance,
            "duration": total_duration,
            "polyline": encoded_polyline
        }