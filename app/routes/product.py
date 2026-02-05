from flask import Blueprint, render_template, abort, jsonify, current_app, request, redirect, url_for
from app.models.product import Product
from app.models.order import Order
from app import db, csrf
import razorpay

product_bp = Blueprint("product", __name__)
payment_bp = Blueprint("payment", __name__)

#home 
@product_bp.route("/")
def home():
    products = Product.query.filter_by(is_active=True).all()
    return render_template("home.html", products=products)

@product_bp.route("/blog")
def blog():
    return render_template("blog.html")



#Product listing page
@product_bp.route("/products")
def get_products():
    products = Product.query.filter_by(is_active = True).all()
    return render_template("product.html", products = products)

#Product detail page
@product_bp.route("/products/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)

    if not product.is_active:
        abort(404)
    
    return render_template("product_detail.html", product = product)

#payment page
@payment_bp.route("/create-payment/<int:order_id>", methods=["POST"])
@csrf.exempt
def create_payment(order_id):
    from flask import session
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "login required"}), 401

    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    if order.payment_status == "paid":
        return jsonify({"error": "order already paid"}), 400

    if not current_app.config.get('RAZORPAY_KEY_ID') or not current_app.config.get('RAZORPAY_KEY_SECRET'):
        return jsonify({"error": "payment not configured"}), 500

    client = razorpay.Client(auth=(
        current_app.config.get('RAZORPAY_KEY_ID'),
        current_app.config.get('RAZORPAY_KEY_SECRET')
    ))

    try:
        payment = client.order.create({
            "amount": int(float(order.total_amount) * 100),
            "currency": "INR",
            "payment_capture": 1
        })
    except Exception as exc:
        current_app.logger.warning("Razorpay create order failed: %s", exc)
        return jsonify({"error": "Payment setup failed. Check Razorpay keys."}), 400

    order.razorpay_order_id = payment['id']
    db.session.commit()

    return jsonify(payment)

#payment varifing
@payment_bp.route("/verify-payment", methods=['POST'])
@csrf.exempt
def verify_payment():
    data = request.get_json()
    if not data or not all(k in data for k in ["razorpay_order_id", "razorpay_payment_id", "razorpay_signature"]):
        return jsonify(success=False), 400

    if not current_app.config.get('RAZORPAY_KEY_ID') or not current_app.config.get('RAZORPAY_KEY_SECRET'):
        return jsonify(success=False), 500

    client = razorpay.Client(auth=(
        current_app.config.get('RAZORPAY_KEY_ID'),
        current_app.config.get('RAZORPAY_KEY_SECRET')
    ))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })

        order = Order.query.filter_by(
            razorpay_order_id=data['razorpay_order_id']
        ).first()

        if not order:
            return jsonify(success=False), 404

        if order.payment_status == "paid":
            return jsonify(success=True)

        order.payment_status = "paid"
        order.status = "pending"
        order.razorpay_payment_id = data['razorpay_payment_id']
        order.razorpay_signature = data['razorpay_signature']

        # reduce stock + clear cart items for this order
        from app.models.cart import Cart, CartItem
        product_ids = set()
        for item in order.items:
            product = item.product
            if product.stock < item.quantity:
                return jsonify(success=False), 409
            product.stock -= item.quantity
            product_ids.add(item.product_id)

        cart = Cart.query.filter_by(user_id=order.user_id).first()
        if cart:
            CartItem.query.filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id.in_(product_ids)
            ).delete(synchronize_session=False)

        db.session.commit()

        return jsonify(success=True)

    except Exception:
        return jsonify(success=False)
#payment page
@payment_bp.route("/payment/<int:order_id>")
def pay(order_id):
    from flask import session
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    return render_template(
        "payment.html",
        order=order,
        razorpay_key=current_app.config.get("RAZORPAY_KEY_ID", "")
    )
