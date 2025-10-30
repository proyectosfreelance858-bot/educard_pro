# Archivo: app.py
import os
import psycopg2
# Importar 'request', 'session', y 'redirect' para manejar el login y la redirección
from flask import Flask, render_template, request, session, redirect, url_for 
from dotenv import load_dotenv
import urllib.parse 
import json # Necesario para parsear el JSON de módulos (si usas JSONB)

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Configuración CRÍTICA para usar sesiones (¡DEBE ESTAR PRESENTE!)
# En un entorno de producción, esta clave debe ser muy compleja y secreta.
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_secreta_super_default_insegura')

# ... (Resto de datos fijos y la función get_db_connection son las mismas) ...
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

# --- NUEVA RUTA: Manejar el POST del Login y Establecer Sesión ---
# Reemplazamos el login de JavaScript por una ruta de Flask para manejar la sesión.
# Nota: La validación real de las credenciales debe ocurrir aquí consultando la DB.

@app.route('/auth_login', methods=['POST'])
def auth_login():
    nombre = request.form.get('nombre')
    contrasena = request.form.get('contrasena')
    
    # *** SIMULACIÓN DE LA CONSULTA A LA BASE DE DATOS ***
    # En un sistema real, aquí buscarías el usuario, obtendrías el hash y lo compararías.
    
    # Simulando la obtención de datos de usuario (solo para que el dashboard funcione)
    # ¡Necesitas reemplazar esto con una consulta real a la tabla 'usuarios'!
    
    # Asumimos que la validación ha ocurrido con éxito y obtenemos el rol:
    if nombre == 'Nicolas' or nombre == 'Kaleth':
        session['username'] = nombre
        session['role'] = 'Administrador'
        return redirect(url_for('dashboard_admin'))
    elif nombre == 'Rogger':
        session['username'] = nombre
        session['role'] = 'Estudiante'
        return redirect(url_for('dashboard_student'))
    
    # Si las credenciales fallan, redirige al login.
    return redirect(url_for('index')) # O a una página de login con error
    
# --- RUTAS PRINCIPALES DEL DASHBOARD ---

# Ruta para el login de ESTUDIANTES (debe coincidir con la redirección en JS/HTML)
@app.route('/dashboard')
def dashboard_student():
    # 1. Asegurar que haya una sesión activa (autenticación)
    if 'username' not in session or session.get('role') != 'Estudiante':
        return redirect(url_for('index')) # Redirigir al login si no está autenticado como estudiante

    user_name = session['username']
    modules_list = []
    db_status = "Desconectado"
    
    conn = get_db_connection()

    if conn:
        try:
            cur = conn.cursor()
            # Consultar el campo 'modulos_acceso'
            cur.execute("SELECT modulos_acceso FROM usuarios WHERE nombre = %s;", (user_name,))
            module_data = cur.fetchone()
            
            if module_data and module_data[0]:
                # Asumiendo la Opción 1 (TEXTO separado por comas) del paso anterior
                modules_raw = module_data[0]
                modules_list = [m.strip() for m in modules_raw.split(',')]
                db_status = f"✅ Conexión exitosa. Módulos encontrados para {user_name}."
            else:
                db_status = f"⚠️ Usuario {user_name} no encontrado o sin módulos asignados."

            cur.close()

        except Exception as e:
            db_status = f"⚠️ La consulta a 'usuarios' falló: {e}"
            print(f"ERROR DURANTE LA CONSULTA DE MÓDULOS: {e}")
        finally:
            if conn:
                conn.close()
    else:
        db_status = "❌ Fallo Crítico de Conexión a DB."

    # Pasar los datos al template HTML
    return render_template(
        'dashboard.html', 
        user_name=user_name,
        modules=modules_list,
        db_status=db_status
    )

# Ruta para el login de ADMINISTRADORES (debe coincidir con la redirección en JS/HTML)
@app.route('/dashboardadmin')
def dashboard_admin():
    if 'username' not in session or session.get('role') != 'Administrador':
        return redirect(url_for('index'))

    # Esta ruta es más sencilla y solo verifica la autenticación.
    # El dashboard real de admin tendrá sus propias consultas.
    return render_template('dashboardadmin.html', user_name=session['username'])


# --- RUTAS DE LA APLICACIÓN (el resto se mantiene igual) ---
@app.route('/')
def index():
    # ... (El código de la ruta index se mantiene igual) ...
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

@app.route('/refuerzos') 
def refuerzos():
    return render_template('refuerzos.html') 

@app.route('/nosotros') 
def nosotros():
    return render_template('nosotros.html')

@app.route('/beneficios') 
def beneficios():
    return render_template('beneficios.html')

@app.route('/faq') 
def faq():
    return render_template('faq.html')


# --- 4. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)