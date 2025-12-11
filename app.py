#Mas profesional

# dashboard_censo_powerbi_final_dark.py
# dashboard_censo_powerbi_final_dark_v3.py
#conda activate env



import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from datetime import datetime

# --- Configuración general ---
st.set_page_config(page_title="Dashboard ICSOH", layout="wide", page_icon="📊")

# --- Tema oscuro global ---
# ------------------------
# Estilo general de la app
# ------------------------
st.markdown("""
<style>
/* ------------------------
   Fondo y tipografía general
------------------------ */
.stApp {
    background-color: #F0F0F0;  /* gris claro para ver mapas */
    #background-color: #E0E0E0;  /* gris claro para que mapa se vea */        
    color: #202124;
    font-family: 'Roboto', sans-serif;
}
            


/* ------------------------
   Títulos
------------------------ */
h1 { color: #202124; font-weight: 700; font-size: 2.5rem; }
h2 { color: #202124; font-weight: 600; font-size: 2rem; }
h3 { color: #202124; font-weight: 500; font-size: 1.5rem; }

/* ------------------------
   Sidebar
------------------------ */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    color: #202124;
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
    border-radius: 0 8px 8px 0;
    padding: 1rem;
}

/* ------------------------
   Botones tipo Google
------------------------ */
.stButton>button {
    background-color: #1A73E8;
    color: white;
    border-radius: 4px;
    font-weight: 500;
    padding: 0.5rem 1rem;
    box-shadow: 0 2px 2px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #1669C1;
    transform: translateY(-2px);
}

/* ------------------------
   Métricas / KPI
------------------------ */
.stMetric-value { color: #1A73E8 !important; font-size: 2rem; font-weight: 700; }
.stMetric-label { color: #202124 !important; font-weight: 500; }

/* ------------------------
   Cards y contenedores
------------------------ */
.stContainer {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}
.stContainer:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

/* ------------------------
   DataFrames
------------------------ */
.stDataFrameHeader, .stDataFrame th, .stDataFrame td {
    color: #202124 !important;
    background-color: #FFFFFF !important;
    border-color: #E0E0E0 !important;
}
</style>
""", unsafe_allow_html=True)


# --- Cargar datos ---
@st.cache_data
def cargar_datos(ruta):
    df = pd.read_csv(ruta, encoding='latin1', sep=';')
    #df = pd.read_csv(ruta, encoding='utf-8', sep=';')

    df.columns = df.columns.str.strip()
    #df['fec_nac'] = pd.to_datetime(df['fec_nac'], errors='coerce')
    
    df['fec_nac'] = pd.to_datetime(df['fec_nac'], dayfirst=True, errors='coerce')
    #
    


    hoy = pd.Timestamp(datetime.today().date())
    df['edad'] = ((hoy - df['fec_nac']).dt.days / 365.25).astype(int)
    for col in ['BecaInicio','BecaFin','DoctoradoInicio','DoctoradoDefensa','AnoEgreso','AnoNacimiento']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

#df = cargar_datos("CensoA.csv")
df = cargar_datos("limpio.csv")

# --- Sidebar filtros ---
st.sidebar.title("Filtros Globales")
edad_min, edad_max = int(df['edad'].min()), int(df['edad'].max())
edad = st.sidebar.slider("Rango de edad", edad_min, edad_max, (edad_min, edad_max))

provincias = st.sidebar.multiselect("Provincia / País", df['lugar_nac'].unique(), placeholder="Elegir opciones")
generos = st.sidebar.multiselect("Género", df['genero'].unique(), placeholder="Elegir opciones")
estados_civiles = st.sidebar.multiselect("Estado civil", df['estado_civil'].unique(), placeholder="Elegir opciones")
niveles_academicos = st.sidebar.multiselect("Nivel académico", df['titulo'].unique(), placeholder="Elegir opciones")
instituciones = st.sidebar.multiselect("Institución / Área", df['institucion'].unique(), placeholder="Elegir opciones")
lineas = st.sidebar.multiselect("Líneas de investigación", df['tema'].dropna().unique(), placeholder="Elegir opciones")

df_filtrado = df[
    (df['edad'] >= edad[0]) & (df['edad'] <= edad[1]) &
    (df['lugar_nac'].isin(provincias if provincias else df['lugar_nac'])) &
    (df['genero'].isin(generos if generos else df['genero'])) &
    (df['estado_civil'].isin(estados_civiles if estados_civiles else df['estado_civil'])) &
    (df['titulo'].isin(niveles_academicos if niveles_academicos else df['titulo'])) &
    (df['institucion'].isin(instituciones if instituciones else df['institucion'])) &
    (df['tema'].isin(lineas if lineas else df['tema']))
]

# --- Función color KPI ---
def color_kpi(valor, minimo, maximo):
    if valor >= maximo*0.7:
        return "🟢"
    elif valor >= maximo*0.4:
        return "🟡"
    else:
        return "🔴"

st.title("📊 Dashboard Censo ICSOH")

# --- Pestañas ---
tabs = st.tabs([
    "Resumen / KPIs",
    "Perfil Demográfico",
    "Formación Académica",
    "Becas Doc.y Financiamiento",
    "Analisis Temporal de becas",
    "Becas PosDoc. y externas",
    "Docencia y Capacitación",
    "Producción Académica",
    "Tabla General",
    "Otros"
    
])

