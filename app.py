# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Lista de Categorías y Temas para la Simulación
MODULOS_INFO = [
    {"grado": "MÓDULO INICIAL (6°)", "categoria": "FUNDAMENTOS", "tema_1": "El Origen del Dinero y el Trueque", "tema_2": "Presupuesto Personal Básico"},
    {"grado": "MÓDULO BÁSICO (7°)", "categoria": "AHORRO Y CRÉDITO", "tema_1": "La Cuenta de Ahorros", "tema_2": "Préstamo vs. Deuda"},
    {"grado": "MÓDULO INTERMEDIO (8°)", "categoria": "CÁLCULO DE INTERÉS", "tema_1": "Porcentajes Aplicados a la Banca", "tema_2": "Fórmula del Interés Simple"},
    {"grado": "MÓDULO AVANZADO (9°)", "categoria": "INTERÉS COMPUESTO", "tema_1": "El Poder del Interés Compuesto", "tema_2": "Valor Futuro (VF) y Presente (VP)"},
    {"grado": "MÓDULO SUPERIOR (10°)", "categoria": "VALORACIÓN", "tema_1": "Cálculo de Anualidades", "tema_2": "Amortización de Deudas"},
    {"grado": "MÓDULO PROFESIONAL (11°)", "categoria": "MODELOS FINANCIEROS", "tema_1": "VPN (Valor Presente Neto) y TIR", "tema_2": "Flujos de Caja Descontados"},
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

            # Consultamos los 6 módulos principales, o más si existen.
            cur.execute('SELECT nombre, instructor, imagen_url, precio, estudiantes, rating FROM productos ORDER BY id ASC LIMIT 6;')
            
            productos_data = cur.fetchall()
            
            # Mapeamos los resultados y ASIGNAMOS la información de los grados
            for i, p in enumerate(productos_data):
                # Usamos la información de la lista predefinida (MODULOS_INFO) para enriquecer el producto
                info = MODULOS_INFO[i % len(MODULOS_INFO)] # Cicla si hay más de 6 productos
                
                productos.append({
                    'nombre': p[0],
                    'instructor': p[1],
                    # Usamos una imagen de placeholder, ya que el diseño es minimalista
                    'imagen_url': p[2] if p[2] else "https://i.postimg.cc/QtxK54zN/placeholder-finance.jpg", 
                    'precio': p[3],
                    'estudiantes': p[4],
                    'rating': p[5],
                    'categoria': info["grado"], # e.g., "MÓDULO INICIAL (6°)"
                    'tema_1': info["tema_1"],
                    'tema_2': info["tema_2"]
                })

            cur.close()

        except Exception as e:
            # En caso de error (e.g., la tabla 'productos' no tiene la columna 'imagen_url' o no existe)
            print(f"Error al obtener productos: {e}") 
        finally:
            conn.close()
    
    return render_template('index.html', productos=productos)

# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)