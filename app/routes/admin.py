from flask import Blueprint, flash, render_template, url_for, session, request, redirect, current_app
from app.models.product import Product, ProductImage
from app.models.user import User
from app import db
import os
import uuid 
from werkzeug.utils import secure_filename
from decimal import Decimal, InvalidOperation


admin_bp = Blueprint("admin", __name__ )

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

#Admin check, it is a reusuable function which checks admin
def admin_required():
    user_id = session.get('user_id')
    
    if not user_id:
        return None

    user = User.query.get(user_id)
    if user and user.role == "admin":
        return user
    
    return None

#Admin Dashboard
@admin_bp.route("/admin")
def admin_dashboard():
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    return redirect(url_for("admin_dashboard.admin_dashboard"))

#See all Products List
@admin_bp.route("/admin/products")
def admin_products():
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    products = Product.query.all()
    return render_template("admin/product_list.html", products=products)

#Add Product
@admin_bp.route("/admin/products/add", methods = ['GET', 'POST'])
def add_product():
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        title = (request.form.get("title") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        description = (request.form.get("description") or "").strip()
        stock_raw = (request.form.get("stock") or "").strip()

        if not title:
            flash("Title is required", "danger")
            return redirect(url_for("admin.add_product"))

        try:
            price = Decimal(price_raw)
            stock = int(stock_raw)
        except (InvalidOperation, ValueError):
            flash("Invalid price or stock", "danger")
            return redirect(url_for("admin.add_product"))
        if stock < 0 or price < 0:
            flash("Price and stock must be positive", "danger")
            return redirect(url_for("admin.add_product"))

        product = Product(
            title = title,
            price = price,
            description = description,
            stock = stock
        )

        db.session.add(product)
        db.session.commit()

        images = request.files.getlist("images")
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "products")
        os.makedirs(upload_dir, exist_ok=True)

        for img in images:
            if img and img.filename:
                if not allowed_file(img.filename):
                    flash("Invalid image type", "danger")
                    return redirect(url_for("admin.add_product"))
                ext = img.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"{uuid.uuid4()}.{ext}")
                file_path = os.path.join(upload_dir, filename)
                img.save(file_path)

                product_image = ProductImage(
                    product_id=product.id,
                    image_path=f"uploads/products/{filename}"
                )
                db.session.add(product_image)
        
        db.session.commit()

        flash("Product added successfully", "success")
        return redirect(url_for("admin.admin_products"))
    
    return render_template("admin/add_product.html")


#edit product
@admin_bp.route("/admin/products/edit/<int:id>", methods = ['GET', 'POST'])
def edit_product(id):
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(id)
    from app.models.order import OrderItem
    if OrderItem.query.filter_by(product_id=product.id).first():
        flash("Cannot delete product linked to orders", "danger")
        return redirect(url_for("admin.admin_products"))

    if request.method == 'POST':
        title = (request.form.get("title") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        description = (request.form.get("description") or "").strip()
        stock_raw = (request.form.get("stock") or "").strip()

        if not title:
            flash("Title is required", "danger")
            return redirect(url_for("admin.edit_product", id=product.id))

        try:
            price = Decimal(price_raw)
            stock = int(stock_raw)
        except (InvalidOperation, ValueError):
            flash("Invalid price or stock", "danger")
            return redirect(url_for("admin.edit_product", id=product.id))
        if stock < 0 or price < 0:
            flash("Price and stock must be positive", "danger")
            return redirect(url_for("admin.edit_product", id=product.id))

        product.title = title
        product.price = price
        product.description = description
        product.stock = stock
        db.session.commit()

        images = request.files.getlist("images")
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "products")
        os.makedirs(upload_dir, exist_ok=True)

        for img in images:
            if img and img.filename:
                if not allowed_file(img.filename):
                    flash("Invalid image type", "danger")
                    return redirect(url_for("admin.edit_product", id=product.id))
                ext = img.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"{uuid.uuid4()}.{ext}")
                file_path = os.path.join(upload_dir, filename)
                img.save(file_path)

                product_image = ProductImage(
                    product_id=product.id,
                    image_path=f"uploads/products/{filename}"
                )
                db.session.add(product_image)
        db.session.commit()
        

        flash("Product updated", "success")
        return redirect(url_for("admin.admin_products"))

    return render_template("admin/edit_product.html", product=product)

#Delete Product
@admin_bp.route("/admin/products/delete/<int:id>", methods=["POST"])
def delete_product(id):
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(id)
    from app.models.order import OrderItem
    if OrderItem.query.filter_by(product_id=product.id).first():
        flash("Cannot delete product linked to orders", "danger")
        return redirect(url_for("admin.admin_products"))

    for img in product.images:
        image_rel = img.image_path.replace("static/", "").lstrip("/")
        file_path = os.path.join(current_app.root_path, "static", image_rel)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass

    try:
        db.session.delete(product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Unable to delete product right now", "danger")
        return redirect(url_for("admin.admin_products"))

    flash("Product Deleted", "success")

    return redirect(url_for("admin.admin_products"))

#Toggle Active/Inactive
@admin_bp.route("/admin/products/toggle/<int:id>", methods=["POST"])
def toggle_product(id):
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    product = Product.query.get_or_404(id)
    product.is_active = not product.is_active
    db.session.commit()

    flash("Product status update", "success")
    return redirect(url_for("admin.admin_products"))

#Delete individual image
@admin_bp.route("/admin/products/image/delete/<int:image_id>", methods=["POST"])
def delete_image(image_id):
    admin = admin_required()
    if not admin:
        flash("Admin access required", "danger")
        return redirect(url_for("auth.login"))

    image = ProductImage.query.get_or_404(image_id)
    
    # delete file from disk
    image_rel = image.image_path.replace("static/", "").lstrip("/")
    file_path = os.path.join(current_app.root_path, "static", image_rel)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(image)
    db.session.commit()
    flash("Image Deleted Successfully", "success")
    return redirect(url_for("admin.edit_product", id = image.product_id))
