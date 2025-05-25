from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import teacher_required
from app.models import db, Usuario, Rol, Docente, Estudiante, Grado, Contenido, Ejercicio, RespuestaEstudiante
from werkzeug.security import generate_password_hash

docentes_bp = Blueprint('docentes', __name__, url_prefix='/docentes')

@docentes_bp.route('/')
@login_required
@teacher_required
def index():
    return render_template('docentes/index.html')

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

@docentes_bp.route('/ejercicios', methods=['GET', 'POST'])
@login_required
@teacher_required
def ejercicios():
    grados = Grado.query.all()
    ejercicios = Ejercicio.query.filter_by(docente_id=current_user.docente.id).all()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        enunciado = request.form.get('enunciado')
        tipo_interaccion = request.form.get('tipo_interaccion')
        grado_destinado_id = request.form.get('grado_destinado_id')
        
        nuevo_ejercicio = Ejercicio(
            titulo=titulo,
            enunciado=enunciado,
            tipo_interaccion=tipo_interaccion,
            grado_destinado_id=grado_destinado_id,
            docente_id=current_user.docente.id
        )
        
        db.session.add(nuevo_ejercicio)
        db.session.commit()
        
        flash('Ejercicio creado exitosamente', 'success')
        return redirect(url_for('docentes.ejercicios'))
    
    return render_template('docentes/ejercicios.html', grados=grados, ejercicios=ejercicios)

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
