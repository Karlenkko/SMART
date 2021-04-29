from flask import Blueprint
from model import Farm, Product, Order, Request, User
from flask import abort, request, jsonify
from flask_cors import cross_origin
from exts import db
import json

index_bp = Blueprint('index', __name__)


@index_bp.route('/index/getAllFarmOrders/', methods=['GET'])
@cross_origin()
def getAllFarmOrders():
    orders = Order.query.all()
    farms = Farm.query.all()
    farmuserids = {}
    res = []
    for farm in farms:
        farmuserids[farm.userid] = farm
    for order in orders:
        if order.ownerid in farmuserids.keys():
            requests = Request.query.filter(Request.orderid == order.id)
            count = 0
            for req in requests:
                if len(req.volunteertime) > 0:
                    count = count + 1;
            totalMembers = len(order.requestlist.split(',')) - 1
            res.append({
                "orderId": order.id,
                "farmId": farmuserids[order.ownerid].id,
                "farmOwnerId": farmuserids[order.ownerid].userid,
                "farmName": farmuserids[order.ownerid].name,
                "farmAddress": farmuserids[order.ownerid].address,
                "url": farmuserids[order.ownerid].photourl,
                "totalMembers": totalMembers,
                "totalVolunteers": count
            })
    return jsonify(res), 200


@index_bp.route('/index/getAllUserOrders/', methods=['GET'])
@cross_origin()
def getAllUserOrders():
    orders = Order.query.all()
    users = User.query.all()
    userdict = {}
    res = []
    for user in users:
        if user.type == "user":
            userdict[user.id] = user
    for order in orders:
        if order.ownerid in userdict.keys():
            totalMembers = len(order.requestlist.split(',')) - 1
            points = order.entrepotlist.split(';')
            res.append({
                "orderId": order.id,
                "userId": order.ownerid,
                "userName": userdict[order.ownerid].name,
                "date": order.time,
                "state": order.state,
                "description": order.description,
                "totalCandidate": totalMembers,
                "depart": points[0],
                "destination": points[1],
                "url": userdict[order.ownerid].photourl,
                "tel": userdict[order.ownerid].mobile,
                "price": order.price
            })

    return jsonify(res), 200


@index_bp.route('/index/getAllFarms/', methods=['GET'])
@cross_origin()
def getAllFarms():
    farms = Farm.query.all()
    products = Product.query.all()
    productLists = []
    temp = 0
    farmid = 0
    productLists.append("")
    for product in products:
        if product.farmid == farmid:
            if temp < 4:
                productLists[farmid] += product.name + ","
                temp = temp + 1
            else:
                productLists.append("")
                farmid = farmid + 1
                temp = 0
    res = []
    for farm in farms:
        res.append({
            "farmId": farm.id,
            "farmOwnerId": farm.userid,
            "farmName": farm.name,
            "location": {
                "longitude": farm.longitude,
                "latitude": farm.latitude
            },
            "url": farm.photourl,
            "productList": productLists[farm.id]
        })
    return jsonify(res), 200


@index_bp.route('/index/participateUserOrder/', methods=['POST'])
@cross_origin()
def participateUserOrder():
    # if True or not request.form or not 'orderId' in request.form:
    #     abort(400)
    # else:
    try:
        data = json.loads(request.get_data(as_text=True))
        requestid = Request.query.count()
        order = Order.query.filter(Order.id == data['orderId']).first()
        user = User.query.filter(User.id == data['userId']).first()
        times = ''
        for time in data['timelist']:
            times = times + time['day'] + " " + time['time'] + ";"
        newRequest = Request(int(requestid), int(data['orderId']), int(data['userId']), str(user.longitude) + "," + str(user.latitude), times, "", data['description'], order.price)
        db.session.add(newRequest)
        print("added new request")
        oldorder = Order.query.filter(Order.id == data['orderId']).first()
        db.session.query(Order).filter(Order.id == data['orderId']).update({"requestlist": oldorder.requestlist + str(requestid) + ","})
        db.session.commit()
        db.session.close()
    except:
        abort(500)
    else:
        return jsonify(request.get_data(as_text=True)), 201
