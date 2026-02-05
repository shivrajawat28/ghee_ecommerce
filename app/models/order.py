from app import db
from sqlalchemy import Numeric
from datetime import datetime

class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)

    total_amount = db.Column(Numeric(10, 2), nullable = False)
    status = db.Column(db.String(20), default = "pending")
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    full_name = db.Column(db.String(200), nullable = False)
    phone = db.Column(db.String(20), nullable = False)
    address = db.Column(db.String(500), nullable = False)
    city = db.Column(db.String(100), nullable = False)
    state = db.Column(db.String(200), nullable = False)
    pincode = db.Column(db.String(12), nullable = False)

    payment_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default = "pending")
    payment_method = db.Column(db.String(50))
    paid_at = db.Column(db.DateTime)
    razorpay_order_id = db.Column(db.String(200))
    razorpay_payment_id = db.Column(db.String(200))
    razorpay_signature = db.Column(db.String(200))


    user = db.relationship("User", backref="orders")
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete")

class OrderItem(db.Model):
    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable = False)

    price = db.Column(Numeric(10, 2), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)

    product = db.relationship("Product")