# ---------- Resumen / KPIs ----------
with tabs[0]:
    st.header("Resumen General del Censo")

    # --- Métricas ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total participantes", df_filtrado.shape[0])
    col2.metric("🎂 Edad promedio", round(df_filtrado['edad'].mean(), 1))
    col3.metric("👶 Promedio de hijos", round(df_filtrado['cta_hijos'].mean(), 1) if 'cta_hijos' in df_filtrado.columns else "N/A")
    col4.metric("⚥ Género más frecuente", df_filtrado['genero'].mode()[0] if not df_filtrado.empty else "N/A")

    # --- Gráficos lado a lado ---
    col_g1, col_g2 = st.columns(2, gap="medium")

    # Contar la cantidad de personas por género
    # Contar la cantidad de personas por género
    df_count = df_filtrado['genero'].value_counts().reset_index()
    df_count.columns = ['genero', 'count']  # ahora sí existe 'count'

    # Gráfico Pie con tooltip mostrando la cantidad
    fig_gen = px.pie(
        df_count,              # <-- paso df_count, no df_filtrado
        names='genero',
        values='count',
        title="Distribución de género",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data={'count': True}  # <-- ya funciona
    )

    fig_gen.update_traces(textinfo='percent+label')  # opcional: mostrar % y label

    fig_gen.update_layout(
        title_font=dict(color='#202124', size=22),
        font=dict(color='#202124', size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    col_g1.plotly_chart(fig_gen, width='stretch')

    # Gráfico 2: Estado civil (Bar)
    df_estado = df_filtrado['estado_civil'].value_counts().reset_index()
    df_estado.columns = ['estado_civil', 'count']
    fig_est = px.bar(
        df_estado,
        x='estado_civil',
        y='count',
        title="Estado Civil",
        color='estado_civil',
        color_discrete_sequence=px.colors.qualitative.Set1,
        text='count'  # 🔹 esto agrega los valores encima de las barras
    )
    fig_est.update_layout(
        #title_font=dict(color='white', size=22),
        #font=dict(color='white', size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #xaxis=dict(title_font=dict(color='white', size=16), tickfont=dict(color='white', size=14)),
        #yaxis=dict(title_font=dict(color='white', size=16), tickfont=dict(color='white', size=14))
    )

    fig_est.update_layout(
        title_font=dict(color='#202124', size=22),
        font=dict(color='#202124', size=14),
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',
        #xaxis=dict(title_font=dict(color='#202124', size=16),
        #           tickfont=dict(color='#202124', size=14)),
        #yaxis=dict(title_font=dict(color='#202124', size=16),
        #           tickfont=dict(color='#202124', size=14))
    )


    col_g2.plotly_chart(fig_est, width='stretch')


    #Lugar de nacimiento
    # 
    # # Gráfico 2: Estado civil (Bar)
    df_nac = df_filtrado['lugar_nac'].value_counts().reset_index()
    df_nac.columns = ['lugar_nac', 'count']
    fig_lug = px.bar(
        df_nac,
        x='lugar_nac',
        y='count',
        title="Lugar Naciomiento",
        color='lugar_nac',
        color_discrete_sequence=px.colors.qualitative.Set1,
        text='count'  # 🔹 esto agrega los valores encima de las barras
    )
    fig_lug.update_layout(
        #title_font=dict(color='white', size=22),
        #font=dict(color='white', size=14),
        showlegend=False,  # 🔹 saca la leyenda lateral
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #xaxis=dict(title_font=dict(color='white', size=16), tickfont=dict(color='white', size=14)),
        #yaxis=dict(title_font=dict(color='white', size=16), tickfont=dict(color='white', size=14))
    )

    fig_lug.update_layout(
        title_font=dict(color='#202124', size=22),
        font=dict(color='#202124', size=14),
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',
        #xaxis=dict(title_font=dict(color='#202124', size=16),
        #           tickfont=dict(color='#202124', size=14)),
        #yaxis=dict(title_font=dict(color='#202124', size=16),
        #           tickfont=dict(color='#202124', size=14))
    )


    st.plotly_chart(fig_lug, use_container_width=True)

    # --- Mapa a todo el ancho ---
    #st.subheader("Mapa de nacimiento")
    
# ---------- Mapa ----------
# ------------------------
# # Mapa de nacimiento
# # ------------------------

    
#     if 'LatitudNacimiento' in df_filtrado.columns and 'LongitudNacimiento' in df_filtrado.columns:
#         st.subheader("Mapa de nacimiento")

#         # Limpiar coordenadas
#         df_map = df_filtrado.dropna(subset=['LatitudNacimiento', 'LongitudNacimiento', 'lugar_nac']).copy()
#         df_map['LatitudNacimiento'] = pd.to_numeric(df_map['LatitudNacimiento'].astype(str).str.replace(',', '.'), errors='coerce')
#         df_map['LongitudNacimiento'] = pd.to_numeric(df_map['LongitudNacimiento'].astype(str).str.replace(',', '.'), errors='coerce')

#         # Filtrar coordenadas válidas
#         df_map = df_map[
#             df_map['LatitudNacimiento'].between(-90, 90) &
#             df_map['LongitudNacimiento'].between(-180, 180)
#         ]

#         if df_map.empty:
#             st.warning("No hay coordenadas válidas para mostrar el mapa.")
#         else:
#             # Agrupar por lugar_nac y coordenadas
#             df_grouped = df_map.groupby(['lugar_nac', 'LatitudNacimiento', 'LongitudNacimiento'], as_index=False).size()
#             df_grouped.rename(columns={'size': 'cantidad'}, inplace=True)

#             lat_centro = df_grouped['LatitudNacimiento'].mean()
#             lon_centro = df_grouped['LongitudNacimiento'].mean()

#             st.pydeck_chart(pdk.Deck(
#                 map_style='light',
#                 initial_view_state=pdk.ViewState(
#                     latitude=lat_centro,
#                     longitude=lon_centro,
#                     zoom=5
#                 ),
#                 layers=[
#                     pdk.Layer(
#                         "ScatterplotLayer",
#                         data=df_grouped,
#                         get_position=["LongitudNacimiento", "LatitudNacimiento"],
#                         get_color=[200, 30, 0, 200],
#                         get_radius="cantidad * 5000",  # tamaño proporcional a la cantidad
#                         pickable=True
#                     )
#                 ],
#                 tooltip={"text": "Lugar: {lugar_nac}\nCantidad: {cantidad}"},
#                 height=600
#             ))


# ---------- Perfil Demográfico ----------

def grafico_categorico(
    df, columna, titulo,
    umbral_horizontal=15, alto_vertical=400, alto_horizontal=400,
    ancho_vertical=600, ancho_horizontal=1200
):
    """
    Gráfico de barras categóricas:
    - Vertical si categorías cortas o numéricas
    - Horizontal si alguna categoría tiene texto largo
    """
    if columna in df.columns and not df[columna].dropna().empty:
        df_count = df[columna].value_counts().reset_index()
        df_count.columns = [columna, 'count']

        # Detectar si hay texto largo
        horizontal = df_count[columna].astype(str).map(len).max() > umbral_horizontal

        if horizontal:
            altura = alto_horizontal
            ancho = ancho_horizontal
            fig = px.bar(
                df_count,
                x='count',
                y=columna,
                color=columna,
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.Bold,
                title=titulo,
                height=altura,
                width=ancho,
                text='count'
            )
            # 👉 Quitar leyenda en horizontales
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition="inside")
            st.plotly_chart(fig, width='stretch')

        else:
            altura = alto_vertical
            ancho = ancho_vertical
            fig = px.bar(
                df_count,
                x=columna,
                y='count',
                color=columna,
                color_discrete_sequence=px.colors.qualitative.Bold,
                title=titulo,
                height=altura,
                width=ancho,
                text='count'
            )
            # 👉 En vertical la dejamos (si querés la podés quitar también)
            fig.update_traces(textposition="inside")
            st.plotly_chart(fig, width=False)

        # Fondo transparente y grillas suaves
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', dtick=1),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', dtick=1)
        )

    else:
        st.warning(f"No hay datos para la columna '{columna}'")


with tabs[1]:
    st.header("Perfil Demográfico Avanzado")

    # --- Histogramas numéricos ---
    #col1, col2 = st.columns(2, gap="medium")

    # Edad
    
    
    import plotly.graph_objects as go
# Histograma base
    fig_edad = px.histogram(
        df_filtrado,
        x="edad",
        nbins=20,
        color="genero" if 'genero' in df_filtrado.columns else None,
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Distribución de Edad",
        text_auto=True
    )

    # 🔹 Calcular la frecuencia por edad
    conteos = df_filtrado['edad'].value_counts().sort_index()
    x_vals = conteos.index
    y_vals = conteos.values

    fig_edad.update_layout(
        yaxis=dict(
            title="Cantidad de agentes"  # 🔹 título en el eje Y
        )
    )

    # 🔹 Agregar línea de tendencia (suavizada o directa)
    fig_edad.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines+markers",
            name="Tendencia",
            line=dict(color="red", width=2)
        )
    )

    st.plotly_chart(fig_edad, width='stretch')

    # Cantidad de hijos
    if 'cta_hijos' in df_filtrado.columns:
        df_filtrado['cta_hijos'] = df_filtrado['cta_hijos'].fillna(0).round(0).astype(int)
    
        fig_hijos = px.histogram(
            df_filtrado,
            x='cta_hijos',
            nbins=10,
            color='genero' if 'genero' in df_filtrado.columns else None,
            color_discrete_sequence=px.colors.qualitative.Bold,
            barmode="group",
            title="Cantidad de hijos por género",
            text_auto=True
        )

        fig_hijos.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )

        fig_hijos.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                dtick=1,
                showgrid=True,
                gridcolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                #visible=False   # 🔹 oculta eje Y (línea y ticks)
                title="Cantidad de agentes",  # 🔹 título del eje Y
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)'
            ),
            width=500,   # 🔹 más compacto
            height=350,  
            margin=dict(l=20, r=20, t=40, b=20)
        )

    st.plotly_chart(fig_hijos, width=False)  # 👈 mejor sin "container_width"
    
    # --- Gráficos categóricos ---
    st.subheader("Otras variables demográficas")
    
    categoricas = [
        ('cta_personas', 'Cantidad de personas a cargo'),
        ('aportemayor', 'Quién aporta más en el hogar'),
        ('habitabilidad','Situación habitacional'),
        #('Habitabilidad de la vivienda','habitabilidad'),
        ('vivienda_trabaja','Espacio de trabajo en la vivienda')
    ]



# Generar gráficos de forma secuencial, sin columnas
    for columna, titulo in categoricas:
        #st.write(columna)
        if columna == 'vivienda_trabaja':
            # Pie chart especial
            if columna in df_filtrado.columns and not df_filtrado[columna].dropna().empty:
                df_count = df_filtrado[columna].value_counts().reset_index()
                df_count.columns = [columna, 'count']

                fig_pie = px.pie(
                    df_count,
                    values='count',
                    names=columna,
                    title=titulo,
                    color=columna,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    hole=0.3  # 👈 donut
                )

                fig_pie.update_traces(
                    textinfo="value+percent",  # 👈 muestra categoría, valor y %
                    textposition="inside"            # 👈 pone los textos dentro de las porciones
                )

                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    width=1000,   # más ancho para la leyenda
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(
                        orientation="v",  # vertical
                        y=0.5,            # centrada verticalmente
                        x=0.85,           # dentro del gráfico, a la derecha
                        xanchor="left",
                        yanchor="middle",
                        font=dict(size=12)
                    )
                )

                st.plotly_chart(fig_pie, width=False)
            else:
                st.warning(f"No hay datos para la columna '{columna}'")
        elif columna == 'Habitabilidad':
                # Pie chart especial
                if columna in df_filtrado.columns and not df_filtrado[columna].dropna().empty:
                    df_count = df_filtrado[columna].value_counts().reset_index()
                    df_count.columns = [columna, 'count']

                    fig_pie = px.pie(
                        df_count,
                        values='count',
                        names=columna,
                        title=titulo,
                        color=columna,
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        hole=0.3  # 👈 donut
                    )

                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        width=1000,   # más ancho para la leyenda
                        height=500,
                        margin=dict(l=20, r=20, t=60, b=20),
                        legend=dict(
                            orientation="v",  # vertical
                            y=0.5,            # centrada verticalmente
                            x=0.85,           # dentro del gráfico, a la derecha
                            xanchor="left",
                            yanchor="middle",
                            font=dict(size=12)
                        )
                    )

                    st.plotly_chart(fig_pie, width=False)
                else:
                    st.warning(f"No hay datos para la columna '{columna}'")
        else:
            grafico_categorico(df_filtrado, columna, titulo)


