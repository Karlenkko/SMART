from exts import db
from flask import jsonify


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields


class User(db.Model, EntityBase):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    passwd = db.Column(db.String(50))
    mobile = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(60))
    type = db.Column(db.String(10))
    photourl = db.Column(db.String(100))
    carbontotal = db.Column(db.Integer)
    carbonactual = db.Column(db.Integer)
    volunteertotal = db.Column(db.Integer)
    volunteeractual = db.Column(db.Integer)
    balance = db.Column(db.Float)
    def __init__(self, id, name, passwd, mobile, latitude, longitude, type, carbonactual, volunteeractual, carbontotal, volunteertotal, balance):
        self.id = id
        self.name = name
        self.passwd = passwd
        self.mobile = mobile
        self.latitude = latitude
        self.longitude = longitude
        self.type = type
        self.carbonactual = carbonactual
        self.volunteeractual = volunteeractual
        self.carbontotal = carbontotal
        self.volunteertotal = volunteertotal
        self.balance = balance

    def __repr__(self):
        return '<User: {}>'.format(self.name)
        

class Farm(db.Model, EntityBase):
    __tablename__ = 'farm'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    name = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(100))
    photourl = db.Column(db.String(100))

    def __init__(self, id, userid, name, latitude, longitude, address):
        self.id = id
        self.userid = userid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.address = address

    def __repr__(self):
        # return '<Farm: {}>'.format(self.name)
        return '{"id":%s,"userid":%s,"name":"%s","latitude":%s,"longitude":%s,"address":"%s","photourl":"%s"}' % (
            self.id, self.userid, self.name, self.latitude, self.longitude, self.address, self.photourl)



class Product(db.Model, EntityBase):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    farmid = db.Column(db.Integer)
    name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    photourl = db.Column(db.String(100))
    category = db.Column(db.String(20))
    carbonredu = db.Column(db.Integer)
    origincarrefour = db.Column(db.String(100))
    pricecarrefour = db.Column(db.Float)
    def __init__(self, id, farmid, name, price, quantity, category, photourl, origincarrefour, pricecarrefour):
        self.id = id
        self.farmid = farmid
        self.name = name
        self.price = price
        self.quantity = 0
        self.category = category
        self.quantity = quantity
        self.photourl = photourl
        self.origincarrefour = origincarrefour
        self.pricecarrefour = pricecarrefour

    def __repr__(self):
        return '{"id":%s,"farmid":%s,"name":%s,"quantity":%s,"price":%s,"photourl":%s,"category":%s,"carbonredu":%s,"origincarrefour":%s,"pricecarrefour":%s}' % (
            self.id, self.farmid, self.name, self.quantity, self.price, self.photourl, self.category, self.carbonredu, self.origincarrefour, self.pricecarrefour)



class SingleOrder(db.Model, EntityBase):
    __tablename__ = 'singleorder'
    id = db.Column(db.Integer, primary_key=True)
    startuserid = db.Column(db.Integer)
    receiveuserid = db.Column(db.Integer)
    destlongitude = db.Column(db.Float)
    destlatitude = db.Column(db.Float)
    description = db.Column(db.String(200))
    candidates = db.Column(db.String(200))
    state = db.Column(db.Integer)
    farmvolunteertime = db.Column(db.String(100))
    desttime = db.Column(db.String(50))
    price = db.Column(db.Float)

    def __init__(self, startuserid, destlongitude, destlatitude, description=''):
        self.startuserid = startuserid
        self.destlongitude = destlongitude
        self.destlatitude = destlatitude
        self.description = description

    def __repr__(self):
        return '{"id":%s,"startuserid":%s,"receiveuserid":%s,"destlongitude":%s,"destlatitude":%s,"description":%s,"candidates":%s,"state":%s,"farmvolunteertime":%s,"desttime":%s,"price":%s}' % (
            self.id, self.startuserid, self.receiveuserid, self.destlongitude, self.destlatitude, self.description, self.candidates, self.state, self.farmvolunteertime, self.desttime, self.price)


class FarmOrder(db.Model, EntityBase):
    __tablename__ = 'farmorder'
    id = db.Column(db.Integer, primary_key=True)
    farmid = db.Column(db.Integer)
    orderlist = db.Column(db.String(200))
    volunteerselected = db.Column(db.String(200))
    timeselected = db.Column(db.String(50))
    entrepotlist = db.Column(db.String(400))
    estimatedfee = db.Column(db.Float)

    def __init__(self, orderlist='', volunteerselected='', timeselected=''):
        self.orderlist = orderlist
        self.volunteerselected = volunteerselected
        self.timeselected = timeselected

    def __repr__(self):
        return '{"id":%s,"farmid":%s,"orderlist":%s,"volunteerselected":%s,"timeselected":%s,"entrepotlist":%s,"estimatedfee":%s}' % (
            self.id, self.farmid, self.orderlist, self.volunteerselected, self.timeselected, self.entrepotlist, self.estimatedfee)


class Coupon(db.Model, EntityBase):
    __tablename__ = 'coupon'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    value = db.Column(db.Float)

    def __init__(self, id, userid, value):
        self.id = id
        self.userid = userid
        self.value = value

    def __repr__(self):
        return '{"id":%s,"userid":%s,"value":%s}' % (self.id, self.userid, self.value)
