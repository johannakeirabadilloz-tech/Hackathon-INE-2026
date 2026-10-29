"""Contrato de las tablas publicadas. La app no necesita el maestro local."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports/perfiles_sexo_edad"
YEARS = [2009, 2012, 2015, 2018, 2021, 2024]
PRESIDENTIAL = {2012, 2018, 2024}
NAMES = {
    1: "PARTICIPACIÓN ALTA",
    2: "PARTICIPACIÓN INTERMEDIA",
    3: "PARTICIPACION BAJA",
    4: "Valores atípicos",
}
COLORS = {1: "#1B6CA8", 2: "#2A9D8F", 3: "#E9A23B", 4: "#D1495B"}
SEXES = {0: "Hombres", 1: "Mujeres"}


def read_tables():
    segments = pd.read_csv(REPORTS / "asignacion_segmentos_sexo_edad.csv")
    segments = segments.rename(columns={"SEXO": "sexo_codigo", "EDAD": "edad", "perfil_numero": "perfil"})
    if len(segments) != 164 or segments.duplicated(["sexo_codigo", "edad"]).any():
        raise ValueError("Se esperaban 164 combinaciones únicas de sexo y edad.")
    if set(segments.perfil) != set(NAMES):
        raise ValueError("La asignación debe contener los cuatro perfiles publicados.")
    segments["sexo"] = segments.sexo_codigo.map(SEXES)
    segments["nombre"] = segments.perfil.map(NAMES)
    trajectories = pd.read_csv(REPORTS / "trayectorias_perfiles.csv").rename(columns={"perfil_n": "perfil"})
    history = trajectories.melt(id_vars=["perfil", "pct_lista_2024"], value_vars=[str(y) for y in YEARS],
                                var_name="anio", value_name="participacion_pct")
    history["anio"] = history.anio.astype(int)
    history["nombre"] = history.perfil.map(NAMES)
    history["tipo_eleccion"] = history.anio.map(lambda y: "Presidencial" if y in PRESIDENTIAL else "Intermedia")
    composition = pd.read_csv(REPORTS / "composicion_perfiles.csv")
    composition["perfil_numero"] = composition.perfil.str.extract(r"^(\d+)").astype(int)
    territory = pd.read_csv(REPORTS / "perfiles_region_tipo_comparacion.csv")
    territorial_long = territory.melt(
        id_vars=["corte", "grupo", "nivel_vs_nacional_pts", "ari_perfiles_propios_vs_nacional"],
        value_vars=[f"perfil{i}_2024" for i in NAMES], var_name="perfil_col", value_name="participacion_pct")
    territorial_long["perfil"] = territorial_long.perfil_col.str.extract(r"perfil(\d)").astype(int)
    territorial_long["nombre"] = territorial_long.perfil.map(NAMES)
    territorial_long["anio"] = 2024
    comparison = pd.read_csv(REPORTS / "perfiles_edad_sexo_comparacion.csv")
    for values in [history.participacion_pct, territorial_long.participacion_pct]:
        if values.isna().any() or not values.between(0, 100).all():
            raise ValueError("Hay porcentajes de participación fuera del rango permitido.")
    return dict(segments=segments, history=history, composition=composition,
                territory=territorial_long, comparison=comparison)


def filter_segments(segments, profiles, sexes, age_range):
    return segments.loc[segments.perfil.isin(profiles) & segments.sexo.isin(sexes)
                        & segments.edad.between(*age_range)].copy()


def previous_same_cycle(year):
    candidates = [y for y in YEARS if y < year and (y in PRESIDENTIAL) == (year in PRESIDENTIAL)]
    return max(candidates) if candidates else None


def csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8-sig")
