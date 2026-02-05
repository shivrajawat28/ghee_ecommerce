from flask import Blueprint, session, request, url_for, redirect, render_template, flash
from app.models.user import User
from app import db
from app.models.order import Order

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile")
def profile():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))
    
    user = User.query.get_or_404(user_id)

    return render_template("user/profile.html", user=user)

#edit profile
@user_bp.route("/profile/edit", methods = ['GET', 'POST'])
def edit_profile():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')

        if not name:
            flash("Name is required", "danger")
            return redirect(url_for("user.edit_profile"))

        if phone and not phone.isdigit():
            flash("Phone must be numeric", "danger")
            return redirect(url_for("user.edit_profile"))
        
        user.name = name
        user.phone = phone
        

        db.session.commit()
        
        flash("Profile updated successfully", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/edit_profile.html", user = user)

#User All orders
@user_bp.route("/my-orders")
def my_orders():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    orders = (
        Order.query.filter_by(user_id = user_id).order_by(Order.created_at.desc()).all()
    )

    return render_template("user/orders.html", orders=orders)


#User Order Details
@user_bp.route("/my-orders/<int:order_id>")
def order_details(order_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    order = Order.query.get_or_404(order_id)

    if order.user_id != user_id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("user.my_orders"))

    return render_template("user/order_detail.html", order=order)
