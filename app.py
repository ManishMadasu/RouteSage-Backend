import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Replace with your actual Google Maps API Key
GOOGLE_API_KEY = 'your_google_maps_api_key'

app = Flask(__name__)
CORS(app)

# Get directions from Google Maps Directions API
def get_route(start, end):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    return response.json()

# Get places near a specific location using Google Places API
def find_places_near_location(lat, lng, keyword):
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={lat},{lng}&radius=1500&keyword={keyword}&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url)
    return response.json()

# Build a route plan with top-rated stops
def plan_route_with_live_data(start, end):
    directions = get_route(start, end)
    if directions['status'] != 'OK':
        return {'error': 'Unable to fetch directions from Google Maps API.'}

    stops = []
    for leg in directions['routes'][0]['legs']:
        for step in leg['steps']:
            lat = step['end_location']['lat']
            lng = step['end_location']['lng']

            cafes = find_places_near_location(lat, lng, 'artisanal coffee')
            restrooms = find_places_near_location(lat, lng, 'public restroom with baby station')
            rest_areas = find_places_near_location(lat, lng, 'highly rated rest area')
            gas_stations = find_places_near_location(lat, lng, 'gas station')

            stops.append({
                'location': f"{lat},{lng}",
                'cafes': cafes.get('results', []),
                'restrooms': restrooms.get('results', []),
                'rest_areas': rest_areas.get('results', []),
                'gas_stations': gas_stations.get('results', [])
            })

    return stops

@app.route('/plan-route', methods=['POST'])
def route_api():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    if not start or not end:
        return jsonify({'error': 'Start and end locations are required.'}), 400

    result = plan_route_with_live_data(start, end)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
