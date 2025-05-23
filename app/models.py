from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tablas de relaciones
roles_permisos = db.Table('roles_permisos',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('rol_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE')),
    db.Column('permiso_id', db.Integer, db.ForeignKey('permisos.id', ondelete='CASCADE'))
)

usuario_rol = db.Table('usuario_rol',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE')),
    db.Column('rol_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
)

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    permisos = db.relationship('Permiso', secondary=roles_permisos, backref=db.backref('roles', lazy='dynamic'))

class Permiso(db.Model):
    __tablename__ = 'permisos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column(db.Text, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship('Rol', secondary=usuario_rol, backref=db.backref('usuarios', lazy='dynamic'))

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def has_role(self, rol_nombre):
        return any(rol.nombre == rol_nombre for rol in self.roles)

    def is_admin(self):
        return self.has_role('administrador')

    def is_teacher(self):
        return self.has_role('docente')

    def is_student(self):
        return self.has_role('estudiante')

    def get_roles(self):
        return [rol.nombre for rol in self.roles]

    def __repr__(self):
        return f'<Usuario {self.nombre_completo}>'

class Administrador(db.Model):
    __tablename__ = 'administradores'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True)
    usuario = db.relationship('Usuario', backref=db.backref('administrador', uselist=False))

class Grado(db.Model):
    __tablename__ = 'grados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    docentes = db.relationship('Docente', backref='grado', lazy=True)
    estudiantes = db.relationship('Estudiante', backref='grado', lazy=True)
    contenidos = db.relationship('Contenido', backref='grado_destinado', lazy=True)
    ejercicios = db.relationship('Ejercicio', backref='grado_destinado', lazy=True)

class Docente(db.Model):
    __tablename__ = 'docentes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True)
    especialidad = db.Column(db.String(100))
    grado_id = db.Column(db.Integer, db.ForeignKey('grados.id', ondelete='SET NULL'))
    usuario = db.relationship('Usuario', backref=db.backref('docente', uselist=False))
    contenidos = db.relationship('Contenido', backref='docente', lazy=True)
    ejercicios = db.relationship('Ejercicio', backref='docente', lazy=True)

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), unique=True)
    grado_id = db.Column(db.Integer, db.ForeignKey('grados.id', ondelete='SET NULL'))
    seccion = db.Column(db.String(10))
    usuario = db.relationship('Usuario', backref=db.backref('estudiante', uselist=False))
    respuestas = db.relationship('RespuestaEstudiante', backref='estudiante', lazy=True)

class Contenido(db.Model):
    __tablename__ = 'contenidos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    archivo_url = db.Column(db.Text, nullable=False)
    tipo_contenido = db.Column(db.String(50))
    grado_destinado_id = db.Column(db.Integer, db.ForeignKey('grados.id', ondelete='SET NULL'))
    validado = db.Column(db.Boolean, default=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('docentes.id', ondelete='SET NULL'))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

class Ejercicio(db.Model):
    __tablename__ = 'ejercicios'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    enunciado = db.Column(db.Text, nullable=False)
    tipo_interaccion = db.Column(db.String(50))
    grado_destinado_id = db.Column(db.Integer, db.ForeignKey('grados.id', ondelete='SET NULL'))
    docente_id = db.Column(db.Integer, db.ForeignKey('docentes.id', ondelete='SET NULL'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    respuestas = db.relationship('RespuestaEstudiante', backref='ejercicio', lazy=True)

class RespuestaEstudiante(db.Model):
    __tablename__ = 'respuestas_estudiantes'
    id = db.Column(db.Integer, primary_key=True)
    ejercicio_id = db.Column(db.Integer, db.ForeignKey('ejercicios.id', ondelete='CASCADE'))
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id', ondelete='CASCADE'))
    respuesta = db.Column(db.Text)
    correcta = db.Column(db.Boolean)
    retroalimentacion = db.Column(db.Text)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)

class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id', ondelete='CASCADE'))
    docente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'))
    asignatura = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    estudiante = db.relationship('Estudiante', backref=db.backref('notas', lazy=True))
    docente = db.relationship('Usuario', backref=db.backref('notas_asignadas', lazy=True))