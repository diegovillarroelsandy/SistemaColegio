from app.models import Usuario, Rol, db, Estudiante, Administrador
from flask import url_for
from flask_login import current_user

def test_index_page_requires_login(client):
    """Prueba que la página principal requiere inicio de sesión."""
    response = client.get('/')
    assert response.status_code == 302  # Redirección a login

def test_index_page_requires_admin(app, client):
    """Prueba que la página principal requiere rol de administrador."""
    with app.app_context():
        # Crear usuario no administrador
        usuario = Usuario(
            correo='test@example.com',
            nombre_completo='Test User'
        )
        usuario.set_password('password123')
        
        # Asignar rol de estudiante
        rol = Rol.query.filter_by(nombre='estudiante').first()
        usuario.roles.append(rol)
        db.session.add(usuario)
        db.session.commit()

        # Iniciar sesión
        response = client.post('/login', data={
            'correo': 'test@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Intentar acceder a la página principal
        response = client.get('/')
        assert response.status_code == 302  # Redirección por no ser admin

def test_estudiantes_index_requires_login(client):
    """Prueba que la página de estudiantes requiere inicio de sesión."""
    response = client.get('/estudiantes/')
    assert response.status_code == 302  # Redirección a login

def test_estudiantes_index_requires_student_role(app, client):
    """Prueba que la página de estudiantes requiere rol de estudiante."""
    with app.app_context():
        # Crear usuario no estudiante
        usuario = Usuario(
            correo='docente@example.com',
            nombre_completo='Docente User'
        )
        usuario.set_password('password123')
        
        # Asignar rol de docente
        rol = Rol.query.filter_by(nombre='docente').first()
        usuario.roles.append(rol)
        db.session.add(usuario)
        db.session.commit()

        # Iniciar sesión
        response = client.post('/login', data={
            'correo': 'docente@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Intentar acceder a la página de estudiantes
        response = client.get('/estudiantes/')
        assert response.status_code == 302  # Redirección por no ser estudiante

def test_estudiantes_notas_requires_login(client):
    """Prueba que la página de notas requiere inicio de sesión."""
    response = client.get('/estudiantes/notas')
    assert response.status_code == 302  # Redirección a login 