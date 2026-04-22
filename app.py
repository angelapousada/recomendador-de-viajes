import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
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
NEARBY_URL = 'https://places.googleapis.com/v1/places:searchNearby'
TEXT_URL   = 'https://places.googleapis.com/v1/places:searchText'
DETAIL_URL = 'https://places.googleapis.com/v1/places/'

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
        'places.currentOpeningHours', 'places.primaryType',
        'places.editorialSummary'
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
    return {
        'place_id':    lugar.get('id', ''),
        'nombre':      lugar.get('displayName', {}).get('text', ''),
        'tipo':        tipo_nombre,
        'rating':      lugar.get('rating'),
        'n_reviews':   lugar.get('userRatingCount', 0),
        'precio':      PRECIO_LABEL.get(pk, '❓ Desconocido'),
        'precio_num':  PRECIO_NUM.get(pk),
        'direccion':   lugar.get('formattedAddress', ''),
        'lat':         lugar.get('location', {}).get('latitude'),
        'lng':         lugar.get('location', {}).get('longitude'),
        'abierto':     lugar.get('currentOpeningHours', {}).get('openNow'),
        'descripcion': lugar.get('editorialSummary', {}).get('text', ''),
    }

# ─────────────────────────────────────────────
#  SESSION STATE — persiste el planning entre rerenders
# ─────────────────────────────────────────────
for key, default in {
    'df_plan': None, 'df_todos': None,
    'ciudad_resultado': None, 'coords': (None, None),
    'dias_res': 3, 'act_por_dia_res': 3
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
    ciudad = st.text_input("Ciudad", placeholder="Madrid, París, Roma...")

    st.markdown("### 📅 Viaje")
    col1, col2 = st.columns(2)
    with col1:
        dias = st.number_input("Días", min_value=1, max_value=14, value=3)
    with col2:
        act_por_dia = st.number_input("Act/día", min_value=1, max_value=6, value=3)

    st.markdown("### 💰 Presupuesto")
    presupuesto = st.select_slider(
        "Nivel de gasto",
        options=['Gratis', 'Económico', 'Moderado', 'Caro', 'Sin límite'],
        value='Moderado'
    )
    presupuesto_num = ['Gratis', 'Económico', 'Moderado', 'Caro', 'Sin límite'].index(presupuesto)

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
        st.error("⚠️ Escribe una ciudad de destino.")
        st.stop()

    with st.spinner(f"🔍 Buscando los mejores sitios en {ciudad}..."):
        lat, lng, nombre_ciudad = obtener_coords(ciudad)

    if lat is None:
        st.error(f"❌ No se pudo encontrar: {nombre_ciudad}")
        st.stop()

    todos    = []
    progress = st.progress(0, text="Consultando la API...")
    for i, tipo_nombre in enumerate(gustos):
        lugares, err = buscar_lugares(lat, lng, TIPOS_GOOGLE[tipo_nombre], radio_km * 1000)
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

    df   = pd.DataFrame(todos)
    df_f = df[
        (df['rating'].notna()) &
        (df['rating'] >= rating_min) &
        (
            (df['precio_num'].isna()) |
            (presupuesto_num == 4) |
            (df['precio_num'] <= presupuesto_num)
        )
    ].drop_duplicates(subset='nombre').sort_values('rating', ascending=False).reset_index(drop=True)

    total   = dias * act_por_dia
    df_plan = df_f.head(total).copy()
    df_plan['dia'] = [math.floor(i / act_por_dia) + 1 for i in range(len(df_plan))]

    # Guardar todo en session_state
    st.session_state.df_plan          = df_plan
    st.session_state.df_todos         = df_f
    st.session_state.ciudad_resultado = nombre_ciudad
    st.session_state.coords           = (lat, lng)
    st.session_state.dias_res         = dias
    st.session_state.act_por_dia_res  = act_por_dia

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
    for dia in range(1, dias_res + 1):
        acts = df_plan[df_plan['dia'] == dia]
        if acts.empty:
            continue
        st.markdown(f'<div class="day-header">Día {dia}</div>', unsafe_allow_html=True)
        for _, act in acts.iterrows():
            abierto_badge = ""
            if act['abierto'] is True:
                abierto_badge = '<span class="badge badge-open">Abierto ahora</span>'
            elif act['abierto'] is False:
                abierto_badge = '<span class="badge" style="background:#FEE2E2;color:#991B1B;">Cerrado</span>'
            n_rev = f"{int(act['n_reviews']):,} reseñas" if act['n_reviews'] else ""
            desc  = f'<div class="desc">{act["descripcion"]}</div>' if act["descripcion"] else ""
            st.markdown(f"""
            <div class="place-card">
                <h4>{act['nombre']}</h4>
                <div class="meta">📍 {act['direccion']} &nbsp;|&nbsp; {n_rev}</div>
                <span class="badge badge-type">{act['tipo']}</span>
                <span class="badge badge-price">{act['precio']}</span>
                {abierto_badge}
                <div style="margin-top:8px;">{'⭐' * int(round(act['rating']))} <span style="color:#888;font-size:0.85rem;">{act['rating']:.1f}/5</span></div>
                {desc}
            </div>
            """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div class="place-card">
            <h4>{row['nombre']}</h4>
            <div class="meta">📍 {row['direccion']} &nbsp;|&nbsp; {n_rev}</div>
            <span class="badge badge-type">{row['tipo']}</span>
            <span class="badge badge-price">{row['precio']}</span>
            <div style="margin-top:8px;">{'⭐' * int(round(row['rating']))} <span style="color:#888;font-size:0.85rem;">{row['rating']:.1f}/5</span></div>
            {desc}
        </div>
        """, unsafe_allow_html=True)