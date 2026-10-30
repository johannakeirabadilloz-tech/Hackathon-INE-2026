"""Mapas municipales con los cuatro perfiles de sexo × edad (elección de 2024).
(a) composición: % de la lista nominal del municipio en cada perfil; (b) participación de cada perfil en el municipio frente
a su valor nacional; (c) cuánto de la participación municipal se explica solo por la composición.
Geometrías: Marco Geoestadístico 2020 de INEGI (dato externo al INE, copia local en data/external/, solo para dibujar)."""
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib.pyplot as plt
from config import PROC, RAIZ
OUT = RAIZ / "reports/perfiles_sexo_edad"
MIN_ESP = 100        # SUPUESTO: mínimo de registros especificados por municipio y perfil para mostrar su participación
NOM = {1: "Perfil 1: alta", 2: "Perfil 2: intermedia", 3: "Perfil 3: baja"}

asig = pd.read_csv(OUT / "asignacion_segmentos_sexo_edad.csv")[["SEXO", "EDAD", "perfil_numero"]]
d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", filters=[("AELEC", "==", 2024)],
                    columns=["EDOCVE", "MPIOCVE", "SEXO", "EDAD", "LN", "SV", "NV"])
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)]
for c in ("LN", "SV", "NV"): d[c] = d[c].astype("int64")
d = d.merge(asig, on=["SEXO", "EDAD"])
m = d.groupby(["EDOCVE", "MPIOCVE", "perfil_numero"])[["LN", "SV", "NV"]].sum().reset_index()
m["esp"] = m.SV + m.NV
nac = m.groupby("perfil_numero")[["SV", "esp"]].sum(); pn = 100 * nac.SV / nac.esp          # participación nacional por perfil, 2024
print("participación nacional 2024 por perfil:", pn.round(1).to_dict())
tot = m.groupby(["EDOCVE", "MPIOCVE"])[["LN", "SV", "esp"]].sum().rename(columns={"LN": "LN_t", "SV": "SV_t", "esp": "esp_t"})
m = m.join(tot, on=["EDOCVE", "MPIOCVE"])
m["pct_lista"] = 100 * m.LN / m.LN_t
m["part"] = np.where(m.esp >= MIN_ESP, 100 * m.SV / m.esp.where(m.esp > 0), np.nan)
m["dif_nacional"] = m.part - m.perfil_numero.map(pn)
W = m.pivot_table(index=["EDOCVE", "MPIOCVE"], columns="perfil_numero", values=["pct_lista", "part", "dif_nacional"])
W.columns = [f"{a}_p{b}" for a, b in W.columns]
# participación esperada por composición: Σ (esp del perfil en el municipio) × tasa nacional del perfil / Σ esp
m["esperados"] = m.esp * m.perfil_numero.map(pn) / 100
t2 = m.groupby(["EDOCVE", "MPIOCVE"]).agg(esperados=("esperados", "sum"), SV=("SV", "sum"), esp=("esp", "sum"))
W["part_total"] = 100 * t2.SV / t2.esp; W["part_esperada_por_composicion"] = 100 * t2.esperados / t2.esp
W["efecto_lugar_pts"] = W.part_total - W.part_esperada_por_composicion
W = W[t2.esp >= MIN_ESP]
W.reset_index().round(2).to_csv(OUT / "municipios_perfiles_2024.csv", index=False)
r2 = np.corrcoef(W.part_total, W.part_esperada_por_composicion)[0, 1] ** 2
print(f"municipios: {len(W)} | R² participación observada vs esperada por composición: {r2:.3f}")
print("efecto del lugar (observada − esperada), pts: media", round(W.efecto_lugar_pts.mean(), 2), "| sd", round(W.efecto_lugar_pts.std(), 2),
      "| p10-p90", W.efecto_lugar_pts.quantile([.1, .9]).round(1).tolist())
print("sd de la participación observada:", round(W.part_total.std(), 2), "| sd de la esperada por composición:", round(W.part_esperada_por_composicion.std(), 2))
print("cobertura de participación por perfil (municipios con dato):", {p: int(W[f'part_p{p}'].notna().sum()) for p in (1, 2, 3, 4)})
print("% lista nominal en cada perfil: mediana", {p: round(W[f'pct_lista_p{p}'].median(), 1) for p in (1, 2, 3, 4)},
      "| p10-p90 perfil 3:", W.pct_lista_p3.quantile([.1, .9]).round(1).tolist())
print("correlación entre % en perfil 3 y participación total:", round(W.pct_lista_p3.corr(W.part_total), 2))
W.reset_index().to_csv(PROC / "municipios_perfiles_2024.csv", index=False)

G = gpd.read_file(RAIZ / "data/external/geom/mexico.json")[["CVEGEO", "geometry"]].dropna()
W = W.reset_index(); W["CVEGEO"] = W.EDOCVE.astype(int).map("{:02d}".format) + W.MPIOCVE.astype(int).map("{:03d}".format)
G = G.merge(W, on="CVEGEO", how="left")
def panel(a, col, titulo, cmap, vmin, vmax, etiqueta):
    G.plot(column=col, ax=a, cmap=cmap, vmin=vmin, vmax=vmax, linewidth=0.03, edgecolor="#aaa", missing_kwds={"color": "#e5e5e5"},
           legend=True, legend_kwds={"shrink": .55, "label": etiqueta})
    a.set_title(titulo, fontsize=11); a.axis("off")
fig, axs = plt.subplots(1, 3, figsize=(18, 3.7))
for a, p in zip(axs, (1, 2, 3)):
    panel(a, f"dif_nacional_p{p}", NOM[p], "RdBu", -15, 15, "puntos vs. perfil a nivel nacional")
fig.suptitle("Participación de cada perfil en cada municipio, 2024, frente a su valor nacional (gris: sin datos suficientes)", x=.01, y=1.0, ha="left", fontsize=11)
fig.savefig(OUT / "fig7_mapa_participacion_por_perfil_2024.png", dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig)
fig, axs = plt.subplots(1, 3, figsize=(18, 3.7))
for a, p, cm in zip(axs, (1, 2, 3), ("Blues", "Greens", "Oranges")):
    v = G[f"pct_lista_p{p}"]; panel(a, f"pct_lista_p{p}", NOM[p], cm, v.quantile(.02), v.quantile(.98), "% de la lista nominal")
fig.suptitle("Composición: % de la lista nominal de cada municipio que pertenece a cada perfil, 2024", x=.01, y=1.0, ha="left", fontsize=11)
fig.savefig(OUT / "fig8_mapa_composicion_por_perfil_2024.png", dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig)
fig, axs = plt.subplots(1, 3, figsize=(18, 3.7))
panel(axs[0], "part_total", "Participación observada", "viridis", 35, 80, "%")
panel(axs[1], "part_esperada_por_composicion", "Esperada solo por la composición", "viridis", 35, 80, "%")
panel(axs[2], "efecto_lugar_pts", "Diferencia (efecto del lugar)", "RdBu", -12, 12, "puntos")
fig.suptitle("¿Cuánto de la participación municipal se explica por su composición de sexo y edad? 2024", x=.01, y=1.0, ha="left", fontsize=11)
fig.savefig(OUT / "fig9_mapa_composicion_vs_lugar_2024.png", dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig)
