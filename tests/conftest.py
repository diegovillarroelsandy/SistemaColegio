import pytest
from app import create_app
from app.models import db as _db
from app.models import Usuario, Rol
from flask_login import FlaskLoginClient

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    with app.app_context():
        _db.create_all()
        # Crear roles básicos
        roles = ['administrador', 'docente', 'estudiante']
        for rol in roles:
            if not Rol.query.filter_by(nombre=rol).first():
                _db.session.add(Rol(nombre=rol))
        _db.session.commit()
        
        yield app
        
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    app.test_client_class = FlaskLoginClient
    return app.test_client()

@pytest.fixture
def db(app):
    return _db

@pytest.fixture
def runner(app):
    """Crear un runner de CLI para pruebas."""
    return app.test_cli_runner() 