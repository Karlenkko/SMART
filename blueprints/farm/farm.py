from flask import Blueprint
from flask import abort, request, jsonify
from model import Product, Request, User
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
                "idProduct" : product.id,
                "productName" : product.name,
                "quantity" : product.quantity,
                "price" : product.price,
                "url" : product.photourl,
                "category" : product.category,
                "carbonRedu" : product.carbonredu,
                "origin" : product.origincarrefour,
                "carrefourPrice" : product.pricecarrefour
            })

    return jsonify(res), 200


@farm_bp.route('/farm/request/', methods=['POST'])
def addRequest():
    if not request.form or not 'userid' in request.form:
        abort(400)
    else:
        try:
            user = User.query.filter(User.id == request.form.get('userid', type=int)).first()
            userlocation = str(user.longitude) + "," + str(user.latitude)
            requestid = Request.query.count()
            newRequest = Request(requestid, request.form.get('orderid', type=int), request.form.get('userid', type=int), userlocation, request.form.get('destTime'), request.form.get('volunteerTime'), request.form.get('description'), request.form.get('totalPrice', type=float))
            db.session.add(newRequest)
            db.session.commit()
        except:
            abort(500)
        else:
            return jsonify(request.form), 201
