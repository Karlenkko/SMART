from flask import Blueprint
from flask import abort, request, jsonify

farm_bp = Blueprint('farm', __name__)


@farm_bp.route('/farm/getAllProducts/', methods=['GET'])
def getAllProducts():
    if not request.args or not 'farmId' in request.args:
        abort(400)
    else:
        print(request.args.get('farmId'))
    return 'Get All Products of' + request.args.get('farmId')


@farm_bp.route('/farm/order/', methods=['POST'])
def addOrder():
    if not request.form or not 'name' in request.form:
        abort(400)
    else:
        try:
            print(request)
        except:
            abort(500)
        else:
            return jsonify(request.form), 201
