import os

# Configuración de la base de datos PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:13416059@localhost/colegio'
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:p%2E210404@localhost/colegio'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)
