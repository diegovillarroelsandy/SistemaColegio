from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import student_required
from app.models import Estudiante, Ejercicio, RespuestaEstudiante, Contenido

estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/estudiantes')

@estudiantes_bp.route('/')
@login_required
@student_required
def index():
    return render_template('estudiantes/index.html')

@estudiantes_bp.route('/notas')
@login_required
@student_required
def notas():
    return render_template('estudiantes/notas/index.html')

