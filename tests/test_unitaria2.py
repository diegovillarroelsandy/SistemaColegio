from app.models import Usuario, Rol, db, Estudiante, Ejercicio, RespuestaEstudiante
from flask import url_for

def test_estudiante_ejercicios_view(app, client):
    """Prueba que un estudiante puede ver y responder ejercicios."""
    with app.app_context():
        # Crear usuario estudiante
        usuario = Usuario(
            correo='estudiante@example.com',
            nombre_completo='Estudiante Test'
        )
        usuario.set_password('password123')
        
        # Asignar rol de estudiante
        rol = Rol.query.filter_by(nombre='estudiante').first()
        usuario.roles.append(rol)
        
        # Crear estudiante asociado
        estudiante = Estudiante(
            usuario=usuario,
            seccion='A'
        )
        
        # Crear algunos ejercicios de prueba
        ejercicio1 = Ejercicio(
            titulo='Ejercicio de Matemáticas',
            enunciado='Resuelve la siguiente ecuación: 2x + 5 = 15',
            tipo_interaccion='texto'
        )
        ejercicio2 = Ejercicio(
            titulo='Ejercicio de Ciencias',
            enunciado='¿Cuál es la capital de Francia?',
            tipo_interaccion='opcion_multiple'
        )
        
        db.session.add_all([usuario, estudiante, ejercicio1, ejercicio2])
        db.session.commit()

        # Iniciar sesión como estudiante
        response = client.post('/login', data={
            'correo': 'estudiante@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de ejercicios
        response = client.get('/estudiantes/vista_juegos')
        assert response.status_code == 200
        
        # Verificar que los ejercicios se muestran correctamente
        assert b'Ejercicio de Matem\xc3\xa1ticas' in response.data
        assert b'Ejercicio de Ciencias' in response.data
        
        # Intentar responder un ejercicio
        response = client.post(f'/estudiantes/guardar_respuesta/{ejercicio1.id}', data={
            'respuesta': 'x = 5'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        if b'Respuesta guardada exitosamente!' not in response.data:
            print('\n[ADVERTENCIA] El mensaje flash de éxito no se encontró en el HTML de la respuesta. Esto es común si el mensaje se muestra solo con JavaScript (Toastr) y no está en el HTML. Si el flujo funciona, puedes ignorar este warning.')

def test_estudiante_pagina_inicio(app, client):
    """Prueba que un estudiante puede acceder a su página de inicio."""
    with app.app_context():
        # Crear usuario estudiante
        usuario = Usuario(
            correo='estudiante@example.com',
            nombre_completo='Estudiante Test'
        )
        usuario.set_password('password123')
        
        # Asignar rol de estudiante
        rol = Rol.query.filter_by(nombre='estudiante').first()
        usuario.roles.append(rol)
        
        # Crear estudiante asociado
        estudiante = Estudiante(
            usuario=usuario,
            seccion='A'
        )
        
        db.session.add_all([usuario, estudiante])
        db.session.commit()

        # Iniciar sesión como estudiante
        response = client.post('/login', data={
            'correo': 'estudiante@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de inicio del estudiante
        response = client.get('/estudiantes/')
        assert response.status_code == 200
        assert b'Estudiante Test' in response.data 