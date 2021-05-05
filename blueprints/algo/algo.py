from flask import Blueprint
from model import Farm, Product, Order, Request, User, Volunteer
from flask import abort, request, jsonify
from exts import db
import json
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np 
from geopy.distance import geodesic
from python_tsp.exact import solve_tsp_dynamic_programming


algo_bp = Blueprint('algo', __name__)

dayList = ["Monday","Tuesday","Wednesday","Thursday","Friday", "Saturday", "Sunday"]
parking = {
	"lat" : 45.77495,
	"lng" : 4.84839
}

@algo_bp.route('/algo/user/', methods=['GET'])
def user():

	requestID = -1
	if request.args.get("requestid") != None:
		requestID = request.args.get("requestid")

	requestID = int(requestID)
	
	if requestID == -1 :
		return "No USERID OR ORDERID"

	requestQuery = db.session.query(Request).filter(Request.id == requestID)
	resquestRES = requestQuery[0]
	userid = int(resquestRES.userid)
	orderid = int(resquestRES.orderid)
	orderQuery = db.session.query(Order).filter(Order.id == orderid)[0]



	query = db.session.query(Volunteer).filter(Volunteer.userid == userid, Volunteer.orderid == orderid)
	
	res = {}

	if query.count() != 0:
		
		volunteer = query[0]
		
		res["isVolunteer"] = 1
		depart = volunteer.entrepotlist.split(";")[0]
		arrival = volunteer.entrepotlist.split(";")[1]
		res["locations"] = [{
			"lat" : float(depart.split(",")[0]),
			"lng" : float(depart.split(",")[1])
		}, {
			"lat" : float(arrival.split(",")[0]),
			"lng" : float(arrival.split(",")[1])
		}]
		userLocations = []

		descriptions = ""


		print("---------------------Volunteer--------------------")
		for id in volunteer.requestlist.strip(",").split(","):
			requestid = int(id)
			requestItem = db.session.query(Request).filter(Request.id == requestid)[0]
			userLocations.append({
					"userid" : requestItem.userid,
					"userlocation" : {
						"lat" : float(requestItem.userlocation.split(",")[0]),
						"lng" : float(requestItem.userlocation.split(",")[1])
					}
				})
			description = requestItem.description.replace("_", " : ").replace(";","\n")
			descriptions = descriptions + "\nFor USER" + str(requestItem.userid) + " :\n" + description
			
		print("---------------------Volunteer--------------------")

		res["date"] = volunteer.date
		res["userLocations"] = userLocations
		res["descriptions"] = descriptions

	else:

		query = db.session.query(Volunteer).filter(Volunteer.orderid == orderid, Volunteer.accept == 1)
		res = {
			"isVolunteer" : 0
		}


		for volunteer in query:
			if str(requestID) in volunteer.requestlist.strip(",").split(","):
				requestQuery.update({"destination" : volunteer.entrepotlist.split(";")[1], "volunteerid": volunteer.userid})
				db.session.commit()

				
				res["hasVolunteer"] = volunteer.userid
				res["locations"] = [{
					"lat" : float(resquestRES.userlocation.split(",")[0]),
					"lng" : float(resquestRES.userlocation.split(",")[1])
				}, {
					"lat" : float(volunteer.entrepotlist.split(";")[1].split(",")[0]),
					"lng" : float(volunteer.entrepotlist.split(";")[1].split(",")[1])
				}]

				res["description"] = resquestRES.description.replace("_", " : ").replace(";","\n")
				res["date"] = volunteer.date

				return jsonify(res), 200
		
		print("----------------TEST-------------")
		print(orderQuery)
		print("----------------TEST-------------")

		res["hasVolunteer"] = "none"
		res["locations"] = [{
			"lat" : float(resquestRES.userlocation.split(",")[0]),
			"lng" : float(resquestRES.userlocation.split(",")[1])
		}, {
			"lat" : parking["lat"],
			"lng" : parking["lng"]
		}]

		res["descriptions"] = resquestRES.description.replace("_", " : ").replace(";","\n")
		res["date"] = orderQuery.time

		requestQuery.update({"destination" : str(parking["lat"])+","+str(parking["lng"]), "volunteerid": -1})
		db.session.commit()



	return jsonify(res), 200


