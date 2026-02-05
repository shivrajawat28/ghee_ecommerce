from datetime import datetime

from app import db
from sqlalchemy import Numeric

class Product(db.Model):
    __tablename__ = "product"


    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    price = db.Column(Numeric(10, 2), nullable = False)
    description = db.Column(db.String(1000))
    stock = db.Column(db.Integer, default = 0)
    is_active = db.Column(db.Boolean, default = True)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    #relationship
    images = db.relationship("ProductImage", backref= "product", lazy = True, cascade="all, delete")



class ProductImage(db.Model):
    __tablename__ = "product_image"

    id = db.Column(db.Integer, primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable = False)
    image_path = db.Column(db.String(255), nullable = False)
