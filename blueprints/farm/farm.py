from flask import Blueprint
from flask import abort, request, jsonify
from model import Product

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
