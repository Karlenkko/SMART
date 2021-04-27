from exts import db, migrate
from model import User, FarmOrder, Farm, SingleOrder, Coupon, Product
def dataInit():
    db.create_all()

    db.session.commit()

# def userInit():
#     farm1 = User()