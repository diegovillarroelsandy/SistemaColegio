from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.decorators import student_required
from app.models import Estudiante, Ejercicio, RespuestaEstudiante, Contenido, Docente, db
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
    try:
        # Obtener todas las respuestas del estudiante con la información del ejercicio
        respuestas = db.session.query(
            RespuestaEstudiante, 
            Ejercicio
        ).join(
            Ejercicio,
            RespuestaEstudiante.ejercicio_id == Ejercicio.id
        ).filter(
            RespuestaEstudiante.estudiante_id == current_user.estudiante.id
        ).order_by(
            RespuestaEstudiante.fecha_respuesta.desc()
        ).all()
        
        # Calcular estadísticas
        total_ejercicios = len(respuestas)
        ejercicios_aprobados = sum(1 for r, _ in respuestas if r.correcta)
        porcentaje_aprobados = (ejercicios_aprobados / total_ejercicios * 100) if total_ejercicios > 0 else 0
        
        return render_template(
            'estudiantes/notas/index.html',
            respuestas=respuestas,
            total_ejercicios=total_ejercicios,
            ejercicios_aprobados=ejercicios_aprobados,
            porcentaje_aprobados=round(porcentaje_aprobados, 2) if total_ejercicios > 0 else 0,
            ahora=datetime.utcnow()
        )
        
    except Exception as e:
        flash(f'Error al cargar las calificaciones: {str(e)}', 'error')
        return render_template('estudiantes/notas/index.html', 
                            respuestas=[], 
                            total_ejercicios=0,
                            ejercicios_aprobados=0,
                            porcentaje_aprobados=0)

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
        # Obtener datos del formulario
        respuesta_texto = request.form.get('respuesta', '').strip()
        
        # Validar que se haya proporcionado una respuesta
        if not respuesta_texto:
            flash('Debes proporcionar una respuesta', 'error')
            return redirect(url_for('estudiantes.responder_ejercicio', ejercicio_id=ejercicio_id))
        
        # Obtener el ejercicio
        ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
        
        # Verificar si el estudiante ya respondió este ejercicio
        respuesta_existente = RespuestaEstudiante.query.filter_by(
            estudiante_id=current_user.estudiante.id,
            ejercicio_id=ejercicio_id
        ).first()
        
        # Calcular si la respuesta es correcta (esto es un ejemplo, ajusta según tu lógica)
        # En un caso real, aquí compararías con la respuesta correcta del ejercicio
        es_correcta = True  # Esto es solo un ejemplo
        retroalimentacion = "¡Buen trabajo!" if es_correcta else "Intenta de nuevo."
        
        if respuesta_existente:
            # Actualizar respuesta existente
            respuesta_existente.respuesta = respuesta_texto
            respuesta_existente.correcta = es_correcta
            respuesta_existente.retroalimentacion = retroalimentacion
            respuesta_existente.fecha_envio = datetime.utcnow()
        else:
            # Crear nueva respuesta
            nueva_respuesta = RespuestaEstudiante(
                estudiante_id=current_user.estudiante.id,
                ejercicio_id=ejercicio_id,
                respuesta=respuesta_texto,
                correcta=es_correcta,
                retroalimentacion=retroalimentacion,
                fecha_envio=datetime.utcnow(),
                valor=100 if es_correcta else 0  # Valor numérico para la calificación
            )
            db.session.add(nueva_respuesta)
        
        db.session.commit()
        
        flash('Tu respuesta ha sido enviada correctamente', 'success')
        return redirect(url_for('estudiantes.vista_juegos'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar la respuesta: {str(e)}', 'error')
        return redirect(url_for('estudiantes.responder_ejercicio', ejercicio_id=ejercicio_id))

@estudiantes_bp.route('/guardar_puntuacion/<int:ejercicio_id>', methods=['POST'])
@login_required
@student_required
def guardar_puntuacion(ejercicio_id):
    try:
        print(f"[DEBUG] Iniciando guardar_puntuacion para ejercicio_id: {ejercicio_id}")
        print(f"[DEBUG] Usuario actual: {current_user.id} - {current_user.nombre_completo}")
        
        if not hasattr(current_user, 'estudiante') or not current_user.estudiante:
            error_msg = 'El usuario no tiene un perfil de estudiante asociado'
            print(f"[ERROR] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
            
        print(f"[DEBUG] Estudiante ID: {current_user.estudiante.id}")
        
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            error_msg = 'No se recibieron datos JSON'
            print(f"[ERROR] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
            
        puntuacion = data.get('puntuacion', 0)
        total_preguntas = data.get('total_preguntas', 1)
        
        print(f"[DEBUG] Datos recibidos - Puntuación: {puntuacion}, Total preguntas: {total_preguntas}")
        
        # Verificar que el ejercicio exista
        ejercicio = Ejercicio.query.get(ejercicio_id)
        if not ejercicio:
            error_msg = f'Ejercicio con ID {ejercicio_id} no encontrado'
            print(f"[ERROR] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 404
        
        # Calcular porcentaje de aciertos
        try:
            porcentaje = (puntuacion / (total_preguntas * 10)) * 100 if total_preguntas > 0 else 0
            es_aprobado = porcentaje >= 60  # Umbral de aprobación del 60%
        except Exception as e:
            error_msg = f'Error al calcular el porcentaje: {str(e)}'
            print(f"[ERROR] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Verificar si el estudiante ya respondió este ejercicio
        respuesta_existente = RespuestaEstudiante.query.filter_by(
            estudiante_id=current_user.estudiante.id,
            ejercicio_id=ejercicio_id
        ).first()
        
        try:
            # Crear o actualizar la respuesta
            if respuesta_existente:
                # Actualizar respuesta existente
                print(f"[DEBUG] Actualizando respuesta existente ID: {respuesta_existente.id}")
                respuesta_existente.valor = porcentaje
                respuesta_existente.correcta = es_aprobado
                respuesta_existente.retroalimentacion = f"Puntuación: {puntuacion}/{total_preguntas * 10}"
                respuesta_existente.fecha_respuesta = datetime.utcnow()
            else:
                # Crear nueva respuesta
                print("[DEBUG] Creando nueva respuesta")
                nueva_respuesta = RespuestaEstudiante(
                    estudiante_id=current_user.estudiante.id,
                    ejercicio_id=ejercicio_id,
                    respuesta=f"Ejercicio de práctica - Puntuación: {puntuacion}/{total_preguntas * 10}",
                    correcta=es_aprobado,
                    retroalimentacion=f"Puntuación: {puntuacion}/{total_preguntas * 10}",
                    fecha_respuesta=datetime.utcnow(),
                    valor=porcentaje
                )
                db.session.add(nueva_respuesta)
            
            db.session.commit()
            print("[DEBUG] Cambios guardados en la base de datos")
            
            return jsonify({
                'success': True,
                'message': 'Puntuación guardada correctamente',
                'puntuacion': puntuacion,
                'total': total_preguntas * 10,
                'porcentaje': round(porcentaje, 2),
                'aprobado': es_aprobado
            })
            
        except Exception as e:
            db.session.rollback()
            error_msg = f'Error al guardar en la base de datos: {str(e)}'
            print(f"[ERROR] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 500
        
    except Exception as e:
        db.session.rollback()
        error_msg = f'Error inesperado: {str(e)}'
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
