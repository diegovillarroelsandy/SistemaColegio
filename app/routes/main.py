from flask import Blueprint, render_template
from app.services.logger_service import Logger

main_bp = Blueprint('main', __name__)
log = Logger().get_logger()
@main_bp.route('/')
def index():
    log.info("Ruta '/' accedida  correctamente")
    return render_template('index.html')