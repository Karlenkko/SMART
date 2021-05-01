from flask import Blueprint
from flask import abort, request, jsonify
from model import User
from exts import db

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
