"""Figuras y tablas de resultados para reports/perfiles_sexo_edad/ (perfiles por sexo × edad)."""
import shutil
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS, RAIZ, ANIOS
from estilo import PAL, plt as _p
OUT = GRAFICAS
NOM = {1: "1. Participación alta", 2: "2. Participación intermedia", 3: "3. Participación baja", 4: "4. Muy mayores (90+)"}
COL = {1: PAL[0], 2: PAL[2], 3: PAL[3], 4: PAL[1]}
def guardar(fig, n): fig.savefig(GRAFICAS / n, dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig)

asig = pd.read_csv(TABLAS / "perfiles_edad_sexo_k4_asignacion.csv")
orden = asig.groupby("perfil")["2024"].mean().sort_values(ascending=False).index.tolist()
asig["perfil_n"] = asig.perfil.map({p: i + 1 for i, p in enumerate(orden)})
d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", columns=["AELEC", "SEXO", "EDAD", "LN", "SV", "NV", "NS"])
for c in ("LN", "SV", "NV", "NS"): d[c] = d[c].astype("int64")
_b = d[(d.AELEC == 2024) & (d.SEXO != 2) & d.EDAD.between(18, 99)].groupby(["SEXO", "EDAD"])[["SV", "NV"]].sum()
_b = (100 * _b.SV / (_b.SV + _b.NV)).unstack("SEXO"); _b["mujeres_menos_hombres"] = _b[1] - _b[0]
_b.rename(columns={0: "hombres", 1: "mujeres"}).round(2).to_csv(TABLAS / "brecha_sexo_edad_2024.csv")
nsel = d[(d.SEXO != 2) & d.EDAD.between(18, 99)].groupby("AELEC")[["NS", "LN"]].sum(); nsel = 100 * nsel.NS / nsel.LN
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)].merge(asig[["SEXO", "EDAD", "perfil_n"]], on=["SEXO", "EDAD"])
t = d.groupby(["perfil_n", "AELEC"])[["SV", "NV", "LN"]].sum()
tray = (100 * t.SV / (t.SV + t.NV)).unstack("AELEC")[ANIOS].round(1)
tam = (100 * d[d.AELEC == 2024].groupby("perfil_n").LN.sum() / d[d.AELEC == 2024].LN.sum()).round(1)
tray["pct_lista_2024"] = tam; tray.to_csv(TABLAS / "trayectorias_perfiles.csv")
# rangos de edad por perfil y sexo
filas = []
for p in range(1, 5):
    for sx, ns in ((0, "hombres"), (1, "mujeres")):
        e = sorted(asig[(asig.perfil_n == p) & (asig.SEXO == sx)].EDAD)
        rg = ", ".join(f"{x[0]}-{x[-1]}" if x[0] != x[-1] else f"{x[0]}" for x in np.split(np.array(e), np.where(np.diff(e) > 1)[0] + 1)) if e else "-"
        filas.append(dict(perfil=NOM[p], sexo=ns, edades=rg))
pd.DataFrame(filas).to_csv(TABLAS / "composicion_perfiles.csv", index=False)
asig.rename(columns={"perfil_n": "perfil_numero"}).drop(columns="perfil").to_csv(TABLAS / "asignacion_segmentos_sexo_edad.csv", index=False)
print(tray); print(pd.DataFrame(filas).to_string(index=False)); print(nsel.round(2).to_dict())

# Fig 1: quiénes son (bandas por edad) + participación 2024
fig, ax = plt.subplots(2, 1, figsize=(11, 5.2), sharex=True)
for a, (sx, tt) in zip(ax, ((0, "Hombres"), (1, "Mujeres"))):
    s = asig[asig.SEXO == sx].sort_values("EDAD")
    a.bar(s.EDAD, s["2024"], width=1.0, color=[COL[p] for p in s.perfil_n])
    a.set_ylabel("Participación 2024 (%)"); a.set_title(tt, loc="left", fontsize=11); a.set_ylim(0, 85)
ax[1].set_xlabel("Edad")
h = [plt.Rectangle((0, 0), 1, 1, color=COL[p]) for p in range(1, 5)]
fig.legend(h, [NOM[p] for p in range(1, 5)], fontsize=8, ncol=4, loc="lower center", bbox_to_anchor=(.5, -.04), frameon=False)
fig.suptitle("Perfil de cada sexo y edad (el color es el perfil; la altura, la participación en 2024)", x=.01, ha="left", fontsize=11)
guardar(fig, "fig1_perfiles_por_sexo_y_edad.png")
# Fig 2: trayectorias
fig, ax = plt.subplots(figsize=(8.5, 4.6))
for p in range(1, 5): ax.plot(ANIOS, tray.loc[p, ANIOS], marker="o", lw=2, color=COL[p], label=NOM[p])
for y in (2012, 2018, 2024): ax.axvspan(y - .6, y + .6, color="#999", alpha=.12)
ax.set_xticks(ANIOS); ax.set_ylabel("Participación entre especificados (%)"); ax.legend(fontsize=8)
ax.set_title("Trayectoria de cada perfil, 2009–2024 (sombreado: elecciones presidenciales)")
guardar(fig, "fig2_trayectorias.png")
# Fig 3: ajuste por lugar
c = pd.read_csv(TABLAS / "perfiles_region_tipo_comparacion.csv"); c = c[c.corte.isin(["region", "tipo"])]
orden_g = ["norte", "centro", "sur", "urbana", "mixta", "rural"]; c = c.set_index("grupo").loc[orden_g]
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.bar(c.index, c.nivel_vs_nacional_pts, color=[PAL[0]] * 3 + [PAL[2]] * 3); ax.axhline(0, color="k", lw=.6)
for i, v in enumerate(c.nivel_vs_nacional_pts): ax.text(i, v + (.15 if v >= 0 else -.45), f"{v:+.1f}", ha="center", fontsize=9)
ax.set_ylabel("Puntos frente al promedio nacional"); ax.set_title("Ajuste por lugar (2009–2024, promedio ponderado)")
guardar(fig, "fig3_ajuste_por_lugar.png")
# Fig 4: no especificados por elección
fig, ax = plt.subplots(figsize=(7, 3.8)); ax.bar([str(y) for y in ANIOS], nsel.loc[ANIOS].values, color=PAL[5])
for i, v in enumerate(nsel.loc[ANIOS].values): ax.text(i, v + .1, f"{v:.1f}%", ha="center", fontsize=9)
ax.set_ylabel("% de la lista nominal"); ax.set_title("Registros con participación no especificada, por elección")
guardar(fig, "fig4_no_especificados.png")
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.plot(_b.index, _b.mujeres_menos_hombres, color=PAL[4], lw=2); ax.axhline(0, color="k", lw=.6); ax.axvspan(85, 99, color="#999", alpha=.15)
ax.set_xlabel("Edad"); ax.set_ylabel("Mujeres menos hombres (puntos)"); ax.set_title("Diferencia de participación entre mujeres y hombres por edad, 2024")
guardar(fig, "fig6_brecha_por_sexo_y_edad.png")
import os
if (GRAFICAS / "perfiles_region_tipo_curvas_2024.png").exists(): os.replace(GRAFICAS / "perfiles_region_tipo_curvas_2024.png", GRAFICAS / "fig5_curvas_por_region_y_tipo.png")
