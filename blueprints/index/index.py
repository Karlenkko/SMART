from flask import Blueprint
from model import Farm, Product
from flask import abort, request, jsonify
import json

index_bp = Blueprint('index', __name__)


@index_bp.route('/index/getAllFarmOrders/', methods=['GET'])
def getAllFarmOrders():
    return 'Get All Farm Orders'


@index_bp.route('/index/getAllUserOrders/', methods=['GET'])
def getAllUserOrders():
    return 'Get All User Orders'


@index_bp.route('/index/getAllFarms/', methods=['GET'])
def getAllFarms():
    farms = Farm.query.all()
    products = Product.query.all()
    productLists = []
    temp = 0
    farmid = 0
    productLists.append("")
    for product in products:
        if product.farmid == farmid:
            if temp < 4:
                productLists[farmid] += product.name + ","
                temp = temp + 1
            else:
                productLists.append("")
                farmid = farmid + 1
                temp = 0
    res = []
    for farm in farms:
        res.append({
            "farmId": farm.id,
            "farmName": farm.name,
            "location": {
                "longitude": farm.longitude,
                "latitude": farm.latitude
            },
            "url": farm.photourl,
            "productList": productLists[farm.id]
        })
    return jsonify(res), 200
