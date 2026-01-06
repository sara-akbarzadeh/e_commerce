import os
import sqlite3
import hashlib
import binascii


class Database:
    """
    Database helper for E-Commerce schema:
      user, product, order, order_item
    """

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.environ.get("DATABASE_PATH", "ecommerce.db")
        self.db_path = db_path

    def get_connection(self):
        """Create a DB connection (dict rows)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ---------------------------
    # Password hashing (PBKDF2)
    # ---------------------------
    def _hash_password(self, password: str) -> str:
        """Hash password with PBKDF2-HMAC-SHA512."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
        pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode("ascii")

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify password."""
        if not stored_password:
            return False

        if len(stored_password) >= 64:
            salt = stored_password[:64]
            rest = stored_password[64:]
            if all(c in "0123456789abcdef" for c in (salt + rest).lower()):
                try:
                    pwdhash = hashlib.pbkdf2_hmac(
                        "sha512",
                        provided_password.encode("utf-8"),
                        salt.encode("ascii"),
                        100000,
                    )
                    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
                    return pwdhash == rest
                except Exception:
                    return stored_password == provided_password

        return stored_password == provided_password

    # ---------------------------
    # Generic execution helpers
    # ---------------------------
    def execute(self, query: str, params=None, fetch=False, fetchone=False):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            result = None
            if fetchone:
                row = cur.fetchone()
                result = dict(row) if row else None
            elif fetch:
                rows = cur.fetchall()
                result = [dict(row) for row in rows]
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------------------------
    # Schema init
    # ---------------------------
    def init_db(self):
        """Create e-commerce tables if they do not exist."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()

            # user table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    role TEXT NOT NULL DEFAULT 'customer',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # product table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS product (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL CHECK (price >= 0),
                    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0) DEFAULT 0,
                    category TEXT NOT NULL,
                    image_url TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # order table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS "order" (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_amount REAL NOT NULL CHECK (total_amount >= 0),
                    status TEXT NOT NULL DEFAULT 'pending',
                    shipping_address TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
                );
                """
            )

            # order_item table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS order_item (
                    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    price REAL NOT NULL CHECK (price >= 0),
                    FOREIGN KEY (order_id) REFERENCES "order"(order_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
                );
                """
            )

            conn.commit()
            self.create_default_admin()
            print("E-commerce database schema created successfully.")

        except Exception as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_default_admin(self):
        """Create default admin user."""
        admin_username = os.environ.get("ADMIN_USERNAME", "sara_2003")
        admin_password = os.environ.get("ADMIN_PASSWORD", "20032003")
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@ecommerce.com")

        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM user WHERE username = ?", (admin_username,))
            if cur.fetchone():
                return

            password_hash = self._hash_password(admin_password)
            cur.execute(
                """
                INSERT INTO user (username, email, password, full_name, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (admin_username, admin_email, password_hash, "Admin User", "admin"),
            )
            conn.commit()
            print(f"Default admin user created: {admin_username}")
        except Exception as e:
            conn.rollback()
            print(f"Error creating default admin: {e}")
        finally:
            conn.close()

    # ---------------------------
    # User methods
    # ---------------------------
    def authenticate_user(self, username: str, password: str):
        """Authenticate user."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, username, email, password, full_name, role FROM user WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                return None

            user = dict(row)
            if not self.verify_password(user["password"], password):
                return None

            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
            }
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
        finally:
            conn.close()

    def get_all_users(self, limit=200):
        return self.execute(
            "SELECT user_id, username, email, full_name, phone, role, created_at FROM user ORDER BY user_id DESC LIMIT ?",
            (limit,),
            fetch=True,
        )

    def get_user_by_id(self, user_id: int):
        return self.execute(
            "SELECT user_id, username, email, full_name, phone, address, role FROM user WHERE user_id = ?",
            (user_id,),
            fetchone=True,
        )

    def add_user(self, username, email, password, full_name, phone=None, address=None, role="customer"):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            password_hash = self._hash_password(password)
            cur.execute(
                """
                INSERT INTO user (username, email, password, full_name, phone, address, role)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, full_name, phone, address, role),
            )
            conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_user(self, user_id, email, full_name, phone=None, address=None, role=None, password=None):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            updates = []
            params = []
            
            if email:
                updates.append("email = ?")
                params.append(email)
            if full_name:
                updates.append("full_name = ?")
                params.append(full_name)
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)
            if address is not None:
                updates.append("address = ?")
                params.append(address)
            if role:
                updates.append("role = ?")
                params.append(role)
            if password:
                password_hash = self._hash_password(password)
                updates.append("password = ?")
                params.append(password_hash)
            
            if updates:
                params.append(user_id)
                cur.execute(
                    f"UPDATE user SET {', '.join(updates)} WHERE user_id = ?",
                    tuple(params),
                )
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_user(self, user_id: int):
        self.execute("DELETE FROM user WHERE user_id = ?", (user_id,))

    # ---------------------------
    # Product methods
    # ---------------------------
    def get_all_products(self, limit=200):
        return self.execute(
            "SELECT product_id, name, description, price, stock_quantity, category, image_url FROM product ORDER BY product_id DESC LIMIT ?",
            (limit,),
            fetch=True,
        )

    def get_product_by_id(self, product_id: int):
        return self.execute(
            "SELECT product_id, name, description, price, stock_quantity, category, image_url FROM product WHERE product_id = ?",
            (product_id,),
            fetchone=True,
        )

    def add_product(self, name, description, price, stock_quantity, category, image_url=None):
        return self.execute(
            """
            INSERT INTO product (name, description, price, stock_quantity, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, price, stock_quantity, category, image_url),
        )

    def update_product(self, product_id, name=None, description=None, price=None, stock_quantity=None, category=None, image_url=None):
        updates = []
        params = []
        if name:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if stock_quantity is not None:
            updates.append("stock_quantity = ?")
            params.append(stock_quantity)
        if category:
            updates.append("category = ?")
            params.append(category)
        if image_url is not None:
            updates.append("image_url = ?")
            params.append(image_url)
        
        if updates:
            params.append(product_id)
            self.execute(
                f"UPDATE product SET {', '.join(updates)} WHERE product_id = ?",
                tuple(params),
            )

    def delete_product(self, product_id: int):
        self.execute("DELETE FROM product WHERE product_id = ?", (product_id,))

    # ---------------------------
    # Order methods
    # ---------------------------
    def create_order(self, user_id, total_amount, shipping_address, order_items):
        """Create order with order items."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            
            # Create order
            cur.execute(
                """
                INSERT INTO "order" (user_id, total_amount, shipping_address, status)
                VALUES (?, ?, ?, 'pending')
                """,
                (user_id, total_amount, shipping_address),
            )
            order_id = cur.lastrowid

            # Add order items and update stock
            for item in order_items:
                cur.execute(
                    """
                    INSERT INTO order_item (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                    """,
                    (order_id, item["product_id"], item["quantity"], item["price"]),
                )
                
                # Update product stock
                cur.execute(
                    "UPDATE product SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                    (item["quantity"], item["product_id"]),
                )

            conn.commit()
            return order_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all_orders(self, limit=200):
        return self.execute(
            """
            SELECT o.order_id, o.user_id, u.username, u.full_name, o.total_amount, o.status, o.created_at
            FROM "order" o
            JOIN user u ON u.user_id = o.user_id
            ORDER BY o.order_id DESC
            LIMIT ?
            """,
            (limit,),
            fetch=True,
        )

    def get_order_by_id(self, order_id: int):
        return self.execute(
            """
            SELECT o.order_id, o.user_id, u.username, u.full_name, o.total_amount, o.status, o.shipping_address, o.created_at
            FROM "order" o
            JOIN user u ON u.user_id = o.user_id
            WHERE o.order_id = ?
            """,
            (order_id,),
            fetchone=True,
        )

    def get_order_items(self, order_id: int):
        return self.execute(
            """
            SELECT oi.order_item_id, oi.product_id, p.name, oi.quantity, oi.price
            FROM order_item oi
            JOIN product p ON p.product_id = oi.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
            fetch=True,
        )

    def update_order_status(self, order_id: int, status: str):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            
            # Get current status
            cur.execute('SELECT status FROM "order" WHERE order_id = ?', (order_id,))
            current_status = cur.fetchone()
            if not current_status:
                raise ValueError("Order not found")
            
            old_status = current_status["status"]
            
            # If changing to canceled, restore stock
            if status == "canceled" and old_status != "canceled":
                order_items = self.get_order_items(order_id)
                for item in order_items:
                    cur.execute(
                        "UPDATE product SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                        (item["quantity"], item["product_id"]),
                    )
            
            # If changing from canceled to another status, reduce stock again
            if old_status == "canceled" and status != "canceled":
                order_items = self.get_order_items(order_id)
                for item in order_items:
                    cur.execute(
                        "UPDATE product SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                        (item["quantity"], item["product_id"]),
                    )
            
            # Update order status
            cur.execute('UPDATE "order" SET status = ? WHERE order_id = ?', (status, order_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_user_orders(self, user_id: int, limit=200):
        return self.execute(
            """
            SELECT o.order_id, o.user_id, u.username, u.full_name, o.total_amount, o.status, o.created_at
            FROM "order" o
            JOIN user u ON u.user_id = o.user_id
            WHERE o.user_id = ?
            ORDER BY o.order_id DESC
            LIMIT ?
            """,
            (user_id, limit),
            fetch=True,
        )

    def delete_order(self, order_id: int):
        self.execute('DELETE FROM "order" WHERE order_id = ?', (order_id,))

    # ---------------------------
    # Stats
    # ---------------------------
    def get_stats(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS c FROM user")
            total_users = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) AS c FROM product")
            total_products = cur.fetchone()["c"]

            cur.execute('SELECT COUNT(*) AS c FROM "order"')
            total_orders = cur.fetchone()["c"]

            # Only count completed orders for revenue
            cur.execute('SELECT COALESCE(SUM(total_amount), 0) AS s FROM "order" WHERE status = "completed"')
            total_revenue = cur.fetchone()["s"]

            return {
                "total_users": total_users,
                "total_products": total_products,
                "total_orders": total_orders,
                "total_revenue": float(total_revenue),
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_users": 0, "total_products": 0, "total_orders": 0, "total_revenue": 0}
        finally:
            conn.close()

    def get_user_stats(self, user_id: int):
        """Get stats for a specific user."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) AS c FROM "order" WHERE user_id = ?', (user_id,))
            total_orders = cur.fetchone()["c"]

            # Only count completed orders for user revenue
            cur.execute('SELECT COALESCE(SUM(total_amount), 0) AS s FROM "order" WHERE user_id = ? AND status = "completed"', (user_id,))
            total_revenue = cur.fetchone()["s"]

            return {
                "total_users": 0,
                "total_products": 0,
                "total_orders": total_orders,
                "total_revenue": float(total_revenue),
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {"total_users": 0, "total_products": 0, "total_orders": 0, "total_revenue": 0}
        finally:
            conn.close()


db = Database()
