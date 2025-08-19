from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.services.logger_service import Logger

main_bp = Blueprint('main', __name__)
log = Logger().get_logger()

@main_bp.route('/')
def index():
    """Ruta raíz: redirige según autenticación y rol"""
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        # Redirigir según rol
        if hasattr(current_user, 'has_role') and current_user.has_role('administrador'):
            return redirect(url_for('admin.index'))
        if hasattr(current_user, 'has_role') and current_user.has_role('docente'):
            return redirect(url_for('docentes.index'))
        if hasattr(current_user, 'has_role') and current_user.has_role('estudiante'):
            return redirect(url_for('estudiantes.index'))
        # Por defecto, ir al chatbot-ui si está autenticado pero sin rol específico
        return redirect(url_for('main.chatbot_ui'))
    # No autenticado: ir al login
    return redirect(url_for('auth.login'))

@main_bp.route('/chatbot-ui')
@login_required
def chatbot_ui():
    log.info("Ruta '/chatbot-ui' accedida correctamente")
    return render_template('chatbot.html')