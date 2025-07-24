# Your current Flask code from the canvas goes here...
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

GOOGLE_API_KEY = 'your_google_maps_api_key'
YELP_API_KEY = 'your_yelp_api_key'

headers = {
    'Authorization': f'Bearer {YELP_API_KEY}'
}

app = Flask(__name__)
CORS(app)

def get_route(start, end):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    return response.json()

def find_stops_along_route(location, term):
    url = f"https://api.yelp.com/v3/businesses/search?location={location}&term={term}&sort_by=rating&limit=3"
    response = requests.get(url, headers=headers)
    return response.json()

def plan_route_with_live_data(start, end):
    directions = get_route(start, end)
    if directions['status'] != 'OK':
        return {'error': 'Unable to fetch directions from Google Maps API.'}

    stops = []
    for leg in directions['routes'][0]['legs']:
        for step in leg['steps']:
            lat = step['end_location']['lat']
            lng = step['end_location']['lng']
            location = f"{lat},{lng}"

            cafes = find_stops_along_route(location, 'artisanal coffee')
            restrooms = find_stops_along_route(location, 'clean restrooms')
            rest_areas = find_stops_along_route(location, 'highly rated rest area')
            gas_stations = find_stops_along_route(location, 'gas station')

            stops.append({
                'location': location,
                'cafes': cafes.get('businesses', []),
                'restrooms': restrooms.get('businesses', []),
                'rest_areas': rest_areas.get('businesses', []),
                'gas_stations': gas_stations.get('businesses', [])
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
