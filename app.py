"""
Solemne II - Análisis del Mercado Laboral en Chile
Encuesta Nacional de Empleo (ENE) - datos.gob.cl
Universidad San Sebastián - FITO9017
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import io
import random  # Reemplazamos numpy por la librería estándar

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Empleo en Chile 🇨🇱",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  ESTILO VISUAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo y tipografía */
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    h1, h2, h3 { color: #38bdf8 !important; }
    .stSidebar { background-color: #1e293b !important; }
    .stSidebar .stMarkdown h2 { color: #38bdf8 !important; }

    /* Tarjetas KPI */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }
    .kpi-title { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 2.2rem; font-weight: 800; color: #38bdf8; margin: 8px 0; }
    .kpi-delta { font-size: 0.85rem; color: #64748b; }
    .kpi-delta.up   { color: #f87171; }
    .kpi-delta.down { color: #4ade80; }

    /* Badge fuente */
    .source-badge {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 16px;
    }
    /* Separador */
    hr { border-color: #1e3a5f; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTES API
# ─────────────────────────────────────────────
CKAN_BASE      = "https://datos.gob.cl/api/3/action"
DATASET_SLUG   = "encuesta-nacional-de-empleo-ene"


# ─────────────────────────────────────────────
#  FUNCIONES DE ACCESO A DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def obtener_metadata_dataset(dataset_id: str) -> dict:
    """
    Llama a la API CKAN de datos.gob.cl para obtener
    la metadata del dataset ENE, incluyendo la lista
    de recursos (URLs de archivos CSV).
    """
    url = f"{CKAN_BASE}/package_show"
    resp = requests.get(url, params={"id": dataset_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600, show_spinner=False)
def descargar_csv_recurso(url_csv: str) -> pd.DataFrame:
    """Descarga un archivo CSV desde la URL del recurso y retorna un DataFrame."""
    resp = requests.get(url_csv, timeout=60)
    resp.raise_for_status()
    # Leemos directamente los bytes, es más rápido y eficiente que procesar el texto
    df = pd.read_csv(io.BytesIO(resp.content), sep=None, engine='python', encoding="utf-8", on_bad_lines="skip")
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_recursos_csv(metadata: dict) -> list[dict]:
    """Filtra y retorna sólo los recursos CSV del dataset."""
    recursos = metadata.get("result", {}).get("resources", [])
    return [r for r in recursos if r.get("format", "").upper() in ("CSV", "TEXT/CSV")]


def generar_datos_ene_ficticios() -> pd.DataFrame:
    """
    Genera un DataFrame representativo de la ENE cuando
    la API no está disponible, usando solo librería estándar (random).
    """
    trimestres = [
        "EFM", "FMA", "MAM", "AMJ", "MJJ", "JJA",
        "JAS", "ASO", "SON", "OND", "NDE", "DEF"
    ]
    años = range(2020, 2025)
    regiones = [
        "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama",
        "Coquimbo", "Valparaíso", "Metropolitana", "O'Higgins",
        "Maule", "Ñuble", "Biobío", "La Araucanía",
        "Los Ríos", "Los Lagos", "Aysén", "Magallanes",
    ]
    random.seed(42)
    filas = []
    for año in años:
        for tri in trimestres:
            for region in regiones:
                for sexo in ["Hombre", "Mujer", "Total"]:
                    # Simulamos tendencias realistas
                    base_desoc = 8.5 if sexo == "Total" else (7.5 if sexo == "Hombre" else 9.8)
                    base_ocup  = 57.0 if sexo == "Total" else (65.0 if sexo == "Hombre" else 49.5)
                    # COVID spike en 2020
                    covid = 4.5 if año == 2020 else (2.0 if año == 2021 else 0.0)
                    # Variación por región usando random estándar
                    reg_var = random.uniform(-1.5, 1.5)
                    filas.append({
                        "ano_trimestre": f"{año}-{tri}",
                        "ano": año,
                        "trimestre": tri,
                        "region": region,
                        "sexo": sexo,
                        "tasa_desocupacion": round(base_desoc + covid + reg_var + random.uniform(-0.5, 0.5), 1),
                        "tasa_ocupacion":    round(base_ocup  - covid/2 + reg_var + random.uniform(-0.5, 0.5), 1),
                        "tasa_participacion": round(base_ocup + base_desoc / 10 + random.uniform(-0.3, 0.3), 1),
                    })
    return pd.DataFrame(filas)


# ─────────────────────────────────────────────
#  CARGA DE DATOS PRINCIPAL
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_datos_completos():
    """
    Intenta cargar datos reales desde datos.gob.cl.
    Si falla, retorna datos de demostración con un aviso.
    """
    try:
        metadata = obtener_metadata_dataset(DATASET_SLUG)
        recursos_csv = buscar_recursos_csv(metadata)

        if not recursos_csv:
            return generar_datos_ene_ficticios(), True, metadata

        # Usamos el primer recurso CSV disponible
        primer_recurso = recursos_csv[0]
        url_csv = primer_recurso.get("url", "")
        df = descargar_csv_recurso(url_csv)
        return df, False, metadata

    except Exception:
        return generar_datos_ene_ficticios(), True, {}


# ─────────────────────────────────────────────
#  NORMALIZACIÓN DE COLUMNAS
# ─────────────────────────────────────────────
def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Intenta mapear columnas del CSV real a los nombres
    estándar que usa la app.
    """
    MAPA = {
        "ano_trimestre": ["ano_trimestre", "periodo", "trimestre_movil", "trimestre"],
        "ano":           ["ano", "año", "anio", "year"],
        "region":        ["region", "región", "nombre_region"],
        "sexo":          ["sexo", "genero", "género", "sex"],
        "tasa_desocupacion": [
            "tasa_desocupacion", "tasa_de_desocupacion",
            "desocupacion", "t_desoc", "tasa desocupación"
        ],
        "tasa_ocupacion": [
            "tasa_ocupacion", "tasa_de_ocupacion",
            "ocupacion", "t_ocup"
        ],
        "tasa_participacion": [
            "tasa_participacion", "tasa_de_participacion",
            "participacion", "t_part"
        ],
    }
    rename = {}
    cols_lower = {c.lower().replace(" ", "_"): c for c in df.columns}
    for destino, candidatos in MAPA.items():
        if destino not in df.columns:
            for cand in candidatos:
                if cand in cols_lower:
                    rename[cols_lower[cand]] = destino
                    break
    if rename:
        df = df.rename(columns=rename)
    return df


