import requests
from config import OPENWEATHERMAP_API_KEY

class WeatherService:
    """Service for retrieving weather data along flight paths"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = OPENWEATHERMAP_API_KEY
        
    def get_weather_at_coordinates(self, lat, lon):
        """Get current weather at specific coordinates"""
        url = f"{self.BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_weather_along_path(self, coordinates, samples=5):
        """Get weather data at sample points along a path"""
        if len(coordinates) < 2:
            return []
            
        # Sample points along the path
        sampled_points = self._sample_path(coordinates, samples)
        
        # Get weather at each sampled point
        weather_data = []
        for lat, lon in sampled_points:
            weather = self.get_weather_at_coordinates(lat, lon)
            if weather:
                weather_data.append({
                    "coordinates": (lat, lon),
                    "temperature": weather.get("main", {}).get("temp"),
                    "wind_speed": weather.get("wind", {}).get("speed"),
                    "wind_direction": weather.get("wind", {}).get("deg"),
                    "conditions": weather.get("weather", [{}])[0].get("main", "Unknown"),
                    "description": weather.get("weather", [{}])[0].get("description", "Unknown")
                })
                
        return weather_data
    
    def _sample_path(self, coordinates, num_samples):
        """Sample points along a path"""
        if num_samples <= 1:
            return [coordinates[0]]
            
        samples = [coordinates[0]]  # Start point
        
        # Calculate total distance to properly space the samples
        total_segments = len(coordinates) - 1
        samples_per_segment = max(1, num_samples // total_segments)
        
        for i in range(total_segments):
            start = coordinates[i]
            end = coordinates[i+1]
            
            # Calculate intermediate points
            for j in range(1, samples_per_segment):
                ratio = j / samples_per_segment
                lat = start[0] + (end[0] - start[0]) * ratio
                lon = start[1] + (end[1] - start[1]) * ratio
                samples.append((lat, lon))
                
            if i < total_segments - 1:
                samples.append(end)  # Add intermediate endpoints
                
        # Ensure the final point is included
        if samples[-1] != coordinates[-1]:
            samples.append(coordinates[-1])
            
        # Trim or extend to match the exact number of requested samples
        if len(samples) > num_samples:
            # Take evenly spaced samples including first and last
            step = (len(samples) - 1) / (num_samples - 1)
            indices = [int(round(i * step)) for i in range(num_samples)]
            samples = [samples[i] for i in indices]
        
        return samples