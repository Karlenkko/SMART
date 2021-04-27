from flask import Blueprint

publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/getUserPublishContent/', methods=['GET'])
def getUserPublishContent():
    return 'get user publish content'


@publish_bp.route('/publish/getFarmPublishContent', methods=['GET'])
def getFarmPublishContent():
    return 'get farm publish content'


@publish_bp.route('/publish/getFarmDeliveryRoute', methods=['GET'])
def getFarmDeliveryRoute():
    return 'get farm delivery route'


@publish_bp.route('/publish/getUserPublishCandidates/', methods=['GET'])
def getUserPublishCandidates():
    return 'get user publish candidates'
