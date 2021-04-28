from exts import db, migrate
from model import User, FarmOrder, Farm, SingleOrder, Coupon, Product
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

farmList = [ {
		"name" : "Earl la Seigliere",
		"longitude" : 5.01988,
		"latitude" : 45.75245,
		"address" : "71 Rue Jean Jaurès, 69740 Genas"
	}, {
		"name" : "Girard Yvonne",
		"longitude" : 5.00056,
		"latitude" : 45.77711,
		"address" : "14 Ter Rue Jean Collet, 69330 Meyzieu"
	}, {
		"name" : "Ferme de la Forestière",
		"longitude" : 5.00227,
		"latitude" : 45.80486,
		"address" : "69330 Lyon"
	}, {
		"name" : "Earl la Ferme de Lena",
		"longitude" : 4.75230,
		"latitude" : 45.72115,
		"address" : "10 Chemin du Pivolet, 69630 Chaponost"
	}, {
		"name" : "Marchetto Marin Cecile Brune",
		"longitude" : 4.90114,
		"latitude" : 45.65470,
		"address" : "60 Chemin des Romanettes, 69960 Corbas"
	}]

legume = pd.read_csv("dataset/legume.csv").to_numpy().tolist()
fruit = pd.read_csv("dataset/fruit.csv").to_numpy().tolist()
other = pd.read_csv("dataset/other.csv").to_numpy().tolist()


def init():
	db.create_all()
	
	userInit()
	farmInit()
	couponInit()
	productInit()

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

		db.session.add(User(i, name, passwd, mobile, latitude, longitude, type, carbonactual, volunteeractual, carbontotal, volunteertotal))

def farmInit():

	Farm.query.delete()

	userid = userNb

	for i in range(len(farmList)):

		name = farmList[i]["name"]
		latitude = farmList[i]["latitude"]
		longitude = farmList[i]["longitude"]
		address = farmList[i]["address"]

		db.session.add(Farm(i, userid, name, latitude, longitude, address))


		name = "user" + str(userid)
		mobile = "0"+str(600000000+randint(0,mobileRange))
		carbonactual = randint(0, carbonactualRange)
		volunteeractual = randint(0, volunteeractualRange)
		carbontotal = randint(0, carbontotalRange)
		volunteertotal = randint(0, volunteertotalRange)

		db.session.add(User(userid, name, "passwd", mobile, latitude, longitude, "farmer", carbonactual, volunteeractual, carbontotal, volunteertotal))

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

			name = legume[item][0]
			price = legume[item][length-2]
			photourl = legume[item][length-1]

			quantity = randint(10, 200)

			db.session.add(Product(id, farmid, name, price, quantity, "legume", photourl))
			id = id + 1

		itemList = []

		for j in range(randint(3, 10)):

			item = randint(0, len(fruit)-1)
			while item in itemList:
				item = randint(0, len(fruit)-1)

			itemList.append(item)

			length = len(legume[item])

			name = legume[item][0]
			price = legume[item][length-2]
			photourl = legume[item][length-1]

			quantity = randint(10, 200)

			db.session.add(Product(id, farmid, name, price, quantity, "fruit", photourl))
			id = id + 1

		itemList = []

		for j in range(randint(3, 10)):

			item = randint(0, len(other)-1)
			while item in itemList:
				item = randint(0, len(other)-1)

			itemList.append(item)

			length = len(legume[item])

			name = legume[item][0]
			price = legume[item][length-2]
			photourl = legume[item][length-1]

			quantity = randint(10, 200)

			db.session.add(Product(id, farmid, name, price, quantity, "other", photourl))
			id = id + 1

		






