from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from .models import db, Usuario

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.remember_cookie_duration = 30 * 24 * 60 * 60  # 30 días en segundos

    @login_manager.user_loader
    def load_user(id):
        return Usuario.query.get(int(id))

    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.docentes import docentes_bp
    from .routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(docentes_bp)
    app.register_blueprint(admin_bp)
    
    return app