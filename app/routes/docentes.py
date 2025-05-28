from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from app.decorators import teacher_required
import os
from werkzeug.utils import secure_filename
from app.models import db, Usuario, Rol, Docente, Estudiante, Grado, Contenido, Ejercicio, RespuestaEstudiante
from werkzeug.security import generate_password_hash

docentes_bp = Blueprint('docentes', __name__, url_prefix='/docentes')

@docentes_bp.route('/')
@login_required
@teacher_required
def index():
    # Estadísticas para el dashboard docente
    docente = current_user.docente
    grado_id = docente.grado_id if docente else None

    estudiantes_total = Estudiante.query.filter_by(grado_id=grado_id).count() if grado_id else 0
    ejercicios_total = Ejercicio.query.filter_by(docente_id=docente.id).count() if docente else 0
    notas_total = RespuestaEstudiante.query \
        .join(Estudiante, RespuestaEstudiante.estudiante_id == Estudiante.id) \
        .join(Ejercicio, RespuestaEstudiante.ejercicio_id == Ejercicio.id) \
        .filter(Estudiante.grado_id == grado_id, Ejercicio.docente_id == docente.id, RespuestaEstudiante.valor != None).count() if docente and grado_id else 0
    contenidos_total = Contenido.query.filter_by(docente_id=docente.id).count() if docente else 0

    return render_template(
        'docentes/index.html',
        estudiantes_total=estudiantes_total,
        ejercicios_total=ejercicios_total,
        notas_total=notas_total,
        contenidos_total=contenidos_total
    )

@docentes_bp.route('/estudiantes')
@login_required
@teacher_required
def estudiantes():
    grado_id = current_user.docente.grado_id if current_user.docente else None
    estudiantes = Estudiante.query.filter_by(grado_id=grado_id).all()
    return render_template('docentes/estudiantes.html', estudiantes=estudiantes)

@docentes_bp.route('/estudiantes/<int:id>')
@login_required
@teacher_required
def ver_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    
    # Seguridad: verifica que el docente solo vea sus propios estudiantes
    if estudiante.grado_id != current_user.docente.grado_id:
        flash("No tienes permiso para ver este estudiante.", "danger")
        return redirect(url_for('docentes.estudiantes'))

    return render_template('docentes/ver_estudiante.html', estudiante=estudiante)

@docentes_bp.route('/contenido', methods=['GET', 'POST'])
@login_required
@teacher_required
def contenido():
    grados = Grado.query.all()
    contenidos = Contenido.query.filter_by(docente_id=current_user.docente.id).all()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        archivo_url = request.form.get('archivo_url')
        tipo_contenido = request.form.get('tipo_contenido')
        grado_destinado_id = request.form.get('grado_destinado_id')
        
        nuevo_contenido = Contenido(
            titulo=titulo,
            descripcion=descripcion,
            archivo_url=archivo_url,
            tipo_contenido=tipo_contenido,
            grado_destinado_id=grado_destinado_id,
            docente_id=current_user.docente.id
        )
        
        db.session.add(nuevo_contenido)
        db.session.commit()
        
        flash('Contenido creado exitosamente', 'success')
        return redirect(url_for('docentes.contenido'))
    
    return render_template('docentes/contenido.html', grados=grados, contenidos=contenidos)


@docentes_bp.route('/calificaciones')
@login_required
@teacher_required
def calificaciones():
    grado_id = current_user.docente.grado_id if current_user.docente else None
    estudiantes = Estudiante.query.filter_by(grado_id=grado_id).all()
    return render_template('docentes/calificaciones.html', estudiantes=estudiantes)

@docentes_bp.route('/notas')
@login_required
@teacher_required
def notas():
    grado_id = current_user.docente.grado_id
    notas = (
        RespuestaEstudiante.query
        .join(Estudiante)
        .join(Ejercicio)
        .filter(Estudiante.grado_id == grado_id, RespuestaEstudiante.valor != None)
        .all()
    )
    return render_template('docentes/notas.html', notas=notas)

@docentes_bp.route('/notas/agregar', methods=['GET', 'POST'])
@login_required
@teacher_required
def agregar_nota():
    grado_id = current_user.docente.grado_id
    estudiantes = Estudiante.query.filter_by(grado_id=grado_id).all()
    ejercicios = Ejercicio.query.filter_by(grado_destinado_id=grado_id, docente_id=current_user.docente.id).all()

    if request.method == 'POST':
        estudiante_id = request.form.get('estudiante_id')
        ejercicio_id = request.form.get('ejercicio_id')
        valor = request.form.get('valor')

        if not estudiante_id or not ejercicio_id or not valor:
            flash('Todos los campos son obligatorios.', 'warning')
        else:
            try:
                valor = float(valor)
                nueva_respuesta = RespuestaEstudiante(
                    estudiante_id=estudiante_id,
                    ejercicio_id=ejercicio_id,
                    valor=valor
                )
                db.session.add(nueva_respuesta)
                db.session.commit()
                flash('Nota agregada exitosamente.', 'success')
                return redirect(url_for('docentes.notas'))
            except ValueError:
                flash('La nota debe ser un número válido.', 'danger')

    return render_template('docentes/agregar_nota.html', estudiantes=estudiantes, ejercicios=ejercicios)

