from flask import Blueprint
from flask import abort, request, jsonify
from model import User, Order, Request, Volunteer
from exts import db
from sqlalchemy import and_
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/login', methods=['GET'])
def login():
    if not request.args or not 'userName' in request.args or not 'passwd' in request.args:
        abort(400)
    else:
        user = User.query.filter(User.name == request.args.get('userName')).first()
        if not user:
            res = {
                "loggedin" : "false",
                "msg" : 'no such user'
            }
            return jsonify(res), 200
        else:
            if not str(user.passwd) == str(request.args.get('passwd')):
                res = {
                    "loggedin": "false",
                    "msg": 'wrong passwd'
                }
                return jsonify(res), 200
            else:
                res = {
                    "loggedin" : "true",
                    "userId" : user.id,
                    "userName" : user.name,
                    "userMobile" : user.mobile,
                    "userType" : user.type,
                    "userPhotoUrl" : user.photourl,
                    "balance" : user.balance,
                    "carbonTotal" : user.carbontotal,
                    "carbonActual" : user.carbonactual,
                    "volunteerTotal" : user.volunteertotal,
                    "volunteerActual" : user.volunteeractual
                }
                return jsonify(res), 200

@user_bp.route('/user/confirmRequest/', methods=['PUT'])
def confirmRequest():
    if not request.args or not 'orderId' in request.args or not 'userId' in request.args:
        abort(400)
    else:
        order = Order.query.filter(Order.id == request.args.get('orderId')).first()
        req = Request.query.filter(and_(Request.orderid == request.args.get('orderId'), Request.userid == request.args.get('userId'))).first()
        db.session.query(Order).filter(Order.id == request.args.get('orderId')).update({
            "confirmlist": order.confirmlist + str(req.id) + ","
        })
        db.session.commit()
        return 'confirmed', 201

@user_bp.route('/user/getMyRequests/', methods=['GET'])
def getMyRequests():
    if not request.args or not 'userId' in request.args:
        abort(400)
    else:
        requestList = Request.query.filter(Request.userid == request.args.get('userId'))

        res = []
        for req in requestList:
            order = Order.query.filter(Order.id == req.orderid)

        return 'under construction', 200

@user_bp.route('/user/getMyVolunteers/', methods=['GET'])
def getMyVolunteers():
    if not request.args or not 'userId' in request.args:
        abort(400)
    else:
        volunteers = Volunteer.query.filter(Volunteer.userid == request.args.get('userId'))
        res = []
        for volunteer in volunteers:
            points = volunteer.entrepotlist.split(";")
            requests = volunteer.requestlist.split(",")
            requests.pop()
            localUsers = []
            for req in requests:
                onereq = Request.query.filter(Request.id == req.id).first()
                user = User.query.filter(User.id == onereq.userid).first()
                localUsers.append({
                    "userName" : user.name,
                    "userTel" : user.mobile,
                    "userTimes" : onereq.timeproposed,
                    "userItems" : onereq.description
                })

            res.append({
                "date" : volunteer.date,
                "centroid" : points[1],
                "users" : localUsers
            })
        return jsonify(res), 200