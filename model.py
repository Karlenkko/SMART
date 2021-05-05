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
    photourl = db.Column(db.String(200))
    carbontotal = db.Column(db.Integer)
    carbonactual = db.Column(db.Integer)
    volunteertotal = db.Column(db.Integer)
    volunteeractual = db.Column(db.Integer)
    balance = db.Column(db.Float)
    def __init__(self, id, name, passwd, mobile, latitude, longitude, address, type, photourl, carbonactual, volunteeractual, carbontotal, volunteertotal, balance):
        self.id = id
        self.name = name
        self.passwd = passwd
        self.mobile = mobile
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.type = type
        self.photourl = photourl
        self.carbonactual = carbonactual
        self.volunteeractual = volunteeractual
        self.carbontotal = carbontotal
        self.volunteertotal = volunteertotal
        self.balance = balance

    def __repr__(self):
        return '{"id":%s,"name":%s,"passwd":%s,"mobile":%s,"latitude":%s,"longitude":%s,"address":%s,"type":%s,"photourl":%s,"carbontotal":%s,"carbonactual":%s,"volunteertotal":%s,"volunteeractual":%s,"balance":%s}' % (
            self.id, self.name, self.passwd, self.mobile, self.latitude, self.longitude, self.address, self.type, self.photourl, self.carbontotal, self.carbonactual, self.volunteertotal, self.volunteeractual, self.balance)
        

class Farm(db.Model, EntityBase):
    __tablename__ = 'farm'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    name = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(100))
    photourl = db.Column(db.String(100))

    def __init__(self, id, userid, name, latitude, longitude, address, photourl):
        self.id = id
        self.userid = userid
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.photourl = photourl

    def __repr__(self):
        # return '<Farm: {}>'.format(self.name)
        return '{"id":%s,"userid":%s,"name":"%s","latitude":%s,"longitude":%s,"address":"%s","photourl":"%s"}' % (
            self.id, self.userid, self.name, self.latitude, self.longitude, self.address, self.photourl)



class Product(db.Model, EntityBase):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    farmid = db.Column(db.Integer)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    photourl = db.Column(db.String(200))
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



class Order(db.Model, EntityBase):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    # farmer or the person publishes
    ownerid = db.Column(db.Integer)             
    # depart and destination for the personal request (initialized when publish the order) 
    # path of delivery for the farm order (initialized when validate the order)
    entrepotlist = db.Column(db.String(400))
    # detail of the order for personal order
    # detail of delivery for farm order 
    description = db.Column(db.String(200))
    # selected candidates for personal order
    # selected volunteers for farm order
    selectedperson = db.Column(db.String(200))
    # requestId list
    requestlist = db.Column(db.String(200))
    # 0 en cours; 1 validé; 2 annulé
    state = db.Column(db.Integer)
    time = db.Column(db.String(50))
    price = db.Column(db.Float)
    distancetotal = db.Column(db.Float)
    clusters = db.Column(db.String(200))
    confirmlist = db.Column(db.String(200))

    def __init__(self, id, ownerid, entrepotlist, description, selectedperson, requestlist, state, time, price, distancetotal, clusters, confirmlist):
        self.id = id
        self.ownerid = ownerid
        self.entrepotlist = entrepotlist
        self.description = description
        self.selectedperson = selectedperson
        self.requestlist = requestlist
        self.state = state
        self.time = time
        self.price = price
        self.distancetotal = distancetotal
        self.clusters = clusters
        self.confirmlist = confirmlist

    def __repr__(self):
        return '{"id":%s,"ownerid":%s,"entrepotlist":%s,"description":%s,"selectedperson":%s,"requestlist":%s,"state":%s,"time":%s,"price":%s, "distancetotal":%s, "clusters":%s,"confirmlist":%s}' % (
            self.id, self.ownerid, self.entrepotlist, self.description, self.selectedperson, self.requestlist,self.state, self.time, self.price, self.distancetotal, self.clusters, self.confirmlist)


class Request(db.Model, EntityBase):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    orderid = db.Column(db.Integer)
    userid = db.Column(db.Integer)
    userlocation = db.Column(db.String(50))
    timeproposed = db.Column(db.String(100))
    volunteertime = db.Column(db.String(100))
    description = db.Column(db.String(800))
    price = db.Column(db.Float)
    destination = db.Column(db.String(100))
    volunteerid = db.Column(db.Integer)
    cluster = db.Column(db.String(50))
    

    def __init__(self,id ,orderid, userid, userlocation, timeproposed, volunteertime, description, price, cluster):
        self.id = id
        self.orderid = orderid
        self.userid = userid
        self.userlocation = userlocation
        self.timeproposed = timeproposed
        self.volunteertime = volunteertime
        self.description = description
        self.price = price
        self.cluster = cluster

    def __repr__(self):
        return '{"id":%s,"orderid":%s,"userid":%s,"userlocation":%s,"timeproposed":%s,"volunteertime":%s,"description":%s,"price":%s,"destination":%s,"volunteerid":%s, "cluster":%s}' % (
            self.id, self.orderid, self.userid, self.userlocation, self.timeproposed, self.volunteertime, self.description, self.price, self.destination, self.volunteerid, self.cluster)

class Volunteer(db.Model, EntityBase):
    __tablename__ = 'volunteer'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    entrepotlist = db.Column(db.String(400))
    requestlist = db.Column(db.String(200))
    date = db.Column(db.String(50))
    orderid = db.Column(db.Integer)
    accept = db.Column(db.Integer)

    def __init__(self, id, userid, entrepotlist, requestlist, date, orderid, accept):
        self.id = id
        self.userid = userid
        self.entrepotlist = entrepotlist
        self.requestlist = requestlist
        self.date = date
        self.orderid = orderid
        self.accept = accept

    def __repr__(self):
        return '{"id":%s,"userid":%s,"entrepotlist":%s,"requestlist":%s,"date":%s,"orderid":%s,"accept":%s}' % (self.id, self.userid, self.entrepotlist, self.requestlist, self.date, self.orderid, self.accept)


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
