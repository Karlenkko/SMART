from flask import Blueprint
from model import Farm, Product, Order, Request, User
from flask import abort, request, jsonify
import json
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np 

algo_bp = Blueprint('algo', __name__)


@algo_bp.route('/algo/map/', methods=['GET'])
def map():
    id = -1
    if request.args.get("orderid") != None:
        id = request.args.get("orderid")

    id = int(id)
    if id == -1 :
        return "No ID"

    order = Order.query.filter(Order.id == id)
    requestList = order[0].requestlist
    requests = Request.query.all()

    locations = []

    requestList = requestList.split(",")


    for i in range(len(requestList)-1):
        location = {}
        location["lat"] = requests[int(requestList[i])].userlocation.split(",")[0]
        location["lng"] = requests[int(requestList[i])].userlocation.split(",")[1]
        locations.append(location)

    centroids = clustering(locations)

    res = []

    res.append(locations)
    res.append(centroids[0])
    res.append(centroids[1])

    return jsonify(res), 200


def clustering(locations):
    nb = int(len(locations)/3)

    dataset = []
    for location in locations:
        data = [location["lat"], location["lng"]]
        dataset.append(data)

    X = np.array(dataset)
    kmeans = KMeans(n_clusters=nb, random_state=0)
    kmeans.fit(X)

    centroids = kmeans.cluster_centers_.tolist()

    res = [[],[]]

    for item in centroids:
        centroid = {}
        centroid["lat"] = item[0]
        centroid["lng"] = item[1]
        res[0].append(centroid)

    labels = kmeans.labels_.tolist()
    res[1] = labels

    return res