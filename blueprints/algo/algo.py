from flask import Blueprint
from model import Farm, Product, Order, Request, User
from flask import abort, request, jsonify
from exts import db
import json
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np 

algo_bp = Blueprint('algo', __name__)

dayList = ["Monday","Tuesday","Wednesday","Thursday","Friday", "Saturday", "Sunday"]
parking = {
    "lat" : 45.77495,
    "lng" : 4.84839
}

@algo_bp.route('/algo/updatePath/', methods=['POST'])
def updatePath():

    data = request.form.to_dict()

    print("---------------post---------------")
    print(data)
    print("---------------post---------------")


    id = int(data["id"])
    order = Order.query.filter(Order.id == id)

    entrepot = order[0].entrepotlist.split(";")[0] + ";"
    index = 0
    for i in data:
        if index == 0:
            index = index + 1
            continue
        if index%2 == 1:
            entrepot = entrepot + data[i] + ","
        else:
            entrepot = entrepot + data[i] + ";"
        index = index + 1


    db.session.query(Order).filter(
                                    Order.id == id
                                ).update({"entrepotlist" : entrepot})
    db.session.commit()
    db.session.close()

    return jsonify(""), 200


@algo_bp.route('/algo/map/', methods=['GET'])
def map():
    id = -1
    if request.args.get("orderid") != None:
        id = request.args.get("orderid")

    id = int(id)
    if id == -1 :
        return "No ID"

    order = Order.query.filter(Order.id == id)
    users = User.query.all()
    requestList = order[0].requestlist
    requests = Request.query.all()
    depart = {
        "lat" : order[0].entrepotlist.split(";")[0].split(",")[0],
        "lng" : order[0].entrepotlist.split(";")[0].split(",")[1]
    }

    waypointsTmp = order[0].entrepotlist.strip(";").split(";")
    waypoints = []
    for i in range(len(waypointsTmp)):
        if i == 0:
            continue
        waypoint = {}
        waypoint["lat"] = waypointsTmp[i].split(",")[0]
        waypoint["lng"] = waypointsTmp[i].split(",")[1]
        waypoints.append(waypoint)




    locations = []
    timeProposed = []
    volunteerTime = []

    requestList = requestList.strip(",").split(",")


    for i in range(len(requestList)):
        location = {}
        location["lat"] = requests[int(requestList[i])].userlocation.split(",")[0]
        location["lng"] = requests[int(requestList[i])].userlocation.split(",")[1]
        locations.append(location)

        timeProposed.append({
            "id"   : i,
            "time" : requests[int(requestList[i])].timeproposed
            })
        volunteerTime.append({
            "id"   : i,
            "time" : requests[int(requestList[i])].volunteertime
            })
 

    centroids = clustering(locations)
    res = {}
    resLocation = []

    resLocation.append(locations)
    resLocation.append(centroids[0])
    resLocation.append(centroids[1])
    res["location"] = resLocation
    res["parking"] = parking


    for i in range(len(timeProposed)):
        timeProposed[i]["time"] = timeProposed[i]["time"].strip(";").split(";")
        volunteerTime[i]["time"] = volunteerTime[i]["time"].strip(";").split(";")

    bestDayRes = bestDay(timeProposed)
    bestday = bestDayRes["bestday"]

    deliveryDay = "Monday"
    if bestday != "Monday":
        deliveryDay = dayList[dayList.index(bestday)-1]

    volunteerDayRes = bestDay(volunteerTime)

    group = countUserByDay(timeProposed, bestDayRes["countList"], deliveryDay)
    volunteerGroup = countUserByDay(volunteerTime, volunteerDayRes["countList"], deliveryDay)
    selected = volunteerSelected(centroids[1], volunteerGroup, volunteerTime)

    waypointsLabel = []
    for i in waypoints:
        index = 0
        for j in centroids[0]:
            if j["lat"] == float(i["lat"]) and j["lng"] == float(i["lng"]):
                waypointsLabel.append(index)
            index = index + 1


    finalVolunteer = {}

    for key in selected:
        for index in selected[key]:
            if (centroids[1][index] in finalVolunteer) or (centroids[1][index] in waypointsLabel):
                continue
            else:
                finalVolunteer[centroids[1][index]] = index

    print("----------------------------test-------------------------")
    print(waypointsLabel)
    print("----------------------------volunteerTime-------------------------")
    print(centroids[0])
    print("----------------------------volunteerGroup-------------------------")
    print(waypoints)
    print("----------------------------getStartTime-------------------------")
    print(finalVolunteer)
    print("----------------------------getStartTime-------------------------")
    print(finalVolunteer)
    print("----------------------------test-------------------------")

    selectedperson = ""
    voluteerName = ""

    for i in finalVolunteer:
        userid = requests[int(requestList[finalVolunteer[i]])].userid
        selectedperson = selectedperson + str(userid) + ";"
        voluteerName = voluteerName + users[userid].name + "_" + str(i) + ";"


    db.session.query(Order).filter(
                                    Order.id == id
                                ).update({"selectedperson" : selectedperson})
    db.session.commit()
    db.session.close()


    res["volunteer"] = voluteerName
    res["deliveryDay"] = deliveryDay
    res["depart"] = depart
    res["id"] = id
    res["waypoints"] = waypoints

    return jsonify(res), 200



