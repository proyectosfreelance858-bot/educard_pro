# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv
import urllib.parse # <--- NUEVA IMPORTACIÓN

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# --- DATOS FIJOS/GENÉRICOS (sin cambios) ---
GENERIC_MATH_TOPICS = [
    ("Operaciones con números enteros", "Matemáticas 6°", "Valor Posicional", "Polinomios Aritméticos"),
    ("Fraccionarios y decimales", "Matemáticas 6°", "Operaciones Básicas", "Conversión Decimal"),
    ("Geometría básica (figuras, ángulos y áreas)", "Matemáticas 6°", "Área y Perímetro", "Clasificación de Figuras"),
    ("Proporcionalidad y porcentajes", "Matemáticas 6°", "Regla de Tres", "Escalas y Mapas"),
    ("Lógica, conjuntos y sistema de coordenadas", "Matemáticas 6°", "Tablas de Frecuencia", "Probabilidad Elemental"),
    ("Funciones y Gráficos", "Matemáticas 6°", "Dominio y Rango", "Interpretación de Gráficos"),
]

# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS (MÉTODO EXPLÍCITO FINAL) ---
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        # Esto solo se verá en los logs de Render si la variable no está configurada.
        print("ERROR: La variable DATABASE_URL no está definida.") 
        return None
        
    print(f"DEBUG DB URL (START): {DATABASE_URL[:30]}...") 
    
    # Asegurar el prefijo 'postgresql' para un parseo correcto con urllib
    if DATABASE_URL.startswith('postgres://'):
        safe_url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        safe_url = DATABASE_URL
    
    try:
        # Descomponer la URL
        url = urllib.parse.urlparse(safe_url)
        
        # Conectar usando parámetros explícitos y SSL
        conn = psycopg2.connect(
            database=url.path[1:],  # Ignora el "/" inicial
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode='require'  # CRÍTICO para Render y otras plataformas cloud
        )
        return conn
        
    except Exception as e:
        print(f"Error CRÍTICO al conectar a la base de datos (Método Explícito): {e}")
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
            print(f"ERROR DURANTE LA CONSULTA SQL: {e}")
        finally:
            if conn:
                conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión a DB."
    
    return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos,
        generic_products=GENERIC_MATH_TOPICS 
    )

# --- RUTAS DE NAVEGACIÓN (DEFINIDAS SIN .html) ---

@app.route('/refuerzos') # URL: /refuerzos
def refuerzos():
    return render_template('refuerzos.html') # Renderiza el archivo: refuerzos.html

@app.route('/nosotros') # URL: /nosotros
def nosotros():
    return render_template('nosotros.html')

@app.route('/beneficios') # URL: /beneficios
def beneficios():
    return render_template('beneficios.html')

@app.route('/faq') # URL: /faq
def faq():
    return render_template('faq.html')


# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)