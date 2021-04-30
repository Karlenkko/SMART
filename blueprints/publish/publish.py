import json

from flask import Blueprint
from flask import abort, request, jsonify
from model import Order, User, Farm, Request
from exts import db

publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/getUserOrderContent/', methods=['GET'])
def getUserPublishContent():
    if not request.args or not 'ownerId' in request.args:
        abort(400)
    else:
        orders = Order.query.filter(Order.ownerid == request.args.get('ownerId'))
        res = []
        for order in orders:
            requestlist = Request.query.filter(Request.orderid == order.id)
            reqs = []
            for onerequest in requestlist:
                user = User.query.filter(User.id == onerequest.userid).first()
                reqs.append({
                    "userId" : onerequest.userid,
                    "userName" : user.name,
                    "userTel" : user.mobile,
                    "userDescription" : onerequest.description,
                    "userProposeTime" : onerequest.timeproposed,
                    "volunteerTime" : onerequest.volunteertime
                })
            res.append({
                "dateString": order.time,
                "price" : order.price,
                "state" : order.state,
                "description" : order.description,
                "entrepotlist" : order.entrepotlist,
                "selectedperson" : order.selectedperson,
                "candidates" : reqs
            })
        return jsonify(res), 200


@publish_bp.route('/publish/getFarmOrderContent/', methods=['GET'])
def getFarmPublishContent():
    if not request.args or not 'ownerId' in request.args:
        abort(400)
    else:
        return 'get farm publish content'


@publish_bp.route('/publish/getFarmDeliveryRoute/', methods=['GET'])
def getFarmDeliveryRoute():
    if not request.args or not 'orderId' in request.args:
        abort(400)
    else:
        order = Order.query.filter(Order.id == request.args.get('orderId')).first()
        res = []
        points = order.entrepotlist.split(';')
        for point in points:
            coord = point.split(',')
            res.append({
                "longitude": coord[0],
                "latitude": coord[1]
            })
        return jsonify(res), 200


@publish_bp.route('/publish/getUserOrderCandidates/', methods=['GET'])
def getUserPublishCandidates():
    if not request.args or not 'orderId' in request.args:
        abort(400)
    else:
        order = Order.query.filter(Order.id == request.args.get('orderId')).first()
        requestlist = order.requestlist
        if len(requestlist) > 0:
            requestlist = requestlist.split(',')
            requestlist.pop()
        orderrequests = Request.query.filter(Request.id.in_(requestlist)).all()
        useridlist = []
        for orderrequest in orderrequests:
            if len(orderrequest.volunteertime) > 0:
                useridlist.append(orderrequest.userid)

        users = User.query.filter(User.id.in_(useridlist)).all()
        res = []
        for i in range(0, len(users)):
            res.append({
                "userId": users[i].id,
                "candidateName": users[i].name,
                "phoneNumber": users[i].mobile
            })
        return jsonify(res), 200


@publish_bp.route('/publish/postUserOrderContent/', methods=['POST'])
def postUserPublishContent():
    # if not request.form or not 'userId' in request.form:
    #     abort(400)
    # else:
    try:
        data = json.loads(request.get_data(as_text=True))
        orderid = Order.query.count()
        newOrder = Order(orderid,
                         data['userId'],
                         data['entrepotlist'],
                         data['description'],
                         "",
                         "",
                         0,
                         data['time'])
        db.session.add(newOrder)
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.form), 201


@publish_bp.route('/publish/postFarmOrderContent/', methods=['POST'])
def postFarmPublishContent():
    # if not request.form or not 'userId' in request.form:
    #     abort(400)
    # else:
    try:
        data = json.loads(request.get_data(as_text=True))
        orderid = Order.query.count()
        farm = Farm.query.filter(Farm.userid == data['userId'])
        farmPos = str(farm.longitude) + "," + str(farm.latitude)
        newOrder = Order(orderid,
                         data['userId'],
                         farmPos,
                         "",
                         "",
                         "",
                         0,
                         ""
                         )
        db.session.add(newOrder)
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.form), 201


@publish_bp.route('/publish/assignCandidate/', methods=['PUT'])
def assignCandidate():
    if not request.args or not 'orderId' in request.form:
        abort(400)
    else:
        oldorder = Order.query.filter(Order.id == request.form.get('orderId', type=int)).first()
        db.session.query(Order).filter(
            Order.id == request.form.get('orderId', type=int)
        ).update({"selectedperson": oldorder.selectedperson + request.form.get('candidateId') + ","})
        db.session.commit()
        db.session.close()
        return jsonify(request.form), 200


@publish_bp.route('/publish/validateDelivery/', methods=['PUT'])
def validateDelivery():
    if not request.args or not 'orderId' in request.args:
        abort(400)
    else:
        oldorder = Order.query.filter(Order.id == request.form.get('orderId', type=int)).first()
        db.session.query(Order).filter(
            Order.id == request.form.get('orderId', type=int)
        ).update({"state": int(oldorder.state) + 1})
        db.session.commit()
        db.session.close()
        return jsonify(request.form), 200


@publish_bp.route('/publish/deleteUserPublishContent', methods=['DELETE'])
def deleteUserPublishContent():
    if not request.args or not 'userPublishId' in request.args:
        abort(400)
    else:
        return 'delete user publish content'


@publish_bp.route('/publish/deleteFarmPublishContent/', methods=['DELETE'])
def deleteFarmPublishContent():
    if not request.args or not 'farmPublishId' in request.args:
        abort(400)
    else:
        return 'delete user publish content'
