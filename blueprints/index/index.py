from flask import Blueprint
from model import Farm, Product, Order, Request, User
from flask import abort, request, jsonify
from flask_cors import cross_origin
from exts import db

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
                "orderId" : order.id,
                "farmId" : farmuserids[order.ownerid].id,
                "farmOwnerId" : farmuserids[order.ownerid].userid,
                "farmName" : farmuserids[order.ownerid].name,
                "farmAddress" : farmuserids[order.ownerid].address,
                "url" : farmuserids[order.ownerid].photourl,
                "totalMembers" : totalMembers,
                "totalVolunteers" : count
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
                "userId" : order.ownerid,
                "userName" : userdict[order.ownerid].name,
                "date" : order.time,
                "state" : order.state,
                "description" : order.description,
                "totalCandidate" : totalMembers,
                "depart" : points[0],
                "destination" : points[1],
                "url" : userdict[order.ownerid].photourl,
                "tel" : userdict[order.ownerid].mobile,
                "price" : order.price
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
            "farmOwnerId" : farm.userid,
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
    if not request.form or not 'orderId' in request.form:
        abort(400)
    else:
        try:
            requestid = Request.query.count()
            order = Order.query.filter(Order.id == request.form.get('orderId', type=int))
            user = User.query.filter(User.id == request.form.get('userId', type=int)).first()
            times = ''
            for time in request.form.get('timelist'):
                times = times + time.day + " " + time.time + ";"
            newRequest = Request(requestid,
                                 request.form.get('orderId', type=int),
                                 request.form.get('userId', type=int),
                                 str(user.longitude) + "," + str(user.latitude),
                                 times,
                                 "",
                                 request.form.get('description'),
                                 order.price)
            db.session.add(newRequest)
            oldorder = Order.query.filter(Order.id == request.form.get('orderid', type=int)).first()
            db.session.query(Order).filter(Order.id == request.form.get('orderid', type=int)).update(
                {"requestlist": oldorder.requestlist + str(requestid) + ","})
            db.session.commit()
        except:
            abort(500)
        else:
            return jsonify(request.form), 201