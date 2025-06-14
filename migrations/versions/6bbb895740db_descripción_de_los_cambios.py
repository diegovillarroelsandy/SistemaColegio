"""Descripción de los cambios

Revision ID: 6bbb895740db
Revises: 
Create Date: 2025-06-02 08:07:51.293091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bbb895740db'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('grados',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('permisos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('correo', sa.String(length=100), nullable=False),
    sa.Column('contrasena_hash', sa.Text(), nullable=False),
    sa.Column('nombre_completo', sa.String(length=100), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('correo')
    )
    op.create_table('administradores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id')
    )
    op.create_table('docentes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('especialidad', sa.String(length=100), nullable=True),
    sa.Column('grado_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['grado_id'], ['grados.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id')
    )
    op.create_table('estudiantes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('grado_id', sa.Integer(), nullable=True),
    sa.Column('seccion', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['grado_id'], ['grados.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id')
    )
    op.create_table('roles_permisos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.Column('permiso_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['permiso_id'], ['permisos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usuario_rol',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contenidos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=100), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('archivo_url', sa.Text(), nullable=False),
    sa.Column('tipo_contenido', sa.String(length=50), nullable=True),
    sa.Column('grado_destinado_id', sa.Integer(), nullable=True),
    sa.Column('validado', sa.Boolean(), nullable=True),
    sa.Column('docente_id', sa.Integer(), nullable=True),
    sa.Column('fecha_subida', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['docente_id'], ['docentes.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['grado_destinado_id'], ['grados.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ejercicios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=100), nullable=True),
    sa.Column('enunciado', sa.Text(), nullable=False),
    sa.Column('tipo_interaccion', sa.String(length=50), nullable=True),
    sa.Column('archivo_url', sa.String(length=255), nullable=True),
    sa.Column('grado_destinado_id', sa.Integer(), nullable=True),
    sa.Column('docente_id', sa.Integer(), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['docente_id'], ['docentes.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['grado_destinado_id'], ['grados.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('respuestas_estudiantes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ejercicio_id', sa.Integer(), nullable=True),
    sa.Column('estudiante_id', sa.Integer(), nullable=True),
    sa.Column('respuesta', sa.Text(), nullable=True),
    sa.Column('correcta', sa.Boolean(), nullable=True),
    sa.Column('retroalimentacion', sa.Text(), nullable=True),
    sa.Column('fecha_respuesta', sa.DateTime(), nullable=True),
    sa.Column('valor', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['ejercicio_id'], ['ejercicios.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['estudiante_id'], ['estudiantes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('respuestas_estudiantes')
    op.drop_table('ejercicios')
    op.drop_table('contenidos')
    op.drop_table('usuario_rol')
    op.drop_table('roles_permisos')
    op.drop_table('estudiantes')
    op.drop_table('docentes')
    op.drop_table('administradores')
    op.drop_table('usuarios')
    op.drop_table('roles')
    op.drop_table('permisos')
    op.drop_table('grados')
    # ### end Alembic commands ###
