from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# Configuración de Supabase (toma las claves de tu archivo .env)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# NOMBRE DE CANAL FIJO DE TWITCH (Escribe aquí el nombre de tu usuario de Twitch)
TWITCH_CHANNEL = "tu_canal_de_twitch"

@app.route('/')
def index():
    return render_template('index.html', twitch_channel=TWITCH_CHANNEL)

# --- RUTAS DE NOTICIAS ---
@app.route('/api/noticias', methods=['GET', 'POST'])
def handle_noticias():
    if request.method == 'POST':
        data = request.json
        res = supabase.table('noticias').insert(data).execute()
        return jsonify(res.data)
    res = supabase.table('noticias').select('*').order('creado_en', desc=True).execute()
    return jsonify(res.data)

@app.route('/api/noticias/<int:noticia_id>', methods=['DELETE'])
def delete_noticia(noticia_id):
    res = supabase.table('noticias').delete().eq('id', noticia_id).execute()
    return jsonify(res.data)

# --- RUTAS DE BLOGS ---
@app.route('/api/blogs', methods=['GET', 'POST'])
def handle_blogs():
    if request.method == 'POST':
        data = request.json
        res = supabase.table('blogs').insert(data).execute()
        return jsonify(res.data)
    res = supabase.table('blogs').select('*').order('creado_en', desc=True).execute()
    return jsonify(res.data)

@app.route('/api/blogs/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    res = supabase.table('blogs').delete().eq('id', blog_id).execute()
    return jsonify(res.data)

# --- RUTAS DE JUGADORES ---
@app.route('/api/jugadores', methods=['GET', 'POST'])
def handle_jugadores():
    if request.method == 'POST':
        data = request.json
        res = supabase.table('jugadores').insert(data).execute()
        return jsonify(res.data)
    res = supabase.table('jugadores').select('*').order('creado_en', desc=True).execute()
    return jsonify(res.data)

@app.route('/api/jugadores/<int:jugador_id>', methods=['DELETE'])
def delete_jugador(jugador_id):
    res = supabase.table('jugadores').delete().eq('id', jugador_id).execute()
    return jsonify(res.data)

# --- RUTAS DE PARTIDOS ---
@app.route('/api/partidos', methods=['GET', 'POST'])
def handle_partidos():
    if request.method == 'POST':
        data = request.json
        res = supabase.table('partidos').insert(data).execute()
        return jsonify(res.data)
    res = supabase.table('partidos').select('*').order('creado_en', desc=True).execute()
    return jsonify(res.data)

@app.route('/api/partidos/<int:partido_id>', methods=['DELETE'])
def delete_partido(partido_id):
    res = supabase.table('partidos').delete().eq('id', partido_id).execute()
    return jsonify(res.data)

if __name__ == '__main__':
    app.run(debug=True)
