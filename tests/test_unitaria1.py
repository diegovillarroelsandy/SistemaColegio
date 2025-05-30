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

# Pruebas de modelos
def test_create_usuario(app):
    """Prueba la creación de un usuario."""
    with app.app_context():
        # Crear un usuario de prueba
        usuario = Usuario(
            nombre_completo='Test User',
            correo='test@example.com',
            contrasena_hash='password123'
        )
        usuario.set_password('password123')
        db.session.add(usuario)
        db.session.commit()

        # Verificar que el usuario fue creado
        usuario_creado = Usuario.query.filter_by(correo='test@example.com').first()
        assert usuario_creado is not None
        assert usuario_creado.nombre_completo == 'Test User'
        assert usuario_creado.check_password('password123')

def test_usuario_password(app):
    """Prueba el hash de contraseña del usuario."""
    with app.app_context():
        # Crear un usuario de prueba
        usuario = Usuario(
            nombre_completo='Test User 2',
            correo='test2@example.com'
        )
        usuario.set_password('password123')
        
        # Verificar que la contraseña está hasheada
        assert usuario.contrasena_hash != 'password123'
        assert usuario.check_password('password123')
        assert not usuario.check_password('wrongpassword')

# Pruebas de autenticación
def test_login_page(client):
    """Prueba que la página de login se carga correctamente."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Iniciar Sesion' in response.data

def test_register_page(client):
    """Prueba que la página de registro se carga correctamente."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Registro' in response.data

def test_register_user(app, client):
    """Prueba el registro de un nuevo usuario."""
    with app.app_context():
        # Crear un rol de prueba
        rol = Rol(nombre='estudiante')
        db.session.add(rol)
        db.session.commit()

        # Datos de prueba
        test_data = {
            'correo': 'test@example.com',
            'password': 'password123',
            'nombre_completo': 'Test User',
            'rol': 'estudiante'
        }

        # Intentar registrar un usuario
        response = client.post('/register', data=test_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Registro exitoso' in response.data

        # Verificar que el usuario fue creado
        usuario = Usuario.query.filter_by(correo='test@example.com').first()
        assert usuario is not None
        assert usuario.nombre_completo == 'Test User'
        assert usuario.has_role('estudiante')

def test_login_user(app, client):
    """Prueba el inicio de sesión de un usuario."""
    with app.app_context():
        # Crear un usuario de prueba
        usuario = Usuario(
            correo='test@example.com',
            nombre_completo='Test User'
        )
        usuario.set_password('password123')
        
        # Crear y asignar rol
        rol = Rol(nombre='estudiante')
        db.session.add(rol)
        usuario.roles.append(rol)
        db.session.add(usuario)
        db.session.commit()

        # Intentar iniciar sesión
        response = client.post('/login', data={
            'correo': 'test@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Verificar que fue redirigido a la página de estudiantes
        assert b'Estudiantes' in response.data

def test_login_invalid_credentials(client):
    """Prueba el inicio de sesión con credenciales inválidas."""
    response = client.post('/login', data={
        'correo': 'wrong@example.com',
        'password': 'wrongpass',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Correo o contraseña incorrectos' in response.data 