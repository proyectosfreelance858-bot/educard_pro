# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Lista de Módulos (Simulación de Datos detallados)
MODULOS_INFO = [
    {"grado": "MÓDULO INICIAL | 6°", "nombre_base": "Fundamentos del Dinero y Ahorro", "instructor": "Ana L. González", "rating": 4.5, "estudiantes": 3100, "precio": 0.00, "tema_1": "El Origen del Dinero y el Trueque", "tema_2": "Presupuesto Personal Básico"},
    {"grado": "MÓDULO BÁSICO | 7°", "nombre_base": "Introducción al Ahorro y Crédito", "instructor": "David R. Castro", "rating": 4.7, "estudiantes": 2850, "precio": 19.99, "tema_1": "La Cuenta de Ahorros", "tema_2": "Préstamo vs. Deuda"},
    {"grado": "MÓDULO INTERMEDIO | 8°", "nombre_base": "Cálculo Básico de Interés Simple", "instructor": "Sofía T. Pérez", "rating": 4.6, "estudiantes": 2500, "precio": 29.99, "tema_1": "Porcentajes Aplicados a la Banca", "tema_2": "Fórmula del Interés Simple"},
    {"grado": "MÓDULO AVANZADO | 9°", "nombre_base": "Dominio del Interés Compuesto", "instructor": "Javier M. Vargas", "rating": 4.8, "estudiantes": 2200, "precio": 49.99, "tema_1": "El Poder del Interés Compuesto", "tema_2": "Valor Futuro (VF) y Presente (VP)"},
    {"grado": "MÓDULO SUPERIOR | 10°", "nombre_base": "Anualidades y Amortización", "instructor": "Elena P. Díaz", "rating": 4.7, "estudiantes": 1900, "precio": 59.99, "tema_1": "Cálculo de Anualidades", "tema_2": "Amortización de Deudas"},
    {"grado": "MÓDULO PROFESIONAL | 11°", "nombre_base": "Modelos Financieros Avanzados", "instructor": "Ricardo V. Torres", "rating": 4.9, "estudiantes": 1500, "precio": 79.99, "tema_1": "VPN (Valor Presente Neto) y TIR", "tema_2": "Flujos de Caja Descontados"},
]


# --- 2. GESTIÓN DE LA CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    # ... (La función de conexión a la DB se mantiene igual)
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

            # Consultamos los 6 productos necesarios (LIMIT 6)
            cur.execute('SELECT nombre, instructor, imagen_url, precio, estudiantes, rating FROM productos ORDER BY id ASC LIMIT 6;')
            
            productos_data = cur.fetchall()
            
            # Mapeamos los resultados. Utilizamos la información fija de MODULOS_INFO
            for i, p in enumerate(productos_data):
                # Usamos la información de la lista predefinida (MODULOS_INFO)
                info = MODULOS_INFO[i % len(MODULOS_INFO)]
                
                productos.append({
                    # Nota: Sobreescribimos el nombre, instructor, precio, etc.,
                    # con los datos fijos (MODULOS_INFO) para asegurar que la demo coincida con los temas solicitados.
                    # En un entorno de producción real, solo se usarían los datos de la DB.
                    'nombre': info["nombre_base"],
                    'instructor': info["instructor"],
                    # Si la columna imagen_url existe, la usamos, si no, usamos un placeholder genérico
                    'imagen_url': p[2] if len(p) > 2 and p[2] else "https://i.postimg.cc/QtxK54zN/placeholder-finance.jpg", 
                    'precio': info["precio"],
                    'estudiantes': info["estudiantes"],
                    'rating': info["rating"],
                    'categoria': info["grado"], # e.g., "MÓDULO INICIAL | 6°"
                    'tema_1': info["tema_1"],
                    'tema_2': info["tema_2"]
                })

            cur.close()

        except Exception as e:
            # En caso de error, si la tabla 'productos' no tiene la estructura esperada, 
            # generamos al menos los datos simulados para que la página se vea bien.
            print(f"Error al obtener productos de la DB: {e}. Usando datos simulados.")
            productos = [{
                'nombre': item["nombre_base"],
                'instructor': item["instructor"],
                'imagen_url': "https://i.postimg.cc/QtxK54zN/placeholder-finance.jpg", 
                'precio': item["precio"],
                'estudiantes': item["estudiantes"],
                'rating': item["rating"],
                'categoria': item["grado"],
                'tema_1': item["tema_1"],
                'tema_2': item["tema_2"]
            } for item in MODULOS_INFO]
            
        finally:
            if conn:
                conn.close()
    else:
        # Si la conexión falla, usamos los datos simulados
        productos = [{
            'nombre': item["nombre_base"],
            'instructor': item["instructor"],
            'imagen_url': "https://i.postimg.cc/QtxK54zN/placeholder-finance.jpg", 
            'precio': item["precio"],
            'estudiantes': item["estudiantes"],
            'rating': item["rating"],
            'categoria': item["grado"],
            'tema_1': item["tema_1"],
            'tema_2': item["tema_2"]
        } for item in MODULOS_INFO]
    
    return render_template('index.html', productos=productos)

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)