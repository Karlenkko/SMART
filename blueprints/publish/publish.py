from flask import Blueprint
from flask import abort, request, jsonify

publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/getUserPublishContent/', methods=['GET'])
def getUserPublishContent():
    return 'get user publish content'


@publish_bp.route('/publish/getFarmPublishContent/', methods=['GET'])
def getFarmPublishContent():
    return 'get farm publish content'


@publish_bp.route('/publish/getFarmDeliveryRoute/', methods=['GET'])
def getFarmDeliveryRoute():
    return 'get farm delivery route'


@publish_bp.route('/publish/getUserPublishCandidates/', methods=['GET'])
def getUserPublishCandidates():
    if not request.args or not 'userPublishId' in request.args:
        abort(400)
    else:
        return 'get user publish candidates'


@publish_bp.route('/publish/postUserPublishContent/', methods=['POST'])
def postUserPublishContent():
    if not request.form or not 'offerName' in request.form:
        abort(400)
    else:
        try:
            print(request.form)
        except:
            abort(500)
        else:
            return jsonify(request.form), 201


@publish_bp.route('/publish/postFarmPublishContent/', methods=['POST'])
def postFarmPublishContent():
    if not request.form or not 'articleName' in request.form:
        abort(400)
    else:
        try:
            print(request.form)
        except:
            abort(500)
        else:
            return jsonify(request.form), 201


@publish_bp.route('/publish/assignCandidate/', methods=['PUT'])
def assignCandidate():
    if not request.args or not 'candidateId' in request.args:
        abort(400)
    else:
        return 'assign candidate'


@publish_bp.route('/publish/validateDelivery/', methods=['PUT'])
def validateDelivery():
    if not request.args or not 'deliveryId' in request.args:
        abort(400)
    else:
        return 'validate delivery'


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