# ─────────────────────────────────────────────
#  HELPERS DE GRÁFICO
# ─────────────────────────────────────────────
COLORES = {
    "primario": "#38bdf8",
    "secundario": "#818cf8",
    "acento": "#f472b6",
    "verde": "#4ade80",
    "naranja": "#fb923c",
    "fondo": "#0f172a",
    "panel": "#1e293b",
    "texto": "#e2e8f0",
    "grilla": "#334155",
}

def estilo_oscuro():
    plt.rcParams.update({
        "figure.facecolor":  COLORES["fondo"],
        "axes.facecolor":    COLORES["panel"],
        "axes.edgecolor":    COLORES["grilla"],
        "axes.labelcolor":   COLORES["texto"],
        "xtick.color":       COLORES["texto"],
        "ytick.color":       COLORES["texto"],
        "text.color":        COLORES["texto"],
        "grid.color":        COLORES["grilla"],
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "legend.facecolor":  COLORES["panel"],
        "legend.edgecolor":  COLORES["grilla"],
        "font.size":         10,
    })


# ─────────────────────────────────────────────
#  APP PRINCIPAL
# ─────────────────────────────────────────────
def main():
    # ── Encabezado ──────────────────────────────
    st.markdown("""
    <h1 style="margin-bottom:0">📊 Mercado Laboral en Chile</h1>
    <p style="color:#94a3b8;font-size:1rem;margin-top:4px">
        Análisis interactivo de la Encuesta Nacional de Empleo (ENE)
    </p>
    """, unsafe_allow_html=True)
    st.markdown('<div class="source-badge">🔗 Fuente: datos.gob.cl / Instituto Nacional de Estadísticas (INE)</div>',
                unsafe_allow_html=True)

    # ── Carga de datos ───────────────────────────
    with st.spinner("⏳ Consultando API datos.gob.cl..."):
        df_raw, es_demo, metadata = cargar_datos_completos()

    if es_demo:
        st.warning(
            "⚠️ **Aviso de conexión**: No fue posible establecer conexión con el origen CSV de la API en este momento. "
            "Se despliegan datos de demostración estadísticamente representativos de la metodología ENE. "
            "Para consultar los datos reales actualizados diríjase a "
            "[datos.gob.cl](https://datos.gob.cl/dataset/encuesta-nacional-de-empleo-ene)."
        )
    else:
        titulo = metadata.get("result", {}).get("title", "ENE")
        st.success(f"✅ Datos cargados exitosamente desde la API: **{titulo}**")

    # Normalizar
    df = normalizar_columnas(df_raw.copy())

    # ── Sidebar: filtros ────────────────────────
    st.sidebar.markdown("## 🎛️ Filtros")

    años_disp = sorted(df["ano"].dropna().unique()) if "ano" in df.columns else []
    años_sel  = st.sidebar.multiselect(
        "Año", años_disp,
        default=años_disp[-3:] if len(años_disp) >= 3 else años_disp
    )

    regiones_disp = sorted(df["region"].dropna().unique()) if "region" in df.columns else []
    regiones_sel  = st.sidebar.multiselect(
        "Región", regiones_disp, default=regiones_disp
    )

    sexos_disp = sorted(df["sexo"].dropna().unique()) if "sexo" in df.columns else ["Total"]
    sexo_sel   = st.sidebar.selectbox("Sexo", sexos_disp,
                                      index=sexos_disp.index("Total") if "Total" in sexos_disp else 0)

    # Aplicar filtros
    df_f = df.copy()
    if años_sel and "ano" in df_f.columns:
        df_f = df_f[df_f["ano"].isin(años_sel)]
    if regiones_sel and "region" in df_f.columns:
        df_f = df_f[df_f["region"].isin(regiones_sel)]
    if "sexo" in df_f.columns:
        df_f = df_f[df_f["sexo"] == sexo_sel]

    # ── KPIs ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📌 Indicadores Clave")

    col1, col2, col3, col4 = st.columns(4)

    def kpi_html(titulo, valor, delta_texto, clase):
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-delta {clase}">{delta_texto}</div>
        </div>
        """

    if "tasa_desocupacion" in df_f.columns and not df_f.empty:
        t_desoc   = df_f["tasa_desocupacion"].mean()
        t_ocup    = df_f["tasa_ocupacion"].mean()    if "tasa_ocupacion"    in df_f.columns else None
        t_part    = df_f["tasa_participacion"].mean() if "tasa_participacion" in df_f.columns else None
        n_records = len(df_f)

        with col1:
            st.markdown(kpi_html("Tasa Desocupación (prom.)", f"{t_desoc:.1f}%",
                                 "▲ Promedio período seleccionado", "up"), unsafe_allow_html=True)
        with col2:
            val = f"{t_ocup:.1f}%" if t_ocup else "N/D"
            st.markdown(kpi_html("Tasa Ocupación (prom.)", val,
                                 "▼ Mayor es mejor", "down"), unsafe_allow_html=True)
        with col3:
            val = f"{t_part:.1f}%" if t_part else "N/D"
            st.markdown(kpi_html("Tasa Participación (prom.)", val,
                                 "Fuerza de trabajo activa", ""), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_html("Registros analizados", f"{n_records:,}",
                                 "Observaciones en el período", ""), unsafe_allow_html=True)
    else:
        st.info("Selecciona filtros para ver los indicadores.")

    # ── Gráficos ─────────────────────────────────
    st.markdown("---")
    estilo_oscuro()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Evolución temporal",
        "🗺️ Comparación regional",
        "⚖️ Brecha de género",
        "📋 Tabla de datos",
    ])

    # ── Tab 1: Serie temporal ─────────────────────
    with tab1:
        st.markdown("#### Evolución de la Tasa de Desocupación en el tiempo")

        if "ano_trimestre" in df_f.columns and "tasa_desocupacion" in df_f.columns:
            serie = (df_f.groupby("ano_trimestre")["tasa_desocupacion"]
                         .mean()
                         .reset_index()
                         .sort_values("ano_trimestre"))

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.fill_between(range(len(serie)), serie["tasa_desocupacion"],
                            alpha=0.15, color=COLORES["primario"])
            ax.plot(range(len(serie)), serie["tasa_desocupacion"],
                    color=COLORES["primario"], linewidth=2.5, marker="o",
                    markersize=4, markerfacecolor=COLORES["fondo"],
                    markeredgecolor=COLORES["primario"], markeredgewidth=1.5)

            idx_max = serie["tasa_desocupacion"].idxmax()
            idx_min = serie["tasa_desocupacion"].idxmin()
            pos_max = serie.index.get_loc(idx_max)
            pos_min = serie.index.get_loc(idx_min)
            val_max = serie.loc[idx_max, "tasa_desocupacion"]
            val_min = serie.loc[idx_min, "tasa_desocupacion"]

            ax.annotate(f"Máx: {val_max:.1f}%",
                        xy=(pos_max, val_max),
                        xytext=(pos_max + 1, val_max + 0.5),
                        color=COLORES["acento"], fontsize=9,
                        arrowprops=dict(arrowstyle="->", color=COLORES["acento"]))
            ax.annotate(f"Mín: {val_min:.1f}%",
                        xy=(pos_min, val_min),
                        xytext=(pos_min + 1, val_min - 0.8),
                        color=COLORES["verde"], fontsize=9,
                        arrowprops=dict(arrowstyle="->", color=COLORES["verde"]))

            step = max(1, len(serie) // 10)
            ax.set_xticks(range(0, len(serie), step))
            ax.set_xticklabels(serie["ano_trimestre"].iloc[::step], rotation=45, ha="right", fontsize=8)
            ax.set_ylabel("Tasa de Desocupación (%)", fontsize=10)
            ax.set_xlabel("Período (Año-Trimestre)", fontsize=10)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
            ax.grid(axis="y", alpha=0.4)
            ax.set_title("Tasa de Desocupación — Serie histórica", fontsize=12, pad=12)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("Columnas requeridas no encontradas para este gráfico.")

    # ── Tab 2: Regional ───────────────────────────
    with tab2:
        st.markdown("#### Tasa de Desocupación promedio por Región")

        if "region" in df_f.columns and "tasa_desocupacion" in df_f.columns:
            regional = (df_f.groupby("region")["tasa_desocupacion"]
                            .mean()
                            .sort_values(ascending=True)
                            .reset_index())

            prom_nac = regional["tasa_desocupacion"].mean()
            colores_barra = [
                COLORES["acento"]    if v > prom_nac * 1.1 else
                COLORES["primario"]  if v < prom_nac * 0.9 else
                COLORES["secundario"]
                for v in regional["tasa_desocupacion"]
            ]

            fig, ax = plt.subplots(figsize=(10, max(5, len(regional) * 0.45)))
            bars = ax.barh(regional["region"], regional["tasa_desocupacion"],
                           color=colores_barra, edgecolor="none", height=0.65)

            ax.axvline(prom_nac, color=COLORES["naranja"], linestyle="--",
                       linewidth=1.5, label=f"Promedio: {prom_nac:.1f}%")

            for bar, val in zip(bars, regional["tasa_desocupacion"]):
                ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2,
                        f"{val:.1f}%", va="center", ha="left", fontsize=8.5,
                        color=COLORES["texto"])

            ax.set_xlabel("Tasa de Desocupación (%)", fontsize=10)
            ax.set_title("Desocupación Regional — Comparativa", fontsize=12, pad=12)
            ax.legend(fontsize=9)
            ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"🔴 **Por encima** del promedio (+10%)")
            c2.markdown(f"🔵 **Por debajo** del promedio (-10%)")
            c3.markdown(f"🟣 **Cercano** al promedio nacional")
        else:
            st.info("Columnas requeridas no encontradas.")

    # ── Tab 3: Género ─────────────────────────────
    with tab3:
        st.markdown("#### Brecha de Desocupación por Género")

        if "sexo" in df.columns and "tasa_desocupacion" in df.columns:
            df_genero = df.copy()
            if "ano_trimestre" not in df_genero.columns and "ano" in df_genero.columns:
                df_genero["ano_trimestre"] = df_genero["ano"].astype(str)

            if años_sel and "ano" in df_genero.columns:
                df_genero = df_genero[df_genero["ano"].isin(años_sel)]
            
            # Filtro corregido: agregamos la validación regional
            if regiones_sel and "region" in df_genero.columns:
                df_genero = df_genero[df_genero["region"].isin(regiones_sel)]

            df_pivot = (df_genero[df_genero["sexo"].isin(["Hombre", "Mujer"])]
                        .groupby(["ano_trimestre", "sexo"])["tasa_desocupacion"]
                        .mean()
                        .unstack("sexo")
                        .sort_index())

            if not df_pivot.empty and "Hombre" in df_pivot.columns and "Mujer" in df_pivot.columns:
                df_pivot["Brecha"] = df_pivot["Mujer"] - df_pivot["Hombre"]

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

                x = range(len(df_pivot))
                ax1.plot(x, df_pivot["Hombre"], color=COLORES["primario"],
                         linewidth=2, label="Hombre", marker="o", markersize=3)
                ax1.plot(x, df_pivot["Mujer"],  color=COLORES["acento"],
                         linewidth=2, label="Mujer", marker="s", markersize=3)
                ax1.fill_between(x, df_pivot["Hombre"], df_pivot["Mujer"],
                                 alpha=0.12, color=COLORES["secundario"])
                ax1.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
                ax1.set_ylabel("Tasa Desocupación (%)")
                ax1.legend()
                ax1.set_title("Tasa de Desocupación por Sexo", fontsize=11)
                ax1.grid(axis="y", alpha=0.4)

                colores_brecha = [COLORES["acento"] if v >= 0 else COLORES["primario"]
                                  for v in df_pivot["Brecha"]]
                ax2.bar(x, df_pivot["Brecha"], color=colores_brecha, alpha=0.8)
                ax2.axhline(0, color=COLORES["texto"], linewidth=0.8, linestyle="-")
                ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
                ax2.set_ylabel("Brecha (Mujer − Hombre)")
                ax2.set_title("Brecha de Género en Desocupación (pp)", fontsize=11)
                ax2.grid(axis="y", alpha=0.4)

                step = max(1, len(df_pivot) // 8)
                ax2.set_xticks(range(0, len(df_pivot), step))
                ax2.set_xticklabels(list(df_pivot.index)[::step], rotation=45, ha="right", fontsize=8)

                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

                brecha_prom = df_pivot["Brecha"].mean()
                col_m, col_h, col_b = st.columns(3)
                col_m.metric("Desocupación Mujer (prom.)", f"{df_pivot['Mujer'].mean():.1f}%")
                col_h.metric("Desocupación Hombre (prom.)", f"{df_pivot['Hombre'].mean():.1f}%")
                col_b.metric("Brecha promedio", f"{brecha_prom:+.1f} pp",
                             delta_color="inverse")
            else:
                st.info("No hay datos suficientes de Hombre/Mujer para el período seleccionado.")
        else:
            st.info("Columna 'sexo' no disponible en los datos.")

    # ── Tab 4: Tabla ──────────────────────────────
    with tab4:
        st.markdown("#### Datos filtrados")
        mostrar_cols = [c for c in ["ano_trimestre", "ano", "trimestre", "region",
                                     "sexo", "tasa_desocupacion",
                                     "tasa_ocupacion", "tasa_participacion"]
                        if c in df_f.columns]
        st.dataframe(
            df_f[mostrar_cols].sort_values(by=mostrar_cols[:2] if len(mostrar_cols) >= 2 else mostrar_cols)
                              .reset_index(drop=True),
            use_container_width=True,
            height=420
        )

        csv_bytes = df_f[mostrar_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv_bytes,
            file_name="ene_empleo_chile_filtrado.csv",
            mime="text/csv",
        )

    # ── Footer ─────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<small style='color:#475569'>Solemne II — Universidad San Sebastián | "
        "Fuente de datos: <a href='https://datos.gob.cl/dataset/encuesta-nacional-de-empleo-ene' "
        "style='color:#38bdf8'>datos.gob.cl / INE</a> | "
        "Librerías: requests · pandas · matplotlib · streamlit</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()