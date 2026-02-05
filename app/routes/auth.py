from flask import Blueprint, flash, render_template, url_for, session, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db

auth_bp = Blueprint("auth", __name__)

#register route
@auth_bp.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = (request.form.get('name') or "").strip()
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""

        if not name or not email or not password:
            flash("All fields are required", "danger")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email = email).first()

        if existing_user:
            flash("User already exists", "danger")
            return redirect(url_for('auth.register'))

        #create new user
        if len(password) < 8:
            flash("Password must be at least 8 characters", "danger")
            return redirect(url_for('auth.register'))

        hash_password = generate_password_hash(password)
        new_user = User(
            name = name, 
            email = email,
            password_hash = hash_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Succesfull", "success")
        return redirect(url_for('auth.login'))
    
    return render_template("register.html")

#login
@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        password = request.form.get('password') or ""

        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email = email).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role

            flash("Login Success", "success")

            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("product.home"))
        
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

#logout
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged Out Successfully", "success")
    return redirect(url_for("auth.login"))

#profile
@auth_bp.route("/account")
def profile():
    return redirect(url_for("user.profile"))
