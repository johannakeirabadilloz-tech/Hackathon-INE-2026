"""Streamlit: panel estadístico de perfiles ciudadanos de participación."""
from html import escape

import streamlit as st

from dashboard import charts
from dashboard.data import (COLORS, NAMES, PRESIDENTIAL, REPORTS, YEARS, csv_bytes,
                            filter_segments, previous_same_cycle, read_tables)
from dashboard.theme import apply_theme, profile_card

st.set_page_config(page_title="Perfiles de participación · INE 2026", page_icon="◈",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data(show_spinner=False)
def load_data():
    return read_tables()


def chart(fig, key):
    st.plotly_chart(fig, width="stretch", theme=None, key=key,
                    config={"displaylogo": False, "scrollZoom": False,
                            "toImageButtonOptions": {"format": "png", "scale": 2}})


def heading(kicker, title, description):
    st.markdown(f'<div class="eyebrow">{escape(kicker)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="intro">{escape(description)}</div>', unsafe_allow_html=True)


def download_table(df, name, label="Descargar tabla CSV"):
    st.download_button(label, csv_bytes(df), file_name=name, mime="text/csv", key="download_" + name)


def overview(data, profiles, year, tokens):
    heading("RETO 1 / PANEL ESTADÍSTICO", "La participación tiene distintos perfiles",
            "Explora cuatro tipologías nacionales por sexo y edad. Compara su participación histórica y las diferencias territoriales.")
    st.caption(f"México · {year} · Elección {'presidencial' if year in PRESIDENTIAL else 'intermedia'} · Datos agregados del INE")
    if not profiles:
        st.info("Selecciona al menos un perfil en la barra lateral.")
        return
    history = data["history"][data["history"].perfil.isin(profiles)]
    current = history[history.anio == year].set_index("perfil")
    previous = previous_same_cycle(year)
    for col, p in zip(st.columns(len(profiles)), profiles):
        row = current.loc[p]
        change = "Primera elección de este tipo en la serie"
        if previous:
            earlier = history[(history.perfil == p) & (history.anio == previous)].iloc[0]
            change = f"{row.participacion_pct - earlier.participacion_pct:+.1f} puntos frente a {previous}"
        with col:
            profile_card(p, NAMES[p], COLORS[p], row.participacion_pct, change, row.pct_lista_2024)
    st.caption("Las variaciones comparan elecciones del mismo tipo. La proporción de lista nominal siempre corresponde a 2024 y puede no sumar 100% al seleccionar solo algunos perfiles.")
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.subheader("Seis elecciones, cuatro trayectorias")
        chart(charts.history_chart(history, tokens, year), "overview_history")
    with right:
        st.subheader("¿Qué tamaño tiene cada perfil?")
        chart(charts.share_chart(history, tokens), "overview_share")
        st.caption("Proporción de LN de hombres y mujeres de 18–99 años incluidos en el análisis. No es porcentaje de participación.")
    with st.container(border=True):
        st.subheader("Cómo leer los perfiles")
        st.write("Los niveles de participación cambian de forma continua con la edad. Los cuatro perfiles resumen ese patrón; sus límites no son umbrales naturales ni describen decisiones individuales.")
        st.write("El perfil 4, Valores atípicos, incluye hombres de 93–99 y mujeres de 90–99 años. Su nombre no implica errores ni una detección estadística de anomalías.")


def demographics(data, profiles, year, tokens):
    heading("EXPLORACIÓN / SEXO Y EDAD", "¿Quiénes componen cada perfil?",
            "Cada punto es una combinación de sexo y edad exacta. Los colores conservan la asignación construida con las seis elecciones.")
    c1, c2 = st.columns([1, 2])
    with c1:
        sexes = st.multiselect("Sexo", ["Hombres", "Mujeres"], default=["Hombres", "Mujeres"], key="sexes")
    with c2:
        ages = st.slider("Rango de edad", 18, 99, (18, 99), key="ages")
    selected = filter_segments(data["segments"], profiles, sexes, ages)
    if selected.empty:
        st.info("No hay segmentos para esta combinación. Amplía la edad, el sexo o los perfiles seleccionados.")
        return
    st.caption(f"{len(selected)} combinaciones de sexo y edad · Participación {year} · Asignaciones nacionales fijas")
    chart(charts.age_chart(selected, tokens, year), "age_scatter")
    st.subheader("Asignación por sexo y edad")
    chart(charts.profile_matrix(selected, tokens), "profile_matrix")
    st.caption("Los filtros seleccionan segmentos; no recalculan perfiles ni una tasa agregada. Las tasas por edad no se promedian para producir un total.")
    for p in profiles:
        group = data["composition"].query("perfil_numero == @p")
        with st.expander(f"{p}. {NAMES[p]} · composición nacional completa"):
            for row in group.itertuples():
                st.write(f"**{row.sexo.capitalize()}:** {row.edades} años.")
            st.caption("La ficha muestra la definición completa, independientemente del rango de edad visible.")
    table = selected[["perfil", "nombre", "sexo", "edad", str(year)]].rename(columns={str(year): "participacion_pct"})
    with st.expander("Consultar los valores de la gráfica"):
        st.dataframe(table, hide_index=True, width="stretch")
    download_table(table, f"perfiles_sexo_edad_{year}.csv")


def evolution(data, profiles, year, tokens):
    heading("COMPARACIÓN / 2009–2024", "Un patrón que cambia con la elección",
            "Compara trayectorias nacionales y distingue las elecciones presidenciales de las intermedias.")
    kind = st.radio("Procesos a comparar", ["Todos", "Presidenciales", "Intermedias"], horizontal=True, key="cycle")
    selected = data["history"][data["history"].perfil.isin(profiles)].copy()
    if kind != "Todos":
        selected = selected[selected.tipo_eleccion == ("Presidencial" if kind == "Presidenciales" else "Intermedia")]
    if selected.empty:
        st.info("Selecciona al menos un perfil en la barra lateral.")
        return
    chart(charts.history_chart(selected, tokens, year), "evolution_history")
    st.caption("Las tasas publicadas están redondeadas a un decimal. Las líneas conectan cortes agregados; no siguen a las mismas personas entre elecciones.")
    st.subheader("Participación por perfil y elección")
    pivot = selected.pivot(index="nombre", columns="anio", values="participacion_pct")
    st.dataframe(pivot, width="stretch")
    download_table(selected[["perfil", "nombre", "anio", "tipo_eleccion", "participacion_pct"]], "trayectorias_perfiles.csv")


def territory(data, profiles, tokens):
    heading("CONTEXTO / CORTE 2024", "El lugar también cambia la participación",
            "Los perfiles conservan su definición nacional. Aquí comparamos su participación observada por región y tipo de sección.")
    st.caption("Corte disponible: 2024. Estas tablas no permiten filtrar simultáneamente por sexo o edad ni reconstruir historias territoriales por perfil.")
    cut_label = st.radio("Comparación territorial", ["Región", "Tipo de sección", "Región y tipo de sección"], horizontal=True, key="territorial_cut")
    cut = {"Región": "region", "Tipo de sección": "tipo", "Región y tipo de sección": "region_x_tipo"}[cut_label]
    base = data["territory"].query("corte == @cut")
    groups = sorted(base.grupo.unique())
    selected_groups = st.multiselect("Territorios", groups, default=groups, key="groups_" + cut)
    selected = base[base.grupo.isin(selected_groups) & base.perfil.isin(profiles)]
    if selected.empty:
        st.info("Selecciona al menos un territorio y un perfil.")
        return
    chart(charts.territorial_chart(selected, tokens), "territorial_chart")
    if cut == "region_x_tipo":
        st.info("Sur rural presenta una forma por edad menos parecida al patrón nacional; conviene interpretarlo como un contexto particular.")
    st.subheader("Valores observados en 2024")
    table = selected[["grupo", "perfil", "nombre", "participacion_pct", "anio"]]
    st.dataframe(table, hide_index=True, width="stretch")
    download_table(table, "participacion_territorial_2024.csv")
    with st.expander("Diferencias de nivel y concordancia con los perfiles nacionales"):
        st.dataframe(selected[["grupo", "nivel_vs_nacional_pts", "ari_perfiles_propios_vs_nacional"]].drop_duplicates(), hide_index=True, width="stretch")
        st.caption("El ajuste de nivel resume 2009–2024. No debe sumarse automáticamente a tasas de otro corte para predecir participación. ARI mide concordancia de agrupaciones, no exactitud.")


def methodology(data):
    heading("TRANSPARENCIA / MÉTODO Y DATOS", "Qué podemos afirmar con estos datos",
            "Una segmentación descriptiva de grupos poblacionales, basada en los Conteos Censales de Participación Ciudadana del INE.")
    a, b, c = st.columns(3)
    a.metric("Perfiles nacionales", "4")
    b.metric("Segmentos sexo × edad", "164")
    c.metric("Elecciones", "6")
    st.subheader("Definiciones de los indicadores")
    st.markdown("**Participación entre especificados:** `SV / (SV + NV) × 100`.\n\n**No especificados:** `NS / LN × 100`. NS no se considera abstención.\n\n**Composición del perfil:** proporción de la lista nominal analizada en 2024; usa un denominador diferente al de participación.")
    st.subheader("Por qué cuatro perfiles")
    st.write("Se compararon K-means y Ward con dos a seis grupos. La propuesta utiliza K-means con cuatro perfiles por interpretabilidad y estabilidad. Dos grupos tienen mayor silhouette; cuatro es una decisión analítica, no una prueba de cuatro tipos naturales de ciudadanía.")
    st.dataframe(data["comparison"], hide_index=True, width="stretch")
    st.subheader("Cobertura y límites")
    st.markdown("- Perfiles de hombres y mujeres de 18–99 años; la categoría no binario solo tiene registros en 2024 y se conserva en una tabla descriptiva aparte.\n- Las edades de 100 o más quedan fuera de estos perfiles.\n- Los mismos rangos de edad no representan a las mismas personas a lo largo del tiempo.\n- No hay escolaridad, ingreso ni motivos para votar en estas tablas.\n- Norte, centro y sur son una regionalización propia del proyecto.\n- Los cuadernillos no incluyen voto desde el extranjero ni participación en casillas especiales.\n- Los perfiles no identifican causas; las estrategias de educación cívica requieren validación.")
    with st.expander("Ver la cobertura de registros no especificados"):
        st.image(str(REPORTS / "fig4_no_especificados.png"),
                 caption="Figura publicada: NS como porcentaje de la lista nominal de hombres y mujeres de 18–99 años por elección.")
    st.subheader("Descargas y documentación")
    st.download_button("Descargar composición de los cuatro perfiles", (REPORTS / "composicion_perfiles.csv").read_bytes(), "composicion_perfiles.csv", "text/csv")
    st.download_button("Descargar explicación completa", (REPORTS / "README.md").read_bytes(), "metodologia_perfiles.md", "text/markdown")
    st.link_button("Fuente: Hackathon INE 2026", "https://www.ine.mx/hackathon-2026/")


def main():
    try:
        data = load_data()
    except (OSError, ValueError, KeyError) as exc:
        st.error("No se pudieron cargar las tablas publicadas del análisis.")
        st.code(str(exc))
        st.stop()
    with st.sidebar:
        st.markdown('<div class="brand">◈ <span>INE</span> / Análisis electoral</div><div class="brand-note">HACKATHON 2026 · RETO 1</div>', unsafe_allow_html=True)
        section = st.radio("Panel estadístico", ["Panorama", "Sexo y edad", "Evolución", "Territorio", "Metodología"], key="section")
        st.divider()
        theme = st.radio("Apariencia", ["Claro", "Oscuro"], horizontal=True, key="theme")
        if section in ["Panorama", "Sexo y edad", "Evolución"]:
            year = st.selectbox("Elección de referencia", YEARS, index=5, key="year")
        else:
            year = 2024
        if section != "Metodología":
            profiles = st.multiselect("Perfiles", list(NAMES), default=list(NAMES),
                                     format_func=lambda p: f"{p}. {NAMES[p]}", key="profiles")
        else:
            profiles = list(NAMES)
        st.divider()
        st.caption("Participación = SV / (SV + NV).\n\nRegistros no especificados se analizan por separado.")
        st.caption("Fuente: INE · 2009–2024\n\nPerfiles agregados, sin datos personales.")
    tokens = apply_theme(theme)
    if section == "Panorama":
        overview(data, profiles, year, tokens)
    elif section == "Sexo y edad":
        demographics(data, profiles, year, tokens)
    elif section == "Evolución":
        evolution(data, profiles, year, tokens)
    elif section == "Territorio":
        territory(data, profiles, tokens)
    else:
        methodology(data)
    st.markdown('<div class="source-note">Centro de Inteligencia y Visualización de Información para el Análisis Electoral · Nombre provisional · Hackathon INE 2026</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
