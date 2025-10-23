# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Lista de Módulos y Temas CLAVE: Refuerzo de Matemática Grado Sexto
MODULOS_INFO = [
    {"grado": "MÓDULO 1 (6°)", "categoria": "NÚMEROS Y OPERACIONES", "tema_1": "Valor Posicional y Descomposición", "tema_2": "Suma y Resta de Polinomios Aritméticos"},
    {"grado": "MÓDULO 2 (6°)", "categoria": "FRACCIONES Y DECIMALES", "tema_1": "Conversión Fracción-Decimal", "tema_2": "Operaciones Básicas con Fracciones"},
    {"grado": "MÓDULO 3 (6°)", "categoria": "MÚLTIPLOS Y DIVISORES", "tema_1": "Criterios de Divisibilidad", "tema_2": "M.C.M. y M.C.D. Aplicado a Problemas"},
    {"grado": "MÓDULO 4 (6°)", "categoria": "GEOMETRÍA EUCLIDIANA", "tema_1": "Cálculo de Área y Perímetro de Figuras", "tema_2": "Clasificación de Ángulos y Triángulos"},
    {"grado": "MÓDULO 5 (6°)", "categoria": "ESTADÍSTICA Y AZAR", "tema_1": "Tablas de Frecuencia y Gráficos", "tema_2": "Conceptos Fundamentales de Probabilidad"},
    {"grado": "MÓDULO 6 (6°)", "categoria": "RAZONES Y PROPORCIONES", "tema_1": "Introducción a las Razones (Comparación)", "tema_2": "Regla de Tres Simple y Aplicaciones"},
]

# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    # ... (Se mantiene la lógica de conexión a la DB)
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
            # Consultamos los módulos (limitados para llenar los 6 espacios de la estructura)
            cur.execute('SELECT nombre, instructor, imagen_url, precio, estudiantes, rating FROM productos ORDER BY id ASC LIMIT 6;')
            productos_data = cur.fetchall()
            
            for i, p in enumerate(productos_data):
                # Asignamos el contenido específico de refuerzo de 6to grado
                info = MODULOS_INFO[i % len(MODULOS_INFO)] 
                
                productos.append({
                    'nombre': p[0] if p[0] else info["categoria"],
                    'instructor': p[1] if p[1] else "Experto en Didáctica",
                    'imagen_url': p[2], 
                    # Definimos precios de ejemplo, con algunos gratis para refuerzo
                    'precio': p[3] if p[3] is not None else (0 if i == 0 else 19.99), 
                    'estudiantes': p[4] if p[4] is not None else 850,
                    'rating': p[5] if p[5] is not None else 4.7,
                    'categoria': info["grado"], 
                    'tema_1': info["tema_1"],
                    'tema_2': info["tema_2"]
                })

            cur.close()
        except Exception as e:
            print(f"Error al obtener productos: {e}") 
        finally:
            conn.close()
    
    return render_template('index.html', productos=productos)

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)