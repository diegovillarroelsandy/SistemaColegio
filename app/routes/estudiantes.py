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
    # Obtener el grado del estudiante
    try:
        grado_id = current_user.estudiante.grado_id
        
        # Obtener los docentes asignados a este grado
        docentes = Docente.query.filter_by(grado_id=grado_id).all()
        
        # Obtener las materias únicas de los docentes
        materias = set()
        for docente in docentes:
            if docente.especialidad:
                materias.add(docente.especialidad)
        
        return render_template('estudiantes/vista_juegos/index.html', materias=materias)
    except Exception as e:
        flash('Error al cargar las materias: ' + str(e), 'error')
        return render_template('estudiantes/vista_juegos/index.html', materias=['Error al cargar materias'])