# ---------- Formación Académica ----------

with tabs[2]:
    st.header("Formación Académica")
    
    if df_filtrado.empty:
        st.warning("No hay datos disponibles después de aplicar los filtros.")
    else:
        df_tab = df_filtrado.copy()
        # ------------------------
        # Titulo
        # ------------------------
        if 'titulo' in df_tab.columns:
            col1, col2 = st.columns(2)
            # Contar todas las carreras
            titulos = df_tab['titulo'].value_counts().reset_index()
            titulos.columns = ['titulo','cantidad']

            # Orden descendente
            titulos = titulos.sort_values(by='cantidad', ascending=True)  # ascending=True para que la más grande quede arriba

            fig_otro = px.bar(
                titulos,
                x='cantidad',
                y='titulo',
                orientation='h',
                labels={'titulo':'Título de carrera', 'cantidad':'Cantidad'},
                title="Distribución de títulos ",
                color='cantidad',
                color_continuous_scale='Blues',
                text='cantidad'
            )
            fig_otro.update_yaxes(automargin=True)  # 🔹 que entren todos los nombres
            fig_otro.update_layout(
                margin=dict(l=200, r=20, t=60, b=20)
            )
            # Forzar que respete el orden
            with col1:
  
                fig_otro.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_otro, width='stretch')


            titulos = df_tab['titulo'].value_counts().reset_index()
            titulos.columns = ['titulo','cantidad']

            fig_pie = px.pie(
                titulos,
                values='cantidad',
                names='titulo',
                title="Proporción de títulos",
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            fig_otro.update_layout(
                height=800,  # 🔹 más alto
                margin=dict(l=150, r=20, t=60, b=20)
                )

            # Opcional: mostrar valores y porcentajes en las etiquetas
            with col2:
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                
                fig_otro.update_layout(
                    height=800,  # 🔹 más alto
                    margin=dict(l=150, r=20, t=60, b=20)
                    )

                st.plotly_chart(fig_pie, width='stretch')

        
        
        # ------------------------
        # Promedio
        # ------------------------
        if 'promedio' in df_tab.columns:
            
            # Limpiar y convertir a float
            df_tab['promedio'] = (
                df_tab['promedio']
                .astype(str)                  # asegurar que sea string
                .str.replace(',', '.')        # reemplazar coma decimal si existe
                .str.extract(r'(\d+\.?\d*)')  # extraer solo números y punto
                .astype(float)                # convertir a float
            )
            
           
            #col1, col2 = st.columns(2)

            with col1:
                if 'institucion' in df_tab.columns:
                    # Contar cantidad de personas por institución
                    df_inst = df_tab['institucion'].value_counts().reset_index()
                    df_inst.columns = ['institucion', 'cantidad']

                    # Calcular porcentaje
                    total = df_inst['cantidad'].sum()
                    df_inst['porcentaje'] = (df_inst['cantidad'] / total * 100).round(2)

                    # Gráfico de barras con cantidad y color por porcentaje
                    fig_inst = px.bar(
                        df_inst,
                        x='institucion',
                        y='cantidad',
                        text='porcentaje',  # muestra el porcentaje encima de la barra
                        color='porcentaje',
                        color_continuous_scale=px.colors.sequential.Viridis,
                        title="Cantidad y porcentaje de personas por institución"
                        
                    )

                    # Ajustes visuales
                    fig_inst.update_traces(texttemplate='%{text}%')
                    fig_inst.update_layout(
                        xaxis_title="Institución",
                        yaxis_title="Cantidad de personas",
                        coloraxis_showscale=True
                    )

                    st.plotly_chart(fig_inst, width='stretch', key="inst_cantidad_porcentaje")

            with col2:
                fig_prom = px.histogram(
                    df_tab,
                    x='promedio',
                    title="Distribución general de promedios",
                    color_discrete_sequence=px.colors.sequential.Viridis,
                    text_auto=True
                )
                fig_prom.update_traces(textposition="inside")  # 👈 coloca los valores dentro de la barra
                fig_prom.update_layout(
                    bargap=0.2,
                    bargroupgap=0.1
                )

                st.plotly_chart(fig_prom, width='stretch', key="dist_general")

            
            if 'titulo' in df_tab.columns:
                fig_box = px.box(
                    df_tab,
                    x='promedio',
                    y='titulo',
                    title="Promedios por título(mediana)",
                    color='titulo',
                    color_discrete_sequence=px.colors.qualitative.Bold,

                    orientation='h',       # opcional: hace que las cajas sean horizontales y más legibles
                    height=600             # aumentamos la altura del gráfico

                )

                # Ocultar leyenda
                fig_box.update_layout(showlegend=False)


                # Tooltip simple solo con cuartiles
                fig_box.update_layout(showlegend=False)

                # Calcular cuartiles y mediana para cada categoría
                stats = df_tab.groupby("titulo")["promedio"].describe()[["25%","50%","75%"]].reset_index()
                # Renombrar para customdata
                stats.rename(columns={"25%":"q1","50%":"median","75%":"q3"}, inplace=True)

                # Asignar customdata a cada trazo
                # Calcular cuartiles para cada categoría

                # Asignar customdata y hovertemplate
                for trace in fig_box.data:
                    categoria = trace.name
                    q1, median, q3 = stats[stats["titulo"]==categoria][["q1","median","q3"]].values[0]
                    trace.customdata = [[q1, median, q3]] * len(trace.y)
                    trace.hovertemplate = (
                        "Q1: %{customdata[0]}<br>"
                        "Mediana: %{customdata[1]}<br>"
                        "Q3: %{customdata[2]}<extra></extra>"
                    )

                # Después de crear fig_box y calcular stats
                for trace in fig_box.data:
                    categoria = trace.name
                    median = stats[stats["titulo"]==categoria]["median"].values[0]
    
                    # Agregar anotación de la mediana
                    fig_box.add_trace(
                        go.Scatter(
                            x=[median],
                            y=[categoria],
                            text=[f"{median:.2f}"],   # formato con 2 decimales
                            mode="text",
                            showlegend=False,
                            textfont=dict(
                                size=12,       # 🔹 tamaño más grande
                                color="black", # 🔹 color
                                family="Arial Black"  # 🔹 negrita
                            )
                        )
                    )

                fig_box.update_xaxes(
                   showgrid=True,
                    gridcolor='rgba(128,128,128,0.5)',  # gris muy tenue
                    gridwidth=1
                )

                fig_box.update_yaxes(
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.5)',  # gris muy tenue
                    gridwidth=1,
                    automargin=True  # para que entren los labels largos
                )


                st.plotly_chart(fig_box, width='stretch')





        else:
            st.write("No está promedio")

        # ------------------------
        # Finalizó más de una carrera / Títulos de otra carrera
        # ------------------------
        col3, col4 = st.columns(2)

        with col3:
            if 'finalizo_masdeunacarrera' in df_tab.columns and not df_tab['finalizo_masdeunacarrera'].dropna().empty:
                fig_multi = px.pie(
                    df_tab,
                    names='finalizo_masdeunacarrera',
                    title="Finalizó más de una carrera",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4  # esto convierte el pie chart en dona
                )

                # Opcional: tooltip más simple
                fig_multi.update_traces(hovertemplate="%{label}: %{value}<extra></extra>")

                # Ajustes de layout (opcional)
                fig_multi.update_layout(
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend_title_text='',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )

                st.plotly_chart(fig_multi, width='stretch')

        with col4:
            if 'titulo_otracarrera' in df_tab.columns:
                top10_titulos = df_tab['titulo_otracarrera'].value_counts().nlargest(10).reset_index()
                top10_titulos.columns = ['titulo_otracarrera','cantidad']
                fig_otro = px.bar(
                    top10_titulos, x='cantidad', y='titulo_otracarrera',
                    orientation='h',
                    labels={'titulo_otracarrera':'Título otra carrera', 'cantidad':'Cantidad'},
                    title="Top 10 títulos de otra carrera",
                    color='cantidad',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig_otro, width='stretch')

        # ------------------------
        # Universidades / Fecha finalización
        # ------------------------
        col5, col6 = st.columns(2)

        with col5:
            if 'universidad_otracarrera' in df_tab.columns:
                top10_uni = df_tab['universidad_otracarrera'].value_counts().nlargest(10).reset_index()
                top10_uni.columns = ['universidad','cantidad']
                fig_uni = px.bar(
                    top10_uni, x='cantidad', y='universidad',
                    orientation='h',
                    labels={'universidad':'Universidad', 'cantidad':'Cantidad'},
                    title="Top 10 universidades de otra carrera",
                    color='cantidad',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_uni, width='stretch')

        with col6:
            if 'fec_finalizootracarrera' in df_tab.columns:
                    # Convertir a número, ignorando errores
                    df_tab['anio'] = pd.to_numeric(df_tab['fec_finalizootracarrera'], errors='coerce')

                    # Filtrar filas con años válidos
                    df_year = df_tab.dropna(subset=['anio'])

                    if not df_year.empty:
                        df_year['anio'] = df_year['anio'].astype(int)

                        # Crear décadas
                        min_anio = df_year['anio'].min()
                        max_anio = df_year['anio'].max()
                        bins = list(range(min_anio - min_anio % 10, max_anio + 10, 10))
                        labels = [f"{b}-{b+9}" for b in bins[:-1]]
                        df_year['decada'] = pd.cut(df_year['anio'], bins=bins, labels=labels, right=True)

                        # Contar cantidad por década
                        df_count = df_year['decada'].value_counts().reset_index()
                        df_count.columns = ['decada', 'cantidad']
                        df_count = df_count.sort_values('decada')

                        # Gráfico de barras verticales
                        fig_year = px.bar(
                            df_count,
                            x='decada',
                            y='cantidad',
                            text='cantidad',
                            title="Cantidad de personas por década de finalizaciónde otra carrera",
                            color='cantidad',
                            color_continuous_scale=px.colors.sequential.Plasma,
                            height=500
                        )

                        fig_year.update_traces(textposition='outside')
                        fig_year.update_layout(
                            xaxis_title="Década",
                            yaxis_title="Cantidad de personas"
                        )

                        st.plotly_chart(fig_year, width='stretch')
                    else:
                        st.write("No hay datos válidos de años de finalización de otra carrera.")
    ##idiomas

    # Lista de columnas de idiomas

    idiomas = ['ingles', 'frances', 'italiano', 'portugues', 'aleman', 'otroidioma']

    # Transformar el dataframe a formato largo (long format)
    df_idiomas_long = pd.DataFrame()

    for col in idiomas:
        temp = df_tab[[col]].dropna().copy()
        temp[col] = temp[col].str.split(';')  # separar valores múltiples
        temp = temp.explode(col)              # una fila por valor
        temp['idioma'] = col
        temp.rename(columns={col:'nivel'}, inplace=True)
        df_idiomas_long = pd.concat([df_idiomas_long, temp], axis=0)

    # Contar frecuencia de cada nivel por idioma
    df_idiomas_count = df_idiomas_long.groupby(['idioma', 'nivel']).size().reset_index(name='count')

    # Ordenar idiomas por total
    totales = df_idiomas_count.groupby('idioma')['count'].sum().reset_index()
    totales = totales.sort_values('count', ascending=False)
    df_idiomas_count['idioma'] = pd.Categorical(df_idiomas_count['idioma'], categories=totales['idioma'], ordered=True)

    # Ordenar niveles dentro de cada idioma
    niveles_ordenados = (
        df_idiomas_count.groupby('nivel')['count'].sum()
        .sort_values(ascending=False)
        .index
    )
    df_idiomas_count['nivel'] = pd.Categorical(df_idiomas_count['nivel'], categories=niveles_ordenados, ordered=True)

    # Gráfico de barras apiladas
    fig = px.bar(
        df_idiomas_count,
        x='idioma',
        y='count',
        color='nivel',
        text='count',
        title='Competencia por idioma',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Ajustar título del eje Y
    fig.update_layout(
        yaxis_title="Cantidad de agentes",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, width='stretch')



        




# ---------- Becas y Financiamiento ----------
with tabs[3]:
    # ---------------------------------
    # Cargar datos
    # ---------------------------------
    #df_tab = pd.read_csv("limpio.csv")  # o tu DataFrame ya cargado
    st.title(" Becas y Doctorados")

    # ---------------------------------
    # Filtros interactivos
    # ---------------------------------
    # ---- Filtros dentro de la pestaña, ocultos por defecto ----
#    with st.expander("Mostrar filtros de selección", expanded=False):
#        universidades = df_tab['uni_doctorado'].dropna().unique()
#        estado_beca = df_tab['estado_becadoc'].dropna().unique()
#        pais_ext = df_tab['pais_becaext'].dropna().unique()

#        uni_sel = st.multiselect("Seleccionar universidades:", universidades, default=universidades)
#        estado_sel = st.multiselect("Seleccionar estado de beca:", estado_beca, default=estado_beca)
#        pais_sel = st.multiselect("Seleccionar país de beca externa:", pais_ext, default=pais_ext)

#    # Si no se selecciona nada (porque el expander está cerrado), se toman todos los valores
#    if 'uni_sel' not in locals():
#        uni_sel = universidades
#    if 'estado_sel' not in locals():
#        estado_sel = estado_beca
#    if 'pais_sel' not in locals():
#        pais_sel = pais_ext

    # Filtrar DataFrame según selección
#    df_filtrado = df_tab[
#        df_tab['uni_doctorado'].isin(uni_sel) &
#        df_tab['estado_becadoc'].isin(estado_sel) &
#        df_tab['pais_becaext'].isin(pais_sel)
#    ]


    # ---------------------------------
    # Layout de columnas
    # ---------------------------------
    col1, col2 = st.columns(2)

    # ---- Columna 1 ----
    with col1:
        # Estado de la beca
        if 'estado_becadoc' in df_filtrado.columns:
            estado_count = df_filtrado['estado_becadoc'].value_counts().reset_index()
            estado_count.columns = ['Estado', 'Cantidad']
            fig_estado = px.pie(
                estado_count,
                values='Cantidad',
                names='Estado',
                title="Estado de las becas",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_estado, width='stretch')

        
        ###    


    # ---- Columna 2 ----
    with col2:
        # Cantidad de becarios por universidad
        if 'uni_doctorado' in df_filtrado.columns:
            # Filtrar nulos
            df_unidoc = df_filtrado.dropna(subset=['uni_doctorado'])
    
            # Separar múltiples universidades (si vienen en la misma celda separadas por ';') y quitar espacios
            universidades = df_unidoc['uni_doctorado'].str.split(';').explode().str.strip()
    
            # Contar correctamente
            uni_count = universidades.value_counts().reset_index()
            uni_count.columns = ['Universidad', 'Cantidad']
    
            #st.write("Conteo final por universidad:")
            #st.dataframe(uni_count)

            # Crear gráfico
            fig_unidoc = px.bar(
                uni_count,
                x='Cantidad',
                y='Universidad',
                orientation='h',
                text='Cantidad',
                title="Cantidad de becarios doctorales por universidad",
                color='Cantidad',
                color_continuous_scale=px.colors.sequential.Viridis,
                height=600
            )

        fig_unidoc.update_traces(textposition='outside')
        st.plotly_chart(fig_unidoc, width='stretch')
    
           
    ##
    col3, col4 = st.columns(2)
    with col3:
        # Becas en el extranjero por país
        # 1️⃣ Filtrar filas con valor
        df_ext = df_filtrado.dropna(subset=['pais_becaext'])

        if not df_ext.empty:
            # 2️⃣ Separar los países por ';' y aplanar la lista
            paises = df_ext['pais_becaext'].str.split(';').explode().str.strip()

            # 3️⃣ Contar cada país
            ext_count = paises.value_counts().reset_index()
            ext_count.columns = ['País', 'Cantidad']

            # 4️⃣ Crear gráfico
            fig_ext = px.bar(
                ext_count,
                x='Cantidad',
                y='País',
                orientation='h',
                text='Cantidad',
                title="Becas externas por país",
                color='Cantidad',
                color_continuous_scale=px.colors.sequential.Magma,
                height=400
            )

            fig_ext.update_traces(textposition='outside')

            st.plotly_chart(fig_ext, width='stretch')

    # ---- Gráfico ancho debajo ----
    # Año de inicio de doctorado
    with col4:
        if 'fec_ini_doc' in df_filtrado.columns:
            df_year = pd.to_numeric(df_filtrado['fec_ini_doc'], errors='coerce').dropna().astype(int)
            if not df_year.empty:
                df_count_year = df_year.value_counts().reset_index()
                df_count_year.columns = ['Año', 'Cantidad']
                df_count_year = df_count_year.sort_values('Año')

                fig_year = px.bar(
                    df_count_year,
                    x='Año',
                    y='Cantidad',
                    text='Cantidad',
                    title="Cantidad de becas doctorales por año de inicio",
                    color='Cantidad',
                    color_continuous_scale=px.colors.sequential.Plasma,
                    height=400
                )
                fig_year.update_traces(textposition='outside')
                st.plotly_chart(fig_year, width='stretch')

       # -----------------------
       # Tabla con temas e investigador
       # -----------------------
    if 'tema_investigacion' in df_filtrado.columns and 'director_doctorado' in df_filtrado.columns:
        df_temas = df_filtrado[['tema_investigacion','nombre', 'director_doctorado']].dropna()
        st.subheader("Tabla de temas de investigación e investigador")
        st.dataframe(df_temas.reset_index(drop=True), width='stretch')

    
    # Temas de investigación Nube
    if 'tema_investigacion' in df_filtrado.columns:
        from wordcloud import WordCloud, STOPWORDS
        import matplotlib.pyplot as plt
        import numpy as np

        textos = " ".join(df_filtrado['tema_investigacion'].dropna().tolist())

        # Stopwords
        mis_stopwords = set(STOPWORDS)
        mis_stopwords.update(["de", "la", "el", "y", "en", "del", "con", "los", "las", "al", "por"])

        # Filtrar palabras según longitud mínima
        palabras = [palabra for palabra in textos.split() if len(palabra) > 3]
        texto_filtrado = " ".join(palabras)

        # Nube de palabras más compacta
        # Generar nube de palabras más compacta
        #if texto_filtrado.strip():  
        pantalla_ancho = 1000  # Podés ajustar o usar st.columns para tamaño relativo
        pantalla_alto = int(pantalla_ancho / 2)  # relación 2:1 para forma ovalada

        # Crear máscara ovalada proporcional
        mask = np.ones((pantalla_alto, pantalla_ancho), dtype=np.uint8) * 255  # fondo blanco
        yy, xx = np.ogrid[:pantalla_alto, :pantalla_ancho]
        center_y, center_x = pantalla_alto // 2, pantalla_ancho // 2
        radius_y, radius_x = int(pantalla_alto * 0.45), int(pantalla_ancho * 0.45)
        ellipse = ((yy - center_y)**2)/(radius_y**2) + ((xx - center_x)**2)/(radius_x**2)
        mask[ellipse <= 1] = 0  # óvalo negro = área donde se dibujan palabras


        # Generar nube de palabras
        if texto_filtrado.strip():
            wordcloud = WordCloud(
                background_color='white',
                mask=mask,
                stopwords=mis_stopwords,
                max_words=300,
                max_font_size=20,
                relative_scaling=0.1,
                prefer_horizontal=0.9,
                collocations=False
            ).generate(texto_filtrado)

            # Mostrar
            st.subheader("Nube de palabras de temas de investigación")
            plt.figure(figsize=(15, 7))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
        else:
            st.warning("⚠️ No hay palabras suficientes para generar la nube de palabras.") 







#Analisis tempopral de becas
with tabs[4]:
    st.header("Analisis Temporal de becas")
    #st.write(df_filtrado)
    # -----------------------
    # Copiar DataFrame filtrado o usar df_tab
    # -----------------------
    #df_becas = df_tab.copy()
    df_becas= df_filtrado.copy()
    
    todas_columnas = []
    categorias = {
        "Datos Becas finalizadas": ['nombre','director_doctorado','director_lugar',
 'fec_ini_doc', 'fec_defensa']
    }

    for columnas in categorias.values():
        todas_columnas.extend(columnas)

    # --- Filtrar solo las que existen en el df ---
    todas_columnas = [c for c in todas_columnas if c in df_tab.columns]

    # --- Mostrar tabla dentro de un expander ---
    with st.expander("Datos Becas finalizadas", expanded=False):
        st.dataframe(df_tab[todas_columnas])


    # -----------------------
    # Convertir fechas a datetime
    # -----------------------
    
    # Convertir solo los años válidos
    # Convertir fec_ini_doc a números y luego a datetime
    df_becas['fec_ini_doc'] = pd.to_numeric(df_becas['fec_ini_doc'], errors='coerce')
    df_becas['fec_ini_doc'] = pd.to_datetime(
       df_becas['fec_ini_doc'].astype('Int64').astype(str) + '-07-01', errors='coerce'
        )   

    # Convertir fec_defensa a datetime
    df_becas['fec_defensa'] = pd.to_datetime(df_becas['fec_defensa'], errors='coerce')

    # Crear columna duracion_anios solo si hay fechas válidas
    df_becas['duracion_anios'] = None
    mask_valid = df_becas['fec_ini_doc'].notna() & df_becas['fec_defensa'].notna()
    df_becas.loc[mask_valid, 'duracion_anios'] = (
        (df_becas.loc[mask_valid, 'fec_defensa'] - df_becas.loc[mask_valid, 'fec_ini_doc']).dt.days / 365.25
    )

    # Filtrar solo filas con duración válida
    df_duracion = df_becas.dropna(subset=['duracion_anios']).copy()

    #st.write(df_duracion[['nombre','fec_ini_doc','fec_defensa','duracion_anios']])

    st.subheader("Duración de las becas")
    if not df_duracion.empty:
        # Estadísticas generales
        promedio = df_duracion['duracion_anios'].mean()
        minimo = df_duracion['duracion_anios'].min()
        maximo = df_duracion['duracion_anios'].max()
    
        #st.write(f"**Duración promedio de las becas:** {promedio:.2f} años")
        #st.write(f"**Duración mínima:** {minimo:.2f} años")
        #st.write(f"**Duración máxima:** {maximo:.2f} años")

        ###
        #st.subheader("📊 Estadísticas generales de duración de becas")

        col1, col2, col3 = st.columns(3)

        col1.metric("Promedio (años)", f"{promedio:.1f}")
        col2.metric("Mínimo (años)", f"{minimo:.1f}")
        col3.metric("Máximo (años)", f"{maximo:.1f}")


        ###
        # 4a. Gráfico: duración promedio por carrera
        # Asegurar que la columna sea numérica
        df_duracion['duracion_anios'] = pd.to_numeric(df_duracion['duracion_anios'], errors='coerce')

        df_group_carrera = df_duracion.groupby('doctorado')['duracion_anios'].mean().reset_index()

        # Ordenar de mayor a menor duración
        df_group_carrera = df_group_carrera.sort_values('duracion_anios', ascending=False)
        ##
        #df_group_carrera = (
        #    df_duracion
        #    .groupby('doctorado', as_index=False)['duracion_anios']
        #    .mean()
        #)

        # Columna redondeada para tooltip
        df_group_carrera['duracion_anios_rd'] = df_group_carrera['duracion_anios'].round(1)

        # Ordenar de mayor a menor duración
        df_group_carrera = df_group_carrera.sort_values('duracion_anios', ascending=False)



        fig_carrera = px.bar(
            df_group_carrera,
            x='doctorado',          # ahora la carrera va en X
            y='duracion_anios',     # la duración en Y
            text='duracion_anios',
            title='Duración promedio de la beca por carrera',
            labels={'duracion_anios':'Duración (años)', 'doctorado':'Carrera'},
            color='duracion_anios',
            color_continuous_scale=px.colors.sequential.Viridis,
            hover_data={
                'duracion_anios_rd': True,
                'duracion_anios': False,
                'doctorado': True
            }
        )

        # Mostrar los valores encima de cada barra
        fig_carrera.update_traces(texttemplate='%{text:.1f}', textposition='inside',)
        fig_carrera.update_layout(coloraxis_colorbar_tickformat=".1f")

        st.plotly_chart(fig_carrera, width='stretch')

        # 4b. Gráfico opcional: duración promedio por universidad
        if 'uni_doctorado' in df_duracion.columns:
            # --- Crear columna redondeada para el tooltip ---
            df_group_uni = (
                df_duracion
                .groupby('uni_doctorado', as_index=False)['duracion_anios']
                .mean()
            )
            df_group_uni['duracion_anios'] = pd.to_numeric(df_group_uni['duracion_anios'], errors='coerce')
            df_group_uni['duracion_anios_rd'] = df_group_uni['duracion_anios'].round(1)
            df_group_uni = df_group_uni.sort_values('duracion_anios', ascending=False)

            fig_uni = px.bar(
                df_group_uni,
                x='duracion_anios',
                y='uni_doctorado',
                text='duracion_anios',
                title='Duración promedio de la beca por Institución',
                hover_data={'duracion_anios_rd': True, 'duracion_anios': False},
                orientation='h',
                color='duracion_anios',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_uni.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_uni.update_layout(coloraxis_colorbar_tickformat=".1f")
            st.plotly_chart(fig_uni, width='stretch')



    # 5. Visualizaciones adicionales
    st.subheader("Visualizaciones adicionales")

    # Distribución de becas por estado
    #if 'estado_becadoc' in df_becas.columns:
        #df_estado = df_becas['estado_becadoc'].value_counts().reset_index()
        #df_estado.columns = ['Estado', 'Cantidad']
        #fig_estado = px.pie(df_estado, names='Estado', values='Cantidad', title="Distribución de becas por estado")
        #st.plotly_chart(fig_estado, width='stretch')

    ###
    # Definir paletas por campo
    paletas = {
        'periodo_beca': px.colors.sequential.Viridis,
        'financia_beca': px.colors.sequential.Plasma,
        'lugar_trabajo': px.colors.sequential.Cividis,
        'intentos_convocatoria': px.colors.sequential.Magma,  # para la torta
        'cant_intentos': px.colors.sequential.Inferno
    }

    campos = ['periodo_beca', 'financia_beca', 'lugar_trabajo', 'intentos_convocatoria', 'cant_intentos']
    col1, col2 = st.columns(2)
    for campo in campos:
        if campo in df_tab.columns and not df_tab[campo].dropna().empty:
            df_count = df_tab[campo].value_counts().reset_index()
            df_count.columns = [campo, 'count']

            if campo == 'periodo_beca':
                df_count = df_count.sort_values(campo, ascending=False)

            paleta = paletas.get(campo, px.colors.sequential.Viridis)

            # Para los dos gráficos que van en columnas
           
            if campo in ['intentos_convocatoria', 'cant_intentos']:
                

                # intentos_convocatoria -> torta
                if campo == 'intentos_convocatoria':
                    fig = px.pie(
                        df_count,
                        names=campo,
                        values='count',
                        title=f"Distribución por {campo}",
                        color_discrete_sequence=paleta
                    )
                    col1.plotly_chart(fig, width='stretch')

                # cant_intentos -> barras verticales
                elif campo == 'cant_intentos':
                    fig = px.bar(
                        df_count,
                        x=campo,
                        y='count',
                        text='count',
                        title=f"Distribución por {campo}",
                        color='count',
                        color_continuous_scale=paleta
                        )
    
                    # Mostrar texto dentro de la barra
                    fig.update_traces(
                        texttemplate='%{text}', 
                        textposition='inside',
                        textfont=dict(
                        color='black',   # Cambiar según el color de la barra
                        size=12          # Tamaño del texto
                        )
                    )
    
                    #fig.update_traces(texttemplate='%{text}', textposition='outside')
                    col2.plotly_chart(fig, width='stretch')

            else:
                # Gráficos normales tipo barra horizontal
                if campo !='estado':
                    fig = px.bar(
                        df_count,
                        x='count',
                        y=campo,
                        orientation='h',
                        text='count',
                        title=f"Distribución por {campo}",
                        color='count',
                        color_continuous_scale=paleta
                    )
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    st.plotly_chart(fig, width='stretch')


# ---------- Producción Académica ----------


with tabs[5]:
    st.header("Becas PosDoc. y Externas")
  

    st.write("Análisis de Becas Doctorales y Posdoctorales")

    # ---------------------------
    # 1️⃣ Campos simples (barras o tortas)
    # ---------------------------
    import streamlit as st
    import plotly.express as px

    # ----- Configuración -----
    campos_barras = ['financia_becaposdoc', 'lugar_becaposdoc',
                     'contacto_red']

    #campos_barras = ['beca_posdoc', 'financia_becaposdoc', 'lugar_becaposdoc',
    #                 'beca_resultadoneg','contacto_red']


    paletas_barras = {
        #'beca_posdoc': px.colors.sequential.Viridis,
        'financia_becaposdoc': px.colors.sequential.Plasma,
        'lugar_becaposdoc': px.colors.sequential.Cividis,
        #'beca_resultadoneg': px.colors.sequential.Magma,
        'contacto_red': px.colors.sequential.Plasma,
    }

    df_tab = df_filtrado.copy()

    # ----- Gráficos de campos simples -----
    with st.expander("Gráficos de campos simples", expanded=True):

        # --- resto de los campos en columnas, excepto contacto_red ---
        campos_restantes = [c for c in campos_barras if c != 'contacto_red']
        #campos_restantes = [c for c in campos_barras ]
        for i in range(0, len(campos_restantes), 2):
            cols = st.columns([0.5, 0.5], gap="medium")
            for j, campo in enumerate(campos_restantes[i:i+2]):
                if campo in df_tab.columns and not df_tab[campo].dropna().empty:
                    df_count = df_tab[campo].value_counts().reset_index()
                    df_count.columns = [campo, 'count']

                    # ≤3 categorías → torta, >3 → barras
                    if df_count.shape[0] <= 3:
                        fig = px.pie(
                            df_count,
                            names=campo,
                            values='count',
                            title=f"Distribución por {campo}",
                            color_discrete_sequence=paletas_barras.get(campo, px.colors.sequential.Viridis),
                            hole=0.4
                        )
                        fig.update_traces(
                            hovertemplate="%{label}: %{value}<extra></extra>",
                            textinfo="label+value",
                            domain=dict(x=[0.2, 0.8], y=[0.2, 0.8])
                        )
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=40, b=20),
                            legend=dict(
                                orientation="h",
                                y=-0.1,
                                x=0.5,
                                xanchor='center',
                                yanchor='top'
                            )
                        )
                    else:
                        fig = px.bar(
                            df_count,
                            x='count',
                            y=campo,
                            orientation='h',
                            text='count',
                            title=f"Distribución por {campo}",
                            color='count',
                            color_continuous_scale=paletas_barras.get(campo, px.colors.sequential.Viridis)
                        )
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        fig.update_layout(yaxis=dict(automargin=True))

                    # Mostrar gráfico en columna con key único
                    cols[j].plotly_chart(fig, use_container_width=True, height=500, key=f"{campo}_{i}_{j}")

        # --- contacto_red como dona al final, ancho completo ---
            if 'contacto_red' in df_tab.columns and not df_tab['contacto_red'].dropna().empty:
                df_count = df_tab['contacto_red'].value_counts().reset_index()
                df_count.columns = ['contacto_red', 'count']

                fig = px.pie(
                    df_count,
                    names='contacto_red',
                    values='count',
                    title="Distribución por contacto_red",
                    color_discrete_sequence=paletas_barras.get('contacto_red', px.colors.sequential.Viridis),
                    hole=0.4
                )
                fig.update_traces(
                    domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
                    hovertemplate="%{label}: %{value}<extra></extra>"
                )
                fig.update_layout(
                    width=1000,
                    height=700,
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend_title_text='',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
           # cols[j].plotly_chart(fig, use_container_width=True, height=500, key=f"{campo}_{i}_{j}")

            st.plotly_chart(fig, use_container_width=True, height=700, key="contacto_red")
            #cols[j].plotly_chart(fig, use_container_width=True, height=700, key="contacto_red")

    # ---------------------------
    # 2️⃣ Campos multivaluados (explode + barras horizontales)
    # ---------------------------
    #campos_multivaluados = ['lineas_investigacion', 'tema', 
    #                        'organismo_financiabecaext']
    campos_multivaluados = ['lineas_investigacion',  
                             'organismo_financiabecaext']


    #with st.expander("Gráficos de campos multivaluados", expanded=False):
        
        # Crear columnas de a pares
        #col1, col2 = st.columns(2)
        #cols = [col1, col2]
        #idx = 0  # para ir alternando entre columnas

        #for campo in campos_multivaluados:

 
    #campos_multivaluados = ['lineas_investigacion', 'organismo_financiabecaext']
    campos_multivaluados = ['lineas_investigacion']


    with st.expander("Gráficos de campos multivaluados", expanded=False):

        for idx, campo in enumerate(campos_multivaluados):

            if campo in df_tab.columns and not df_tab[campo].dropna().empty:

                # --- Preparar dataframe para conteo ---
                temp = df_tab[[campo]].dropna().copy()
                temp[campo] = temp[campo].str.split(';')
                temp = temp.explode(campo)
                df_count = temp[campo].value_counts().reset_index()
                df_count.columns = [campo, 'count']

                # --- Caso lineas_investigacion: barra vertical ---
                if campo == 'lineas_investigacion':
                    fig = px.bar(
                        df_count,
                        x=campo,
                        y='count',
                        orientation='v',
                        text='count',
                        title=f"Distribución por {campo}",
                        color='count',
                        color_continuous_scale=px.colors.sequential.Viridis
                    )

                    # Etiquetas y estilo
                    fig.update_xaxes(tickangle=-45)
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    fig.update_layout(
                        xaxis_title=None,
                        yaxis_title='Agentes',
                        height=800,
                        yaxis=dict(automargin=True)
                    )

                    st.plotly_chart(fig, use_container_width=True, key=f"{campo}")

            # --- Caso organismo_financiabecaext: todos valores 1 → tabla ---
        
            
            if 'tema' in df_tab.columns and 'tema' in df_tab.columns:
                df_dir = df_tab[['nombre','tema','directores_becaposdoc', 'lugar_directoresbecaspocdoc']].dropna().copy()

                # Limpiar espacios
                df_dir['tema'] = df_dir['tema'].str.strip()
                
                st.subheader("Tabla de Temas")
                st.dataframe(df_dir, use_container_width=True)    





        
    # ---------------------------
    # 3️⃣ Campos de periodos → barras verticales ordenadas cronológicamente
    # ---------------------------
        #desde aqui el sankey
        import plotly.graph_objects as go
        import textwrap
###


        import streamlit as st
        import plotly.graph_objects as go
        import textwrap

        # Función para saltos de línea en labels largos
        def wrap_label(text, width=30):
            return textwrap.fill(str(text), width=width).replace("\n", "<br>")

        # Filtrar solo filas con información completa
        df_sankey = df_filtrado.dropna(subset=["niveleduc_ becaexterna", "pais_becaext", "organismo_financiabecaext"])

        # Listas de nodos por tipo
        becas = df_sankey["niveleduc_ becaexterna"].unique().tolist()
        paises = df_sankey["pais_becaext"].unique().tolist()
        instituciones = df_sankey["organismo_financiabecaext"].unique().tolist()

        nodes = becas + paises + instituciones
        node_dict = {node: i for i, node in enumerate(nodes)}

        # Calcular enlaces con conteo
        link_data = []

        # Beca → País
        df_bp = df_sankey.groupby(["niveleduc_ becaexterna", "pais_becaext"]).size().reset_index(name="count")
        for _, row in df_bp.iterrows():
            link_data.append({
                "source": node_dict[row["niveleduc_ becaexterna"]],
                "target": node_dict[row["pais_becaext"]],
                "value": row["count"]
            })

        # País → Institución
        df_pi = df_sankey.groupby(["pais_becaext", "organismo_financiabecaext"]).size().reset_index(name="count")
        for _, row in df_pi.iterrows():
            link_data.append({
                "source": node_dict[row["pais_becaext"]],
                "target": node_dict[row["organismo_financiabecaext"]],
                "value": row["count"]
            })

        # Colores por tipo de nodo
        node_colors = ["#a6cee3"]*len(becas) + ["#b2df8a"]*len(paises) + ["#fdbf6f"]*len(instituciones)

        # Colores de enlaces según valor
        max_value = max([l["value"] for l in link_data])
        link_colors = [
            f"rgba(100,149,237,{l['value']/max_value * 0.6 + 0.2})" if l["source"] < len(becas) else
            f"rgba(144,238,144,{l['value']/max_value * 0.6 + 0.2})"
            for l in link_data
        ]

        # Saltos de línea en labels
        nodes_wrapped = [wrap_label(n, width=30) for n in nodes]

        # Crear Sankey
        fig = go.Figure(go.Sankey(
            node=dict(
                label=nodes_wrapped,
                color=node_colors,
                line=dict(color="black", width=0.2),
                pad=15,
                thickness=20
            ),
            link=dict(
                source=[l["source"] for l in link_data],
                target=[l["target"] for l in link_data],
                value=[l["value"] for l in link_data],
                color=link_colors
            )
        ))

        # Ajustar fuente de los labels de nodos
        fig.update_traces(
            selector=dict(type='sankey'),
            textfont=dict(family="Arial", size=12, color="black")
        )

        # Layout general
        fig.update_layout(
            title_text="Flujo: Beca → País → Institución",
            height=max(700, len(nodes)*30)
        )

        # Mostrar en Streamlit
        st.plotly_chart(fig, use_container_width=True)




    
        ###    
    campos_periodo = ['periodo_becaposdoc', 'periodo_ini_becaext', 'periodo_fina_beca']

    with st.expander("Gráficos de periodos", expanded=False):
        cols = st.columns(2)  # 👉 dos columnas
        for i, campo in enumerate(campos_periodo):
            if campo in df_tab.columns and not df_tab[campo].dropna().empty:
                df_count = df_tab[campo].value_counts().reset_index()
                df_count.columns = [campo, 'count']
                df_count = df_count.sort_values(campo)  # orden cronológico

                fig = px.bar(
                    df_count,
                    x=campo,
                    y='count',
                    text='count',
                    title=f"Distribución por {campo}",
                    color='count',
                    color_continuous_scale=px.colors.sequential.Plasma
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')

                # 👉 enviar gráfico a la columna correspondiente
                cols[i % 2].plotly_chart(fig, width='stretch')


    





# ---------- Docencia y Capacitación ----------
with tabs[6]:
    #st.header("Docencia y Capacitación")
    
    df_tab = df_filtrado.copy()
    cols_doc = ['Nombre','Nivelinstitucion','Sectorinstitucion','HorasSemanales','FormacionGenero','DetalleFormacion']
    df_show = [col for col in cols_doc if col in df_filtrado.columns]
    #df_tab = [col for col in cols_doc if col in df_filtrado.columns]

    #st.dataframe(df_filtrado[df_show])

# ---------- Dashboard ----------
    #st.title("Dashboard ICSOH - Análisis de cargos y capacitación")

    # --- Gráficos de barras ---
    st.subheader("Distribución de cargos y dedicación")

# ---------- Configuración ----------
    paletas_barras = {
        'cargo_icsoh': px.colors.sequential.Viridis,
        'cargodocente': px.colors.sequential.Plasma,
        'categoria_docenteuni': px.colors.sequential.Cividis,
        'dedicacion_docenteuni': px.colors.sequential.Magma,
        'sector_inst_educativa': px.colors.qualitative.Set2
    }

    barras_vars = ['cargo_icsoh',  'categoria_docenteuni', 'dedicacion_docenteuni']
    dona_vars = ['cargodocente', 'sector_inst_educativa', 'dedicacion_horariasemanal','capacitacion_genero']

    MAX_CATEGORIAS_COLUMNAS = 30  # límite para mostrar en columnas

    # ---------- Gráficos de barras ----------
    for var in barras_vars:
        if var in df_tab.columns and not df_tab[var].dropna().empty:
            df_count = df_tab[var].value_counts().reset_index()
            df_count.columns = [var, 'count']
            num_categorias = len(df_count)

            # Gráfico de barras horizontal
            fig = px.bar(
                df_count,
                x='count',
                y=var,
                orientation='h',
                text='count',
                color='count',
                color_continuous_scale=paletas_barras.get(var, px.colors.sequential.Viridis),
                title=f"Distribución por {var}"
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=max(400, num_categorias*40), yaxis=dict(automargin=True))

            if num_categorias > 6:
                # Muchas categorías → gráfico ancho completo + tabla al lado
                cols = st.columns([3,1])
                cols[0].plotly_chart(fig, width='stretch', key=f"{var}_full")
                cols[1].dataframe(df_count, height=400, width='stretch')
            else:
                # Pocas categorías → columnas de 2
                cols = st.columns(2)
                cols[0].plotly_chart(fig, width='stretch', key=f"{var}_col")
                cols[1].dataframe(df_count, width='stretch')


    # ---------- Gráficos de dona ----------
    #st.subheader("Variables con pocas categorías")
    for k in range(0, len(dona_vars), 2):
        cols = st.columns(2, gap="medium")
        for j, var in enumerate(dona_vars[k:k+2]):
            if var in df_tab.columns and not df_tab[var].dropna().empty:
                df_count = df_tab[var].value_counts().reset_index()
                df_count.columns = [var, 'count']
                fig = px.pie(
                    df_count,
                    names=var,
                    values='count',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    title=f"Distribución por {var}"
                )
                #fig.update_traces(hovertemplate="%{label}: %{value}<extra></extra>")
                fig.update_traces(domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]))
                #fig.update_layout(
                #    width=1000,   # ancho más pequeño
                #    height=700,  # alto más pequeño
                #    legend_title_text='',
                #    legend=dict(font=dict(size=10) ,orientation="v", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                #    margin=dict(l=10, r=10, t=40, b=10)
                #)
                fig.update_layout(
                width=1000,      
                height=600,
                margin=dict(l=10, r=10, t=40, b=10),
                legend_title_text='',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                    )
                )



                fig.update_traces(hovertemplate="%{label}: %{value}<extra></extra>")

                cols[j].plotly_chart(fig, width='stretch', key=f"{var}_dona_{k}_{j}")
    
             

            #st.plotly_chart(fig, width='stretch')


