# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
# Cargar variables de entorno desde el archivo .env (solo para desarrollo local)
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Utiliza la variable de entorno DATABASE_URL.
    """
    # Obtener la URL de la base de datos.
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        # Esto solo debería ocurrir si la variable no está configurada en Render.
        print("ERROR: La variable DATABASE_URL no está definida.")
        return None

    # Ajuste de compatibilidad: psycopg2 prefiere 'postgresql://' sobre 'postgres://'.
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    conn = None
    try:
        # Intentar establecer la conexión
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error crítico al conectar a la base de datos: {e}")
        return None

# --- 3. RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    db_status = "Desconectado"
    productos = [] # Lista para almacenar los módulos
    
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()

            # 3.1. Consulta de Módulos en Tendencia
            # Obtenemos los 3 productos con el mayor rating o id para la sección de tendencia
            cur.execute('SELECT nombre, categoria, instructor, imagen_url, precio, estudiantes, rating FROM productos ORDER BY rating DESC, id DESC LIMIT 3;')
            
            # Mapear los resultados a una lista de diccionarios para fácil uso en Jinja
            productos_data = cur.fetchall()
            productos = [{
                'nombre': p[0],
                'categoria': p[1],
                'instructor': p[2],
                'imagen_url': p[3],
                'precio': p[4],
                'estudiantes': p[5],
                'rating': p[6]
            } for p in productos_data]

            # 3.2. Verificación de Conexión (opcional, pero útil)
            cur.execute('SELECT version();')
            data = cur.fetchone()
            db_status = f"✅ Conectado y versión de PostgreSQL: {data[0][:30]}..."

            cur.close()

        except Exception as e:
            db_status = f"⚠️ Error en DB/Consulta (Tabla 'productos' podría no existir): {e}"
        finally:
            conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión. Revisa la DATABASE_URL."
    
    # Renderizar la plantilla HTML, pasando el estado de la DB y la lista de productos
    return render_template('index.html', db_status=db_status, productos=productos)

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Render.com proporciona el puerto en la variable de entorno PORT.
    port = int(os.environ.get('PORT', 5000))
    
    # '0.0.0.0' hace que la app sea accesible desde el exterior, necesario para Render.
    app.run(host='0.0.0.0', port=port)