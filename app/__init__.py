from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_migrate import Migrate
import os
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder="templates", static_folder="static")

    #configration
    os.makedirs(app.instance_path, exist_ok=True)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        secret_key = os.urandom(32)
        app.logger.warning("SECRET_KEY not set. Using a transient key.")
    app.config["SECRET_KEY"] = "My_secret_key"
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'ecommerce.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    db.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app, db)

    #razorpay
    app.config['RAZORPAY_KEY_ID'] = os.environ.get("RAZORPAY_KEY_ID", "")
    app.config['RAZORPAY_KEY_SECRET'] = os.environ.get("RAZORPAY_KEY_SECRET", "")

    #blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.product import product_bp, payment_bp
    app.register_blueprint(product_bp)
    app.register_blueprint(payment_bp)

    from app.routes.cart import cart_bp
    app.register_blueprint(cart_bp)

    from app.routes.order import order_bp
    app.register_blueprint(order_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.admin_dashboard import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp)

    from app.routes.admin_orders import admin_order_bp
    app.register_blueprint(admin_order_bp)

    from app.routes.user import user_bp
    app.register_blueprint(user_bp)

    #visitors data
    @app.before_request
    def track_visitor():
        from app.models.visitor import Visitor
        ip = request.remote_addr

        # Avoid logging static files
        if request.path.startswith("/static"):
            return

        if session.get("visitor_logged"):
            return

        if not ip or ip.startswith(("127.", "10.", "192.168.", "172.")):
            return

        try:
            resp = requests.get(f"https://ip-api.com/json/{ip}", timeout=2)
            if resp.status_code != 200:
                return
            response = resp.json()

            city = response.get("city")
            state = response.get("regionName")

            visitor = Visitor(
                ip_address=ip,
                city=city,
                state=state
            )

            db.session.add(visitor)
            db.session.commit()
            session["visitor_logged"] = True

        except requests.RequestException as exc:
            app.logger.warning("Visitor lookup failed: %s", exc)

    
    return app 