####

with tabs[7]:
    st.header("Revistas y Postu.Becas Ext.")
    cols_prod = ['Nombre','Publicaciones','LineaInvestigacion','ParticipacionSTAN']
    df_show = [col for col in cols_prod if col in df_filtrado.columns]
    #st.dataframe(df_filtrado[df_show])

    ##

    # ---------- Tabla de revistas ----------
    #st.subheader("Tabla de revistas")
    #st.dataframe(df[['revistas']])



    # ---------- Gráficos de barras para sí/no ----------
    #st.subheader("Distribución de respuestas")
    #cols = st.columns(2)  # dos columnas para gráficos
    

    cols = st.columns(2, gap="medium")  # dos columnas iguales

    for i, col in enumerate(['conoce_revistas', 'revistas']):
        if col in df.columns:
            counts = df[col].value_counts(dropna=False).reset_index()
            counts.columns = [col, 'count']

            with cols[i % 2]:  # alterna columnas
                if col == 'revistas':
                    # ---------- Tabla ----------
                    #st.subheader("Tabla de Revistas")
                    st.dataframe(counts, height=400)  # altura igual al gráfico

                    # ---------- Barra horizontal ----------
                    #fig = px.bar(
                    #    counts,
                    #    x='count',
                    #    y=col,
                    #    orientation='h',
                    #    text='count',
                    #    title=f"Distribución de {col}",
                    #    color='count',
                    #    color_continuous_scale=px.colors.sequential.Viridis
                    #)
                    #fig.update_traces(texttemplate='%{text}', textposition='outside')
                    #fig.update_layout(
                    #    yaxis=dict(automargin=True),
                    #    width=None,   # permite usar todo el ancho de la columna
                    #    height=400,  # misma altura que la tabla
                    #    margin=dict(l=10, r=10, t=40, b=10)
                    #)
                    #st.plotly_chart(fig, use_container_width=True, height=400)

                else:
                    # ---------- Dona ----------
                    fig = px.pie(
                        counts,
                        names=col,
                        values='count',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        title=f"Distribución de {col}"
                    )
                    fig.update_traces(
                        hovertemplate="%{label}: %{value}<extra></extra>",
                        textinfo="label+value",
                        domain=dict(x=[0, 1], y=[0, 1])  # ocupa todo el espacio de la figura
                    )
                    fig.update_layout(
                        legend_title_text='',
                        width=None,
                        height=400,  # misma altura que la tabla
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                        margin=dict(l=10, r=10, t=40, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True, height=400)

                
    #cols = st.columns(2)  # dos columnas para gráficos
    cols = st.columns(2, gap="medium")  # dos columnas iguales
    for i, col in enumerate(['conoce_stan', 'si_stan', 'postular_becaexterior','criterios_decision']):
        if col in df.columns:
            counts = df[col].value_counts(dropna=False).reset_index()
            counts.columns = [col, 'count']

            if col == 'si_stan':
                # ---------- Mostrar tabla ----------
                with cols[i % 2]:  # alterna entre la col 0 y 1
                  #  st.subheader("Tabla de Stan")
                    st.dataframe(counts, use_container_width=True)

                    # ---------- Barra horizontal ----------
                    #fig = px.bar(
                    #    counts,
                    #    x='count',
                    #    y=col,
                    #    orientation='h',
                    #    text='count',
                    #    title=f"Distribución de {col}",
                    #    color='count',
                    #    color_continuous_scale=px.colors.sequential.Viridis
                    #)
                    #fig.update_traces(texttemplate='%{text}', textposition='outside')
                    #fig.update_layout(yaxis=dict(automargin=True),width=500,   # 👈 más angosto
                    #    height=500)  # 👈 más bajo
                    
            elif col == 'criterios_decision':
                # ---------- Solo tabla ----------
                with cols[i % 2]:
                    #st.subheader("Tabla de Criterios de Decisión")
                    st.dataframe(counts, use_container_width=True)

            else:
                # ---------- Dona ----------
                fig = px.pie(
                    counts,
                    names=col,
                    values='count',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    title=f"Distribución de {col}"
                )
                fig.update_traces(
                        hovertemplate="%{label}: %{value}<extra></extra>",
                        textinfo="label+value",
                        domain=dict(x=[0, 1], y=[0, 1])  # ocupa todo el espacio de la figura
                    )

                fig.update_layout(
                        legend_title_text='',
                        width=None,
                        height=400,  # misma altura que la tabla
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        ),
                        margin=dict(l=10, r=10, t=40, b=40)
                    )

                with cols[i % 2]:  # alterna entre las dos columnas
                    st.plotly_chart(fig, use_container_width=True, height=400)


