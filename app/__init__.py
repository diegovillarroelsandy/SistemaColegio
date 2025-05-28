import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from .models import db, Usuario
#def create_app():
def create_app(config_name=None):
    app = Flask(__name__)
    #    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
    else:
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

    # Hacer que 'os' esté disponible en todas las plantillas
    @app.context_processor
    def inject_os():
        return dict(os=os)
    
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.docentes import docentes_bp
    from .routes.admin import admin_bp
    from .routes.estudiantes import estudiantes_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(docentes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(estudiantes_bp)
    
    return app