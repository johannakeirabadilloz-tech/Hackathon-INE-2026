import json, numpy as np, pandas as pd
from estilo import *; from config import *
R = json.load(open(TABLAS/"hallazgos_agrupamiento.json")); nulo = np.load(TABLAS/"_nulo.npy")
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.hist(nulo, bins=30, color="#c9ced6"); ax.axvline(R["sil_obs_mejor"], color=PAL[1], lw=2.5)
ax.annotate(f"Datos reales: {R['sil_obs_mejor']:.2f}", (R["sil_obs_mejor"], ax.get_ylim()[1]*.8), (-8, 0), textcoords="offset points", ha="right", color=PAL[1], fontweight="bold")
ax.set_xlabel("mejor separación entre grupos (silhouette)"); ax.set_ylabel("simulaciones")
ax.set_title(f"Datos simulados sin grupos separan igual o mejor que los reales en {R['p_nulo']*100:.0f}% de los casos")

guardar(fig, "08_agrupamiento_vs_nulo.png")
A = pd.read_csv(TABLAS/"agr_04_estabilidad.csv"); a = A[(A.metodo=="kmeans")]
fig, ax = plt.subplots(figsize=(7.5, 4)); x = np.arange(len(a)); w = .38
ax.bar(x-w/2, a.var_entre_agrupamiento*100, w, color=PAL[0]); ax.bar(x+w/2, a.var_entre_corte_nivel*100, w, color=PAL[5])
ax.set_xticks(x, [f"{k} grupos" for k in a.k]); ax.set_ylabel("% de la variación entre entidades explicada")
ax.text(0.02, .93, "azul: agrupamiento (K-means)   gris: simple corte por nivel de participación", transform=ax.transAxes, fontsize=9)
ax.set_title("El agrupamiento explica casi lo mismo que ordenar las entidades por su nivel promedio")
guardar(fig, "09_agrupamiento_vs_corte.png")
P = pd.read_csv(TABLAS/"agr_06_pca_entidades.csv", index_col=0); col = {"Norte":PAL[0],"Centro":PAL[2],"Sur":PAL[1]}
fig, ax = plt.subplots(figsize=(8.5, 6))
for r, d in P.groupby("region_A"): ax.scatter(d.PC1, d.PC2, color=col[r], s=45, label=r)
for n, r in P.iterrows(): ax.annotate(n, (r.PC1, r.PC2), (4, 3), textcoords="offset points", fontsize=7.5)
ax.axhline(0, color="#999", lw=.8); ax.axvline(0, color="#999", lw=.8)
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, frameon=False)
ax.set_xlabel(f"← participa menos que el resto en todas las elecciones | participa más →  ({R['varexp_pca'][0]*100:.0f}% de la variación)")
ax.set_ylabel(f"← relativamente más alto en 2018-24 | en 2009-15 →  ({R['varexp_pca'][1]*100:.0f}%)")
ax.set_title("Las entidades forman un continuo: dos ejes (nivel y momento) resumen su trayectoria, sin grupos separados")
ax.title.set_fontsize(11.5)
guardar(fig, "10_entidades_continuo_pca.png")