# ---------- Nube de palabras de revistas ----------
    st.subheader("Nube de palabras de revistas")
    textos = " ".join(df['revistas'].dropna().tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          max_words=200, colormap='inferno').generate(textos)

    
    # Stopwords
    mis_stopwords = set(STOPWORDS)
    mis_stopwords.update(["de", "la", "el", "y", "en", "del", "con", "los", "las", "al", "por"])

    # Filtrar palabras según longitud mínima
    palabras = [palabra for palabra in textos.split() if len(palabra) > 3]
    texto_filtrado = " ".join(palabras)

    
    pantalla_ancho = 1000  # Podés ajustar o usar st.columns para tamaño relativo
    pantalla_alto = int(pantalla_ancho / 2)  # relación 2:1 para forma ovalada

    # Crear máscara ovalada proporcional
    mask = np.ones((pantalla_alto, pantalla_ancho), dtype=np.uint8) * 255  # fondo blanco
    yy, xx = np.ogrid[:pantalla_alto, :pantalla_ancho]
    center_y, center_x = pantalla_alto // 2, pantalla_ancho // 2
    radius_y, radius_x = int(pantalla_alto * 0.45), int(pantalla_ancho * 0.45)
    ellipse = ((yy - center_y)**2)/(radius_y**2) + ((xx - center_x)**2)/(radius_x**2)
    mask[ellipse <= 1] = 0  # óvalo negro = área donde se dibujan palabras


        # Generar nube de palabras
    if texto_filtrado.strip():
            wordcloud = WordCloud(
                background_color='white',
                mask=mask,
                stopwords=mis_stopwords,
                max_words=300,
                max_font_size=20,
                relative_scaling=0.1,
                prefer_horizontal=0.9,
                collocations=False,
                colormap='inferno'
            ).generate(texto_filtrado)

            # Mostrar
            #st.subheader("Nube de palabras de temas de investigación")
            plt.figure(figsize=(15, 7))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
    else:
            st.warning("⚠️ No hay palabras suficientes para generar la nube de palabras.") 

        # ------------------------
        # Tabla general
        # ------------------------


