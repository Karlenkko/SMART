from flask import Blueprint
from flask import abort, request, jsonify
from model import User, Order, Request, Volunteer, Coupon
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
        print(order)
        req = Request.query.filter(and_(Request.orderid == request.args.get('orderId'), Request.userid == request.args.get('userId'))).first()
        print(req)
        cl = ""
        if not order.confirmlist == None:
            cl = str(order.confirmlist)
        db.session.query(Order).filter(Order.id == request.args.get('orderId')).update({
            "confirmlist": cl + str(req.id) + ","
        })
        db.session.commit()
        newOrder = Order.query.filter(Order.id == request.args.get('orderId')).first()
        if str(newOrder.requestlist) == str(newOrder.confirmlist):
            db.session.query(Order).filter(Order.id == request.args.get('orderId')).update({"state" : 10})
            db.session.query(Volunteer).filter(Volunteer.orderid == request.args.get('orderId')).update({"accept" : 10})
            db.session.commit()
            volunteers = Volunteer.query.filter(Volunteer.orderid == request.args.get('orderId')).all()
            for vol in volunteers:
                user = User.query.filter(User.id == vol.userid).first()
                actual = 0
                if user.volunteeractual >= 96:
                    actual = int(user.volunteeractual) + 4 - 100
                    count = Coupon.query.count()
                    coupon = Coupon(int(count), int(user.id), 5)
                    db.session.add(coupon)
                else:
                    actual = int(user.volunteeractual) + 4
                db.session.query(User).filter(User.id == vol.userid).update({
                    "volunteertotal" : int(user.volunteertotal) + 4,
                    "volunteeractual" : actual
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