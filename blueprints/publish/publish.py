import json

from flask import Blueprint
from flask import abort, request, jsonify
from model import Order, User, Farm, Request, Product
from exts import db
import pandas as pd
import numpy as np
from random import randint 

publish_bp = Blueprint('publish', __name__)

legume = pd.read_csv("dataset/legume.csv").to_numpy().tolist()
fruit = pd.read_csv("dataset/fruit.csv").to_numpy().tolist()
other = pd.read_csv("dataset/other.csv").to_numpy().tolist()
originList = ['FRANCE', 'ESPAGNE', 'PEROU', 'UE', 'MOZAMBIQUE', 'ORIGINEPAYSTIERS', 'COLOMBIE', 'nan', 'COSTARICA', 'VIETNAM', 'AFRIQUEDUSUD', 'PORTUGAL', 'ITALIE', 'ARGENTINE', 'ISRAEL', 'CHINE', 'MAROC']
originCarbonList = [50, 300, 20000, 400, 2000, 1000, 20000, 50, 20000, 25000, 10000, 400, 250, 23000, 7500, 25000, 1000]



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
                    "requestId": req.id,
                    "state": order.state,
                    "pickUpTime": dictifyDate(req.timeproposed),
                    "description": order.description,
                    "photourl": user.photourl
                })
            else:
                farmRequests.append({
                    "requestId": req.id,
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
                if order.selectedperson:
                    selectedId = int(order.selectedperson)
                    selectedUser = User.query.filter(User.id == selectedId).first()
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
        farm = Farm.query.filter(Farm.userid == request.args.get('userId')).first()
        res = []
        order = Order.query.filter(Order.ownerid == farm.userid).first()
        if(farm):
            products = Product.query.filter(Product.farmid == farm.id)
            articles = []
            for product in products:
                articles.append({
                    "articleId": product.id,
                    "name": product.name,
                    "price": product.price,
                    "remainedQuantity": product.quantity
                })
            temp = ""
            if (not order == None) and (not order.id == None):
                temp = order.id
            res.append({
                "orderId": temp,
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
                         "",
                         "")
        db.session.add(newOrder)
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.form), 201

def isNaN(string):
    return string != string


def getProduct(productName):

    res = {
        "category" : "",
        "photourl" : "",
        "origin"   : "",
        "price"    : 0,
        "carbon"   : 0
    }
    print("-------------product--------------")
    print(productName)
    print(legume[0][0])
    for i in range(len(legume)):
        if productName in legume[i][0]:
            res["category"] = "legume"
            res["origin"] = "FRANCE" if isNaN(legume[i][1]) else legume[i][1]
            print("----------entering-----------")
            res["price"] = float(legume[i][2].strip("€"))
            print("----------entering-----------")
            res["photourl"] = legume[i][3]
            print("----------entering-----------")
            print(res["origin"])
            print(originList.index(res["origin"]))
            print(originCarbonList[originList.index(res["origin"])])
            res["carbon"] = int(originCarbonList[originList.index(res["origin"])]*randint(80,100)/100)
            print("----------entering-----------")
            return res

    for i in range(len(fruit)):
        if productName in fruit[i][0]:
            res["category"] = "fruit"
            res["origin"] = "FRANCE" if isNaN(fruit[i][1]) else fruit[i][1]
            res["price"] = float(fruit[i][2].strip("€"))
            res["photourl"] = fruit[i][3]
            res["carbon"] = int(originCarbonList[originList.index(res["origin"])]*randint(80,100)/100)

            return res

    for i in range(len(other)):
        if productName in other[i][0]:
            res["category"] = "other"
            res["origin"] = "FRANCE" if isNaN(other[i][1]) else other[i][1]
            res["price"] = float(other[i][2].strip("€"))
            res["photourl"] = other[i][3]
            res["carbon"] = int(originCarbonList[originList.index(res["origin"])]*randint(80,100)/100)

            return res

    return res


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
        for product in productsDelete:
            db.session.delete(product)
        productList = Product.query.all()
        productLength = Product.query.count()
        lastProductId = productList[productLength-1].id
        for article in articleList:
            productName = article["name"]
            res = getProduct(productName)

            lastProductId += 1

            print("--------------article-------------")
            print(res)
            print("--------------article-------------")

            newProduct = Product(
                lastProductId,
                farmId,
                article["name"],
                article["price"],
                article["quantity"],
                res["category"],
                res["photourl"],
                res["origin"],
                res["price"],
                res["carbon"]
            )

            

            db.session.add(newProduct)
        db.session.commit()
    except:
        abort(500)
    else:
        return jsonify(request.form), 201


@publish_bp.route('/publish/assignCandidate/', methods=['PUT'])
def assignCandidate():
    if not request.args or not 'orderId' in request.args:
        abort(400)
    else:
        oldorder = Order.query.filter(Order.id == request.args.get('orderId', type=int)).first()
        db.session.query(Order).filter(
            Order.id == request.args.get('orderId', type=int)
        ).update({"selectedperson": request.args.get('candidateId'), "state": 1})
        db.session.commit()
        db.session.close()
        return jsonify(request.args), 200


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
