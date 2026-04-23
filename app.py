import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_searchbox import st_searchbox
from datetime import date, timedelta
from math import radians, cos, sin, asin, sqrt
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
    '🍽️ Restaurantes': 'restaurant',
    '🎨 Museos':       'museum',
    '🌿 Parques':      'park',
    '🎭 Arte':         'art_gallery',
    '🎡 Ocio':         'amusement_park',
}
COLORES_DIA = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'cadetblue']
ICONOS_TIPO = {
    '🏛️ Atracciones': 'star', '🍽️ Restaurantes': 'cutlery',
    '🎨 Museos': 'book', '🌿 Parques': 'leaf',
    '🎭 Arte': 'picture-frame', '🎡 Ocio': 'fire',
}

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
    """Construye el planning día a día, sin repetir tipo y respetando el régimen.
    Las actividades de cada día se eligen cerca del hotel si existe, o cerca
    entre sí (usando la primera actividad del día como ancla) si no."""
    if df_f.empty:
        return df_f.assign(dia=[])

    if regimen == 'Pensión completa':
        df_f = df_f[df_f['tipo'] != TIPO_RESTAURANTE]
        max_rest = 0
    elif regimen == 'Media pensión':
        max_rest = max(1, dias // 2)
    else:
        max_rest = dias  # sin restricción extra: la exclusividad de tipo ya limita a 1/día

    df_f = df_f.sort_values('rating', ascending=False).reset_index(drop=True)
    used = set()
    rest_count = 0
    asignaciones = []  # (idx_df, dia)

    def puede_coger(row):
        return not (row['tipo'] == TIPO_RESTAURANTE and rest_count >= max_rest)

    for dia in range(1, dias + 1):
        # Ancla del día: la mejor puntuación disponible
        anchor = None
        for i, row in df_f.iterrows():
            if i in used: continue
            if not puede_coger(row): continue
            anchor = i
            break
        if anchor is None:
            break

        tipos_dia = {df_f.at[anchor, 'tipo']}
        seleccion = [anchor]
        used.add(anchor)
        if df_f.at[anchor, 'tipo'] == TIPO_RESTAURANTE:
            rest_count += 1

        if hotel_coords:
            a_lat, a_lng = hotel_coords
        else:
            a_lat, a_lng = df_f.at[anchor, 'lat'], df_f.at[anchor, 'lng']

        # Candidatos restantes con score mixto (rating + cercanía)
        scored = []
        for i, row in df_f.iterrows():
            if i in used: continue
            if row['tipo'] in tipos_dia: continue
            if not puede_coger(row): continue
            dist = haversine(a_lat, a_lng, row['lat'], row['lng'])
            score = (row['rating'] or 0) - 0.15 * dist
            scored.append((score, i))
        scored.sort(reverse=True)

        for _, i in scored:
            if len(seleccion) >= act_por_dia:
                break
            tipo_i = df_f.at[i, 'tipo']
            if tipo_i in tipos_dia:
                continue
            if not puede_coger(df_f.loc[i]):
                continue
            seleccion.append(i)
            tipos_dia.add(tipo_i)
            used.add(i)
            if tipo_i == TIPO_RESTAURANTE:
                rest_count += 1

        # Si no llegamos al objetivo por falta de tipos distintos, relajamos la regla
        if len(seleccion) < act_por_dia:
            for i, row in df_f.iterrows():
                if len(seleccion) >= act_por_dia: break
                if i in used: continue
                if not puede_coger(row): continue
                seleccion.append(i)
                used.add(i)
                if row['tipo'] == TIPO_RESTAURANTE:
                    rest_count += 1

        for i in seleccion:
            asignaciones.append((i, dia))

    if not asignaciones:
        return df_f.iloc[0:0].assign(dia=pd.Series(dtype=int))

    indices = [i for i, _ in asignaciones]
    dias_col = [d for _, d in asignaciones]
    df_plan = df_f.loc[indices].copy()
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
    PRESUPUESTO_RANGOS = {
        'Hasta 50 €':  1,
        '50 – 150 €': 2,
        '150 – 300 €': 3,
        '300 – 500 €': 4,
        '+500 €':      None,
    }
    presupuesto = st.select_slider(
        "Rango de gasto por persona / día",
        options=list(PRESUPUESTO_RANGOS.keys()),
        value='150 – 300 €',
    )
    presupuesto_max = PRESUPUESTO_RANGOS[presupuesto]

    st.markdown("### 🎯 Preferencias")
    gustos = st.multiselect(
        "Tipos de lugar",
        options=list(TIPOS_GOOGLE.keys()),
        default=['🏛️ Atracciones', '🍽️ Restaurantes', '🌿 Parques'],
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
    df_f = df[
        (df['rating'].notna()) &
        (df['rating'] >= rating_min) &
        df['abierto_en_fechas'] &
        (
            (df['precio_num'].isna()) |
            (presupuesto_max is None) |
            (df['precio_num'] <= presupuesto_max)
        )
    ].drop_duplicates(subset='nombre').sort_values('rating', ascending=False).reset_index(drop=True)

    df_plan = asignar_planning(df_f, dias, act_por_dia, hotel_coords, regimen)

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
            n_rev = f"{int(act['n_reviews']):,} reseñas" if act['n_reviews'] else ""
            desc  = f'<div class="desc">{act["descripcion"]}</div>' if act["descripcion"] else ""
            stars = '⭐' * int(round(act['rating']))
            st.markdown(
                f'<div class="place-card">'
                f'<h4>{act["nombre"]}</h4>'
                f'<div class="meta">📍 {act["direccion"]} &nbsp;|&nbsp; {n_rev}</div>'
                f'<span class="badge badge-type">{act["tipo"]}</span>'
                f'<span class="badge badge-price">{act["precio"]}</span>'
                f'{abierto_badge}'
                f'<div style="margin-top:8px;">{stars} '
                f'<span style="color:#888;font-size:0.85rem;">{act["rating"]:.1f}/5</span></div>'
                f'{desc}'
                f'</div>',
                unsafe_allow_html=True,
            )

            with st.expander(f"Ver reviews de {act['nombre']}"):
                with st.spinner("Cargando reviews..."):
                    det = obtener_detalles(act['place_id'])
                reviews = det.get('reviews', [])
                if not reviews:
                    st.info("No hay reviews disponibles.")
                for rev in reviews[:5]:
                    autor  = rev.get('authorAttribution', {}).get('displayName', 'Anónimo')
                    texto  = rev.get('text', {}).get('text', '')
                    stars  = int(rev.get('rating', 0))
                    tiempo = rev.get('relativePublishTimeDescription', '')
                    st.markdown(f"""
                    <div class="review-box">
                        <div class="author">{'⭐' * stars} {autor} <span style="color:#aaa;font-weight:300;">· {tiempo}</span></div>
                        {texto[:400]}
                    </div>
                    """, unsafe_allow_html=True)
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
                folium.Marker(
                    location=[act['lat'], act['lng']],
                    popup=folium.Popup(
                        f"<b>{act['nombre']}</b><br>Día {dia} · {act['tipo']}<br>"
                        f"⭐ {act['rating']} · {act['precio']}<br>📍 {act['direccion']}",
                        max_width=260
                    ),
                    tooltip=f"Día {dia}: {act['nombre']}",
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
        st.markdown(
            f'<div class="place-card">'
            f'<h4>{row["nombre"]}</h4>'
            f'<div class="meta">📍 {row["direccion"]} &nbsp;|&nbsp; {n_rev}</div>'
            f'<span class="badge badge-type">{row["tipo"]}</span>'
            f'<span class="badge badge-price">{row["precio"]}</span>'
            f'<div style="margin-top:8px;">{stars} '
            f'<span style="color:#888;font-size:0.85rem;">{row["rating"]:.1f}/5</span></div>'
            f'{desc}'
            f'</div>',
            unsafe_allow_html=True,
        )