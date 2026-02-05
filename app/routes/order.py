from flask import Blueprint, session, redirect, render_template, flash, url_for, request
from app.models.order import Order, OrderItem
from app import db
from app.models.cart import Cart
from decimal import Decimal

order_bp = Blueprint("order", __name__)

#checkout route
@order_bp.route("/checkout")
def checkout():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    cart = Cart.query.filter_by(user_id = user_id).first()

    if not cart or not cart.items:
        flash("Your cart is empty", "warning")
        return redirect(url_for("cart.view_cart"))

    total = Decimal("0.00")
    for item in cart.items:
        total += Decimal(str(item.product.price)) * item.quantity
    
    return render_template("checkout.html", total = total, cart = cart)

#place order
@order_bp.route("/checkout", methods=['POST'])
def place_order():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        flash("Your cart is empty", "warning")
        return redirect(url_for("cart.view_cart"))

    # STOCK CHECK FIRST
    for item in cart.items:
        if item.product.stock < item.quantity:
            flash(f"Not enough stock for {item.product.title}", "danger")
            return redirect(url_for("cart.view_cart"))

    total = Decimal("0.00")
    for item in cart.items:
        total += Decimal(str(item.product.price)) * item.quantity

    try:
        # basic validation
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        address = (request.form.get("address") or "").strip()
        city = (request.form.get("city") or "").strip()
        state = (request.form.get("state") or "").strip()
        pincode = (request.form.get("pincode") or "").strip()

        if not all([full_name, phone, address, city, state, pincode]):
            flash("All fields are required", "danger")
            return redirect(url_for("order.checkout"))

        if not phone.isdigit():
            flash("Phone must be numeric", "danger")
            return redirect(url_for("order.checkout"))
        if not pincode.isdigit():
            flash("Pincode must be numeric", "danger")
            return redirect(url_for("order.checkout"))

        order = Order(
            user_id=user_id,
            total_amount=total,
            status="pending",
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode
        )

        db.session.add(order)
        db.session.flush()

        for item in cart.items:
            product = item.product
            if product.stock < item.quantity:
                raise ValueError(f"Not enough stock for {product.title}")

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                price=product.price,
                quantity=item.quantity
            )
            db.session.add(order_item)

        db.session.commit()

    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
        return redirect(url_for("cart.view_cart"))
    except Exception:
        db.session.rollback()
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("order.checkout"))

    flash("Order created. Please complete payment.", "success")
    return redirect(url_for("payment.pay", order_id=order.id))



#order list
@order_bp.route("/orders")
def user_orders():
    return redirect(url_for("user.my_orders"))


#order details
@order_bp.route("/orders/<int:id>")
def order_details(id):
    return redirect(url_for("user.order_details", order_id=id))
