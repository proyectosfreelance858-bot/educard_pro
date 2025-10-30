# Archivo: app.py
import os
import psycopg2
# Importar 'request', 'session', 'redirect', 'url_for' para manejar el flujo de la aplicación
from flask import Flask, render_template, request, session, redirect, url_for 
from dotenv import load_dotenv
import urllib.parse 
import json 

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Configuración CRÍTICA para usar sesiones (¡DEBE ESTAR PRESENTE!)
# La clave secreta debe ser robusta en producción.
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_secreta_super_default_insegura_EDUCARD') 

# --- DATOS FIJOS/GENÉRICOS ---
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
    """Establece y devuelve una conexión a la base de datos PostgreSQL."""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("ERROR: La variable DATABASE_URL no está definida.") 
        return None
        
    if DATABASE_URL.startswith('postgres://'):
        safe_url = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        safe_url = DATABASE_URL
    
    try:
        url = urllib.parse.urlparse(safe_url)
        conn = psycopg2.connect(
            database=url.path[1:],  
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode='require'  # CRÍTICO para plataformas cloud
        )
        return conn
        
    except Exception as e:
        print(f"Error CRÍTICO al conectar a la base de datos: {e}")
        return None

# --- 3. RUTAS DE AUTENTICACIÓN Y DASHBOARD ---

@app.route('/login') 
def login():
    """Muestra el formulario de login. Redirige si ya hay sesión."""
    if 'username' in session:
        if session.get('role') == 'Administrador':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_student'))
            
    # El parámetro 'error' se usa para mostrar mensajes después de un fallo en /auth_login
    error_message = request.args.get('error', None)
    return render_template('login.html', error_message=error_message)

@app.route('/auth_login', methods=['POST'])
def auth_login():
    """Procesa las credenciales enviadas desde el formulario de login."""
    nombre = request.form.get('nombre')
    contrasena = request.form.get('contrasena')
    
    conn = get_db_connection()
    user = None
    
    if conn:
        try:
            cur = conn.cursor()
            # ⚠️ ADVERTENCIA: Esta consulta expone la contraseña. Usa HASH en producción.
            # Buscar usuario por nombre y contraseña
            cur.execute("SELECT nombre, rol FROM usuarios WHERE nombre = %s AND contrasena = %s;", (nombre, contrasena))
            result = cur.fetchone()
            
            if result:
                user = {'nombre': result[0], 'rol': result[1]}
            
            cur.close()
        except Exception as e:
            print(f"ERROR DURANTE LA AUTENTICACIÓN: {e}")
        finally:
            if conn:
                conn.close()

    if user:
        session['username'] = user['nombre']
        session['role'] = user['rol']
        
        if user['rol'] == 'Administrador':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_student'))
    
    # Si las credenciales fallan o hay un error de DB
    return redirect(url_for('login', error='Credenciales incorrectas o acceso denegado.'))

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard_student():
    """Dashboard para estudiantes: Consulta y muestra los módulos asignados."""
    if 'username' not in session or session.get('role') != 'Estudiante':
        return redirect(url_for('login'))

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
                # Asumiendo la Opción 1 (TEXTO separado por comas)
                modules_raw = module_data[0]
                modules_list = [m.strip() for m in modules_raw.split(',') if m.strip()]
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

@app.route('/dashboardadmin')
def dashboard_admin():
    """Dashboard para administradores: Requiere rol de Administrador."""
    if 'username' not in session or session.get('role') != 'Administrador':
        return redirect(url_for('login'))

    return render_template('dashboardadmin.html', user_name=session['username'])


# --- 4. RUTAS DE CONTENIDO ESTÁTICO Y MÓDULOS ---

@app.route('/')
def index():
    """Ruta principal: Muestra la página de inicio."""
    # Redirigir al dashboard si ya hay sesión activa
    if 'username' in session:
        if session.get('role') == 'Administrador':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_student'))

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

# --- Rutas de Navegación ---
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

# --- Rutas de Módulos ---
@app.route('/modulo1')
def modulo1():
    return render_template('modulo1.html')

@app.route('/modulo2')
def modulo2():
    return render_template('modulo2.html')

@app.route('/modulo3')
def modulo3():
    return render_template('modulo3.html')

@app.route('/modulo4')
def modulo4():
    return render_template('modulo4.html')

@app.route('/modulo5')
def modulo5():
    return render_template('modulo5.html')


# --- 5. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
