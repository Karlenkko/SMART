from flask import Flask, render_template, request
from exts import db, migrate
from flask_cors import CORS
from model import User, Request, Farm, Order, Coupon, Product
import config
import pymysql
from blueprints.index.index import index_bp
from blueprints.farm.farm import farm_bp
from blueprints.publish.publish import publish_bp
from blueprints.algo.algo import algo_bp
from datainit import init

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

# print a nice greeting.
def say_hello(username="World"):
    return '<p>Hello %s!</p>\n' % username


# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)
cors = CORS()
cors.init_app(app=application, resources={r"/*": {"origins": "*"}})

application.config['GOOGLEMAPS_KEY'] = "AIzaSyA3mWjEnNcNoGtTWDYvNzZFPzuhjGv1H48" 
GoogleMaps(application)

application.config.from_object(config)
# pymysql.connect(host=config.HOST, port=int(config.PORT), user=config.USERNAME, passwd=config.PASSWORD, db=config.DATABASE)
db.init_app(application)
migrate.init_app(application, db)
# add a rule for the index page.
# application.add_url_rule('/', 'index', (lambda: header_text +
#                                                 say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<username>', 'hello', (lambda username:
                                                  header_text + say_hello(username) + home_link + footer_text))

application.register_blueprint(index_bp)
application.register_blueprint(farm_bp)
application.register_blueprint(publish_bp)
application.register_blueprint(algo_bp)
# @application.before_first_request
# def setup():
#     init()

@application.route("/map/", methods=['GET'])
def map():
    return render_template("map.html")


@application.route("/", methods=['GET'])
def index():
    return application.send_static_file('index.html')
    # return render_template("index.html")
@application.route("/login/", methods=["GET"])
def login():
    return application.send_static_file('login.html')
@application.route("/farm/", methods=["GET"])
def farm():
    return application.send_static_file('farm.html')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # application.debug = True

    application.run()

