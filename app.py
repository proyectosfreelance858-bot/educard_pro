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
    productos = [] 
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()

            # Consultamos hasta 10 productos para llenar la página ampliada
            # La página tendrá 6 módulos como sección principal y 4 más en una vista expandida
            cur.execute('SELECT nombre, instructor, imagen_url, precio, estudiantes, rating FROM productos ORDER BY id ASC LIMIT 10;')
            productos_data = cur.fetchall()
            
            for i, p in enumerate(productos_data):
                # Asignamos contexto temático CÍCLICAMENTE si la base de datos es genérica
                topic_index = i % len(GENERIC_MATH_TOPICS)
                info = GENERIC_MATH_TOPICS[topic_index]
                
                productos.append({
                    'nombre': p[0] if p[0] else info[1], # Priorizamos nombre de DB
                    'instructor': p[1] if p[1] else "Docente Experto", # Priorizamos instructor de DB
                    'imagen_url': p[2], 
                    'precio': p[3] if p[3] is not None else (0.0 if i == 0 else 19.99), # Priorizamos precio de DB
                    'estudiantes': p[4] if p[4] is not None else 850,
                    'rating': p[5] if p[5] is not None else 4.7,
                    'categoria': info[0], # e.g., "MÓDULO NÚMEROS (6°)"
                    'tema_1': info[2],
                    'tema_2': info[3]
                })

            cur.close()

        except Exception as e:
            print(f"Error al obtener productos de la base de datos: {e}") 
        finally:
            if conn:
                conn.close()
    
    return render_template('index.html', productos=productos)

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)