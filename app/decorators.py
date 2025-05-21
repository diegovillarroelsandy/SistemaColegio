from functools import wraps
from flask import redirect, url_for, flash
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
    return role_required(['estudiante'])(f)
