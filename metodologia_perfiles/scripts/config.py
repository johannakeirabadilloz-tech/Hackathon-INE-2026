"""Parámetros y SUPUESTOS del análisis. Todo lo editable vive aquí."""
from pathlib import Path

CARPETA = Path(__file__).resolve().parents[1]       # metodologia_perfiles/
RAIZ = CARPETA.parent                               # raíz del repositorio
RAW = RAIZ / "data" / "raw"
PROC = RAIZ / "data" / "processed"          # ignorado por Git
OUT = CARPETA
TABLAS = CARPETA / "tablas"
GRAFICAS = CARPETA / "figuras"
for d in (PROC, TABLAS, GRAFICAS):
    d.mkdir(parents=True, exist_ok=True)

ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]

# --- SUPUESTO 1: grupos de edad (edición libre). Se estandariza con la
# distribución de edad de la lista nominal agregada de todas las elecciones.
CORTES_EDAD = [18, 25, 30, 40, 50, 60, 70, 200]
ETIQ_EDAD = ["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"]

# --- SUPUESTO 2: dos regionalizaciones PROPIAS de este análisis. El catálogo
# del equipo es solo local y no está disponible aquí; NO son divisiones
# oficiales del INEGI ni del INE (no se verificó ninguna fuente oficial).
# Claves de entidad INE (EDOCVE). Cada entidad debe aparecer una sola vez.
REGIONES_A = {   # 3 regiones: norte / centro / sur
    "Norte": [1, 2, 3, 5, 8, 10, 19, 24, 25, 26, 28, 32],
    "Centro": [6, 9, 11, 13, 14, 15, 16, 17, 18, 21, 22, 29],
    "Sur": [4, 7, 12, 20, 23, 27, 30, 31],
}
REGIONES_B = {   # 5 regiones, más finas
    "Noroeste": [2, 3, 8, 10, 25, 26],
    "Noreste": [5, 19, 24, 28, 32],
    "Occidente y Bajío": [1, 6, 11, 14, 16, 18, 22],
    "Centro": [9, 13, 15, 17, 21, 29],
    "Sur-Sureste": [4, 7, 12, 20, 23, 27, 30, 31],
}
for _r in (REGIONES_A, REGIONES_B):
    _k = sorted(k for v in _r.values() for k in v)
    assert _k == list(range(1, 33)), "regionalización incompleta o con repetidos"

def mapa(regs):
    return {k: r for r, v in regs.items() for k in v}
