from flask import Flask, request, render_template
import json

app = Flask(__name__)

top_pickup_zones = []
top_pickup_zones_counts = []
top_dropoff_zones = []
top_dropoff_zones_counts = []
duration_counts = []
@app.route('/', methods=['GET'])
def render_page():
    global top_pickup_zones
    global top_pickup_zones_counts
    global top_dropoff_zones
    global top_dropoff_zones_counts
    global duration_counts
    return render_template(
        'index.html',
        top_pickup_zones=top_pickup_zones,
        top_pickup_zones_counts=top_pickup_zones_counts,
        top_dropoff_zones=top_dropoff_zones,
        top_dropoff_zones_counts=top_dropoff_zones_counts,
        duration_counts=duration_counts)

@app.route('/top_pickup', methods = ['GET','POST'])
def get_top_pickup():
    global top_pickup_zones
    global top_pickup_zones_counts
    data = request.data
    data_json = json.loads(data)
    zones = []
    counts = []
    for zone in data_json['top_pickup_zones']:
        zones.append(zone['zone'])
        counts.append(zone['count'])
    top_pickup_zones = zones
    top_pickup_zones_counts = counts
    return "received"

@app.route('/top_dropoff', methods = ['GET','POST'])
def get_top_dropoff():
    global top_dropoff_zones
    global top_dropoff_zones_counts
    data = request.data
    data_json = json.loads(data)
    zones = []
    counts = []
    for zone in data_json['top_dropoff_zones']:
        zones.append(zone['zone'])
        counts.append(zone['count'])
    top_dropoff_zones = zones
    top_dropoff_zones_counts = counts
    return "received"

@app.route('/duration', methods = ['GET','POST'])
def get_duration():
    global duration_counts
    data = request.data
    data_json = json.loads(data)
    counts = [0]*13
    for b in data_json['duration']:
        counts[int(float(b['bin']))-1] = b['count']
    duration_counts = counts
    return "received"