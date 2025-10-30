# Archivo: app.py
import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# --- DATOS FIJOS/GENÉRICOS PARA FALLBACK O MUESTRA ---
# ... (El resto de la lista GENERIC_MATH_TOPICS es el mismo)
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
        
    # Diagnóstico: Imprime el inicio de la URL en la consola del servidor (Render)
    # Esto ayuda a confirmar que la variable se está cargando
    print(f"DEBUG DB URL (START): {DATABASE_URL[:30]}...") 
    
    if DATABASE_URL.startswith('postgres://'):
        # Reemplazo requerido por algunas versiones de psycopg2
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
    try:
        # **AÑADIR SSLMODE REQUERIDO:**
        # Render/Heroku a menudo exigen conexiones SSL. Si falla, el problema puede ser este.
        conn = psycopg2.connect(DATABASE_URL, sslmode='require') 
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
            # Diagnóstico: Imprimir error de consulta o tabla no encontrada
            print(f"ERROR DURANTE LA CONSULTA SQL: {e}")
        finally:
            # Aseguramos el cierre de la conexión
            if conn:
                conn.close()
    else:
        # Aquí se imprimirá el error de conexión si get_db_connection() falló
        db_status = "❌ Fallo Crítico de Conexión. Revisa la DATABASE_URL y los logs del servidor."
    
    # Renderizar la plantilla HTML.
    return render_template(
        'index.html', 
        db_status=db_status, 
        productos=productos,
        generic_products=GENERIC_MATH_TOPICS 
    )

# --- RUTAS PARA PÁGINAS ESTÁTICAS DEL MENÚ ---
# ... (Estas rutas no cambian)

@app.route('/refuerzos')
def refuerzos():
    """Renderiza la página de Refuerzos."""
    return render_template('refuerzos.html')

@app.route('/nosotros')
def nosotros():
    """Renderiza la página Nosotros."""
    return render_template('nosotros.html')

@app.route('/beneficios')
def beneficios():
    """Renderiza la página Beneficios."""
    return render_template('beneficios.html')

@app.route('/faq')
def faq():
    """Renderiza la página de Preguntas Frecuentes (FAQ)."""
    return render_template('faq.html')


# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Usamos el puerto del entorno o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)