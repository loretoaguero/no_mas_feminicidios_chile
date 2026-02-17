import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------
# Configuración
# ---------------------------
st.set_page_config(page_title="Feminicidios en Chile", layout="wide")
st.image("assets/banner1.png", width=1200)

# ---------------------------
# Cargar datos
# ---------------------------
with open("consolidated_data.pkl", "rb") as f:
    df = pickle.load(f)

# ---------------------------
# Tipos seguros
# ---------------------------
if "fecha" in df.columns:
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

for c in ["edad_victima", "edad_femicida"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

for c in ["region", "tipificacion_penal", "categoria_red_chilena", "sentencia", "relacion_victimafemicida"]:
    if c in df.columns:
        df[c] = df[c].astype("string")

# TO DO: agregar a main.py
# ---------------------------
# Preprocesamiento
# ---------------------------
df["nombre_victima_sin_apellido"] = df.get("nombre_victima", pd.Series([], dtype="string")).astype("string").str.split().str[0]
df["diferencia_de_edad"] = df.get("edad_femicida") - df.get("edad_victima")

if "fecha" in df.columns:
    df["year"] = df["fecha"].dt.year

df = df[[
    "fecha", "region", "nombre_victima_sin_apellido",
    "edad_victima", "edad_femicida", "diferencia_de_edad",
    "nacionalidad_victima", "nacionalidad_femicida",
    "ocupacion_victima", "ocupacion_femicida",
    "forma_agresion", "violencia_sexual", "relacion_victimafemicida",
    "informacion_sobre_hecho",
    "categoria_red_chilena", "tipificacion_penal", "registro_sernameg",
    "sentencia", "year",
] if set([
    "fecha","region","nombre_victima_sin_apellido","edad_victima","edad_femicida","diferencia_de_edad",
    "nacionalidad_victima","nacionalidad_femicida","ocupacion_victima","ocupacion_femicida","forma_agresion",
    "violencia_sexual","relacion_victimafemicida","informacion_sobre_hecho","categoria_red_chilena",
    "tipificacion_penal","registro_sernameg","sentencia"
]).issubset(df.columns) else df.columns]  # si faltan columnas, no revienta

# ---------------------------
# Filtros
# ---------------------------
st.sidebar.header("Filtros")

regiones = df["region"].dropna().unique() if "region" in df.columns else []
categorias = df["categoria_red_chilena"].dropna().unique() if "categoria_red_chilena" in df.columns else []
tipificacion = df["tipificacion_penal"].dropna().unique() if "tipificacion_penal" in df.columns else []
relacion_victima_femicida = df["relacion_victimafemicida"].dropna().unique() if "relacion_victimafemicida" in df.columns else []

region_sel = st.sidebar.multiselect("Región", sorted(regiones))
categoria_sel = st.sidebar.multiselect("Categoría Red Chilena", sorted(categorias))
tipificacion_sel = st.sidebar.multiselect("Tipificación Penal", sorted(tipificacion))
relacion_sel = st.sidebar.multiselect("Relación Víctima-Femicida", sorted(relacion_victima_femicida))

if "year" in df.columns and df["year"].notna().any():
    year_min = int(df["year"].dropna().min())
    year_max = int(df["year"].dropna().max())
    year_sel = st.sidebar.slider("Año de la fecha del hecho", year_min, year_max, (year_min, year_max))
else:
    year_sel = None
    st.sidebar.info("No se pudo construir el filtro por año (columna 'fecha' inválida o ausente).")

# ---------------------------
# Aplicar filtros
# ---------------------------
df_filtrado = df.copy()

if region_sel and "region" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["region"].isin(region_sel)]
if tipificacion_sel and "tipificacion_penal" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["tipificacion_penal"].isin(tipificacion_sel)]
if categoria_sel and "categoria_red_chilena" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["categoria_red_chilena"].isin(categoria_sel)]
if relacion_sel and "relacion_victimafemicida" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["relacion_victimafemicida"].isin(relacion_sel)]

if year_sel is not None and "year" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["year"].between(year_sel[0], year_sel[1])]

