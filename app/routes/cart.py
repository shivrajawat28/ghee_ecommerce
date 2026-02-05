from flask import Blueprint, session, redirect, render_template, url_for, flash, request
from app.models.cart import Cart, CartItem
from app import db
from app.models.product import Product

cart_bp = Blueprint("cart", __name__)

#login check
def login_required():
    return session.get("user_id")

#add to cart
@cart_bp.route("/cart/add/<int:product_id>", methods= ['POST'])
def add_cart(product_id):
    user_id = login_required()
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)

    if not product.is_active or product.stock <= 0:
        flash("Product not available", "danger")
        return redirect(url_for("product.product_detail", id = product_id))

    
    #get or create cart
    cart = Cart.query.filter_by(user_id = user_id).first()
    if not cart:
        cart = Cart(user_id = user_id)
        db.session.add(cart)
        db.session.commit()

    #checking if item is already cart
    item = CartItem.query.filter_by(cart_id = cart.id, product_id = product.id).first()

    if item:
        if item.quantity + 1 > product.stock:
            flash("Not enough stock available", "warning")
            return redirect(url_for("cart.view_cart"))
        item.quantity += 1
    else:
        item = CartItem(cart_id = cart.id, product_id = product.id, quantity = 1)
        db.session.add(item)

    db.session.commit()

    return redirect(url_for("cart.view_cart"))


#buy now
@cart_bp.route("/buy/<int:product_id>", methods= ['POST'])
def buy_now(product_id):
    user_id = login_required()
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(product_id)

    if not product.is_active or product.stock <= 0:
        flash("Product not available", "danger")
        return redirect(url_for("product.product_detail", id = product_id))

    cart = Cart.query.filter_by(user_id = user_id).first()
    if not cart:
        cart = Cart(user_id = user_id)
        db.session.add(cart)
        db.session.commit()

    item = CartItem.query.filter_by(cart_id = cart.id, product_id = product.id).first()

    if item:
        if item.quantity + 1 > product.stock:
            flash("Not enough stock available", "warning")
            return redirect(url_for("cart.view_cart"))
        item.quantity += 1
    else:
        item = CartItem(cart_id = cart.id, product_id = product.id, quantity = 1)
        db.session.add(item)

    db.session.commit()

    return redirect(url_for("order.checkout"))


#view cart
@cart_bp.route("/cart")
def view_cart():
    user_id = login_required()
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    cart = Cart.query.filter_by(user_id = user_id).first()

    if not cart:
        return render_template("cart.html", items = [], total = 0)

    items = cart.items
    
    total = 0
    for item in items:
        total += float(item.product.price) * item.quantity

    return render_template("cart.html", items = items, total = total)

#update quantity
@cart_bp.route("/cart/update/<int:item_id>", methods = ['POST'])
def update_quantity(item_id):
    user_id = login_required()
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    item = CartItem.query.get_or_404(item_id)

    if item.cart.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("cart.view_cart"))

    try:
        new_qty = int(request.form.get("quantity", 1))
    except ValueError:
        flash("Invalid quantity", "danger")
        return redirect(url_for("cart.view_cart"))

    if new_qty > item.product.stock:
        flash("Not enough stock available", "warning")
        return redirect(url_for("cart.view_cart"))

    if new_qty <= 0 :
        db.session.delete(item)

    else:
        item.quantity = new_qty

    db.session.commit()

    return redirect(url_for("cart.view_cart"))


#remove item
@cart_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    user_id = login_required()
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    item = CartItem.query.get_or_404(item_id)

    if item.cart.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("cart.view_cart"))

    db.session.delete(item)
    db.session.commit()

    flash("Item removed", "success")
    return redirect(url_for("cart.view_cart"))
    
