import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Application settings
DEBUG = True