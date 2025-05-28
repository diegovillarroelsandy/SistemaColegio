from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import student_required
from app.models import Estudiante, Ejercicio, RespuestaEstudiante, Contenido, Docente

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

@estudiantes_bp.route('/vista_juegos')
@login_required
@student_required
def vista_juegos():
    try:
        # Obtener el grado del estudiante
        estudiante = Estudiante.query.filter_by(usuario_id=current_user.id).first()
        if not estudiante:
            flash('No se encontró el estudiante', 'error')
            return redirect(url_for('estudiantes.index'))
            
        # Obtener los ejercicios destinados a este grado
        ejercicios = Ejercicio.query.filter_by(grado_destinado_id=estudiante.grado_id).all()
        
        return render_template('estudiantes/vista_juegos/index.html', 
                            ejercicios=ejercicios)
    except Exception as e:
        flash('Error al cargar los juegos: ' + str(e), 'error')
        return render_template('estudiantes/vista_juegos/index.html', 
                            ejercicios=[])
