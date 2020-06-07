from flask import Flask, request, render_template
import json

app = Flask(__name__)

top_pickup_zones = []
top_pickup_zones_counts = []
top_dropoff_zones = []
top_dropoff_zones_counts = []
duration_counts = []
total_counts = [0]*24
complete_counts = [0]*24
ongoing_counts = [0]*24
@app.route('/', methods=['GET'])
def render_page():
    global top_pickup_zones
    global top_pickup_zones_counts
    global top_dropoff_zones
    global top_dropoff_zones_counts
    global duration_counts
    global ongoing_counts
    global complete_counts
    return render_template(
        'index.html',
        top_pickup_zones=top_pickup_zones,
        top_pickup_zones_counts=top_pickup_zones_counts,
        top_dropoff_zones=top_dropoff_zones,
        top_dropoff_zones_counts=top_dropoff_zones_counts,
        duration_counts=duration_counts,
        ongoing_counts=ongoing_counts,
        complete_counts=complete_counts)

@app.route('/total_count', methods = ['GET','POST'])
def get_total_count():
    global total_counts
    global ongoing_counts
    global complete_counts
    counts = [0]*24
    data = request.data
    data_json = json.loads(data)
    for b in data_json['total_count']:
        counts[int(float(b['hour']))] = b['count']
    total_counts = counts
    ongoing_counts = [pair[0]-pair[1] for pair in zip(total_counts,complete_counts)]
    return "received"

@app.route('/complete_count', methods = ['GET','POST'])
def get_complete_count():
    global total_counts
    global ongoing_counts
    global complete_counts
    counts = [0]*24
    data = request.data
    data_json = json.loads(data)
    for b in data_json['complete_count']:
        counts[int(float(b['hour']))] = b['count']
    complete_counts = counts
    ongoing_counts = [pair[0]-pair[1] for pair in zip(total_counts,complete_counts)]
    return "received"

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