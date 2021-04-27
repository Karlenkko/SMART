from flask import Blueprint
from model import Farm
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
    list = Farm.query.all()
    return str(list), 200
