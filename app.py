import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, logout_user, current_user, login_user
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

from database import db
from auth import User, login_manager

login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "لطفاً برای دسترسی به این صفحه وارد سیستم شوید."


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("شما دسترسی به این صفحه را ندارید.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_now():
    return {"now": datetime.now(), "current_date": datetime.now()}


# -------------------------
# Home / Auth
# -------------------------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        if not username or not password:
            flash("لطفاً نام کاربری و رمز عبور را وارد کنید.", "danger")
            return render_template("login.html")

        user = User.authenticate(username, password)
        if user:
            login_user(user, remember=True)
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash("ورود موفقیت‌آمیز بود!", "success")
            return redirect(url_for("dashboard"))

        flash("نام کاربری یا رمز عبور اشتباه است.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    if current_user.is_authenticated:
        logout_user()
    flash("با موفقیت از سیستم خارج شدید.", "info")
    return redirect(url_for("login"))


# -------------------------
# Dashboard
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        stats = db.get_stats()
        recent_orders = db.get_all_orders(limit=5)
        return render_template("dashboard.html", stats=stats, recent_orders=recent_orders)
    else:
        # Customer dashboard
        user_orders = db.get_user_orders(current_user.id, limit=5)
        user_stats = db.get_user_stats(current_user.id)
        return render_template("dashboard.html", stats=user_stats, recent_orders=user_orders, is_customer=True)


@app.route("/api/stats")
@login_required
def api_stats():
    stats = db.get_stats()
    return jsonify(stats)


# -------------------------
# Users
# -------------------------
@app.route("/users")
@admin_required
def users():
    users_list = db.get_all_users()
    return render_template("users.html", users=users_list)


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    # Users can only edit themselves, admins can edit anyone
    if current_user.role != "admin" and current_user.id != user_id:
        flash("شما دسترسی به این صفحه را ندارید.", "danger")
        return redirect(url_for("profile"))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash("کاربر یافت نشد.", "danger")
        return redirect(url_for("users") if current_user.role == "admin" else url_for("profile"))
    
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip() or None
        address = (request.form.get("address") or "").strip() or None
        password = (request.form.get("password") or "").strip()
        
        # Only admin can change role
        role = user["role"]
        if current_user.role == "admin":
            role = (request.form.get("role") or user["role"]).strip()
        
        if not email or not full_name:
            flash("لطفاً تمام فیلدهای الزامی را پر کنید.", "danger")
            return render_template("edit_user.html", user=user)
        
        try:
            db.update_user(user_id, email, full_name, phone, address, role, password if password else None)
            flash(f'اطلاعات کاربر "{full_name}" با موفقیت بروزرسانی شد.', "success")
            if current_user.role == "admin":
                return redirect(url_for("users"))
            else:
                return redirect(url_for("profile"))
        except Exception as e:
            flash(f"خطا در بروزرسانی کاربر: {str(e)}", "danger")
    
    return render_template("edit_user.html", user=user)


@app.route("/users/add", methods=["GET", "POST"])
@admin_required
def add_user():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = (request.form.get("password") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip() or None
        address = (request.form.get("address") or "").strip() or None
        role = (request.form.get("role") or "customer").strip()

        if not username or not email or not password or not full_name:
            flash("لطفاً تمام فیلدهای الزامی را پر کنید.", "danger")
            return render_template("add_user.html")

        try:
            db.add_user(username, email, password, full_name, phone, address, role)
            flash(f'کاربر "{full_name}" با موفقیت اضافه شد.', "success")
            return redirect(url_for("users"))
        except Exception as e:
            flash(f"خطا در افزودن کاربر: {str(e)}", "danger")

    return render_template("add_user.html")


@app.route("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id):
    try:
        u = db.get_user_by_id(user_id)
        if not u:
            flash("کاربر یافت نشد.", "danger")
        else:
            db.delete_user(user_id)
            flash(f'کاربر "{u["full_name"]}" حذف شد.', "success")
    except Exception as e:
        flash(f"خطا در حذف کاربر: {str(e)}", "danger")
    return redirect(url_for("users"))


# -------------------------
# Products
# -------------------------
@app.route("/products")
@login_required
def products():
    products_list = db.get_all_products()
    return render_template("products.html", products=products_list)


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        flash("محصول یافت نشد.", "danger")
        return redirect(url_for("products"))
    
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        price = (request.form.get("price") or "0").strip()
        stock_quantity = (request.form.get("stock_quantity") or "0").strip()
        category = (request.form.get("category") or "").strip()
        image_url = (request.form.get("image_url") or "").strip() or None
        
        if not name or not category:
            flash("نام و دسته‌بندی الزامی است.", "danger")
            return render_template("edit_product.html", product=product)
        
        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
            if price < 0 or stock_quantity < 0:
                raise ValueError()
        except Exception:
            flash("قیمت و موجودی باید اعداد معتبر باشند.", "danger")
            return render_template("edit_product.html", product=product)
        
        try:
            db.update_product(product_id, name, description, price, stock_quantity, category, image_url)
            flash(f'محصول "{name}" با موفقیت بروزرسانی شد.', "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"خطا در بروزرسانی محصول: {str(e)}", "danger")
    
    return render_template("edit_product.html", product=product)


@app.route("/products/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        price = (request.form.get("price") or "0").strip()
        stock_quantity = (request.form.get("stock_quantity") or "0").strip()
        category = (request.form.get("category") or "").strip()
        image_url = (request.form.get("image_url") or "").strip() or None

        if not name or not category:
            flash("نام و دسته‌بندی الزامی است.", "danger")
            return render_template("add_product.html")

        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
            if price < 0 or stock_quantity < 0:
                raise ValueError()
        except Exception:
            flash("قیمت و موجودی باید اعداد معتبر باشند.", "danger")
            return render_template("add_product.html")

        try:
            db.add_product(name, description, price, stock_quantity, category, image_url)
            flash(f'محصول "{name}" با موفقیت اضافه شد.', "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"خطا در افزودن محصول: {str(e)}", "danger")

    return render_template("add_product.html")


@app.route("/products/<int:product_id>/delete")
@admin_required
def delete_product(product_id):
    try:
        p = db.get_product_by_id(product_id)
        if not p:
            flash("محصول یافت نشد.", "danger")
        else:
            db.delete_product(product_id)
            flash(f"محصول #{product_id} حذف شد.", "success")
    except Exception as e:
        flash(f"خطا در حذف محصول: {str(e)}", "danger")
    return redirect(url_for("products"))


# -------------------------
# Orders
# -------------------------
@app.route("/orders")
@login_required
def orders():
    if current_user.role == "admin":
        orders_list = db.get_all_orders()
    else:
        orders_list = db.get_user_orders(current_user.id)
    return render_template("orders.html", orders=orders_list)


@app.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    order = db.get_order_by_id(order_id)
    if not order:
        flash("سفارش یافت نشد.", "danger")
        return redirect(url_for("orders"))
    
    # Users can only see their own orders
    if current_user.role != "admin" and order["user_id"] != current_user.id:
        flash("شما دسترسی به این سفارش را ندارید.", "danger")
        return redirect(url_for("orders"))
    
    order_items = db.get_order_items(order_id)
    return render_template("order_detail.html", order=order, order_items=order_items)


@app.route("/orders/add", methods=["GET", "POST"])
@login_required
def add_order():
    if request.method == "POST":
        # Users can only create orders for themselves
        if current_user.role == "admin":
            user_id = (request.form.get("user_id") or "").strip()
            try:
                user_id = int(user_id)
            except Exception:
                flash("مقادیر وارد شده معتبر نیستند.", "danger")
                return redirect(url_for("add_order"))
        else:
            user_id = current_user.id
        
        # کل مبلغ از روی آیتم‌ها محاسبه می‌شود (ورودی کاربر نادیده گرفته می‌شود)
        total_amount = 0
        shipping_address = (request.form.get("shipping_address") or "").strip()
        
        product_ids = request.form.getlist("product_ids")
        quantities = request.form.getlist("quantities")
        # قیمت را از دیتابیس می‌خوانیم تا قابل تغییر توسط کاربر نباشد
        prices = request.form.getlist("prices")

        if not product_ids:
            flash("حداقل یک محصول انتخاب کنید.", "danger")
            return redirect(url_for("add_order"))

        order_items = []
        for i, pid in enumerate(product_ids):
            try:
                product_id = int(pid)
                quantity = int(quantities[i]) if i < len(quantities) else 1

                # قیمت را همیشه از دیتابیس می‌گیریم تا قابل تغییر نباشد
                product = db.get_product_by_id(product_id)
                if not product:
                    flash(f"محصول {product_id} یافت نشد.", "danger")
                    return redirect(url_for("add_order"))

                price = float(product["price"])
                total_amount += price * quantity

                order_items.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price,
                })
            except Exception:
                flash(f"خطا در پردازش محصول {pid}", "danger")
                return redirect(url_for("add_order"))

        try:
            order_id = db.create_order(user_id, total_amount, shipping_address, order_items)
            flash(f"سفارش با موفقیت ثبت شد. کد سفارش: {order_id}", "success")
            return redirect(url_for("orders"))
        except Exception as e:
            flash(f"خطا در ثبت سفارش: {str(e)}", "danger")

    users_list = db.get_all_users(limit=500) if current_user.role == "admin" else []
    products_list = db.get_all_products(limit=500)
    return render_template("add_order.html", users=users_list, products=products_list)


@app.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    order = db.get_order_by_id(order_id)
    if not order:
        flash("سفارش یافت نشد.", "danger")
        return redirect(url_for("orders"))
    
    # Users can only update their own orders, admins can update any
    if current_user.role != "admin" and order["user_id"] != current_user.id:
        flash("شما دسترسی به این سفارش را ندارید.", "danger")
        return redirect(url_for("orders"))
    
    status = (request.form.get("status") or "").strip()
    if not status:
        flash("وضعیت جدید را وارد کنید.", "danger")
        return redirect(url_for("order_detail", order_id=order_id))
    
    try:
        old_status = order["status"]
        db.update_order_status(order_id, status)
        
        # Update revenue when status changes to/from completed or canceled
        if old_status == "completed" and status == "canceled":
            # Order was completed, now canceled - decrease revenue
            pass  # Revenue is calculated from completed orders only
        elif old_status == "canceled" and status == "completed":
            # Order was canceled, now completed - increase revenue
            pass  # Revenue is calculated from completed orders only
        
        flash(f"وضعیت سفارش {order_id} بروزرسانی شد.", "success")
    except Exception as e:
        flash(f"خطا در بروزرسانی وضعیت سفارش: {str(e)}", "danger")
    
    return redirect(url_for("order_detail", order_id=order_id))


@app.route("/orders/<int:order_id>/delete")
@login_required
def delete_order(order_id):
    order = db.get_order_by_id(order_id)
    if not order:
        flash("سفارش یافت نشد.", "danger")
        return redirect(url_for("orders"))
    
    # Users can only delete their own orders, admins can delete any
    if current_user.role != "admin" and order["user_id"] != current_user.id:
        flash("شما دسترسی به این سفارش را ندارید.", "danger")
        return redirect(url_for("orders"))
    
    try:
        db.delete_order(order_id)
        flash(f"سفارش {order_id} حذف شد.", "success")
    except Exception as e:
        flash(f"خطا در حذف سفارش: {str(e)}", "danger")
    return redirect(url_for("orders"))


# -------------------------
# Profile
# -------------------------
@app.route("/profile")
@login_required
def profile():
    user = db.get_user_by_id(current_user.id)
    return render_template("profile.html", user=user)


# -------------------------
# Errors
# -------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
