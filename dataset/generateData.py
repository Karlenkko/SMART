import random
from random import randint



def generateUser():
	f = open('users.csv', 'w', encoding='UTF-8')
	title = "name,passwd,mobile,latitude,longitude,type,carbonactual,volunteeractual,carbontotal,volunteertotal\n"
	f.write(title)

	passwd = "passwd"
	mobileRange = 99999999
	latitudeRange = 70000
	longitudeRange = 120000
	type = "user"
	carbonactualRange = 500
	volunteeractualRange = 30
	carbontotalRange = 10000
	volunteertotalRange = 400

	for i in range(100):
		name = "user" + str(i)
		mobile = "0"+str(600000000+randint(0,mobileRange))
		latitude = 45.73192 + randint(0,latitudeRange)/1000000
		longitude = 4.814586 + randint(0,longitudeRange)/1000000
		carbonactual = randint(0, carbonactualRange)
		volunteeractual = randint(0, volunteeractualRange)
		carbontotal = randint(0, carbontotalRange)
		volunteertotal = randint(0, volunteertotalRange)

		user = name + passwd + mobile + str(latitude) + str(longitude) + type + carbonactual + volunteeractual + carbontotal + volunteertotal + "\n"
		f.write(user)

	f.close()


if __name__ == '__main__':
	generateUser()