# ---------------------------
# Métrica superior
# ---------------------------
fecha_min = df_filtrado["fecha"].min() if "fecha" in df_filtrado.columns else pd.NaT
prom_edad = df_filtrado["edad_victima"].mean() if "edad_victima" in df_filtrado.columns else np.nan

sent = (
    df_filtrado["sentencia"].astype("string").replace(["", "null", "None", "nan"], pd.NA).dropna().str.strip()
) if "sentencia" in df_filtrado.columns else pd.Series([], dtype="string")
sent = sent[sent.ne("")]
sentencia_mode = sent.mode().values[0] if len(sent.mode()) else "—"

st.markdown(
    f"<h3 style='color: #8E44AD;'>"
    f"Total de víctimas desde {fecha_min.date() if pd.notna(fecha_min) else '—'} hasta hoy: {len(df_filtrado)} "
    f"· Promedio de edad: {prom_edad:.1f} años " if pd.notna(prom_edad) else ""
    + f"· Sentencia más frecuente: {sentencia_mode}"
    f"</h3>",
    unsafe_allow_html=True
)

# ---------------------------
# Heatmap nombres (mosaico)
# ---------------------------
if "nombre_victima_sin_apellido" in df_filtrado.columns:
    names = (
        df_filtrado["nombre_victima_sin_apellido"]
        .replace(["", "null", "None", "nan"], pd.NA)
        .dropna()
        .astype("string")
        .str.strip()
    )
    names = names[names.ne("")]

    if len(names) == 0:
        st.info("No hay nombres disponibles para mostrar en el heatmap con los filtros actuales.")
    else:
        counts = names.value_counts().reset_index()
        counts.columns = ["nombre", "count"]
        counts = counts.sort_values("count", ascending=False).reset_index(drop=True)

        n_cols = 10
        n_rows = int(np.ceil(len(counts) / n_cols))

        grid = np.full((n_rows, n_cols), "", dtype=object)
        values = np.zeros((n_rows, n_cols))

        for i, row in counts.iterrows():
            r = i // n_cols
            c = i % n_cols
            grid[r, c] = row["nombre"]
            values[r, c] = row["count"]

        z_plot = np.log1p(values)

        fig = go.Figure(
            data=go.Heatmap(
                z=z_plot,
                text=grid,
                texttemplate="%{text}",
                colorscale="Purples",
                showscale=False,
                hoverinfo="text"
            )
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Barras Plotly
# ---------------------------
def bar_plotly(df_in, col, label=None):
    if col not in df_in.columns:
        return None
    s = (
        df_in[col]
        .astype("string")
        .replace(["", "null", "None", "nan"], pd.NA)
        .dropna()
        .str.strip()
    )
    s = s[s.ne("")]
    if len(s) == 0:
        return None

    data = s.value_counts().reset_index()
    data.columns = [label or col, "count"]
    data["count"] = pd.to_numeric(data["count"], errors="coerce").fillna(0)
    data = data.sort_values("count", ascending=True)

    fig = px.bar(
        data,
        x="count",
        y=(label or col),
        orientation="h",
        color="count",
        color_continuous_scale="Purples"
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        xaxis_title="",
        yaxis_title=""
    )
    return fig

# ---------------------------
# GRILLA 2x2
# ---------------------------
c1, c2 = st.columns(2, gap="large")
c3, c4 = st.columns(2, gap="large")

with c1:
    st.subheader("Casos por Región")
    fig_r = bar_plotly(df_filtrado, "region", "Región")
    if fig_r is not None:
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Sin datos para Región.")

with c3:
    st.subheader("Casos por Categoría")
    fig_c = bar_plotly(df_filtrado, "categoria_red_chilena", "Categoría")
    if fig_c is not None:
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.info("Sin datos para Categoría.")

with c2:
    st.subheader("Casos por Tipificación Penal")
    fig_t = bar_plotly(df_filtrado, "tipificacion_penal", "Tipificación")
    if fig_t is not None:
        st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("Sin datos para Tipificación.")

with c4:
    st.subheader("Casos por Sentencia")
    fig_s = bar_plotly(df_filtrado, "sentencia", "Sentencia")
    if fig_s is not None:
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Sin datos para Sentencia.")