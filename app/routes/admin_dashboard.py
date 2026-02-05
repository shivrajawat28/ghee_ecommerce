from flask import Blueprint, render_template, redirect, url_for, flash, session
from app import db
from datetime import datetime, timedelta
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.models.visitor import Visitor
from sqlalchemy import func

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

#Admin check
def admin_required():
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return False
    
    return True


#Dashboard route
@admin_dashboard_bp.route("/admin/dashboard")
def admin_dashboard():
    if not admin_required():
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    #Order count
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    last_7_days = now - timedelta(days=7)

    total_orders = Order.query.count()
    total_users = User.query.count()
    total_products = Product.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    today_orders = Order.query.filter(Order.created_at >= today_start).count()
    last_7_days_orders = Order.query.filter(Order.created_at >= last_7_days).count()

    pending_orders = Order.query.filter(func.lower(Order.status) == "pending").count()
    shipped_orders = Order.query.filter(func.lower(Order.status) == "shipped").count()
    delivered_orders = Order.query.filter(func.lower(Order.status) == "delivered").count()

    

    #Revenue Calculations
    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.lower(Order.status) == "delivered"
    ).scalar()

    todays_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.lower(Order.status) == "delivered",
        Order.created_at >= today_start
    ).scalar()

    last_7_days_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.lower(Order.status) == "delivered", 
        Order.created_at >= last_7_days
    ).scalar()


    #visitors data
    today_visitors = db.session.query(func.count(Visitor.id)).filter(Visitor.visited_at>= today_start).scalar()

    #order_by_state
    order_by_state = db.session.query(Order.state, func.count(Order.id)).group_by(Order.state).all()

    return render_template(
        "admin/dashboard.html", 
        total_orders = total_orders,
        total_users = total_users,
        total_products = total_products,
        today_orders = today_orders,
        last_7_days_orders = last_7_days_orders,
        pending_orders = pending_orders,
        shipped_orders = shipped_orders,
        delivered_orders = delivered_orders, 
        total_revenue = total_revenue,
        todays_revenue = todays_revenue,
        last_7_days_revenue = last_7_days_revenue,
        today_visitors = today_visitors,
        order_by_state = order_by_state,
        recent_orders = recent_orders
    )
