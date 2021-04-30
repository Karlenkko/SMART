import json

from flask import Blueprint
from flask import abort, request, jsonify
from model import Product, Request, User, Order, Farm
from exts import db

farm_bp = Blueprint('farm', __name__)


@farm_bp.route('/farm/getAllProducts/', methods=['GET'])
def getAllProducts():
    if not request.args or not 'farmId' in request.args:
        abort(400)
    else:
        products = Product.query.filter(Product.farmid == request.args.get('farmId'))
        res = []
        for product in products:
            res.append({
                "idProduct": product.id,
                "productName": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "url": product.photourl,
                "category": product.category,
                "carbonRedu": product.carbonredu,
                "origin": product.origincarrefour,
                "carrefourPrice": product.pricecarrefour
            })

    return jsonify(res), 200


@farm_bp.route('/farm/request/', methods=['POST'])
def addRequest():
    # if not request.form or not 'userid' in request.form:
    #     abort(400)
    # else:
    try:
        data = json.loads(request.get_data(as_text=True))
        user = User.query.filter(User.id == data['userId']).first()
        userlocation = str(user.longitude) + "," + str(user.latitude)
        requestid = Request.query.count()
        desttime = ''

        for time in data['deliveryTime']:
            desttime = desttime + time['day'] + " " + time['time'] + ";"

        volunteertime = ''
        if data['volunteer']['do'] == 1:
            for time in data['volunteer']['timelist']:
                volunteertime = volunteertime + time['day'] + " " + time['time'] + ";"
        requestorderid = 0

        existingorder = Order.query.filter(Order.ownerid == data['farmOwnerId']).first()

        if not existingorder:
            orderid = Order.query.count()
            farm = Farm.query.filter(Farm.userid == data['farmOwnerId']).first()
            neworder = Order(int(orderid),
                             int(data['farmOwnerId']),
                             str(farm.longitude) + "," + str(farm.latitude),
                             "",
                             "",
                             "",
                             0,
                             "",
                             0)
            db.session.add(neworder)
            requestorderid = orderid
        else:
            requestorderid = existingorder.id

        description = ''
        for item in data['cart']:
            description = description + item['productName'] + "_" + item['amount'] + ";"

        newRequest = Request(int(requestid),
                             int(requestorderid),
                             int(data['userId']),
                             userlocation,
                             desttime,
                             volunteertime,
                             description,
                             float(data['totalPrice']))
        db.session.add(newRequest)
        oldorder = Order.query.filter(Order.ownerid == data['farmOwnerId']).first()
        db.session.query(Order).filter(Order.ownerid == data['farmOwnerId']).update(
            {"requestlist": oldorder.requestlist + str(requestid) + ","})
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.get_data(as_text=True)), 201
