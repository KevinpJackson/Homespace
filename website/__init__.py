from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default_secret_key")

    # Use SQLite locally, but PostgreSQL in production
    if os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)  # ✅ Initialize database before importing models
    migrate.init_app(app, db)

    # ✅ Register blueprints and import models inside app context
    with app.app_context():
        from .models import User, Note  # ✅ Import models AFTER initializing db
        db.create_all()  # ✅ Ensure the database exists before queries

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  # ✅ Use `db.session.get()`

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))  # Render assigns a port dynamically
    app.run(host="0.0.0.0", port=port, debug=True)