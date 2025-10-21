import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# 1. Cargar variables de entorno desde .env
# Esto hace que DATABASE_URL esté disponible en os.environ
load_dotenv()

# 2. Inicializar la aplicación Flask
app = Flask(__name__)

# 3. Función para establecer la conexión a la base de datos
def get_db_connection():
    # Obtener la URL de la base de datos del entorno
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # Esto debería ocurrir si .env no se cargó correctamente o la variable no existe
        print("Error: DATABASE_URL no está definida.")
        raise ValueError("DATABASE_URL no encontrada en las variables de entorno.")

    # Render a veces usa el esquema 'postgres://', pero psycopg2 prefiere 'postgresql://'
    # Esta línea asegura la compatibilidad, aunque Render generalmente usa el formato correcto.
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    try:
        # Establecer la conexión usando psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        # En una aplicación real, se podría intentar una reconexión o registrar el error.
        return None

# 4. Ruta principal
@app.route('/')
def index():
    db_status = "Desconectado"
    data = []

    conn = get_db_connection()

    if conn:
        try:
            # Crear un cursor para ejecutar comandos SQL
            cur = conn.cursor()

            # Ejemplo simple: Obtener la versión de PostgreSQL para confirmar la conexión
            cur.execute('SELECT version();')
            data = cur.fetchone()
            db_status = f"Conectado y versión: {data[0][:30]}..."

            # Ejemplo de creación de tabla si no existe (opcional)
            # cur.execute("CREATE TABLE IF NOT EXISTS mensajes (id SERIAL PRIMARY KEY, texto VARCHAR(255));")
            # conn.commit()

            cur.close()

        except Exception as e:
            db_status = f"Conectado, pero hubo un error en la consulta: {e}"
        finally:
            # Asegurarse de cerrar la conexión
            conn.close()
    
    # Renderizar la plantilla HTML
    return render_template('index.html', db_status=db_status)

# 5. Punto de entrada para Render.com (usa el puerto provisto por el entorno)
if __name__ == '__main__':
    # Render.com proporciona el puerto en la variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    # '0.0.0.0' hace que la app sea accesible desde el exterior, necesario para Render
    app.run(host='0.0.0.0', port=port)
