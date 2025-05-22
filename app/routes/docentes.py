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


@docentes_bp.route('/estudiante/<int:id>')
@login_required
@teacher_required
def ver_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    # Verificar que el estudiante pertenece al grado del docente
    if estudiante.grado_id != current_user.docente.grado_id:
        flash('No tienes permiso para ver este estudiante', 'error')
        return redirect(url_for('docentes.estudiantes'))
    return render_template('docentes/ver.html', estudiante=estudiante)


