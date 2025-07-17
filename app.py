from flask import Flask, render_template, request, jsonify
from modules.flight_optimizer import FlightOptimizer
from config import GOOGLE_MAPS_API_KEY, DEBUG

app = Flask(__name__)
flight_optimizer = FlightOptimizer()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/optimize', methods=['POST'])
def optimize():
    """Optimize a flight route"""
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')
    
    if not origin or not destination:
        return jsonify({'error': 'Origin and destination are required'}), 400
        
    # Convert to coordinates if they are provided as addresses
    # In a real app, you would geocode here if needed
    
    # Optimize the route
    routes = flight_optimizer.optimize_route(origin, destination)
    
    if not routes:
        return jsonify({'error': 'Could not find any routes'}), 404
        
    return jsonify({'routes': routes})

@app.route('/results')
def results():
    """Show the results page"""
    return render_template('results.html', api_key=GOOGLE_MAPS_API_KEY)

if __name__ == '__main__':
    app.run(debug=DEBUG)