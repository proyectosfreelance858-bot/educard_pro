import os
import psycopg2
# Importar 'request', 'session', 'redirect', 'url_for' para manejar el login y la redirección
from flask import Flask, render_template, request, session, redirect, url_for 
from dotenv import load_dotenv
import urllib.parse
import json 

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
app = Flask(__name__)

# Configuración CRÍTICA para usar sesiones
# En producción, usar una variable de entorno secreta y compleja.
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_secreta_super_default_insegura_debes_cambiarla')

# --- DATOS FIJOS/GENÉRICOS (sin cambios) ---
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
            sslmode='require' # CRÍTICO para Render
        )
        return conn
        
    except Exception as e:
        print(f"Error CRÍTICO al conectar a la base de datos: {e}")
        return None

# --- 3. RUTAS DE AUTENTICACIÓN Y DASHBOARD ---

# Ruta para mostrar el formulario de login (Corregido)
@app.route('/login') 
def login():
    # Si el usuario ya está autenticado, redirigir a su dashboard correspondiente.
    if 'username' in session:
        if session.get('role') == 'Administrador':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_student'))
            
    return render_template('login.html')

# Ruta para procesar el formulario de login (POST)
@app.route('/auth_login', methods=['POST'])
def auth_login():
    nombre = request.form.get('nombre')
    contrasena = request.form.get('contrasena')
    
    # --- SIMULACIÓN DE LA CONSULTA A LA BASE DE DATOS (REEMPLAZAR CON LÓGICA REAL) ---
    
    # Aquí debería ir la consulta a la DB para validar el hash de la contraseña
    # y obtener el rol. Por ahora, usamos la simulación basada en el nombre:
    
    # Nota: En un sistema real, si el login falla, deberías volver a /login con un mensaje de error.
    if (nombre == 'Nicolas' or nombre == 'Kaleth') and contrasena == '1072':
        session['username'] = nombre
        session['role'] = 'Administrador'
        return redirect(url_for('dashboard_admin'))
    elif nombre == 'Rogger' and contrasena == '1072':
        session['username'] = nombre
        session['role'] = 'Estudiante'
        return redirect(url_for('dashboard_student'))
    
    # Si las credenciales fallan o el usuario no existe.
    return redirect(url_for('login', error='Credenciales incorrectas'))


# Ruta para el dashboard de ESTUDIANTES
@app.route('/dashboard')
def dashboard_student():
    # 1. Asegurar que haya una sesión activa y el rol correcto
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
    
    # Pasar los datos al template HTML
    return render_template(
        'dashboard.html', 
        user_name=user_name,
        modules=modules_list,
        db_status=db_status
    )

# Ruta para el dashboard de ADMINISTRADORES
@app.route('/dashboardadmin')
def dashboard_admin():
    if 'username' not in session or session.get('role') != 'Administrador':
        return redirect(url_for('login'))

    return render_template('dashboardadmin.html', user_name=session['username'])

# Ruta para cerrar la sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# --- 4. RUTAS DE NAVEGACIÓN Y MÓDULOS (Nuevas Rutas Añadidas) ---

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

# Rutas de Módulos (Nuevas)
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


# Rutas de Navegación Existentes
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


# --- 5. INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```
eof

### Próximos Pasos (Frontend):

Para que todo funcione correctamente, debes asegurarte de que tu `dashboard.html` use las nuevas rutas con la función `url_for`:

1.  **En el encabezado del `dashboard.html`**, cambia el enlace de "Salir" para usar la nueva ruta de `logout`:
    ```html
    <a href="{{ url_for('logout') }}" style="...">Salir</a>
    ```

2.  **En el cuerpo del `dashboard.html`**, cambia la redirección de los módulos para usar el índice del ciclo `for` y llamar a la ruta de Flask:

    ```html
    <!-- En dashboard.html, dentro del loop: -->
    <div class="module-card" onclick="window.location.href='{{ url_for('modulo' ~ loop.index) }}'">
        <!-- ... contenido ... -->
    </div>
    
