# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# --- DATOS FIJOS/GENÉRICOS PARA FALLBACK O MUESTRA ---
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
    productos = [] 
    
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT version();')
            data = cur.fetchone()
            db_status = f"✅ Conectado y versión de PostgreSQL: {data[0][:30]}..."

            cur.execute("SELECT nombre, categoria, instructor, imagen_url, precio, estudiantes, rating FROM productos LIMIT 6;")
            
            col_names = [desc[0] for desc in cur.description] 
            productos = [dict(zip(col_names, row)) for row in cur.fetchall()]
            
            if not productos:
                db_status += " | ⚠️ La tabla 'productos' está vacía."

            cur.close()

        except Exception as e:
            db_status = f"⚠️ Conectado, pero la consulta falló: {e}"
        finally:
            if conn:
                conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión. Revisa la DATABASE_URL."
    
    return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos,
        generic_products=GENERIC_MATH_TOPICS 
    )

# --- RUTAS DE NAVEGACIÓN ADICIONALES (SOLUCIONANDO 404s) ---

@app.route('/refuerzos')
def refuerzos():
    """Renderiza la página de Refuerzos."""
    # Nota: Si refuerzos.html necesita datos de productos, la lógica de BD debe ir aquí.
    return render_template('refuerzos.html')

@app.route('/nosotros')
def nosotros():
    """Renderiza la página de Nosotros."""
    return render_template('nosotros.html')

@app.route('/beneficios')
def beneficios():
    """Renderiza la página de Beneficios."""
    return render_template('beneficios.html')


# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)