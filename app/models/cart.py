from app import db
from datetime import datetime


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow)

    items = db.relationship("CartItem", backref = "cart", lazy = True, cascade = "all, delete")
    
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    __table_args__ = (
        db.UniqueConstraint("cart_id", "product_id", name="uix_cart_product"),
        db.CheckConstraint("quantity > 0", name="ck_cartitem_qty"),
    )

    id = db.Column(db.Integer, primary_key = True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable = False)
    quantity = db.Column(db.Integer, default = 1)

    product = db.relationship("Product")
