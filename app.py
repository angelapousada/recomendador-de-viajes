import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_searchbox import st_searchbox
from datetime import date, timedelta
from math import radians, cos, sin, asin, sqrt
from urllib.parse import quote
import time
import math

# ─────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TravelPlanner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
.main { background-color: #F7F4EF; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background-color: #1A1A2E; color: white; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #E8E4DC !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: #2D2D4E; border: 1px solid #4A4A7A; color: white; border-radius: 8px;
}
.place-card {
    background: white; border-radius: 16px; padding: 1.2rem 1.4rem;
    margin-bottom: 1rem; border-left: 4px solid #E8C547;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.place-card h4 { margin: 0 0 4px 0; font-family: 'DM Serif Display', serif; font-size: 1.1rem; color: #1A1A2E; }
.place-card .meta { font-size: 0.82rem; color: #888; margin-bottom: 6px; }
.place-card .desc { font-size: 0.88rem; color: #555; line-height: 1.5; }
.hora-slot { display: inline-block; background: #1A1A2E; color: #E8C547; font-weight: 500; padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 6px; letter-spacing: 0.04em; }
.place-card .links { margin-top: 10px; font-size: 0.85rem; }
.place-card .links a { color: #0F3460; text-decoration: none; margin-right: 14px; }
.place-card .links a:hover { text-decoration: underline; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-right: 6px; }
.badge-type  { background: #EEF2FF; color: #4338CA; }
.badge-price { background: #ECFDF5; color: #065F46; }
.badge-open  { background: #FEF9C3; color: #854D0E; }
.day-header {
    font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: #1A1A2E;
    border-bottom: 2px solid #E8C547; padding-bottom: 6px; margin: 1.5rem 0 1rem 0;
}
.hero {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    border-radius: 20px; padding: 3rem 2.5rem; color: white;
    margin-bottom: 2rem; position: relative; overflow: hidden;
}
.hero::before { content: '✈'; position: absolute; right: 2rem; top: 1.5rem; font-size: 6rem; opacity: 0.08; }
.hero h1 { color: white !important; font-size: 2.8rem; margin: 0; line-height: 1.1; }
.hero p  { color: #B0B8D4; margin: 0.5rem 0 0 0; font-size: 1.05rem; }
.stat-box { background: white; border-radius: 12px; padding: 1rem 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.stat-box .num { font-size: 2rem; font-family: 'DM Serif Display', serif; color: #1A1A2E; }
.stat-box .lbl { font-size: 0.78rem; color: #999; text-transform: uppercase; letter-spacing: 0.05em; }
.stButton > button {
    background: #E8C547; color: #1A1A2E; border: none; border-radius: 10px;
    font-weight: 500; font-size: 1rem; padding: 0.6rem 1.8rem; width: 100%;
}
.empty-state { text-align: center; padding: 4rem 2rem; color: #999; }
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state h3 { font-family: 'DM Serif Display', serif; color: #555; }
.review-box {
    background: #F7F4EF; border-radius: 10px; padding: 0.8rem 1rem;
    margin-bottom: 0.5rem; font-size: 0.85rem; color: #444; border-left: 3px solid #E8C547;
}
.review-box .author { font-weight: 500; color: #1A1A2E; margin-bottom: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
NEARBY_URL       = 'https://places.googleapis.com/v1/places:searchNearby'
TEXT_URL         = 'https://places.googleapis.com/v1/places:searchText'
DETAIL_URL       = 'https://places.googleapis.com/v1/places/'
AUTOCOMPLETE_URL = 'https://places.googleapis.com/v1/places:autocomplete'

PRECIO_LABEL = {
    'PRICE_LEVEL_FREE':           '🆓 Gratis',
    'PRICE_LEVEL_INEXPENSIVE':    '💚 Económico',
    'PRICE_LEVEL_MODERATE':       '💛 Moderado',
    'PRICE_LEVEL_EXPENSIVE':      '🟠 Caro',
    'PRICE_LEVEL_VERY_EXPENSIVE': '🔴 Muy caro',
}
PRECIO_NUM = {
    'PRICE_LEVEL_FREE': 0, 'PRICE_LEVEL_INEXPENSIVE': 1,
    'PRICE_LEVEL_MODERATE': 2, 'PRICE_LEVEL_EXPENSIVE': 3,
    'PRICE_LEVEL_VERY_EXPENSIVE': 4,
}
TIPOS_GOOGLE = {
    '🏛️ Atracciones':  'tourist_attraction',
    '🎨 Museos':       'museum',
    '🎭 Arte':         'art_gallery',
    '🍽️ Restaurantes': 'restaurant',
    '☕ Cafeterías':   'cafe',
    '🍻 Bares/Pubs':   'bar',
    '🌿 Parques':      'park',
    '🎡 Ocio':         'amusement_park',
    '🎬 Cines':        'movie_theater',
}
COLORES_DIA = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'cadetblue']
ICONOS_TIPO = {
    '🏛️ Atracciones': 'star',       '🍽️ Restaurantes': 'cutlery',
    '🎨 Museos':       'book',       '🌿 Parques':      'leaf',
    '🎭 Arte':         'picture',    '🎡 Ocio':         'fire',
    '☕ Cafeterías':   'glass',      '🍻 Bares/Pubs':   'glass',
    '🎬 Cines':        'film',
}
TIPO_PESO = {
    '🏛️ Atracciones':  1.30,
    '🎨 Museos':       1.25,
    '🎭 Arte':         1.10,
    '🎡 Ocio':         1.05,
    '🎬 Cines':        1.00,
    '🍽️ Restaurantes': 1.00,
    '🍻 Bares/Pubs':   0.95,
    '☕ Cafeterías':   0.90,
    '🌿 Parques':      0.85,
}
TIPO_IDEAL_HORAS = {
    '☕ Cafeterías':   [9.5, 11.0, 17.0],
    '🎨 Museos':       [10.0, 11.5, 16.0],
    '🏛️ Atracciones': [10.0, 11.5, 16.0, 17.5],
    '🎭 Arte':         [11.0, 16.0],
    '🌿 Parques':      [11.0, 16.0],
    '🍽️ Restaurantes': [13.5, 21.0],
    '🎡 Ocio':         [16.0, 18.5, 20.0],
    '🎬 Cines':        [18.5, 21.0],
    '🍻 Bares/Pubs':   [21.0, 22.5, 18.5],
}
HORA_PREF_ORDEN = [
    '🍻 Bares/Pubs', '🍽️ Restaurantes', '🎬 Cines',
    '☕ Cafeterías', '🎡 Ocio',
    '🏛️ Atracciones', '🎨 Museos', '🎭 Arte', '🌿 Parques',
]

# ─────────────────────────────────────────────
#  API KEY DESDE SECRETS
# ─────────────────────────────────────────────
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    API_KEY = None

# ─────────────────────────────────────────────
#  FUNCIONES API
# ─────────────────────────────────────────────
def get_headers(field_mask):
    return {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': field_mask
    }

@st.cache_data(ttl=600, show_spinner=False)
def _autocompletar(texto, tipos_tuple=None, bias_lat=None, bias_lng=None):
    if not texto or len(texto.strip()) < 2 or not API_KEY:
        return []
    body = {'input': texto, 'languageCode': 'es'}
    if tipos_tuple:
        body['includedPrimaryTypes'] = list(tipos_tuple)
    if bias_lat is not None and bias_lng is not None:
        body['locationBias'] = {
            'circle': {
                'center': {'latitude': bias_lat, 'longitude': bias_lng},
                'radius': 30000.0,
            }
        }
    try:
        r = requests.post(
            AUTOCOMPLETE_URL,
            headers={'Content-Type': 'application/json', 'X-Goog-Api-Key': API_KEY},
            json=body,
            timeout=5,
        )
        data = r.json()
    except Exception:
        return []
    out = []
    for s in data.get('suggestions', []):
        pp = s.get('placePrediction')
        if pp:
            txt = pp.get('text', {}).get('text', '')
            if txt:
                out.append(txt)
    return out

def buscar_ciudades(texto):
    return _autocompletar(texto, tipos_tuple=('(cities)',))

def hacer_buscador_hoteles(lat, lng):
    def _buscar(texto):
        return _autocompletar(texto, bias_lat=lat, bias_lng=lng)
    return _buscar

def haversine(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        return float('inf')
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return 2 * R * asin(sqrt(a))

def abierto_en_fechas(periods, fechas):
    """True si el lugar está abierto al menos un día del viaje, o si no hay datos."""
    if not periods:
        return True
    dias_google = {(f.weekday() + 1) % 7 for f in fechas}
    for p in periods:
        dia_abierto = p.get('open', {}).get('day')
        if dia_abierto in dias_google:
            return True
    return False

def eur_to_level(eur, infinito_arriba=False):
    """Convierte un valor en € a price level de Google. Si infinito_arriba y eur=500, no hay tope."""
    if infinito_arriba and eur >= 500:
        return None
    if eur <= 0:   return 0
    if eur <= 50:  return 1
    if eur <= 150: return 2
    if eur <= 300: return 3
    return 4

def formato_hora(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh, mm = hh + 1, 0
    return f"{hh:02d}:{mm:02d}"

def asignar_horas_df(df_plan):
    """Añade columna 'hora' a df_plan distribuyendo las actividades por franjas
    horarias según el tipo. Devuelve el df ordenado cronológicamente por día."""
    if df_plan.empty:
        df_plan = df_plan.copy()
        df_plan['hora'] = pd.Series(dtype='float64')
        return df_plan

    df = df_plan.copy().reset_index(drop=True)
    df['hora'] = None

    for dia, grupo in df.groupby('dia'):
        n = len(grupo)
        # Franjas base: mañana, media mañana, comida, tarde, tarde-noche, noche
        slots = [9.5, 11.5, 13.5, 16.0, 18.5, 21.0][:max(n, 1)]
        slots_libres = list(slots)
        # Los tipos con franjas más estrechas eligen primero
        idx_ordenados = sorted(
            grupo.index,
            key=lambda i: HORA_PREF_ORDEN.index(df.at[i, 'tipo']) if df.at[i, 'tipo'] in HORA_PREF_ORDEN else 999
        )
        for i in idx_ordenados:
            tipo = df.at[i, 'tipo']
            ideales = TIPO_IDEAL_HORAS.get(tipo, [11.0, 16.0, 18.5])
            mejor = None
            mejor_dist = float('inf')
            for cand in slots_libres:
                d = min(abs(cand - p) for p in ideales)
                if d < mejor_dist:
                    mejor_dist = d
                    mejor = cand
            if mejor is None and slots_libres:
                mejor = slots_libres[0]
            if mejor is not None:
                slots_libres.remove(mejor)
                df.at[i, 'hora'] = mejor

    df = df.sort_values(['dia', 'hora'], na_position='last').reset_index(drop=True)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_coords(ciudad):
    r = requests.post(
        TEXT_URL,
        headers=get_headers('places.location,places.displayName'),
        json={'textQuery': ciudad}, timeout=10
    )
    data = r.json()
    if 'error' in data:
        return None, None, data['error']['message']
    places = data.get('places', [])
    if not places:
        return None, None, f'Ciudad no encontrada: {ciudad}'
    loc    = places[0]['location']
    nombre = places[0].get('displayName', {}).get('text', ciudad)
    return loc['latitude'], loc['longitude'], nombre

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_lugares(lat, lng, tipo_google, radio_m):
    body = {
        'includedTypes': [tipo_google],
        'maxResultCount': 20,
        'locationRestriction': {
            'circle': {'center': {'latitude': lat, 'longitude': lng}, 'radius': float(radio_m)}
        },
        'rankPreference': 'POPULARITY'
    }
    field_mask = ','.join([
        'places.id', 'places.displayName', 'places.rating',
        'places.userRatingCount', 'places.priceLevel',
        'places.formattedAddress', 'places.location',
        'places.currentOpeningHours', 'places.regularOpeningHours',
        'places.primaryType', 'places.editorialSummary',
    ])
    r    = requests.post(NEARBY_URL, headers=get_headers(field_mask), json=body, timeout=10)
    data = r.json()
    if 'error' in data:
        return [], data['error']['message']
    return data.get('places', []), None

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_detalles(place_id):
    field_mask = ','.join([
        'displayName', 'rating', 'userRatingCount', 'priceLevel',
        'formattedAddress', 'nationalPhoneNumber', 'websiteUri',
        'regularOpeningHours', 'reviews', 'editorialSummary'
    ])
    r = requests.get(
        f'{DETAIL_URL}{place_id}',
        headers=get_headers(field_mask),
        params={'languageCode': 'es'}, timeout=10
    )
    return r.json()

def extraer(lugar, tipo_nombre):
    pk = lugar.get('priceLevel')
    periods = (lugar.get('regularOpeningHours') or {}).get('periods') or []
    return {
        'place_id':        lugar.get('id', ''),
        'nombre':          lugar.get('displayName', {}).get('text', ''),
        'tipo':            tipo_nombre,
        'rating':          lugar.get('rating'),
        'n_reviews':       lugar.get('userRatingCount', 0),
        'precio':          PRECIO_LABEL.get(pk, '❓ Desconocido'),
        'precio_num':      PRECIO_NUM.get(pk),
        'direccion':       lugar.get('formattedAddress', ''),
        'lat':             lugar.get('location', {}).get('latitude'),
        'lng':             lugar.get('location', {}).get('longitude'),
        'abierto':         lugar.get('currentOpeningHours', {}).get('openNow'),
        'descripcion':     lugar.get('editorialSummary', {}).get('text', ''),
        'opening_periods': periods,
    }

TIPO_RESTAURANTE = '🍽️ Restaurantes'

def asignar_planning(df_f, dias, act_por_dia, hotel_coords, regimen):
    """Construye el planning día a día sin repetir tipo y respetando el régimen.
    Prioriza museos y atracciones sobre parques/cafés/bares (TIPO_PESO). Si hay
    hotel usa sus coords como ancla estricta; si no, usa como ancla global la
    actividad con mayor rating·peso, para que todo el viaje se agrupe allí."""
    if df_f.empty:
        return df_f.assign(dia=pd.Series(dtype=int))

    if regimen == 'Pensión completa':
        df_f = df_f[df_f['tipo'] != TIPO_RESTAURANTE]
        max_rest = 0
    elif regimen == 'Media pensión':
        max_rest = max(1, dias // 2)
    else:
        max_rest = dias

    df_f = df_f.copy()
    df_f['peso'] = df_f['tipo'].map(TIPO_PESO).fillna(1.0)
    df_f['pts']  = df_f['rating'].fillna(0) * df_f['peso']
    df_f = df_f.sort_values('pts', ascending=False).reset_index(drop=True)

    # Ancla global si no hay hotel: la mejor puntuación del pool (con coords)
    global_anchor = None
    if not hotel_coords:
        con_coords = df_f.dropna(subset=['lat', 'lng'])
        if not con_coords.empty:
            top = con_coords.iloc[0]
            global_anchor = (top['lat'], top['lng'])

    dist_penalty = 0.25 if hotel_coords else 0.20

    used = set()
    rest_count = 0
    asignaciones = []

    def puede_coger(row):
        return not (row['tipo'] == TIPO_RESTAURANTE and rest_count >= max_rest)

    for dia in range(1, dias + 1):
        ancla_dia = hotel_coords or global_anchor

        # Elegir actividades del día con tipos distintos, priorizando score mixto
        scored = []
        for i, row in df_f.iterrows():
            if i in used: continue
            if not puede_coger(row): continue
            if ancla_dia and pd.notna(row['lat']) and pd.notna(row['lng']):
                dist = haversine(ancla_dia[0], ancla_dia[1], row['lat'], row['lng'])
            else:
                dist = 0
            scored.append((row['pts'] - dist_penalty * dist, i))
        scored.sort(reverse=True)

        seleccion = []
        tipos_dia = set()
        for _, i in scored:
            if len(seleccion) >= act_por_dia:
                break
            tipo_i = df_f.at[i, 'tipo']
            if tipo_i in tipos_dia:
                continue
            seleccion.append(i)
            tipos_dia.add(tipo_i)
            used.add(i)
            if tipo_i == TIPO_RESTAURANTE:
                rest_count += 1

        # Relajar exclusividad de tipo si no llegamos al objetivo
        if len(seleccion) < act_por_dia:
            for _, i in scored:
                if len(seleccion) >= act_por_dia: break
                if i in used: continue
                if not puede_coger(df_f.loc[i]): continue
                seleccion.append(i)
                used.add(i)
                if df_f.at[i, 'tipo'] == TIPO_RESTAURANTE:
                    rest_count += 1

        if not seleccion:
            break

        for i in seleccion:
            asignaciones.append((i, dia))

    if not asignaciones:
        return df_f.iloc[0:0].assign(dia=pd.Series(dtype=int))

    indices = [i for i, _ in asignaciones]
    dias_col = [d for _, d in asignaciones]
    df_plan = df_f.loc[indices].drop(columns=['peso', 'pts']).copy()
    df_plan['dia'] = dias_col
    return df_plan.reset_index(drop=True)

# ─────────────────────────────────────────────
#  SESSION STATE — persiste el planning entre rerenders
# ─────────────────────────────────────────────
for key, default in {
    'df_plan': None, 'df_todos': None,
    'ciudad_resultado': None, 'coords': (None, None),
    'dias_res': 3, 'act_por_dia_res': 3,
    'fechas_res': None, 'hotel_res': None, 'regimen_res': 'Solo alojamiento',
    'coords_ciudad': (None, None),
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ TravelPlanner")
    st.markdown("---")

    if not API_KEY:
        st.error("⚠️ Añade GOOGLE_API_KEY en Settings → Secrets")

    st.markdown("### 📍 Destino")
    ciudad = st_searchbox(
        buscar_ciudades,
        key="ciudad_sb",
        placeholder="Madrid, París, Roma...",
        label="Ciudad",
        clear_on_submit=False,
    )

    # Coords de la ciudad (para sesgar hoteles al escribir)
    lat_ciudad = lng_ciudad = None
    if ciudad and API_KEY:
        lat_ciudad, lng_ciudad, _ = obtener_coords(ciudad)
        if lat_ciudad is not None:
            st.session_state.coords_ciudad = (lat_ciudad, lng_ciudad)

    st.markdown("### 🏨 Alojamiento (opcional)")
    hotel = st_searchbox(
        hacer_buscador_hoteles(lat_ciudad, lng_ciudad),
        key="hotel_sb",
        placeholder="Nombre del hotel o dirección…",
        label="Hotel / dirección",
        clear_on_submit=False,
    )
    regimen = st.radio(
        "Régimen",
        options=['Solo alojamiento', 'Media pensión', 'Pensión completa'],
        index=0,
        horizontal=False,
    )

    st.markdown("### 📅 Fechas del viaje")
    hoy = date.today()
    fechas_sel = st.date_input(
        "Rango",
        value=(hoy, hoy + timedelta(days=2)),
        min_value=hoy,
    )
    if isinstance(fechas_sel, (tuple, list)) and len(fechas_sel) == 2:
        fecha_ini, fecha_fin = fechas_sel
    elif isinstance(fechas_sel, (tuple, list)) and len(fechas_sel) == 1:
        fecha_ini = fecha_fin = fechas_sel[0]
    else:
        fecha_ini = fecha_fin = fechas_sel
    dias = (fecha_fin - fecha_ini).days + 1
    st.caption(f"🗓️ {dias} día(s) de viaje")

    act_por_dia = st.number_input("Actividades por día", min_value=1, max_value=6, value=3)

    st.markdown("### 💰 Presupuesto")
    precio_min_eur, precio_max_eur = st.slider(
        "Rango por persona / día (€)",
        min_value=0, max_value=500, value=(50, 300), step=25,
    )
    txt_max = "+500 € (sin límite)" if precio_max_eur == 500 else f"{precio_max_eur} €"
    st.caption(f"💰 Desde {precio_min_eur} €  →  hasta {txt_max}")

    st.markdown("### 🎯 Preferencias")
    gustos = st.multiselect(
        "Tipos de lugar",
        options=list(TIPOS_GOOGLE.keys()),
        default=['🏛️ Atracciones', '🎨 Museos', '🍽️ Restaurantes', '☕ Cafeterías'],
    )
    if not gustos:
        gustos = list(TIPOS_GOOGLE.keys())

    st.markdown("### ⭐ Calidad mínima")
    rating_min = st.slider("Rating mínimo", 1.0, 5.0, 4.0, 0.1)
    radio_km   = st.slider("Radio de búsqueda (km)", 1, 20, 5)

    st.markdown("---")
    buscar = st.button("🗺️ Generar Planning")

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Planifica tu viaje perfecto</h1>
    <p>Recomendaciones personalizadas basadas en ratings reales, adaptadas a tu presupuesto y gustos.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BÚSQUEDA — solo al pulsar el botón
# ─────────────────────────────────────────────
if buscar:
    if not API_KEY:
        st.error("⚠️ Falta la API Key.")
        st.stop()
    if not ciudad:
        st.error("⚠️ Elige una ciudad de destino.")
        st.stop()

    with st.spinner(f"🔍 Buscando los mejores sitios en {ciudad}..."):
        lat_c, lng_c, nombre_ciudad = obtener_coords(ciudad)

    if lat_c is None:
        st.error(f"❌ No se pudo encontrar: {nombre_ciudad}")
        st.stop()

    # Si hay hotel, sus coords son el centro de búsqueda; si no, la ciudad.
    hotel_coords = None
    if hotel:
        h_lat, h_lng, _ = obtener_coords(hotel)
        if h_lat is not None:
            hotel_coords = (h_lat, h_lng)
    centro = hotel_coords or (lat_c, lng_c)

    # Lista de fechas del viaje
    fechas_viaje = [fecha_ini + timedelta(days=i) for i in range(dias)]

    todos    = []
    progress = st.progress(0, text="Consultando la API...")
    for i, tipo_nombre in enumerate(gustos):
        lugares, err = buscar_lugares(centro[0], centro[1], TIPOS_GOOGLE[tipo_nombre], radio_km * 1000)
        if err:
            st.warning(f"⚠️ Error buscando {tipo_nombre}: {err}")
        for l in lugares:
            todos.append(extraer(l, tipo_nombre))
        progress.progress((i + 1) / len(gustos), text=f"Buscando {tipo_nombre}...")
        time.sleep(0.1)
    progress.empty()

    if not todos:
        st.error("❌ No se encontraron lugares.")
        st.stop()

    df = pd.DataFrame(todos)
    df['abierto_en_fechas'] = df['opening_periods'].apply(
        lambda p: abierto_en_fechas(p, fechas_viaje)
    )
    precio_min_lvl = eur_to_level(precio_min_eur)
    precio_max_lvl = eur_to_level(precio_max_eur, infinito_arriba=True)
    precio_ok = df['precio_num'].isna() | (
        (df['precio_num'] >= precio_min_lvl) &
        ((df['precio_num'] <= (precio_max_lvl if precio_max_lvl is not None else 4)))
    )
    df_f = df[
        (df['rating'].notna()) &
        (df['rating'] >= rating_min) &
        df['abierto_en_fechas'] &
        precio_ok
    ].drop_duplicates(subset='nombre').sort_values('rating', ascending=False).reset_index(drop=True)

    df_plan = asignar_planning(df_f, dias, act_por_dia, hotel_coords, regimen)
    df_plan = asignar_horas_df(df_plan)

    # Guardar todo en session_state
    st.session_state.df_plan          = df_plan
    st.session_state.df_todos         = df_f
    st.session_state.ciudad_resultado = nombre_ciudad
    st.session_state.coords           = centro
    st.session_state.dias_res         = dias
    st.session_state.act_por_dia_res  = act_por_dia
    st.session_state.fechas_res       = (fecha_ini, fecha_fin)
    st.session_state.hotel_res        = hotel if hotel else None
    st.session_state.regimen_res      = regimen

# ─────────────────────────────────────────────
#  MOSTRAR RESULTADOS (siempre desde session_state)
# ─────────────────────────────────────────────
if st.session_state.df_plan is None:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">🧳</div>
        <h3>¿A dónde vamos?</h3>
        <p>Configura tu viaje en el panel de la izquierda y pulsa <b>Generar Planning</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Recuperar del estado
df_plan       = st.session_state.df_plan
df_todos      = st.session_state.df_todos
nombre_ciudad = st.session_state.ciudad_resultado
lat, lng      = st.session_state.coords
dias_res      = st.session_state.dias_res
act_res       = st.session_state.act_por_dia_res

if len(df_plan) == 0:
    st.warning("⚠️ No hay lugares con esos filtros. Baja el rating mínimo o amplía el presupuesto.")
    st.stop()

# Stats
st.markdown(f"## 📍 {nombre_ciudad}")
fechas_res = st.session_state.get('fechas_res')
hotel_res  = st.session_state.get('hotel_res')
regimen_res = st.session_state.get('regimen_res', 'Solo alojamiento')
subline = []
if fechas_res:
    fi, ff = fechas_res
    subline.append(f"🗓️ {fi.strftime('%d %b %Y')} → {ff.strftime('%d %b %Y')}")
if hotel_res:
    subline.append(f"🏨 {hotel_res}")
subline.append(f"🍽️ {regimen_res}")
if subline:
    st.caption("  ·  ".join(subline))

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="num">{dias_res}</div><div class="lbl">Días de viaje</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="num">{len(df_plan)}</div><div class="lbl">Actividades</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="num">{df_plan["rating"].mean():.1f}⭐</div><div class="lbl">Rating medio</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-box"><div class="num">{df_plan["tipo"].nunique()}</div><div class="lbl">Tipos de plan</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_planning, tab_mapa, tab_explorar = st.tabs(["📅 Planning", "🗺️ Mapa", "🔍 Explorar lugares"])

# ── TAB 1: PLANNING ──────────────────────────
with tab_planning:
    fecha_ini_res = fechas_res[0] if fechas_res else None
    for dia in range(1, dias_res + 1):
        acts = df_plan[df_plan['dia'] == dia]
        if acts.empty:
            continue
        if fecha_ini_res:
            fecha_dia = fecha_ini_res + timedelta(days=dia - 1)
            encabezado = f'Día {dia} · {fecha_dia.strftime("%a %d %b %Y").capitalize()}'
        else:
            encabezado = f'Día {dia}'
        st.markdown(f'<div class="day-header">{encabezado}</div>', unsafe_allow_html=True)
        for _, act in acts.iterrows():
            abierto_badge = ""
            if act['abierto'] is True:
                abierto_badge = '<span class="badge badge-open">Abierto ahora</span>'
            elif act['abierto'] is False:
                abierto_badge = '<span class="badge" style="background:#FEE2E2;color:#991B1B;">Cerrado</span>'
            n_rev    = f"{int(act['n_reviews']):,} reseñas" if act['n_reviews'] else ""
            desc     = f'<div class="desc">{act["descripcion"]}</div>' if act["descripcion"] else ""
            stars    = '⭐' * int(round(act['rating']))
            hora_html = (
                f'<div class="hora-slot">🕐 {formato_hora(act["hora"])}</div>'
                if pd.notna(act.get('hora')) else ''
            )
            maps_url = (
                f'https://www.google.com/maps/search/?api=1'
                f'&query={quote(act["nombre"])}'
                f'&query_place_id={act["place_id"]}'
            )
            links_html = (
                f'<div class="links">'
                f'<a href="{maps_url}" target="_blank" rel="noopener">🗺️ Ver en Google Maps</a>'
                f'</div>'
            )
            st.markdown(
                f'<div class="place-card">'
                f'{hora_html}'
                f'<h4>{act["nombre"]}</h4>'
                f'<div class="meta">📍 {act["direccion"]} &nbsp;|&nbsp; {n_rev}</div>'
                f'<span class="badge badge-type">{act["tipo"]}</span>'
                f'<span class="badge badge-price">{act["precio"]}</span>'
                f'{abierto_badge}'
                f'<div style="margin-top:8px;">{stars} '
                f'<span style="color:#888;font-size:0.85rem;">{act["rating"]:.1f}/5</span></div>'
                f'{desc}'
                f'{links_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            with st.expander(f"Más detalles de {act['nombre']}"):
                with st.spinner("Cargando detalles..."):
                    det = obtener_detalles(act['place_id'])
                web = det.get('websiteUri')
                tel = det.get('nationalPhoneNumber')
                if web:
                    st.markdown(f"**🌐 Web:** [{web}]({web})")
                if tel:
                    st.markdown(f"**📞 Teléfono:** {tel}")
                reviews = det.get('reviews', [])
                if not reviews:
                    st.info("No hay reviews disponibles.")
                for rev in reviews[:5]:
                    autor   = rev.get('authorAttribution', {}).get('displayName', 'Anónimo')
                    texto   = rev.get('text', {}).get('text', '')
                    n_stars = int(rev.get('rating', 0))
                    tiempo  = rev.get('relativePublishTimeDescription', '')
                    st.markdown(
                        f'<div class="review-box">'
                        f'<div class="author">{"⭐" * n_stars} {autor} '
                        f'<span style="color:#aaa;font-weight:300;">· {tiempo}</span></div>'
                        f'{texto[:400]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                horarios = det.get('regularOpeningHours', {}).get('weekdayDescriptions', [])
                if horarios:
                    st.markdown("**🕐 Horarios:**")
                    for h in horarios:
                        st.markdown(f"- {h}")

# ── TAB 2: MAPA ──────────────────────────────
with tab_mapa:
    mapa = folium.Map(location=[lat, lng], zoom_start=13, tiles='CartoDB positron')
    if hotel_res:
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(f"<b>🏨 {hotel_res}</b>", max_width=260),
            tooltip=f"Alojamiento: {hotel_res}",
            icon=folium.Icon(color='black', icon='home', prefix='glyphicon'),
        ).add_to(mapa)
    for dia in range(1, dias_res + 1):
        grupo = folium.FeatureGroup(name=f'Día {dia}')
        color = COLORES_DIA[(dia - 1) % len(COLORES_DIA)]
        for _, act in df_plan[df_plan['dia'] == dia].iterrows():
            if act['lat'] and act['lng']:
                hora_txt = formato_hora(act['hora']) if pd.notna(act.get('hora')) else ''
                hora_popup = f"🕐 {hora_txt}<br>" if hora_txt else ''
                tooltip_prefix = f"Día {dia}" + (f" · {hora_txt}" if hora_txt else '')
                folium.Marker(
                    location=[act['lat'], act['lng']],
                    popup=folium.Popup(
                        f"<b>{act['nombre']}</b><br>{hora_popup}Día {dia} · {act['tipo']}<br>"
                        f"⭐ {act['rating']} · {act['precio']}<br>📍 {act['direccion']}",
                        max_width=260
                    ),
                    tooltip=f"{tooltip_prefix}: {act['nombre']}",
                    icon=folium.Icon(color=color, icon=ICONOS_TIPO.get(act['tipo'], 'info-sign'), prefix='glyphicon')
                ).add_to(grupo)
        grupo.add_to(mapa)
    folium.LayerControl().add_to(mapa)
    st_folium(mapa, width=None, height=550)

# ── TAB 3: EXPLORAR ──────────────────────────
with tab_explorar:
    st.markdown("#### Todos los lugares encontrados")
    st.caption(f"{len(df_todos)} lugares que cumplen tus filtros.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipo_filtro = st.selectbox("Filtrar por tipo", ['Todos'] + list(df_todos['tipo'].unique()))
    with col_f2:
        orden = st.selectbox("Ordenar por", ['Rating (mayor)', 'Rating (menor)', 'Nº reseñas'])

    df_vista = df_todos.copy()
    if tipo_filtro != 'Todos':
        df_vista = df_vista[df_vista['tipo'] == tipo_filtro]
    df_vista = df_vista.sort_values(
        'rating' if 'Rating' in orden else 'n_reviews',
        ascending=orden == 'Rating (menor)'
    )

    for _, row in df_vista.iterrows():
        n_rev = f"{int(row['n_reviews']):,} reseñas" if row['n_reviews'] else ""
        desc  = f'<div class="desc">{row["descripcion"]}</div>' if row["descripcion"] else ""
        stars = '⭐' * int(round(row['rating']))
        maps_url = (
            f'https://www.google.com/maps/search/?api=1'
            f'&query={quote(row["nombre"])}'
            f'&query_place_id={row["place_id"]}'
        )
        st.markdown(
            f'<div class="place-card">'
            f'<h4>{row["nombre"]}</h4>'
            f'<div class="meta">📍 {row["direccion"]} &nbsp;|&nbsp; {n_rev}</div>'
            f'<span class="badge badge-type">{row["tipo"]}</span>'
            f'<span class="badge badge-price">{row["precio"]}</span>'
            f'<div style="margin-top:8px;">{stars} '
            f'<span style="color:#888;font-size:0.85rem;">{row["rating"]:.1f}/5</span></div>'
            f'{desc}'
            f'<div class="links">'
            f'<a href="{maps_url}" target="_blank" rel="noopener">🗺️ Ver en Google Maps</a>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )