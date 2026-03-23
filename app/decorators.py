from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user
from flask import request

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if not any(current_user.has_role(role) for role in roles):
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decoradores específicos por rol
def admin_required(f):
    return role_required(['administrador'])(f)

def teacher_required(f):
    return role_required(['docente'])(f)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.debug(
            "Verificando estudiante_required para usuario: %s",
            current_user.id if current_user.is_authenticated else 'No autenticado'
        )
        if not current_user.is_authenticated:
            current_app.logger.debug("Usuario no autenticado, redirigiendo a login")
            return redirect(url_for('auth.login'))
            
        current_app.logger.debug(
            "Roles del usuario: %s",
            [r.nombre for r in current_user.roles] if hasattr(current_user, 'roles') else 'Sin roles'
        )
        
        if not any(role.nombre == 'estudiante' for role in current_user.roles):
            current_app.logger.debug("Usuario no tiene rol de estudiante")
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('main.index'))
            
        current_app.logger.debug("Usuario tiene rol de estudiante, permitiendo acceso")
        return f(*args, **kwargs)
    return decorated_function