# Tabs principales

# Mini-dashboard dentro de tabs[6]

#with tabs[8]:  # tabs[5] porque los índices empiezan en 0
    
#    import streamlit as st

# Definimos la contraseña
#    PASSWORD = "12345678"
    

#    st.header("🔒 Acceso restringido")
#    password_input = st.text_input("Ingrese contraseña", type="password")

#    if not password_input:
#        st.info("Ingrese la contraseña para acceder a los datos 🔑")

#    elif password_input != PASSWORD:
#        st.error("Contraseña incorrecta ❌")

#    else:  # contraseña correcta
#        st.success("Acceso concedido ✅")

#        df_tab= df_filtrado.copy()
#        st.subheader("Datos del Censo")

#        # Categorías
#        categorias = {
#            "Datos personales y familiares": ['nombre','fec_nac', 'lugar_nac', 'genero', 'estado_civil', 'hijos', 'cta_hijos', 'edad', 'flia_cargo', 'cta_personas', 'aportemayor'],
#            "Vivienda y trabajo": ['nombre','habitabilidad', 'vivienda_trabaja'],
#            "Formación académica": ['nombre','titulo', 'institucion', 'anio_final', 'promedio', 'finalizo_masdeunacarrera', 'titulo_otracarrera', 'universidad_otracarrera', 'fec_finalizootracarrera'],
#            "Idiomas y becas": ['nombre','ingles', 'frances', 'italiano', 'portugues', 'aleman', 'otroidioma', 'estado_becadoc', 'doctorado', 'uni_doctorado', 'fec_ini_doc', 'fec_defensa_tesis', 'tema_investigacion', 'director_doctorado', 'director_lugar',
#                                     'becadoctoral', 'periodo_beca', 'financia_beca', 'directores_beca', 'lugar_directores'],
#            "Experiencia profesional y docente": ['nombre','cargo_icsoh', 'lineas_investigacion', 'capacitacion_genero', 'cargodocente', 'institucion_cargodocente', 'sector_inst_educativa', 'lugar_institucioneduc', 'dedicacion_horariasemanal', 'experiencia_docente', 'categoria_docenteuni', 'dedicacion_docenteuni'],
#            "Redes, revistas y becas externas":['nombre','conoce_revistas', 'revistas', 'conoce_stan', 'si_stan', 'postular_becaexterior', 'criterios_decision', 'becaexterna', 'financia_becaexterna', 'organismo_financiabecaext', 'pais_becaext', 'periodo_ini_becaext', 'periodo_fina_becaext']
#        }

#        for cat, columnas in categorias.items():
#            with st.expander(cat, expanded=False):
#                # Multiselect para elegir columnas
#                columnas_disponibles = [c for c in columnas if c in df_tab.columns]
#                cols_seleccionadas = st.multiselect(f"Selecciona columnas a mostrar en {cat}", columnas_disponibles, default=columnas_disponibles)
#                st.dataframe(df_tab[cols_seleccionadas])

#        # Estilo CSS opcional para los expanders
#        st.markdown("""
#            <style>
#            div[data-testid="stExpander"] > .stExpanderHeader {
#                background-color: #e8f0fe;
#                color: #1a1a1a;
#                font-weight: bold;
#                font-size: 15px;
#            }
#            </style>
#        """, unsafe_allow_html=True)
    
    
    
# ---------- Exportar CSV ----------
#with tabs[9]:

#    st.header("💾 ")


#    st.dataframe(df_filtrado)
#    csv = df_filtrado.to_csv(index=False).encode('utf-8')
#    st.download_button("📥 Descargar CSV", data=csv, file_name='censo_filtrado.csv', mime='text/csv')
