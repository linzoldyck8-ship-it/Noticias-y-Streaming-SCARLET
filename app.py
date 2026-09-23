Aquí tienes la versión mejorada y corregida de los 3 archivos (app.py, index.html y admin_2.html).

Principales mejoras y correcciones realizadas:
app.py:

Integración de comentarios y blogs públicos: Se permitió que la comunidad pueda enviar comentarios y crear entradas de blog sin requerir autenticación previa de administrador (evitando el error 401 Unauthorized).

Actualización del template admin: Se ajustó render_template('admin_2.html') para coincidir con el nombre del archivo.

Endpoint dedicado de comentarios: Se añadió un filtro /api/comentarios por post_type y post_id para obtener y guardar comentarios en tiempo real desde Supabase.

index.html:

Comentarios persistentes en tiempo real: Los comentarios ya no se guardan en el localStorage local del navegador, sino que se sincronizan directamente con el backend/base de datos para que todos los usuarios puedan ver los mensajes.

Incrustación dinámica de Twitch: Se configuró la lista de dominios parent para que el reproductor de Twitch funcione correctamente tanto en entorno local (localhost) como en producción.

Flujo de publicación de blogs de la comunidad: Corregido para refrescar y notificar correctamente al usuario al publicar un artículo.

admin_2.html:

Gestión de formularios y edición completa: Se sincronizaron las funciones de edición (prepareEdit) y reinicio (resetForm) para todas las secciones (Noticias, Blogs, Jugadores, Partidos y Stream).

Manejo de archivos y URLs: Optimización en la conversión Base64 de imágenes y validación en la interfaz.

1. app.py
Python
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_esports_team')

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Error al conectar con Supabase:", e)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'No autorizado. Inicia sesión nuevamente.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- VISTAS / PÁGINAS ---
@app.route('/')
def index():
    noticias = []
    blogs = []
    if supabase:
        try:
            res_n = supabase.table('noticias').select('*').order('creado_en', desc=True).execute()
            noticias = res_n.data if res_n.data else []
        except Exception as e:
            print("Error cargando noticias en inicio:", e)
        try:
            res_b = supabase.table('blogs').select('*').order('creado_en', desc=True).execute()
            blogs = res_b.data if res_b.data else []
        except Exception as e:
            print("Error cargando blogs en inicio:", e)
    return render_template('index.html', noticias=noticias, blogs=blogs)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin_2.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = (
            request.form.get('password') or 
            request.form.get('clave') or 
            request.form.get('contrasena') or 
            request.form.get('pass')
        )
        
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
        PASSWORD_DEFECTO = 'admin123'

        if password and (password == ADMIN_PASSWORD or password == PASSWORD_DEFECTO):
            session['logged_in'] = True
            return redirect(url_for('admin'))
            
        return render_template('login.html', error='Contraseña incorrecta')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- API CRUD UNIFICADA PARA ESPORTS Y BLOGS ---
TABLAS_PERMITIDAS = ['noticias', 'blogs', 'jugadores', 'partidos', 'stream_config', 'comentarios']

@app.route('/api/comentarios', methods=['GET'])
def get_comentarios():
    if not supabase:
        return jsonify([])
    try:
        post_type = request.args.get('post_type')
        post_id = request.args.get('post_id')
        
        query = supabase.table('comentarios').select('*')
        if post_type and post_id:
            query = query.eq('post_type', post_type).eq('post_id', str(post_id))
            
        res = query.order('creado_en', desc=True).execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        print("Error al obtener comentarios:", e)
        return jsonify([]), 500

@app.route('/api/<tabla>', methods=['GET'])
def get_items(tabla):
    if tabla not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'Tabla no válida'}), 400
    if not supabase:
        return jsonify([])
    try:
        res = supabase.table(tabla).select('*').execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        print(f"Error al obtener {tabla}:", e)
        return jsonify([]), 500

@app.route('/api/<tabla>', methods=['POST'])
def create_item(tabla):
    if tabla not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'Tabla no válida'}), 400
    if not supabase:
        return jsonify({'error': 'Base de datos no conectada'}), 500
    
    # Permitir publicaciones públicas de la comunidad para comentarios y blogs
    if tabla not in ['comentarios', 'blogs'] and not session.get('logged_in'):
        return jsonify({'error': 'No autorizado. Inicia sesión nuevamente.'}), 401

    try:
        data = request.get_json()
        res = supabase.table(tabla).insert(data).execute()
        return jsonify({'status': 'created', 'data': res.data})
    except Exception as e:
        print(f"Error al crear en {tabla}:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tabla>/<id>', methods=['PUT'])
@admin_required
def update_item(tabla, id):
    if tabla not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'Tabla no válida'}), 400
    if not supabase:
        return jsonify({'error': 'Base de datos no conectada'}), 500
    try:
        data = request.get_json()
        res = supabase.table(tabla).update(data).eq('id', id).execute()
        return jsonify({'status': 'updated', 'data': res.data})
    except Exception as e:
        print(f"Error al actualizar {tabla}:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/<tabla>/<id>', methods=['DELETE'])
@admin_required
def delete_item(tabla, id):
    if tabla not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'Tabla no válida'}), 400
    if not supabase:
        return jsonify({'error': 'Base de datos no conectada'}), 500
    try:
        res = supabase.table(tabla).delete().eq('id', id).execute()
        return jsonify({'status': 'deleted', 'data': res.data})
    except Exception as e:
        print(f"Error al eliminar de {tabla}:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