def getStartTime(id, day, volunteerTime):

    for time in volunteerTime:
        if time["id"] == id :
            for item in time["time"]:
                if day == item.split(" ")[0]:
                    return int(item.split(" ")[1].split("-")[0])

    return 25


def volunteerSelected(labels, volunteerGroup, volunteerTime):

    res = {}
    
    for key in volunteerGroup:
        
        if key == "Past":
            continue
        res[key] = []
        selectedLabel = {}
        selectedLabelTime = {}
        
        for id in volunteerGroup[key]:
            if labels[id] in selectedLabel:
                if getStartTime(id, key, volunteerTime) < selectedLabelTime[labels[id]]:
                    selectedLabelTime[labels[id]] = getStartTime(id, key, volunteerTime)
                    selectedLabel[labels[id]] = id

            else:
                selectedLabel[labels[id]] = id
                selectedLabelTime[labels[id]] = getStartTime(id, key, volunteerTime)

        for id in selectedLabel:
            res[key].append(selectedLabel[id])

    return res



def countUserByDay(timeproposed, countList, deliveryDay):
    group = {}

    for time in timeproposed:
        chosen = -1
        count = 0
        for name in time["time"]:
            if name == "":
                continue 
            index = dayList.index(name.split(" ")[0])
            if index > dayList.index(deliveryDay):
                if countList[index] > count:
                    count = countList[index]
                    chosen = index
        
        if chosen == -1:
            if name == "":
                continue
            if "Past" in group:
                group["Past"].append(time["id"])
            else:
                group["Past"] = []
                group["Past"].append(time["id"])
        else:
            if dayList[chosen] in group:
                group[dayList[chosen]].append(time["id"])
            else:
                group[dayList[chosen]] = []
                group[dayList[chosen]].append(time["id"])

    return group

        

def bestDay(timeproposed):
    
    days = [ 0 for i in range(len(dayList))]

    for time in timeproposed:
        for name in time["time"]:
            if name == "":
                continue
            index = dayList.index(name.split(" ")[0])
            days[index] = days[index] + 1
    
    res = {
        "countList" : days,
        "bestday" : dayList[days.index(max(days))]
    }

    return res

def updateTimeProposed(timeproposed, day):

    newTimeProposed = []

    for time in timeproposed:
        exist = 0
        for name in time["time"]:
            if name.split(" ")[0] == day:
                exist = 1
                break
        if exist == 0:
            newTimeProposed.append(time)

    return newTimeProposed


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