from flask_login import LoginManager, UserMixin
from flask import redirect, url_for, flash
from database import db


class User(UserMixin):
    """Flask-Login user model."""

    def __init__(self, user_id, username, email, full_name, role):
        self.id = int(user_id)
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id: int):
        """Load user by user_id from DB."""
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        try:
            user = db.execute(
                "SELECT user_id, username, email, full_name, role FROM user WHERE user_id = ?",
                (user_id,),
                fetchone=True,
            )
            if not user:
                return None

            return User(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                role=user["role"],
            )
        except Exception as e:
            print(f"Error loading user: {e}")
            return None

    @staticmethod
    def authenticate(username: str, password: str):
        """Authenticate user."""
        try:
            username = (username or "").strip()
            if not username or not password:
                return None

            user_data = db.authenticate_user(username, password)
            if not user_data:
                return None

            return User(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
            )
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login: load current user by id from session."""
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access."""
    flash("لطفاً برای دسترسی به این صفحه وارد سیستم شوید.", "warning")
    return redirect(url_for("login"))
