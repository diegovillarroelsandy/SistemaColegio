from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import student_required
from app.models import Estudiante, Ejercicio, RespuestaEstudiante, Contenido, Docente
from datetime import datetime

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
        # Obtener todos los ejercicios disponibles
        ejercicios = Ejercicio.query.all()
        
        return render_template('estudiantes/vista_juegos/index.html', 
                            ejercicios=ejercicios)
    except Exception as e:
        flash('Error al cargar los ejercicios: ' + str(e), 'error')
        return render_template('estudiantes/vista_juegos/index.html', 
                            ejercicios=[])

@estudiantes_bp.route('/responder/<int:ejercicio_id>')
@login_required
@student_required
def responder_ejercicio(ejercicio_id):
    try:
        ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
        return render_template('estudiantes/vista_juegos/juego.html', ejercicio=ejercicio)
    except Exception as e:
        flash('Error al cargar el juego: ' + str(e), 'error')
        return redirect(url_for('estudiantes.vista_juegos'))

@estudiantes_bp.route('/guardar_respuesta/<int:ejercicio_id>', methods=['POST'])
@login_required
@student_required
def guardar_respuesta(ejercicio_id):
    try:
        ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
        respuesta = request.form.get('respuesta')
        
        if not respuesta:
            flash('Por favor, ingresa una respuesta.', 'warning')
            return redirect(url_for('estudiantes.vista_juegos'))
        
        # Crear una nueva respuesta
        nueva_respuesta = RespuestaEstudiante(
            estudiante_id=current_user.estudiante.id,
            ejercicio_id=ejercicio_id,
            respuesta=respuesta,
            fecha_envio=datetime.utcnow()
        )
        
        db.session.add(nueva_respuesta)
        db.session.commit()
        
        flash('Respuesta guardada exitosamente!', 'success')
        return redirect(url_for('estudiantes.vista_juegos'))
        
    except Exception as e:
        flash('Error al guardar la respuesta: ' + str(e), 'error')
        return redirect(url_for('estudiantes.vista_juegos'))
    except Exception as e:
        flash('Error al cargar los ejercicios: ' + str(e), 'error')
        return render_template('estudiantes/vista_juegos/index.html', 
                            ejercicios=[],
                            grado_id=None)

