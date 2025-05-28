from app.models import Usuario, Rol, db
from flask import url_for

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