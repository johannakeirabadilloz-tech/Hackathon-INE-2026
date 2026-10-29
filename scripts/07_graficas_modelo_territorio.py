import json, numpy as np, pandas as pd
from estilo import *; from config import *
# ---- 11. factores del modelo
T = pd.read_csv(TABLAS/"mod_01_factores.csv").sort_values("explica_solo")
fig, ax = plt.subplots(figsize=(7.5, 3.8)); y = np.arange(len(T))
ax.barh(y, T.explica_solo*100, color=PAL[0])
for i, v in enumerate(T.explica_solo*100): ax.annotate(f"{v:.0f}%", (v, i), (4, -3), textcoords="offset points", fontsize=10)
ax.set_yticks(y, T.factor); ax.set_xlabel("% de la variación en la participación que explica cada factor por sí solo")
top = T.iloc[-1]; ax.set_title(f"La edad explica más que cualquier otro factor ({top.explica_solo*100:.0f}%); el tipo de sección casi nada ({T.iloc[0].explica_solo*100:.0f}%)")
ax.title.set_fontsize(11.5); guardar(fig, "11_factores_modelo.png")
# ---- 12. efectos en puntos porcentuales
A = pd.read_csv(TABLAS/"mod_03_efectos_pp.csv", index_col=0)
sel = ["Mujeres vs Hombres", "Edad 18-24 vs 30-39", "Edad 25-29 vs 30-39", "Edad 40-49 vs 30-39", "Edad 50-59 vs 30-39", "Edad 60-69 vs 30-39", "Edad 70+ vs 30-39", "Elección 2024 vs 2018", "Elección 2024 vs 2021", "Rural vs urbana, elección 2015", "Rural vs urbana, elección 2024"]
S = A.loc[sel].iloc[::-1]; fig, ax = plt.subplots(figsize=(8.5, 5)); y = np.arange(len(S))
cols = [PAL[1] if v < 0 else PAL[0] for v in S.efecto_pp]
ax.hlines(y, S.ic95_inf, S.ic95_sup, color="#999", lw=2); ax.scatter(S.efecto_pp, y, color=cols, s=45, zorder=3); ax.axvline(0, color="k", lw=1)
for i, v in enumerate(S.efecto_pp): ax.annotate(f"{v:+.1f}", (S.ic95_sup.iloc[i], i), (6, -3), textcoords="offset points", fontsize=9)
ax.set_yticks(y, S.index, fontsize=9.5); ax.set_xlabel("diferencia en puntos porcentuales de participación (con intervalo de 95%)")
ax.set_title("Con todo lo demás igual, las mujeres votan ~8 puntos más y 60-69 años, ~18 más que 30-39", fontsize=11.5)
guardar(fig, "12_efectos_puntos.png")
# ---- 13. territorio: captura
G = pd.read_csv(TABLAS/"ter_01_captura.csv"); fig, ax = plt.subplots(figsize=(7.5, 4)); x = np.arange(2)
ax.bar(x, G.captura_global*100, .5, color=PAL[0])
ax.hlines(G.azar_p95*100, x-.3, x+.3, color=PAL[1], lw=2.5)
for i, r in G.iterrows():
    ax.annotate(f"{r.captura_global*100:.0f}%", (i, r.captura_global*100), (0, -16), textcoords="offset points", ha="center", fontweight="bold", color="white")
    ax.annotate(f"azar (p95): {r.azar_p95*100:.0f}%", (i+.3, r.azar_p95*100), (4, -3), textcoords="offset points", color=PAL[1], fontsize=9)
ax.set_xticks(x, ["3 regiones\n(norte, centro, sur)", "5 regiones"]); ax.set_ylabel("% del efecto de entidad que recoge")
ax.set_title(f"5 regiones recogen {G.captura_global[1]*100:.0f}% del efecto de entidad; 3 regiones, {G.captura_global[0]*100:.0f}% (no supera al azar)", fontsize=11.5)
ax.set_xlim(-.6, 1.9); guardar(fig, "13_regiones_captura.png")
# ---- 14. dispersión dentro de región
W = pd.read_csv(TABLAS/"ter_04_dispersion_dentro_region.csv"); W = W[(W.eleccion == 2024) & (W.regionalizacion == "B")].sort_values("mediana")
fig, ax = plt.subplots(figsize=(8, 4)); y = np.arange(len(W))
ax.hlines(y, W.p10, W.p90, color=PAL[0], lw=6, alpha=.45); ax.scatter(W.mediana, y, color=PAL[0], s=50, zorder=3, label="mediana")
for i, r in enumerate(W.itertuples()): ax.annotate(f"amplitud {r.amplitud_p10_p90:.0f} pts", (r.p90, i), (6, -3), textcoords="offset points", fontsize=9)
ax.set_yticks(y, W.region); ax.set_xlabel("participación 2024 por municipio, ajustada por sexo y edad (el 80% central de municipios)"); ax.set_xlim(40, 95)
ax.set_title(f"Dentro de cada región, el 80% central de los municipios abarca de {W.amplitud_p10_p90.min():.0f} a {W.amplitud_p10_p90.max():.0f} puntos", fontsize=11.5)
guardar(fig, "14_municipios_dentro_region.png")
print(W.round(1).to_string())
