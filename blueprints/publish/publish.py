import json

from flask import Blueprint
from flask import abort, request, jsonify
from model import Order, User, Farm, Request, Product
from exts import db

publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/getRequests/', methods=['GET'])
def getRequests():
    def dictifyDate(str):
        resDate = []
        dateList = str.split(';')
        dateList.pop()
        for date in dateList:
            pair = date.split(' ');
            resDate.append({
                "day": pair[0],
                "time": pair[1]
            })
        return resDate

    def dictifyArticles(str):
        resAticles = []
        articleList = str.split(';')
        articleList.pop()
        for article in articleList:
            pair = article.split('_');
            resAticles.append({
                "name": pair[0],
                "orderedQuantity": pair[1]})
        return resAticles

    if not request.args or not 'userId' in request.args:
        abort(400)
    else:
        requestList = Request.query.filter(Request.userid == request.args.get('userId'))
        clientRequests = []
        farmRequests = []
        res = {}
        for req in requestList:
            orderList = Order.query.filter(Order.id == req.orderid)
            order = orderList[0]
            user = User.query.filter(User.id == order.ownerid).first()
            if order.description:
                clientRequests.append({
                    "resquestId": req.id,
                    "state": order.state,
                    "pickUpTime": dictifyDate(req.timeproposed),
                    "description": order.description,
                    "photourl": user.photourl
                })
            else:
                farmRequests.append({
                    "resquestId": req.id,
                    "state": order.state,
                    "pickUpTime": dictifyDate(req.timeproposed),
                    "volunteerTime": dictifyDate(req.volunteertime),
                    "articles": dictifyArticles(req.description),
                })
            res = {
                "clientRequests": clientRequests,
                "farmRequests": farmRequests
            }
        return jsonify(res), 200

@publish_bp.route('/publish/getUserOrderContent/', methods=['GET'])
def getUserPublishContent():
    if not request.args or not 'ownerId' in request.args:
        abort(400)
    else:
        userLogin = User.query.filter(User.id == request.args.get('ownerId')).first()
        orders = Order.query.filter(Order.ownerid == request.args.get('ownerId'))
        res = []
        for order in orders:
            if order.description != "":
                requestlist = Request.query.filter(Request.orderid == order.id)
                selectedPersons = []
                if selectedPersons:
                    selectedIdList = order.selectedperson.split(';')
                    selectedIdList.pop()
                    for selectedId in selectedIdList:
                        selectedUser = User.query.filter(User.id == selectedId)
                        if(selectedUser):
                            selectedUserInfo = {
                                "userId" : selectedUser.id,
                                "userName": selectedUser.name,
                                "userMobile": selectedUser.mobile
                            }
                            selectedPersons.append(selectedUserInfo)
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
                    "orderId" : order.id,
                    "dateString": order.time,
                    "price" : order.price,
                    "state" : order.state,
                    "description" : order.description,
                    "entrepotlist" : order.entrepotlist,
                    "selectedpersons" : selectedPersons,
                    "photourl": userLogin.photourl,
                    "candidates" : reqs
                })
        return jsonify(res), 200


@publish_bp.route('/publish/getFarmOrderContent/', methods=['GET'])
def getFarmPublishContent():
    if not request.args or not 'userId' in request.args:
        abort(400)
    else:
        farmList = Farm.query.filter(Farm.userid == request.args.get('userId'))
        res = []
        if(farmList):
            farm = farmList[0]
            products = Product.query.filter(Product.farmid == farm.id)
            articles = []
            for product in products:
                articles.append({
                    "articleId": product.id,
                    "name": product.name,
                    "price": product.price,
                    "remainedQuantity": product.quantity
                })
            res.append({
                "offerId": farm.id,
                "name": farm.name,
                "state": 0,
                "articles": articles
            })
    return jsonify(res), 200


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
    #if not request.args or not 'userId' in request.args:
    #    abort(400)
    #else:
    try:
        data = json.loads(request.get_data(as_text=True))
        orderid = Order.query.count()
        newOrder = Order(orderid,
                         request.args.get('userId'),
                         "",
                         data['description'],
                         "",
                         "",
                         0,
                         data['timeProposed'],
                         data['price'],
                         "",
                         "")
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
        articleList = data["articles"]
        farmId = Farm.query.filter(Farm.userid == request.args.get('userId'))[0].id
        productsDelete = Product.query.filter(Product.farmid == farmId).all()
        print("productsDelete")
        print(productsDelete)
        print("fin du produit")
        for product in productsDelete:
            db.session.delete(product)
        productList = Product.query.all()
        productLength = Product.query.count()
        lastProductId = productList[productLength-1].id
        print("lastProductId")
        print(lastProductId)
        for article in articleList:
            lastProductId += 1
            newProduct = Product(
                lastProductId,
                farmId,
                article["name"],
                article["price"],
                article["quantity"],
                "",
                "",
                "",
                0
            )
            db.session.add(newProduct)
        db.session.commit()
        print("done")
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
        ).update({"selectedperson": request.form.get('candidateId')})
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
