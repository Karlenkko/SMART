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
            desttime = ''
            for time in request.form.get('deliveryTime'):
                desttime = desttime + time.day + " " + time.time + ";"

            volunteertime = ''
            for time in request.form.get('volunteerTime'):
                volunteertime = volunteertime + time.day + " " + time.time + ";"
            requestorderid = 0
            existingorder = Order.query.filter(Order.ownerid == request.form.get('farmOwnerId', type=int)).first()
            if not existingorder:
                orderid = Order.query.count()
                farm = Farm.query.filter(Farm.userid == request.form.get('farmOwnerId')).first()
                neworder = Order(orderid,
                                 request.form.get('farmOwnerId', type=int),
                                 str(farm.longitude) + "," + str(farm.latitude),
                                 "",
                                 "",
                                 "",
                                 0,
                                 "",
                                 0)
                db.session.add(neworder)
                db.commit()
                requestorderid = orderid
            else:
                requestorderid = existingorder.id

            newRequest = Request(requestid,
                                 requestorderid,
                                 request.form.get('userid', type=int),
                                 userlocation,
                                 desttime,
                                 volunteertime,
                                 request.form.get('description'),
                                 request.form.get('totalPrice', type=float))
            db.session.add(newRequest)
            oldorder = Order.query.filter(Order.ownerid == request.form.get('farmOwnerId', type=int)).first()
            db.session.query(Order).filter(Order.ownerid == request.form.get('farmOwnerId', type=int)).update({"requestlist" : oldorder.requestlist + str(requestid) + ","})
            db.session.commit()
        except:
            abort(500)
        else:
            return jsonify(request.form), 201
