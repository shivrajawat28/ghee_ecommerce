from flask import Blueprint, session, flash, redirect, render_template, request, url_for
from app import db
from app.models.user import User
from app.models.order import Order

admin_order_bp = Blueprint("admin_order", __name__)

def admin_required():
    user_id = session.get("user_id")
    if not user_id:
        return False
    
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return False

    return True


#Admin Orders List
@admin_order_bp.route("/admin/orders")
def admin_orders():
    if not admin_required():
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template("admin/orders.html", orders=orders)


#Admin order detail
@admin_order_bp.route("/admin/orders/<int:order_id>")
def admin_order_detail(order_id):
    if not admin_required():
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))
    
    order = Order.query.get_or_404(order_id)

    return render_template("admin/order_detail.html", order=order)


#Admin status update
@admin_order_bp.route("/admin/orders/<int:order_id>/status", methods = ['POST'])
def update_order_status(order_id):
    if not admin_required():
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    order = Order.query.get_or_404(order_id)

    new_status = (request.form.get("status") or "").lower()

    allowed_status = ["pending", "shipped", "delivered", "cancelled"]

    if new_status not in allowed_status:
        flash("Invalid status", "danger")
        return redirect(url_for("admin_order.admin_order_detail", order_id= order.id))

    order.status = new_status
    db.session.commit()

    flash("Order status updated successfully", "success")
    return redirect(url_for("admin_order.admin_order_detail", order_id= order.id))

#Admin order cancel 
@admin_order_bp.route("/admin/orders/<int:order_id>/cancel", methods = ['POST'])
def cancel_order(order_id):
    if not admin_required():
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))
    
    order = Order.query.get_or_404(order_id)

    if (order.status or "").lower() == "delivered":
        flash("Delivered orders can't be canceled", "warning")
        return redirect(url_for("admin_order.admin_order_detail", order_id=order.id))

    if (order.status or "").lower() == "cancelled":
        flash("Order already cancelled", "info")
        return redirect(url_for("admin_order.admin_order_detail", order_id=order.id))

    for item in order.items:
        product = item.product
        product.stock += item.quantity
    
    order.status = "cancelled"

    db.session.commit()

    flash("Order cancelled and stock restored", "success")
    return redirect(url_for("admin_order.admin_order_detail", order_id=order.id))
