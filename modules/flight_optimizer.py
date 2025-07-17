import numpy as np
from geopy.distance import geodesic
from .weather_service import WeatherService
from .map_service import MapService

class FlightOptimizer:
    """Optimizes flight routes considering distance, time, and weather conditions"""
    
    # Constants for optimization weights
    WEATHER_WEIGHT = 0.4
    DISTANCE_WEIGHT = 0.3
    FUEL_WEIGHT = 0.3
    
    # Weather condition penalties (higher means worse)
    WEATHER_PENALTIES = {
        "Clear": 0.0,
        "Clouds": 0.1,
        "Drizzle": 0.3,
        "Rain": 0.5,
        "Thunderstorm": 0.9,
        "Snow": 0.7,
        "Fog": 0.6,
        "Mist": 0.4
    }
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.map_service = MapService()
        
    def optimize_route(self, origin, destination, alternative_routes=3):
        """Find the optimal flight route considering weather and distance"""
        # Get the direct route first
        direct_route = self.map_service.get_route(origin, destination)
        
        if not direct_route:
            return None
            
        # Generate alternative routes with waypoints
        routes = [direct_route]
        
        # Generate alternative routes with waypoints
        for i in range(alternative_routes):
            # Generate a waypoint by offsetting from the midpoint
            if isinstance(origin, tuple) and isinstance(destination, tuple):
                midpoint = (
                    (origin[0] + destination[0]) / 2, 
                    (origin[1] + destination[1]) / 2
                )
                
                # Create an offset based on the route number
                offset_lat = (i + 1) * 0.5 * ((-1) ** i)
                offset_lon = (i + 1) * 0.5 * ((-1) ** (i+1))
                
                waypoint = (midpoint[0] + offset_lat, midpoint[1] + offset_lon)
                alt_route = self.map_service.get_route(origin, destination, [waypoint])
                
                if alt_route:
                    routes.append(alt_route)
        
        # Evaluate each route
        evaluated_routes = []
        for route in routes:
            route_with_metrics = self._evaluate_route(route)
            evaluated_routes.append(route_with_metrics)
            
        # Sort by the score (lower is better)
        evaluated_routes.sort(key=lambda r: r["score"])
        
        return evaluated_routes
    
    def _evaluate_route(self, route):
        """Evaluate a route based on distance, estimated fuel, and weather conditions"""
        if not route or "path" not in route:
            return None
            
        # Get weather along the path
        path_coordinates = [(lat, lon) for lat, lon in route["path"]]
        weather_data = self.weather_service.get_weather_along_path(path_coordinates)
        
        # Calculate the weather score (lower is better)
        weather_score = 0
        for weather_point in weather_data:
            condition = weather_point.get("conditions", "Clear")
            penalty = self.WEATHER_PENALTIES.get(condition, 0.5)
            
            # Add wind factor - higher wind speeds increase penalty
            wind_speed = weather_point.get("wind_speed", 0)
            wind_factor = min(1.0, wind_speed / 30.0)  # Normalize wind speed
            
            weather_score += penalty + (wind_factor * 0.5)
            
        # Normalize weather score
        if weather_data:
            weather_score /= len(weather_data)
        
        # Distance score (normalize based on direct route distance)
        distance = route["distance"]
        distance_score = distance / 1000  # Convert to km for easier scaling
        
        # Estimate fuel consumption based on distance
        fuel_score = distance_score * 0.1  # Simplified fuel calculation
        
        # Calculate combined score
        total_score = (
            self.WEATHER_WEIGHT * weather_score +
            self.DISTANCE_WEIGHT * (distance_score / 1000) +  # Further normalize for reasonable values
            self.FUEL_WEIGHT * fuel_score
        )
        
        # Add the computed metrics to the route
        evaluated_route = route.copy()
        evaluated_route.update({
            "weather_score": weather_score,
            "weather_data": weather_data,
            "distance_score": distance_score,
            "fuel_score": fuel_score,
            "score": total_score
        })
        
        return evaluated_route