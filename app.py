import os
import time
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Configuración de la conexión a PostgreSQL desde variables de entorno
DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "db_villacis")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres123")
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_db_connection():
    """Intenta conectar a PostgreSQL reintentando en caso de que la BD tardé en levantar."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            return conn
        except psycopg2.OperationalError as e:
            retries -= 1
            print(f"Esperando a PostgreSQL... Reintentos restantes: {retries}")
            time.sleep(2)
    raise Exception("No se pudo conectar a la base de datos PostgreSQL.")

def init_db():
    """Crea la tabla si no existe al iniciar la app."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id SERIAL PRIMARY KEY,
                descripcion TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Tabla 'tareas' verificada/creada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nueva_tarea = request.form.get('tarea')
        if nueva_tarea:
            cur.execute("INSERT INTO tareas (descripcion) VALUES (%s);", (nueva_tarea,))
            conn.commit()
        return redirect(url_for('index'))

    cur.execute("SELECT id, descripcion, TO_CHAR(fecha, 'YYYY-MM-DD HH24:MI:SS') FROM tareas ORDER BY id DESC;")
    tareas = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('index.html', tareas=tareas)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)