@algo_bp.route('/algo/validate/', methods=['GET'])
def validate():
	id = -1
	if request.args.get("orderid") != None:
		id = request.args.get("orderid")

	db.session.query(Order).filter(Order.id == id).update({"state" : 1})
	db.session.commit()
	db.session.close()

	return jsonify(""), 200




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


	if order[0].state == 3:
		res = show(id)
		return jsonify(res), 200




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
	departTuple = (float(depart["lat"]), float(depart["lng"]))
	parkingTuple = (float(parking["lat"]), float(parking["lng"]))
	distance = 2*(geodesic(departTuple, parkingTuple).km)

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
	print(selected)
	print("----------------------------getStartTime-------------------------")
	print(finalVolunteer)
	print("----------------------------test-------------------------")

	selectedperson = ""
	voluteerName = ""

	updateRequestsClustersTSP(centroids, requestList, id)

	deleteAllRelatedVolunteer(id)

	for i in finalVolunteer:
		userid = requests[int(requestList[finalVolunteer[i]])].userid
		selectedperson = selectedperson + str(userid) + ";"
		voluteerName = voluteerName + users[userid].name + "_" + str(i) + ";"
		userEntrepot = str(users[userid].latitude) + "," + str(users[userid].longitude) + ";" + str(centroids[0][i]["lat"]) + "," + str(centroids[0][i]["lng"])
		volunteerRequestList = getAllRequestByLabel(centroids[1], requestList, i)
		addVolunteer(id, userid, userEntrepot, volunteerRequestList, getVolunteerDay(finalVolunteer[i] ,selected))



	db.session.query(Order).filter(
									Order.id == id
								).update({"selectedperson" : selectedperson, "time" : bestday, "distancetotal": round(distance, 2), "clusters": toStringCentroids(centroids[0])})
	db.session.commit()
	db.session.close()

	distance = distance + updateRequestsClusters(centroids, requestList, id)


	res["volunteer"] = voluteerName
	res["deliveryDay"] = deliveryDay
	res["depart"] = depart
	res["id"] = id
	res["waypoints"] = waypoints
	res["state"] = order[0].state
	res["distanceNaive"] = calculateDistance(id)
	res["distance"] = round(distance, 2)

	return jsonify(res), 200




def getVolunteerDay(requestId, selected):
	for i in selected:
		if requestId in selected[i]:
			return i
	return "none"

def getAllRequestByLabel(labels, requestlist, label):

	res = ""
	for i in range(len(requestlist)):
		if labels[i] == label:
			res = res + requestlist[i] + ","

	return res

def deleteAllRelatedVolunteer(orderid):
	
	volunteerItem = Volunteer.query.filter(Volunteer.orderid == orderid).delete()

	# if volunteerItem.count()>0:
	# 	return

	# for item in volunteerItem:
	# 	db.session.delete(item)

	db.session.commit()




def addVolunteer(orderid, userid, userEntrepot, volunteerRequestList, date):

	volunteerItem = db.session.query(Volunteer).filter(Volunteer.orderid == orderid)
	volunteers = Volunteer.query.all()
	length = Volunteer.query.count()
	voluteerid = int(volunteers[length-1].id) + 1
	db.session.add(Volunteer(voluteerid, userid, userEntrepot, volunteerRequestList, date, orderid,1))
	db.session.commit() 








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


@algo_bp.route('/algo/test/', methods=['GET'])
def test():
	
	id = -1
	if request.args.get("orderid") != None:
		id = request.args.get("orderid")

	id = int(id)
	order = Order.query.filter(Order.id == id)[0]

	if int(order.state) == 3:
		print("-----------------HERE ! ------------------")
	else:
		print("-----------------TSP PROB-----------------")
		res = init(id)
		entrepotlist = ""
		for location in res["location"]:
			entrepotlist = entrepotlist + str(location["lat"]) + "," + str(location["lng"])+";"

		db.session.query(Order).filter(Order.id == id).update({"entrepotlist": entrepotlist, "state":3})
		db.session.commit()
		print("------------------RESULT---------------")
		print(res)
		print("------------------RESULT---------------")



	return jsonify(""), 200


