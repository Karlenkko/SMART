from exts import db, migrate
from model import User, Request, Farm, Order, Coupon, Product
from random import randint
import pandas as pd
import numpy as np 
import os

userNb = 100
mobileRange = 99999999
latitudeRange = 70000
longitudeRange = 120000
carbonactualRange = 500
volunteeractualRange = 30
carbontotalRange = 10000
volunteertotalRange = 400
balanceRange = 400

origin = ['FRANCE', 'ESPAGNE', 'PEROU', 'UE', 'MOZAMBIQUE', 'ORIGINEPAYSTIERS', 'COLOMBIE', 'nan', 'COSTARICA', 'VIETNAM', 'AFRIQUEDUSUD', 'PORTUGAL', 'ITALIE', 'ARGENTINE', 'ISRAEL', 'CHINE', 'MAROC']
originCarbon = [50, 300, 20000, 400, 2000, 1000, 20000, 50, 20000, 25000, 10000, 400, 250, 23000, 7500, 25000, 1000]


farmList = [ {
		"name" : "Earl la Seigliere",
		"longitude" : 5.01988,
		"latitude" : 45.75245,
		"address" : "71 Rue Jean Jaurès, 69740 Genas",
		"url" : "https://images.unsplash.com/photo-1560493676-04071c5f467b?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MXx8ZmFybXxlbnwwfHwwfHw%3D&ixlib=rb-1.2.1&w=1000&q=80"
	}, {
		"name" : "Girard Yvonne",
		"longitude" : 5.00056,
		"latitude" : 45.77711,
		"address" : "14 Ter Rue Jean Collet, 69330 Meyzieu",
		"url" : "https://images.unsplash.com/photo-1464226184884-fa280b87c399?ixid=MnwxMjA3fDB8MHxzZWFyY2h8Nnx8ZmFybXxlbnwwfHwwfHw%3D&ixlib=rb-1.2.1&w=1000&q=80"
	}, {
		"name" : "Ferme de la Forestière",
		"longitude" : 5.00227,
		"latitude" : 45.80486,
		"address" : "69330 Lyon",
		"url" : "https://images.unsplash.com/photo-1500076656116-558758c991c1?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTh8fGZhcm18ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80"
	}, {
		"name" : "Earl la Ferme de Lena",
		"longitude" : 4.75230,
		"latitude" : 45.72115,
		"address" : "10 Chemin du Pivolet, 69630 Chaponost",
		"url" : "https://images.unsplash.com/photo-1535649900424-c09963c4fd8e?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTl8fGZhcm18ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80"
	}, {
		"name" : "Marchetto Marin Cecile Brune",
		"longitude" : 4.90114,
		"latitude" : 45.65470,
		"address" : "60 Chemin des Romanettes, 69960 Corbas",
		"url" : "https://images.unsplash.com/photo-1489657780376-e0d8630c4bd3?ixid=MnwxMjA3fDB8MHxzZWFyY2h8MjB8fGZhcm18ZW58MHx8MHx8&ixlib=rb-1.2.1&w=1000&q=80"
	}]

legume = pd.read_csv("dataset/legume.csv").to_numpy().tolist()
fruit = pd.read_csv("dataset/fruit.csv").to_numpy().tolist()
other = pd.read_csv("dataset/other.csv").to_numpy().tolist()
peopleurl = pd.read_csv("dataset/peopleURL.csv").to_numpy().tolist()

def isNaN(string):
	return string != string


def init():
	db.create_all()
	
	userInit()
	farmInit()
	couponInit()
	productInit()

	db.session.commit()
	db.session.close()

def initOrder():
	db.create_all()
	
	orderInit()
	requestInit()

	db.session.commit()
	db.session.close()


def userInit():
	
	User.query.delete()
	
	passwd = "passwd"
	type = "user"


	for i in range(userNb):
		name = "user" + str(i)
		mobile = "0"+str(600000000+randint(0,mobileRange))
		latitude = 45.73192 + randint(0,latitudeRange)/1000000
		longitude = 4.814586 + randint(0,longitudeRange)/1000000
		carbonactual = randint(0, carbonactualRange)
		volunteeractual = randint(0, volunteeractualRange)
		carbontotal = randint(0, carbontotalRange)
		volunteertotal = randint(0, volunteertotalRange)
		balance = randint(100, balanceRange)
		photourl = peopleurl[i][0]
		address = ""

		db.session.add(User(i, name, passwd, mobile, latitude, longitude, address, type, photourl, carbonactual, volunteeractual, carbontotal, volunteertotal, balance))

