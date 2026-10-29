"""¿Cambia con el lugar la brecha de participación por edad? Datos agregados; sin causas."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS, ANIOS

MIN_ESP = 100   # SUPUESTO: mínimo de votantes+abstencionistas especificados por celda municipal
GRUPOS = ["18-34", "35-64", "65-84", "85+"]
BINS = [18, 35, 65, 85, 200]

d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet",
                    columns=["AELEC", "EDOCVE", "MPIOCVE", "EDAD", "SV", "NV"])
d = d[d.EDAD >= 18]
d["g"] = pd.cut(d.EDAD, BINS, right=False, labels=GRUPOS)
m = d.groupby(["AELEC", "EDOCVE", "MPIOCVE", "g"], observed=True)[["SV", "NV"]].sum().reset_index()
del d
m["esp"] = m.SV + m.NV
m["part"] = 100 * m.SV / m.esp.where(m.esp > 0)

# entidad × grupo × año
e = m.groupby(["AELEC", "EDOCVE", "g"], observed=True)[["SV", "NV"]].sum()
e["part"] = 100 * e.SV / (e.SV + e.NV)
ent = e.part.unstack("g")
ent["brecha_joven"] = ent["35-64"] - ent["18-34"]
ent["brecha_85"] = ent["35-64"] - ent["85+"]
ent.round(2).to_csv(TABLAS / "territorial_entidad_grupo_anio.csv")

# municipio 2024: ancho, con mínimo de soporte en ambos grupos
res = []
for y in ANIOS:
    w = m[m.AELEC == y].pivot_table(index=["EDOCVE", "MPIOCVE"], columns="g", values=["part", "esp"], observed=True)
    ok = (w["esp"][["18-34", "35-64", "85+"]] >= MIN_ESP).all(axis=1)
    w = w[ok]
    p = w["part"]
    t = pd.DataFrame({"brecha_joven": p["35-64"] - p["18-34"], "brecha_85": p["35-64"] - p["85+"]}).reset_index()
    t["AELEC"] = y
    res.append(t)
mun = pd.concat(res)
mun.round(2).to_csv(TABLAS / "territorial_municipio_brechas.csv", index=False)

# descomposición: parte de la varianza municipal que corresponde a diferencias entre entidades (eta²)
def eta2(df, col):
    tot = ((df[col] - df[col].mean()) ** 2).sum()
    ent_ = df.groupby("EDOCVE")[col].transform("mean")
    return ((ent_ - df[col].mean()) ** 2).sum() / tot

filas = []
for y, t in mun.groupby("AELEC"):
    filas.append(dict(
        anio=y, municipios=len(t),
        brecha_joven_media=t.brecha_joven.mean(), brecha_joven_sd=t.brecha_joven.std(),
        brecha_joven_p10=t.brecha_joven.quantile(.1), brecha_joven_p90=t.brecha_joven.quantile(.9),
        brecha_85_media=t.brecha_85.mean(), brecha_85_sd=t.brecha_85.std(),
        brecha_85_p10=t.brecha_85.quantile(.1), brecha_85_p90=t.brecha_85.quantile(.9),
        eta2_entidad_joven=eta2(t, "brecha_joven"), eta2_entidad_85=eta2(t, "brecha_85"),
        corr_joven_vs_85=t.brecha_joven.corr(t.brecha_85)))
resumen = pd.DataFrame(filas).round(3)
resumen.to_csv(TABLAS / "territorial_resumen.csv", index=False)

# efecto de ciclo por grupo: presidencial (2012,2018,2024) vs intermedia (2009,2015,2021)
n = e.part.unstack("g").reset_index()
n["tipo"] = np.where(n.AELEC.isin([2012, 2018, 2024]), "presidencial", "intermedia")
ciclo = n.groupby("tipo")[GRUPOS].mean().T
ciclo["diferencia"] = ciclo.presidencial - ciclo.intermedia
ciclo.round(2).to_csv(TABLAS / "territorial_ciclo.csv")

# gráficas (2024)
t24 = mun[mun.AELEC == 2024]
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(t24.brecha_joven, 40, color="#207b9b"); ax[0].set_title("Brecha 35-64 menos 18-34 (pts), municipios 2024")
ax[1].hist(t24.brecha_85, 40, color="#e28632"); ax[1].set_title("Brecha 35-64 menos 85+ (pts), municipios 2024")
fig.tight_layout(); fig.savefig(GRAFICAS / "territorial_histograma_brechas.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(t24.brecha_joven, t24.brecha_85, s=6, alpha=.4, color="#207b9b")
ax.set_xlabel("Brecha joven (pts)"); ax.set_ylabel("Brecha 85+ (pts)"); ax.set_title("¿Se mueven juntas? Municipios 2024")
fig.tight_layout(); fig.savefig(GRAFICAS / "territorial_dispersion_brechas.png", dpi=150); plt.close(fig)

x = ent.loc[2024].sort_values("brecha_joven")
fig, ax = plt.subplots(figsize=(8, 7))
ax.barh(x.index.astype(str), x.brecha_joven, color="#207b9b", label="joven")
ax.scatter(x.brecha_85, x.index.astype(str), color="#e28632", zorder=3, label="85+")
ax.set_xlabel("Brecha vs 35-64 (pts)"); ax.set_ylabel("Clave de entidad"); ax.legend(); ax.set_title("Brechas por entidad, 2024")
fig.tight_layout(); fig.savefig(GRAFICAS / "territorial_entidades_2024.png", dpi=150); plt.close(fig)

print(resumen.T.to_string()); print(ciclo.round(2)); print(ent.loc[2024].round(1).sort_values("brecha_joven").iloc[[0,1,2,-3,-2,-1]])
