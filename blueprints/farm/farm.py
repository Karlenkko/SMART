import json

from flask import Blueprint
from flask import abort, request, jsonify
from sqlalchemy import and_

from model import Product, Request, User, Order, Farm, Coupon
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


@farm_bp.route('/farm/getRequestStats', methods=['GET'])
def getRequestStats():
    if not request.args or not 'farmOwnerId' in request.args:
        abort(400)
    else:
        farmorder = Order.query.filter(Order.ownerid == request.args.get('farmOwnerId')).first()
        requestidlist = farmorder.requestlist.split(',')
        dayarray = [0,0,0,0,0,0,0]
        if len(requestidlist) > 0:
            requestidlist.pop()
        for req in requestidlist:
            onereq = Request.query.filter(Request.id == req).first()
            times = onereq.timeproposed.split(";")
            times.pop()
            onepersonday = [0,0,0,0,0,0,0]
            for time in times:
                if "Monday" in time:
                    onepersonday[0] = 1
                elif "Tuesday" in time:
                    onepersonday[1] = 1
                elif "Wednesday" in time:
                    onepersonday[2] = 1
                elif "Thursday" in time:
                    onepersonday[3] = 1
                elif "Friday" in time:
                    onepersonday[4] = 1
                elif "Saturday" in time:
                    onepersonday[5] = 1
                elif "Sunday" in time:
                    onepersonday[6] = 1
            for i in range(len(onepersonday)):
                dayarray[i] = dayarray[i] + onepersonday[i]

        res = {
            "Monday" : dayarray[0],
            "Tuesday" : dayarray[1],
            "Wednesday" : dayarray[2],
            "Thursday" : dayarray[3],
            "Friday" : dayarray[4],
            "Saturday" : dayarray[5],
            "Sunday" : dayarray[6]
        }
        return jsonify(res), 200
        

@farm_bp.route('/farm/request/', methods=['POST'])
def addRequest():
    # if not request.form or not 'userid' in request.form:
    #     abort(400)
    # else:
    try:
        data = json.loads(request.get_data(as_text=True))
        user = User.query.filter(User.id == data['userId']).first()
        userlocation = str(user.latitude) + "," + str(user.longitude)
        requstList = Request.query.all()
        nb = Request.query.count()
        requestid = int(requstList[nb-1].id) + 1
        desttime = ''

        for time in data['deliveryTime']:
            desttime = desttime + time['day'] + " " + time['time'] + ";"

        volunteertime = ''
        if int(data['volunteer']['do']) == 1:
            for time in data['volunteer']['timelist']:
                volunteertime = volunteertime + time['day'] + " " + time['time'] + ";"
        requestorderid = 0

        existingorder = Order.query.filter(and_(Order.ownerid == data['farmOwnerId'], Order.description == "")).first()
        if not existingorder:
            orderid = Order.query.count()
            farm = Farm.query.filter(Farm.userid == data['farmOwnerId']).first()
            neworder = Order(int(orderid),
                             int(data['farmOwnerId']),
                             str(farm.latitude) + "," + str(farm.longitude),
                             "",
                             "",
                             "",
                             0,
                             "",
                             0,
                             0,
                             "",
                             "")
            db.session.add(neworder)
            requestorderid = orderid
        else:
            requestorderid = existingorder.id

        description = ''
        carbon = 0
        for item in data['cart']:
            description = description + item['productName'] + "_" + str(item['amount']) + ";"
            product = Product.query.filter(Product.name == item['productName']).first()
            carbon += int(product.carbonredu) * int(item['amount'])
            nbr = int(product.quantity) - int(item['amount'])
            db.session.query(Product).filter(Product.name == item['productName']).update({
                "quantity" : nbr if nbr > 0 else 0
            })

            db.session.commit()
        actual = carbon + user.carbonactual
        if (actual >= 100):
            actual = actual - 100
            count = Coupon.query.count()
            coupon = Coupon(int(count), int(user.id), 5)
            db.session.add(coupon)
        db.session.query(User).filter(User.id == user.id).update({
            "carbonactual" : int(actual),
            "carbontotal" : int(carbon) + int (user.carbontotal)
        })
        db.session.commit()
        db.session.add(Request(int(requestid),
                             int(requestorderid),
                             int(data['userId']),
                             userlocation,
                             desttime,
                             volunteertime,
                             description,
                             float(data['totalPrice'])
                             ))
        oldorder = Order.query.filter(Order.ownerid == data['farmOwnerId']).first()
        db.session.query(Order).filter(Order.ownerid == data['farmOwnerId']).update(
            {"requestlist": oldorder.requestlist + str(requestid) + ","})
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.get_data(as_text=True)), 201