def farmInit():

	Farm.query.delete()

	userid = userNb

	for i in range(len(farmList)):

		name = farmList[i]["name"]
		latitude = farmList[i]["latitude"]
		longitude = farmList[i]["longitude"]
		address = farmList[i]["address"]
		url = farmList[i]["url"]

		db.session.add(Farm(i, userid, name, latitude, longitude, address, url))


		name = "user" + str(userid)
		mobile = "0"+str(600000000+randint(0,mobileRange))
		carbonactual = randint(0, carbonactualRange)
		volunteeractual = randint(0, volunteeractualRange)
		carbontotal = randint(0, carbontotalRange)
		volunteertotal = randint(0, volunteertotalRange)
		balance = randint(100, balanceRange)
		photourl = peopleurl[i][0]
		address = ""

		db.session.add(User(userid, name, "passwd", mobile, latitude, longitude, address, "farmer", photourl, carbonactual, volunteeractual, carbontotal, volunteertotal, balance))

		userid = userid + 1 

def couponInit():

	Coupon.query.delete()

	id = 0

	for i in range(userNb+len(farmList)):
		for j in range(randint(0, 3)):
			userid = i
			value = 3 if randint(0,1) == 0 else 5

			db.session.add(Coupon(id, userid, value))

			id = id +1 

def productInit():

	Product.query.delete()

	id = 0;

	for i in range(len(farmList)):
		farmid = i

		itemList = []

		for j in range(randint(3, 10)):

			item = randint(0, len(legume)-1)
			while item in itemList:
				item = randint(0, len(legume)-1)

			itemList.append(item)

			length = len(legume[item])

			name = legume[item][0].replace("CARREFOUR", "").replace("carrefour", "")
			pricecarrefour = float(legume[item][length-2].replace("€",""))
			price = pricecarrefour*(float(randint(80, 90))/100)
			photourl = legume[item][length-1]

			quantity = randint(10, 200)

			origincarrefour = "FRANCE" if isNaN(legume[item][1]) else legume[item][1]

			carbonredu = float(originCarbon[origin.index(origincarrefour)]*randint(80,100)/100)


			db.session.add(Product(id, farmid, name, round(price,2), quantity, "legume", photourl, origincarrefour, pricecarrefour, carbonredu))
			id = id + 1

		itemList = []

		for j in range(randint(3, 10)):

			item = randint(0, len(fruit)-1)
			while item in itemList:
				item = randint(0, len(fruit)-1)

			itemList.append(item)

			length = len(fruit[item])

			name = fruit[item][0].replace("CARREFOUR", "").replace("carrefour", "")
			pricecarrefour = float(fruit[item][length-2].replace("€",""))
			price = pricecarrefour*(float(randint(80, 90))/100)
			photourl = fruit[item][length-1]

			quantity = randint(10, 200)

			origincarrefour = "FRANCE" if isNaN(fruit[item][1]) else fruit[item][1]
			carbonredu = float(originCarbon[origin.index(origincarrefour)]*randint(80,100)/100)
			db.session.add(Product(id, farmid, name, round(price,2), quantity, "fruit", photourl, origincarrefour, pricecarrefour, carbonredu))
			id = id + 1

		itemList = []

		for j in range(randint(3, 10)):

			item = randint(0, len(other)-1)
			while item in itemList:
				item = randint(0, len(other)-1)

			itemList.append(item)

			length = len(other[item])

			name = other[item][0].replace("CARREFOUR", "").replace("carrefour", "")
			pricecarrefour = float(other[item][length-2].replace("€",""))
			price = pricecarrefour*(float(randint(80, 90))/100)
			photourl = other[item][length-1]

			quantity = randint(10, 200)
			
			origincarrefour = "FRANCE" if isNaN(other[item][1]) else other[item][1]
			
			carbonredu = float(originCarbon[origin.index(origincarrefour)]*randint(80,100)/100)
			db.session.add(Product(id, farmid, name, round(price,2), quantity, "other", photourl, origincarrefour, pricecarrefour, carbonredu))
			
			id = id + 1

orderList = [	   {
					"latitude"  : 44.8366,
					"longitude" : -0.5781,
					"requestlist" : [0, 1, 2, 3],
					"time" : "Lundi 8-10;Vendredi 16-18"
				   },
				   {
					"latitude"  : 43.6178,
					"longitude" : 1.4349,
					"requestlist" : [4, 5],
					"time" : "Jeudi 12-18"
				   },
				   {
					"latitude"  : 43.6178,
					"longitude" : 1.4349,
					"requestlist" : [],
					"time" : "Mercredi 10-12"
				   },
				   {
					"latitude"  : 43.6241,
					"longitude" : 3.8669,
					"requestlist" : [6, 7, 8],
					"time" : "Samedi 8-10;Dimanche 10-18"
				   },
				   {
					"latitude"  : 48.8302,
					"longitude" : 2.3590,
					"requestlist" : [9],
					"time" : "Lundi 14-16"
				   }]

descriptionList = ["I can help you carry something during my journey ! ", "Can someone help me to carry something ? "]
dayList = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi", "Samedi", "Dimanche"]
farmRequests = []

