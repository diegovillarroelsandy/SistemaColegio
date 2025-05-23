from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, Usuario, Rol
from werkzeug.security import generate_password_hash
from ..forms.auth import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(correo=form.correo.data).first()
        
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
           
            if usuario.has_role('administrador'):
                return redirect(url_for('admin.index'))
            elif usuario.has_role('docente'):
                return redirect(url_for('docentes.index'))
            elif usuario.has_role('estudiante'):
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        nombre_completo = request.form.get('nombre_completo')
        rol = request.form.get('rol')
        
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('auth.register'))

        nuevo_usuario = Usuario(
            correo=correo,
            nombre_completo=nombre_completo
        )
        nuevo_usuario.set_password(password)
        
        # Asignar rol
        rol_obj = Rol.query.filter_by(nombre=rol).first()
        if not rol_obj:
            flash('Rol no válido', 'error')
            return redirect(url_for('auth.register'))
        
        nuevo_usuario.roles.append(rol_obj)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))