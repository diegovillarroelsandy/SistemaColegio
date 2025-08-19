import os
from dotenv import load_dotenv

# Cargar variables desde .env si existe
load_dotenv()

# Configuración de la base de datos
# Prioridad: DATABASE_URL > POSTGRES_* > SQLite local
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    pg_user = os.getenv('POSTGRES_USER')
    pg_pwd = os.getenv('POSTGRES_PASSWORD')
    pg_host = os.getenv('POSTGRES_HOST', 'localhost')
    pg_port = os.getenv('POSTGRES_PORT', '5432')
    pg_db = os.getenv('POSTGRES_DB')
    if all([pg_user, pg_pwd, pg_db]):
        DATABASE_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

# Fallback a SQLite si no hay configuración de Postgres
if not DATABASE_URL:
    # Guardar base en carpeta instance/
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance'), exist_ok=True)
    DATABASE_URL = 'sqlite:///../instance/colegio.db'

SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Clave secreta
SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