def orderInit():

	Order.query.delete()
	users = User.query.all()
	id = 0

	# personal order
	for i in range(len(orderList)):
		ownerindex = randint(0, len(users)-1)
		ownerid = users[ownerindex].id
		depart = str(users[ownerindex].latitude) + "," + str(users[ownerindex].longitude)
		arrival = str(orderList[i]["latitude"]) + "," + str(orderList[i]["longitude"])
		entrepotlist = depart + ";" + arrival
		description = descriptionList[randint(0,1)]
		selectedperson = ""
		requestlist = ""
		
		for j in range(len(orderList[i]["requestlist"])):
			requestlist = requestlist + str(orderList[i]["requestlist"][j]) + ","

		state = 0
		time = orderList[i]["time"]
		price = randint(0, 300)/100

		db.session.add(Order(id, ownerid, entrepotlist, description, selectedperson, requestlist, state, time, price, 0, "",""))
		id = id + 1
	# farm order

	requestId = 10

	for i in range(len(farmList)):

		farm = Farm.query.filter(Farm.name == farmList[i]["name"])[0]

		ownerid = farm.userid
		depart = str(farm.latitude) + "," + str(farm.longitude)
		entrepotlist = depart
		description = ""
		selectedperson = ""
		requestlist = ""
		
		clients = []
		for i in range(randint(3, 25)):
			client = randint(0, len(users)-6)
			while client in clients:
				client = randint(0, len(users)-1)

			clients.append(client)
			requestlist = requestlist + str(requestId) + ","
			requestId = requestId + 1

		farmRequests.append(clients)

		state = 0
		time = ""
		price = ""
		db.session.add(Order(id, ownerid, entrepotlist, description, selectedperson, requestlist, state, time, price, 0, "", ""))

		id = id + 1


def requestInit():

	Request.query.delete()

	users = User.query.all()

	for i in range(len(orderList)):
		index = 0
		for j in range(len(orderList[i]["requestlist"])):

			id = orderList[i]["requestlist"][j]
			orderid = i
			userindex = randint(0, len(users)-1)
			userid = users[userindex].id
			userlocation = str(users[userindex].latitude) + "," + str(users[userindex].longitude)
			timeproposed = ""
			for nb in range(randint(1,3)):
				day = dayList[randint(0,6)]
				start = randint(8, 14)
				end = start + randint(1, 5)
				timeproposed = timeproposed + day + " " + str(start) + "-" + str(end) + ";"

			volunteertime = ""
			# if randint(0,1) == 1:
			# 	for nb in range(randint(1,3)):
			# 		day = dayList[randint(0,6)]
			# 		start = randint(8, 14)
			# 		end = start + randint(1, 5)
			# 		volunteertime = volunteertime + day + " " + str(start) + "-" + str(end) + ";"

			description = "xxxxxxxxxxx"
			price = randint(100, 1000)/100

			if index==0:
				db.session.add(Request(id, orderid, 100, userlocation, timeproposed, volunteertime, description, price))
				index = index + 1
				continue


			db.session.add(Request(id, orderid, userid, userlocation, timeproposed, volunteertime, description, price))

	id = 10
	orderid = len(orderList)
	nb = 0

	for request in farmRequests:
		nb = nb + len(request)

	for i in range(len(farmRequests)):
		index = 0
		products = Product.query.filter(Product.farmid == i)
		productsTotalNb = Product.query.filter(Product.farmid == i).count()
		for j in range(len(farmRequests[i])):
			userid = farmRequests[i][j]
			userlocation = str(users[userid].latitude) + "," + str(users[userid].longitude)
			timeproposed = ""
			for nb in range(randint(1,3)):
				day = dayList[randint(0,6)]
				start = randint(8, 14)
				end = start + randint(1, 5)
				timeproposed = timeproposed + day + " " + str(start) + "-" + str(end) + ";"

			volunteertime = ""
			if randint(0,1) == 1:
				for nb in range(randint(1,3)):
					day = dayList[randint(0,6)]
					start = randint(8, 14)
					end = start + randint(1, 5)
					volunteertime = volunteertime + day + " " + str(start) + "-" + str(end) + ";"

			description = ""
			productSelected = []
			for index in range(randint(1,5)):
				productId = randint(0, productsTotalNb-1)
				while (productId in productSelected):
					productId = randint(0, productsTotalNb-1)
				productSelected.append(productId)
				if products[productId].quantity > 2:
					productNb = randint(1, int(products[productId].quantity/2))
					products[productId].quantity = products[productId].quantity - productNb
				else:
					productNb = 1
					products[productId].quantity = products[productId].quantity - productNb
				description = description + products[productId].name + "_" + str(productNb) + ";"



			price = randint(100, 1000)/100

			if index==0:
				db.session.add(Request(id, orderid, 100, userlocation, timeproposed, volunteertime, description, price))
				index = index + 1
				id = id + 1
				continue

			db.session.add(Request(id, orderid, userid, userlocation, timeproposed, volunteertime, description, price))
			id = id + 1

		orderid = orderid + 1



			










		






