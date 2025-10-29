# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# --- NOTA CRÍTICA: ELIMINAMOS MODULOS_INFO ---
# Definimos una lista de temas genéricos SÓLO para asegurar que los productos tengan contexto
# si la base de datos sólo contiene los campos básicos (nombre, precio, etc.)
GENERIC_MATH_TOPICS = [
    ("MÓDULO NÚMEROS (6°)", "NÚMEROS Y OPERACIONES", "Valor Posicional", "Polinomios Aritméticos"),
    ("MÓDULO FRACCIONES (6°)", "FRACCIONES Y DECIMALES", "Operaciones Básicas", "Conversión Decimal"),
    ("MÓDULO DIVISIBILIDAD (6°)", "MÚLTIPLOS Y DIVISORES", "M.C.M. y M.C.D.", "Criterios de Divisibilidad"),
    ("MÓDULO GEOMETRÍA (6°)", "GEOMETRÍA BÁSICA", "Área y Perímetro", "Clasificación de Figuras"),
    ("MÓDULO ESTADÍSTICA (6°)", "ESTADÍSTICA Y AZAR", "Tablas de Frecuencia", "Probabilidad Elemental"),
    ("MÓDULO PROPORCIONES (6°)", "RAZONES Y PROPORCIONES", "Regla de Tres", "Escalas y Mapas"),
]

# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("ERROR: La variable DATABASE_URL no está definida.")
        return None
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error crítico al conectar a la base de datos: {e}")
        return None

# --- 3. RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    db_status = "Desconectado"
    productos = []  # Inicializar la lista de productos
    
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()

            # 1. Obtener la versión de PostgreSQL
            cur.execute('SELECT version();')
            data = cur.fetchone()
            db_status = f"✅ Conectado y versión de PostgreSQL: {data[0][:30]}..."

            # 2. Intentar cargar los productos (Ajusta la consulta a tu esquema real)
            # Nota: Los campos deben coincidir con lo que esperas en el HTML (nombre, precio, etc.)
            cur.execute("SELECT nombre, precio, categoria, instructor, tema_1, tema_2, estudiantes, rating, imagen_url FROM productos LIMIT 6;")
            
            # Obtener los nombres de las columnas para crear una lista de diccionarios
            col_names = [desc[0] for desc in cur.description]
            productos = [dict(zip(col_names, row)) for row in cur.fetchall()]
            
            # Si no hay productos, añade un mensaje al estado para debug
            if not productos:
                db_status += " | ⚠️ La tabla 'productos' está vacía o no existe."


            cur.close()

        except Exception as e:
            db_status = f"⚠️ Conectado, pero la consulta falló: {e}"
        finally:
            conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión. Revisa la DATABASE_URL."
    
    # Renderizar la plantilla HTML, pasando el estado y los productos
   return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos, 
        generic_products=GENERIC_MATH_TOPICS # <-- ¡Añade esto!
    )

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)