def show(orderid):
	res = {}
	order = Order.query.filter(Order.id == orderid)[0]
	requestlist = order.requestlist.strip(",").split(",")
	requests = Request.query.all()

	res["deliveryDay"] = order.time
	locations = []
	for i in requestlist:
		location = {
			"lat":  float(requests[int(i)].userlocation.split(",")[0]),
			"lng":  float(requests[int(i)].userlocation.split(",")[1])
		}
		locations.append(location)

	res["waypoints"] = []

	first = 0
	centroids = []
	for i in order.entrepotlist.strip(";").split(";"):
		if first==0:
			res["depart"] = {
				"lat": float(i.split(",")[0]),
				"lng": float(i.split(",")[1])
			}
			first = 1
			continue
		location = {
			"lat": float(i.split(",")[0]),
			"lng": float(i.split(",")[1])
		}
		if float(i.split(",")[0])==parking["lat"] and float(i.split(",")[1])==parking["lng"]:
			res["parking"] = location
			res["waypoints"].append(location)
			continue
		res["waypoints"].append(location)
		centroids.append(location)


	res["state"] = 3
	res["location"] = []
	res["location"].append(locations) 
	res["location"].append(centroids)
	res["distanceNaive"] = calculateDistance(orderid)
	res["distance"] = order.distancetotal

	return res


def updateRequestsClustersTSP(centroids, requestlist, orderid):

	labels = centroids[1]
	index = 0
	distance = 0 
	requests = Request.query.all()

	for requestid in requestlist:
		
		centroid = (float(centroids[0][labels[index]]["lat"]), float(centroids[0][labels[index]]["lng"]))
		location = (float(requests[int(requestid)].userlocation.split(",")[0]), float(requests[int(requestid)].userlocation.split(",")[1]))
		dis = geodesic(centroid, location).km
		if dis > 1:
			distance = distance + dis
		db.session.query(Request).filter(Request.id == requestid).update({"cluster" : labels[index]})
		db.session.commit()
		index = index + 1

	return round(distance*2,2)

def updateRequestsClusters(centroids, requestlist, orderid):

	labels = centroids[1]
	index = 0
	distance = 0 

	order = Order.query.filter(Order.id == orderid)[0]
	requests = Request.query.all()

	parkingTuple = (float(parking["lat"]), float(parking["lng"]))

	selectedperson = order.selectedperson.strip(";").split(";")
	if len(selectedperson) > 1:
		for i in range(len(selectedperson)):
			selectedperson[i] = int(selectedperson[i])

	labelsAide = []
	requestidVol = []

	for requestid in requestlist:
		id = int(requestid)
		if int(requests[id].userid) in selectedperson:
			print("-----------oneAide---------------")
			labelsAide.append(int(requests[id].cluster))
			centroid = (float(centroids[0][int(requests[id].cluster)]["lat"]), float(centroids[0][int(requests[id].cluster)]["lng"]))
			distance = distance + 2*(geodesic(centroid, parkingTuple).km)
			requestidVol.append(id)

	pointRetraits = []
	entrepotlist = order.entrepotlist.strip(";").split(";")
	i = 1
	print("-----------entrepotlist----------------")
	while i < len(entrepotlist):
		index = 0
		for centroid in centroids[0]:
			if float(centroid["lat"]) == float(entrepotlist[i].split(",")[0]) and float(centroid["lng"]) == float(entrepotlist[i].split(",")[1]):
				labelsAide.append(index)
				print(index)
				break
			index = index + 1
		i = i + 1
	print("-----------entrepotlist----------------")


	index = 0

	for requestid in requestlist:
		id = int(requestid)

		if requestid in requestidVol:
			index = index + 1
			continue

		if int(labels[index]) in labelsAide:
			print("-----------Aide---------------")
			centroid = (float(centroids[0][labels[index]]["lat"]), float(centroids[0][labels[index]]["lng"]))
			location = (float(requests[id].userlocation.split(",")[0]), float(requests[id].userlocation.split(",")[1]))
			dis = geodesic(centroid, location).km
			if dis > 1:
				distance = distance + dis*2
			index = index + 1
			continue

		location = (float(requests[id].userlocation.split(",")[0]), float(requests[id].userlocation.split(",")[1]))
		dis = geodesic(parkingTuple, location).km
		if dis > 1:
			distance = distance + dis*2
		
		index = index + 1

	return round(distance,2)

def toStringCentroids(centroids):
	res = ""
	for centroid in centroids:
		res = res + str(centroid["lat"]) + "," +  str(centroid["lng"]) + ";"

	return res