@docentes_bp.route('/notas/editar/<int:respuesta_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def editar_nota(respuesta_id):
    respuesta = RespuestaEstudiante.query.get_or_404(respuesta_id)

    if respuesta.estudiante.grado_id != current_user.docente.grado_id:
        flash('No tienes permiso para editar esta nota.', 'danger')
        return redirect(url_for('docentes.notas'))

    if request.method == 'POST':
        nuevo_valor = request.form.get('valor')
        try:
            respuesta.valor = float(nuevo_valor)
            db.session.commit()
            flash('Nota actualizada correctamente.', 'success')
            return redirect(url_for('docentes.notas'))
        except ValueError:
            flash('Valor inválido.', 'danger')

    return render_template('docentes/editar_nota.html', respuesta=respuesta)

@docentes_bp.route('/notas/eliminar/<int:respuesta_id>', methods=['POST'])
@login_required
@teacher_required
def eliminar_nota(respuesta_id):
    respuesta = RespuestaEstudiante.query.get_or_404(respuesta_id)

    if respuesta.estudiante.grado_id != current_user.docente.grado_id:
        flash('No tienes permiso para eliminar esta nota.', 'danger')
        return redirect(url_for('docentes.notas'))

    db.session.delete(respuesta)
    db.session.commit()
    flash('Nota eliminada correctamente.', 'success')
    return redirect(url_for('docentes.notas'))


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'html'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@docentes_bp.route('/ejercicios')
@login_required
@teacher_required
def ejercicios():
    ejercicios = Ejercicio.query.filter_by(docente_id=current_user.docente.id).order_by(Ejercicio.fecha_creacion.desc()).all()
    return render_template('docentes/ejercicios/index.html', ejercicios=ejercicios)

@docentes_bp.route('/ejercicios/nuevo', methods=['GET', 'POST'])
@login_required
@teacher_required
def nuevo_ejercicio():
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo')
            enunciado = request.form.get('enunciado')
            tipo_interaccion = request.form.get('tipo_interaccion')
            grado_destinado_id = request.form.get('grado_destinado_id')

            if not all([titulo, tipo_interaccion, grado_destinado_id]):
                flash('Los campos marcados con * son obligatorios', 'error')
                return redirect(request.url)

            grado = Grado.query.get(grado_destinado_id)
            if not grado:
                flash('El grado seleccionado no existe', 'error')
                return redirect(request.url)

            archivo_url = None
            if 'archivo' in request.files and request.files['archivo'].filename != '':
                archivo = request.files['archivo']
                if archivo and allowed_file(archivo.filename):
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'ejercicios')
                    os.makedirs(upload_folder, exist_ok=True)
                    filename = secure_filename(archivo.filename)
                    unique_filename = f"{os.urandom(8).hex()}_{filename}"
                    filepath = os.path.join(upload_folder, unique_filename)
                    archivo.save(filepath)
                    archivo_url = f'uploads/ejercicios/{unique_filename}'.replace('\\', '/')
                else:
                    flash('Tipo de archivo no permitido', 'error')
                    return redirect(request.url)

            ejercicio = Ejercicio(
                titulo=titulo,
                enunciado=enunciado,
                tipo_interaccion=tipo_interaccion,
                grado_destinado_id=grado_destinado_id,
                docente_id=current_user.docente.id,
                archivo_url=archivo_url
            )
            db.session.add(ejercicio)
            db.session.commit()

            flash('Ejercicio creado exitosamente', 'success')
            return redirect(url_for('docentes.ver_ejercicio', id=ejercicio.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear ejercicio: {str(e)}")
            flash('Ocurrió un error al crear el ejercicio', 'error')
            return redirect(request.url)

    grados = Grado.query.all()
    return render_template('docentes/ejercicios/nuevo.html', grados=grados)

@docentes_bp.route('/ejercicios/<int:id>')
@login_required
@teacher_required
def ver_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    if ejercicio.docente_id != current_user.docente.id:
        abort(403)
    return render_template('docentes/ejercicios/ver.html', ejercicio=ejercicio)

@docentes_bp.route('/ejercicios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@teacher_required
def editar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    if ejercicio.docente_id != current_user.docente.id:
        abort(403)

    if request.method == 'POST':
        try:
            ejercicio.titulo = request.form.get('titulo')
            ejercicio.enunciado = request.form.get('enunciado')
            ejercicio.tipo_interaccion = request.form.get('tipo_interaccion')
            ejercicio.grado_destinado_id = request.form.get('grado_destinado_id')

            if not all([ejercicio.titulo, ejercicio.enunciado, ejercicio.tipo_interaccion, ejercicio.grado_destinado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(request.url)

            grado = Grado.query.get(ejercicio.grado_destinado_id)
            if not grado:
                flash('El grado seleccionado no existe', 'error')
                return redirect(request.url)

            if 'archivo' in request.files:
                archivo = request.files['archivo']
                if archivo.filename != '':
                    if archivo and allowed_file(archivo.filename):
                        if ejercicio.archivo_url:
                            try:
                                filepath = os.path.join(current_app.static_folder, ejercicio.archivo_url)
                                if os.path.exists(filepath):
                                    os.remove(filepath)
                            except Exception as e:
                                current_app.logger.error(f"Error al eliminar archivo anterior: {str(e)}")

                        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'ejercicios')
                        os.makedirs(upload_folder, exist_ok=True)
                        filename = secure_filename(archivo.filename)
                        unique_filename = f"{os.urandom(8).hex()}_{filename}"
                        filepath = os.path.join(upload_folder, unique_filename)
                        archivo.save(filepath)
                        ejercicio.archivo_url = f'uploads/ejercicios/{unique_filename}'.replace('\\', '/')
                    else:
                        flash('Tipo de archivo no permitido', 'error')
                        return redirect(request.url)

            db.session.commit()
            flash('Ejercicio actualizado exitosamente', 'success')
            return redirect(url_for('docentes.ver_ejercicio', id=ejercicio.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar ejercicio: {str(e)}")
            flash('Ocurrió un error al actualizar el ejercicio', 'error')
            return redirect(request.url)

    grados = Grado.query.all()
    return render_template('docentes/ejercicios/editar.html', ejercicio=ejercicio, grados=grados)

@docentes_bp.route('/ejercicios/<int:id>/eliminar', methods=['POST'])
@login_required
@teacher_required
def eliminar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    if ejercicio.docente_id != current_user.docente.id:
        abort(403)

    try:
        if ejercicio.archivo_url:
            try:
                filepath = os.path.join(current_app.static_folder, ejercicio.archivo_url)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                current_app.logger.error(f"Error al eliminar archivo: {str(e)}")

        db.session.delete(ejercicio)
        db.session.commit()

        flash('Ejercicio eliminado exitosamente', 'success')
        return redirect(url_for('docentes.ejercicios'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar ejercicio: {str(e)}")
        flash('Ocurrió un error al eliminar el ejercicio', 'error')
        return redirect(url_for('docentes.ejercicios'))

@docentes_bp.route('/ejercicios/<int:id>/eliminar-archivo', methods=['POST'])
@login_required
@teacher_required
def eliminar_archivo_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    if ejercicio.docente_id != current_user.docente.id:
        abort(403)

    try:
        if ejercicio.archivo_url:
            try:
                filepath = os.path.join(current_app.static_folder, ejercicio.archivo_url)
                if os.path.exists(filepath):
                    os.remove(filepath)
                ejercicio.archivo_url = None
                db.session.commit()
                flash('Archivo eliminado exitosamente', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error al eliminar archivo: {str(e)}")
                flash('Ocurrió un error al eliminar el archivo', 'error')
        else:
            flash('El ejercicio no tiene archivo adjunto', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar archivo: {str(e)}")
        flash('Ocurrió un error al procesar la solicitud', 'error')

    return redirect(url_for('docentes.editar_ejercicio', id=ejercicio.id))

@docentes_bp.route('/ejercicios/<int:ejercicio_id>/respuestas/<int:respuesta_id>/calificar', methods=['GET', 'POST'])
@login_required
@teacher_required
def calificar_respuesta(ejercicio_id, respuesta_id):
    respuesta = RespuestaEstudiante.query.get_or_404(respuesta_id)

    if respuesta.ejercicio_id != ejercicio_id or respuesta.ejercicio.docente_id != current_user.docente.id:
        abort(403)

    if request.method == 'POST':
        try:
            respuesta.correcta = request.form.get('correcta') == 'true'
            respuesta.retroalimentacion = request.form.get('retroalimentacion', '')
            db.session.commit()
            flash('Respuesta calificada exitosamente', 'success')
            return redirect(url_for('docentes.ver_ejercicio', id=ejercicio_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al calificar respuesta: {str(e)}")
            flash('Ocurrió un error al calificar la respuesta', 'error')

    return render_template('docentes/ejercicios/calificar_respuesta.html', respuesta=respuesta, ejercicio=respuesta.ejercicio)

