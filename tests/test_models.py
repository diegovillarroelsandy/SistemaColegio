from app.models import Usuario, db

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