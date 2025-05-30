from app.models import Usuario, Rol, db, Docente, Ejercicio, Grado
from flask import url_for

def test_docente_ejercicios_management(app, client):
    """Prueba que un docente puede gestionar ejercicios."""
    with app.app_context():
        # Crear usuario docente
        usuario = Usuario(
            correo='docente@example.com',
            nombre_completo='Docente Test'
        )
        usuario.set_password('password123')
        
        # Asignar rol de docente
        rol = Rol.query.filter_by(nombre='docente').first()
        usuario.roles.append(rol)
        
        # Crear grado
        grado = Grado(
            nombre='10A',
            descripcion='Décimo grado sección A'
        )
        
        # Crear docente asociado
        docente = Docente(
            usuario=usuario,
            especialidad='Matemáticas',
            grado=grado
        )
        
        # Crear algunos ejercicios de prueba
        ejercicio1 = Ejercicio(
            titulo='Ejercicio de Álgebra',
            enunciado='Resuelve la ecuación cuadrática: x² + 5x + 6 = 0',
            tipo_interaccion='texto',
            grado_destinado=grado,
            docente=docente
        )
        ejercicio2 = Ejercicio(
            titulo='Ejercicio de Geometría',
            enunciado='Calcula el área de un triángulo con base 5 y altura 8',
            tipo_interaccion='texto',
            grado_destinado=grado,
            docente=docente
        )
        
        db.session.add_all([usuario, grado, docente, ejercicio1, ejercicio2])
        db.session.commit()

        # Iniciar sesión como docente
        response = client.post('/login', data={
            'correo': 'docente@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de ejercicios del docente
        response = client.get('/docentes/ejercicios')
        assert response.status_code == 200
        
        # Verificar que los ejercicios se muestran correctamente
        assert b'Ejercicio de \xc3\x81lgebra' in response.data
        assert b'Ejercicio de Geometr\xc3\xada' in response.data
        assert b'10A' in response.data

def test_docente_pagina_inicio(app, client):
    """Prueba que un docente puede acceder a su página de inicio."""
    with app.app_context():
        # Crear usuario docente
        usuario = Usuario(
            correo='docente@example.com',
            nombre_completo='Docente Test'
        )
        usuario.set_password('password123')
        
        # Asignar rol de docente
        rol = Rol.query.filter_by(nombre='docente').first()
        usuario.roles.append(rol)
        
        # Crear docente asociado
        docente = Docente(
            usuario=usuario,
            especialidad='Matemáticas'
        )
        
        db.session.add_all([usuario, docente])
        db.session.commit()

        # Iniciar sesión como docente
        response = client.post('/login', data={
            'correo': 'docente@example.com',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Acceder a la página de inicio del docente
        response = client.get('/docentes/')
        assert response.status_code == 200
        assert b'Docente Test' in response.data 