from app.models import Usuario, Rol, db, Administrador, Grado
from flask import url_for

def test_admin_usuarios_management(app, client):
    """Prueba que un administrador puede gestionar usuarios."""
    with app.app_context():
        # Crear usuario administrador
        admin_usuario = Usuario(
            correo='admin@example.com',
            nombre_completo='Admin Test'
        )
        admin_usuario.set_password('password123')
        
        # Asignar rol de administrador
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        admin_usuario.roles.append(rol_admin)
        
        # Crear administrador asociado
        admin = Administrador(
            usuario=admin_usuario
        )
        
        # Crear un usuario de prueba para gestionar
        test_usuario = Usuario(
            correo='test@example.com',
            nombre_completo='Test User'
        )
        test_usuario.set_password('password123')
        
        # Asignar rol de estudiante al usuario de prueba
        rol_estudiante = Rol.query.filter_by(nombre='estudiante').first()
        test_usuario.roles.append(rol_estudiante)
        
        db.session.add_all([admin_usuario, admin, test_usuario])
        db.session.commit()

        # Iniciar sesión como administrador
        response = client.post('/login', data={
            'correo': 'admin@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de gestión de usuarios
        response = client.get('/admin/usuarios')
        assert response.status_code == 200
        
        # Verificar que se muestran los usuarios
        assert b'Test User' in response.data
        assert b'test@example.com' in response.data

def test_admin_pagina_inicio(app, client):
    """Prueba que un administrador puede acceder a su página de inicio."""
    with app.app_context():
        # Crear usuario administrador
        admin_usuario = Usuario(
            correo='admin@example.com',
            nombre_completo='Admin Test'
        )
        admin_usuario.set_password('password123')
        
        # Asignar rol de administrador
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        admin_usuario.roles.append(rol_admin)
        
        # Crear administrador asociado
        admin = Administrador(
            usuario=admin_usuario
        )
        
        db.session.add_all([admin_usuario, admin])
        db.session.commit()

        # Iniciar sesión como administrador
        response = client.post('/login', data={
            'correo': 'admin@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de inicio del administrador
        response = client.get('/admin/')
        assert response.status_code == 200
        assert b'Admin Test' in response.data 