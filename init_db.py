from app import create_app, db
from app.models import Rol, Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear roles si no existen
    roles = ['administrador', 'docente', 'estudiante']
    for rol_nombre in roles:
        if not Rol.query.filter_by(nombre=rol_nombre).first():
            rol = Rol(nombre=rol_nombre)
            db.session.add(rol)
    
    # Crear usuario administrador si no existe
    admin_correo = "admin@colegio.com"
    admin = Usuario.query.filter_by(correo=admin_correo).first()
    
    if not admin:
        admin = Usuario(
            correo=admin_correo,
            nombre_completo="Administrador Principal",
        )
        admin.set_password("admin123")  # Contraseña inicial
        
        # Asignar rol de administrador
        rol_admin = Rol.query.filter_by(nombre='administrador').first()
        if rol_admin:
            admin.roles.append(rol_admin)
            
        db.session.add(admin)
    
    db.session.commit()
    print("Base de datos inicializada con éxito!")
    print(f"Usuario administrador creado: {admin_correo}")
    print("Contraseña inicial: admin123")
