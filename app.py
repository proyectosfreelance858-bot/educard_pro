# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# --- DATOS FIJOS/GENÉRICOS PARA FALLBACK O MUESTRA ---
# Esta lista se usa en index.html para mostrar tarjetas fijas.
GENERIC_MATH_TOPICS = [
    ("Operaciones con números enteros", "Matemáticas 6°", "Valor Posicional", "Polinomios Aritméticos"),
    ("Fraccionarios y decimales", "Matemáticas 6°", "Operaciones Básicas", "Conversión Decimal"),
    ("Geometría básica (figuras, ángulos y áreas)", "Matemáticas 6°", "Área y Perímetro", "Clasificación de Figuras"),
    ("Proporcionalidad y porcentajes", "Matemáticas 6°", "Regla de Tres", "Escalas y Mapas"),
    ("Lógica, conjuntos y sistema de coordenadas", "Matemáticas 6°", "Tablas de Frecuencia", "Probabilidad Elemental"),
    ("Funciones y Gráficos", "Matemáticas 6°", "Dominio y Rango", "Interpretación de Gráficos"),
]

# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # Nota: En un entorno de producción, esto debería ser un error fatal.
        print("ERROR: La variable DATABASE_URL no está definida.")
        return None
    if DATABASE_URL.startswith('postgres://'):
        # Reemplazo requerido por algunas versiones de psycopg2
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
    productos = []  # Inicializar la lista de productos de la BD
    
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()

            # 1. Obtener la versión de PostgreSQL
            cur.execute('SELECT version();')
            data = cur.fetchone()
            db_status = f"✅ Conectado y versión de PostgreSQL: {data[0][:30]}..."

            # 2. Intentar cargar los productos (Usando los 7 campos visibles)
            # NOTA: Esta consulta debe coincidir con los campos de tu tabla 'productos'.
            cur.execute("SELECT nombre, categoria, instructor, imagen_url, precio, estudiantes, rating FROM productos LIMIT 6;")
            
            # Obtenemos los nombres de las columnas para crear una lista de diccionarios
            col_names = [desc[0] for desc in cur.description] 
            productos = [dict(zip(col_names, row)) for row in cur.fetchall()]
            
            if not productos:
                db_status += " | ⚠️ La tabla 'productos' está vacía."

            cur.close()

        except Exception as e:
            # Capturar cualquier error de SQL o conexión
            db_status = f"⚠️ Conectado, pero la consulta falló: {e}"
        finally:
            # Aseguramos el cierre de la conexión
            if conn:
                conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión. Revisa la DATABASE_URL."
    
    # Renderizar la plantilla HTML.
    # CRÍTICO: Pasamos la lista GENERIC_MATH_TOPICS como 'generic_products' para los datos fijos.
    return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos,
        generic_products=GENERIC_MATH_TOPICS 
    )

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Usamos el puerto del entorno o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)