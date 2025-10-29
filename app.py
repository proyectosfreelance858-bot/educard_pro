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
        # psycopg2 requiere 'postgresql://' en lugar de 'postgres://' para algunas configuraciones
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

            # 2. Intentar cargar los productos. Usamos los 7 campos visibles en tu tabla.
            # NO incluimos tema_1 ni tema_2 porque no están en tu tabla.
            cur.execute("SELECT nombre, categoria, instructor, imagen_url, precio, estudiantes, rating FROM productos LIMIT 6;")
            
            # **CLAVE DE LA SOLUCIÓN:** Obtenemos los nombres de las columnas directamente desde la consulta
            # Esto hace que el código sea resistente a cambios menores en el orden de las columnas.
            col_names = [desc[0] for desc in cur.description]
            
            # Mapeamos los resultados a una lista de diccionarios
            productos = [dict(zip(col_names, row)) for row in cur.fetchall()]
            
            if not productos:
                db_status += " | ⚠️ La tabla 'productos' está vacía o no existe. Mostrando fallback."

            cur.close()

        except Exception as e:
            # Ahora el error exacto aparecerá en el estado si la consulta falla.
            db_status = f"⚠️ Conectado, pero la consulta falló: {e}"
        finally:
            conn.close()
    else:
        db_status = " Fallo Crítico de Conexión. Revisa la DATABASE_URL."
    
    # Renderizar la plantilla HTML, pasando el estado, los productos de la BD, 
    # y la lista genérica como 'generic_products' para el fallback.
    return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos,
        generic_products=GENERIC_MATH_TOPICS # <-- ¡Añadido para el fallback en el template!
    )

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)