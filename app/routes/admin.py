from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import db, Usuario, Rol, Docente, Estudiante, Grado
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Obtener estadísticas
    usuarios_total = Usuario.query.count()
    estudiantes_total = Estudiante.query.count()
    docentes_total = Docente.query.count()
    grados_total = Grado.query.count()
    
    return render_template('admin/index.html',
                         usuarios_total=usuarios_total,
                         estudiantes_total=estudiantes_total,
                         docentes_total=docentes_total,
                         grados_total=grados_total)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios/index.html', usuarios=usuarios)

@admin_bp.route('/usuarios/seleccion')
@login_required
@admin_required
def seleccion_usuario():
    return render_template('admin/usuarios/seleccion.html')



@admin_bp.route('/docentes')
@login_required
@admin_required
def docentes():
    docentes = Docente.query.all()
    return render_template('admin/docentes/index.html', docentes=docentes)

@admin_bp.route('/docentes/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_docente():
    if request.method == 'POST':
        correo = request.form.get('correo')
        nombre_completo = request.form.get('nombre_completo')
        password = request.form.get('password')
        especialidad = request.form.get('especialidad')
        grado_id = request.form.get('grado_id')
        
        # Verificar si el correo ya existe
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('admin.nuevo_docente'))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            correo=correo,
            nombre_completo=nombre_completo
        )
        nuevo_usuario.set_password(password)
        
        # Asignar rol de docente
        rol_obj = Rol.query.filter_by(nombre='docente').first()
        if not rol_obj:
            flash('Rol no válido', 'error')
            return redirect(url_for('admin.nuevo_docente'))
        
        nuevo_usuario.roles.append(rol_obj)
        
        try:
            # Guardar el usuario primero
            db.session.add(nuevo_usuario)
            db.session.commit()  # Guardar el usuario antes de crear el docente
            
            # Verificar que el usuario se guardó correctamente
            usuario_guardado = Usuario.query.get(nuevo_usuario.id)
            if not usuario_guardado:
                raise ValueError('El usuario no se guardó correctamente en la base de datos')
            
            # Crear docente con el ID del usuario
            nuevo_docente = Docente(
                usuario_id=usuario_guardado.id,
                especialidad=especialidad,
                grado_id=grado_id
            )
            db.session.add(nuevo_docente)
            db.session.commit()
            
            flash('Docente creado exitosamente', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()  # Revertir cambios si algo falla
            flash('Error al crear el docente: {}'.format(str(e)), 'error')
            return redirect(url_for('admin.nuevo_docente'))
        
        flash('Docente creado exitosamente', 'success')
        return redirect(url_for('admin.docentes'))
    
    grados = Grado.query.all()
    return render_template('admin/docentes/nuevo.html', grados=grados)

@admin_bp.route('/docentes/<int:id>')
@login_required
@admin_required
def ver_docente(id):
    docente = Docente.query.get_or_404(id)
    # Verificar si el usuario está correctamente relacionado
    if not docente.usuario:
        flash('El docente no tiene un usuario asociado', 'warning')
    return render_template('admin/docentes/ver.html', docente=docente)

@admin_bp.route('/docentes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_docente(id):
    docente = Docente.query.get_or_404(id)
    
    if request.method == 'POST':
        # Verificar si el usuario existe
        if not docente.usuario:
            flash('No se puede editar un docente sin usuario asociado', 'error')
            return redirect(url_for('admin.docentes'))
            
        docente.usuario.nombre_completo = request.form.get('nombre_completo')
        docente.especialidad = request.form.get('especialidad')
        docente.grado_id = request.form.get('grado_id')
        
        try:
            db.session.commit()
            flash('Docente actualizado exitosamente', 'success')
            return redirect(url_for('admin.docentes'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el docente: {}'.format(str(e)), 'error')
            return redirect(url_for('admin.docentes'))
    
    grados = Grado.query.all()
    return render_template('admin/docentes/editar.html', docente=docente, grados=grados)

@admin_bp.route('/docentes/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_docente(id):
    docente = Docente.query.get_or_404(id)
    
    # Eliminar usuario asociado
    db.session.delete(docente.usuario)
    db.session.commit()
    
    flash('Docente eliminado exitosamente', 'success')
    return redirect(url_for('admin.docentes'))

@admin_bp.route('/estudiantes')
@login_required
@admin_required
def estudiantes():
    estudiantes = Estudiante.query.all()
    return render_template('admin/estudiantes/index.html', estudiantes=estudiantes, Docente=Docente)

@admin_bp.route('/estudiantes/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_estudiante():
    if request.method == 'POST':
        correo = request.form.get('correo')
        nombre_completo = request.form.get('nombre_completo')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        grado_id = request.form.get('grado_id')
        seccion = request.form.get('seccion')
        
        # Validar contraseñas
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('admin.nuevo_estudiante'))
        
        # Verificar si el correo ya existe
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('admin.nuevo_estudiante'))
        
        # Verificar que se haya seleccionado un grado
        if not grado_id:
            flash('Debe seleccionar un grado para el estudiante', 'error')
            return redirect(url_for('admin.nuevo_estudiante'))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            correo=correo,
            nombre_completo=nombre_completo
        )
        nuevo_usuario.set_password(password)
        
        # Asignar rol de estudiante
        rol_obj = Rol.query.filter_by(nombre='estudiante').first()
        if not rol_obj:
            flash('Rol no válido', 'error')
            return redirect(url_for('admin.nuevo_estudiante'))
        
        nuevo_usuario.roles.append(rol_obj)
        
        # Guardar el usuario primero para obtener su ID
        db.session.add(nuevo_usuario)
        db.session.flush()  # Esto genera el ID del usuario
        
        # Crear estudiante con el ID del usuario
        nuevo_estudiante = Estudiante(
            usuario_id=nuevo_usuario.id,
            grado_id=grado_id,
            seccion=seccion
        )
        db.session.add(nuevo_estudiante)
        
        db.session.commit()
        
        flash('Estudiante creado exitosamente', 'success')
        return redirect(url_for('admin.estudiantes'))
    
    grados = Grado.query.all()
    docentes = Docente.query.all()  # Obtener todos los docentes
    return render_template('admin/estudiantes/nuevo.html', grados=grados, docentes=docentes)

@admin_bp.route('/estudiantes/<int:id>')
@login_required
@admin_required
def ver_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    docentes = Docente.query.all()
    return render_template('admin/estudiantes/ver.html', estudiante=estudiante, docentes=docentes)

@admin_bp.route('/estudiantes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    
    if request.method == 'POST':
        estudiante.usuario.nombre_completo = request.form.get('nombre_completo')
        estudiante.grado_id = request.form.get('grado_id')
        estudiante.seccion = request.form.get('seccion')
        
        # Actualizar contraseña si se proporciona
        nueva_contraseña = request.form.get('password')
        if nueva_contraseña:
            estudiante.usuario.set_password(nueva_contraseña)
        
        db.session.commit()
        flash('Estudiante actualizado exitosamente', 'success')
        return redirect(url_for('admin.estudiantes'))
    
    grados = Grado.query.all()
    return render_template('admin/estudiantes/editar.html', estudiante=estudiante, grados=grados)

@admin_bp.route('/estudiantes/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    
    # Eliminar usuario asociado
    db.session.delete(estudiante.usuario)
    db.session.commit()
    
    flash('Estudiante eliminado exitosamente', 'success')
    return redirect(url_for('admin.estudiantes'))

@admin_bp.route('/roles')
@login_required
@admin_required
def roles():
    # Obtener todos los roles con sus usuarios relacionados
    roles = Rol.query.all()
    # Convertir las consultas de usuarios en listas
    for rol in roles:
        rol.usuarios = list(rol.usuarios)
    return render_template('admin/roles/index.html', roles=roles)

@admin_bp.route('/roles/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_rol():
    # Esta ruta está deshabilitada
    return redirect(url_for('admin.roles'))

@admin_bp.route('/roles/nuevo-predefinido', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_rol_predefinido():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        # Verificar si el rol ya existe
        if Rol.query.filter_by(nombre=nombre).first():
            flash('El rol ya existe', 'error')
            return redirect(url_for('admin.nuevo_rol_predefinido'))
        
        nuevo_rol = Rol(
            nombre=nombre,
            descripcion=descripcion
        )
        db.session.add(nuevo_rol)
        db.session.commit()
        
        flash('Rol creado exitosamente', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin/roles/nuevo.html')

@admin_bp.route('/roles/<int:id>')
@login_required
@admin_required
def ver_rol(id):
    rol = Rol.query.get_or_404(id)
    return render_template('admin/roles/ver.html', rol=rol)

@admin_bp.route('/roles/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_rol(id):
    rol = Rol.query.get_or_404(id)
    
    if request.method == 'POST':
        rol.nombre = request.form.get('nombre')
        rol.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Rol actualizado exitosamente', 'success')
        return redirect(url_for('admin.roles'))
    
    return render_template('admin/roles/editar.html', rol=rol)

@admin_bp.route('/roles/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_rol(id):
    rol = Rol.query.get_or_404(id)
    
    # Verificar si el rol está siendo usado
    if rol.usuarios.count() > 0:
        flash('No se puede eliminar un rol que está siendo usado por usuarios', 'error')
        return redirect(url_for('admin.roles'))
    
    db.session.delete(rol)
    db.session.commit()
    
    flash('Rol eliminado exitosamente', 'success')
    return redirect(url_for('admin.roles'))

@admin_bp.route('/grados')
@login_required
@admin_required
def grados():
    grados = Grado.query.all()
    return render_template('admin/grados/index.html', grados=grados)

@admin_bp.route('/grados/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_grado():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        # Verificar si el grado ya existe
        if Grado.query.filter_by(nombre=nombre).first():
            flash('El grado ya existe', 'error')
            return redirect(url_for('admin.nuevo_grado'))
        
        nuevo_grado = Grado(
            nombre=nombre,
            descripcion=descripcion
        )
        db.session.add(nuevo_grado)
        db.session.commit()
        
        flash('Grado creado exitosamente', 'success')
        return redirect(url_for('admin.grados'))
    
    return render_template('admin/grados/nuevo.html')

@admin_bp.route('/grados/<int:id>')
@login_required
@admin_required
def ver_grado(id):
    grado = Grado.query.get_or_404(id)
    return render_template('admin/grados/ver.html', grado=grado)

@admin_bp.route('/grados/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_grado(id):
    grado = Grado.query.get_or_404(id)
    
    if request.method == 'POST':
        grado.nombre = request.form.get('nombre')
        grado.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Grado actualizado exitosamente', 'success')
        return redirect(url_for('admin.grados'))
    
    return render_template('admin/grados/editar.html', grado=grado)

@admin_bp.route('/grados/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_grado(id):
    grado = Grado.query.get_or_404(id)
    
    # Verificar si el grado está siendo usado
    if Docente.query.filter_by(grado_id=id).count() > 0 or Estudiante.query.filter_by(grado_id=id).count() > 0:
        flash('No se puede eliminar un grado que está siendo usado por usuarios', 'error')
        return redirect(url_for('admin.grados'))
    
    db.session.delete(grado)
    db.session.commit()
    
    flash('Grado eliminado exitosamente', 'success')
    return redirect(url_for('admin.grados'))
