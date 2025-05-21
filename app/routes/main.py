from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import admin_required
from app.services.logger_service import Logger

main_bp = Blueprint('main', __name__)
log = Logger().get_logger()

@main_bp.route('/')
@login_required
@admin_required
def index():
    log.info("Ruta '/' accedida  correctamente")
    return render_template('index.html')