def init(orderid):

	order = Order.query.filter(Order.id == orderid)
	requestList = order[0].requestlist
	requests = Request.query.all()
	depart = {
		"lat" : order[0].entrepotlist.split(";")[0].split(",")[0],
		"lng" : order[0].entrepotlist.split(";")[0].split(",")[1]
	}

	locations = []
	requestList = requestList.strip(",").split(",")

	for i in range(len(requestList)):
		location = {}
		location["lat"] = requests[int(requestList[i])].userlocation.split(",")[0]
		location["lng"] = requests[int(requestList[i])].userlocation.split(",")[1]
		locations.append(location)

	centroids = clustering(locations)

	print("--------------------CLUSTERING-----------------------")
	distance = updateRequestsClustersTSP(centroids, requestList, orderid)
	print("--------------------CLUSTERING-----------------------")

	ptsTmp = changeToTuple(centroids[0])

	pts = []
	pts.append((float(depart["lat"]), float(depart["lng"])))
	for i in ptsTmp:
		pts.append(i)
	pts.append((45.77495,4.84839))

	tspRES = solveTSP(pts)

	path = tspRES["locations"]
	distance = distance + tspRES["distance"]

	db.session.query(Order).filter(Order.id == orderid).update({"distancetotal" : distance, "clusters": toStringCentroids(centroids[0])})
	db.session.commit()


	res = {}
	res["location"] = path
	res["depart"] = depart
	res["arrival"] = {
		"lat" : 45.77495,
		"lng" : 4.84839
	}

	return res


def changeToTuple(centroids):
	res = []
	for i in centroids:
		item = (i["lat"], i["lng"])
		res.append(item)

	return res


def solveTSP(locations):

	graph = []

	print("---------------locations-------------------")
	print(locations)
	print("---------------locations-------------------")
	
	for i in range(len(locations)):
		item = []
		for j in range(len(locations)):
			item.append(geodesic(locations[i], locations[j]).km)
		graph.append(item)

	distance_matrix = np.array(graph)

	permutation, distance = solve_tsp_dynamic_programming(distance_matrix)

	res = []

	index = 0

	print("---------------permutation-------------------")
	print(permutation)
	print("---------------permutation-------------------")

	for i in permutation:
		if i == 0:
			break
		index = index + 1

	print("---------------index-------------------")
	print(index)
	print("---------------index-------------------")

	for i in range(len(permutation)):
		res.append({
			"lat" : locations[(permutation[index+i])%len(locations)][0], 
			"lng" : locations[(permutation[index+i])%len(locations)][1]
		})

	print("---------------res-------------------")
	print(res)
	print("---------------res-------------------")

	return {"locations":res, "distance": distance}


def calculateDistance(orderid):
	order = Order.query.filter(Order.id == orderid)[0]
	depart = (float(order.entrepotlist.split(";")[0].split(",")[0]), float(order.entrepotlist.split(";")[0].split(",")[1]))
	stockage = (parking["lat"], parking["lng"])
	distance = 0
	distance = distance + geodesic(depart, stockage).km

	requestlist = order.requestlist.strip(",").split(",")
	requests = Request.query.all()
	for requestid in requestlist:
		request = requests[int(requestid)]
		location = (float(request.userlocation.split(",")[0]), float(request.userlocation.split(",")[1]))
		distance = distance + geodesic(location, stockage).km


	distance = distance*2
	distance = round(distance, 2)
	return distance



@algo_bp.route('/algo/userOrder/', methods=['GET'])
def userOrder():
	id = -1
	if request.args.get("orderid") != None:
		id = request.args.get("orderid")

	order = Order.query.filter(Order.id == id)[0]
	owner = User.query.filter(User.id == order.ownerid)[0]
	selectedperson = User.query.filter(User.id == int(order.selectedperson))[0]
	res = {}

	res["depart"] = {
		"lat": float(order.entrepotlist.split(";")[0].split(",")[0]),
		"lng": float(order.entrepotlist.split(";")[0].split(",")[1])
	}

	res["arrival"] = {
		"lat": float(order.entrepotlist.split(";")[1].split(",")[0]),
		"lng": float(order.entrepotlist.split(";")[1].split(",")[1])
	}

	res["description"] = order.description

	res["time"] = order.time
	res["price"] = order.price
	
	res["contact1"] = "USER"+str(order.ownerid)+" : " + str(owner.mobile)
	res["contact2"] = "USER"+str(selectedperson.id)+" : " + str(selectedperson.mobile)



	return jsonify(res), 200





























	

