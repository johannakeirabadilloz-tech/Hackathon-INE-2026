"""Análisis espacial de la participación municipal. Geometrías: Marco Geoestadístico 2020 de INEGI (copia de un repositorio
público de terceros, PhantomInsights/mexico-geojson); solo se usan para definir vecindad. Asociación, no causa."""
import json, warnings
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen, w_subset
from esda import Moran, Moran_Local
from config import RAIZ, PROC, TABLAS, GRAFICAS
from estilo import guardar, PAL
warnings.filterwarnings("ignore")
SEED, PERM = 42, 999
np.random.seed(SEED)

G = gpd.read_file(RAIZ / "data/external/geom/mexico.json")[["CVEGEO", "NOM_ENT", "NOM_MUN", "geometry"]]
G = G.dropna(subset=["geometry"]).reset_index(drop=True)
wfull = Queen.from_dataframe(G, use_index=False)
print("municipios en geometría:", len(G), "| islas (sin vecinos):", len(wfull.islands))

# participación general por municipio (todas las edades, sin no binario) y brechas
cubo = pd.read_parquet(PROC / "cubo.parquet", columns=["AELEC", "EDOCVE", "MPIOCVE", "SEXO", "SV", "NV"])
cubo = cubo[cubo.SEXO != 2]
p = cubo.groupby(["AELEC", "EDOCVE", "MPIOCVE"])[["SV", "NV"]].sum().reset_index()
p["part"] = 100 * p.SV / (p.SV + p.NV).where((p.SV + p.NV) > 0)
b = pd.read_csv(TABLAS / "territorial_municipio_brechas.csv")
D = p.merge(b, on=["AELEC", "EDOCVE", "MPIOCVE"], how="left")
D["CVEGEO"] = D.EDOCVE.astype(int).map("{:02d}".format) + D.MPIOCVE.astype(int).map("{:03d}".format)
cob = {}
for y in (2021, 2024):
    k = set(D[D.AELEC == y].CVEGEO); gk = set(G.CVEGEO)
    cob[y] = dict(municipios_conteos=len(k), con_geometria=len(k & gk), sin_geometria=len(k - gk), geometrias_sin_datos=len(gk - k))
print("cobertura de la unión por clave:", cob)

def prepara(y, col):
    t = D[(D.AELEC == y)].dropna(subset=[col]).drop_duplicates("CVEGEO")
    idx = G.reset_index().merge(t[["CVEGEO", col, "EDOCVE"]], on="CVEGEO").dropna(subset=[col])
    ids = idx["index"].tolist()
    w = w_subset(wfull, ids); w.transform = "r"
    # w_subset reindexa por posición en 'ids'
    return idx.reset_index(drop=True), w

filas, lisa_res = [], {}
for y in (2021, 2024):
    for col, nom in (("part", "participación general"), ("brecha_joven", "brecha de jóvenes"), ("brecha_85", "brecha de 85+")):
        idx, w = prepara(y, col)
        mi = Moran(idx[col].values, w, permutations=PERM)
        # estructura espacial que queda tras quitar la media de la entidad
        res = idx[col] - idx.groupby("EDOCVE")[col].transform("mean")
        mr = Moran(res.values, w, permutations=PERM)
        filas.append(dict(anio=y, variable=nom, n=len(idx), moran_I=mi.I, p_sim=mi.p_sim, moran_I_sin_efecto_entidad=mr.I, p_sim_resid=mr.p_sim,
                          islas=len(w.islands)))
        if y == 2024:
            lm = Moran_Local(idx[col].values, w, permutations=PERM, seed=SEED)
            q = np.where(lm.p_sim < 0.05, lm.q, 0)       # 1 AA, 2 BA, 3 BB, 4 AB
            idx["cluster"] = pd.Series(q).map({0: "No significativo", 1: "Alto-Alto", 2: "Bajo-Alto", 3: "Bajo-Bajo", 4: "Alto-Bajo"})
            lisa_res[col] = idx
M_ = pd.DataFrame(filas).round(3); M_.to_csv(TABLAS / "espacial_moran.csv", index=False); print(M_.to_string(index=False))

# ¿predicen los vecinos mejor que la entidad? (promedio de vecinos excluyendo al propio municipio, frente a media de entidad sin él)
filas = []
for y in (2021, 2024):
    for col in ("part", "brecha_joven", "brecha_85"):
        idx, w = prepara(y, col)
        v = idx[col].values
        ids = idx["index"].tolist(); pos = {g_: i for i, g_ in enumerate(ids)}
        vec = np.array([np.mean([v[pos[j]] for j in w.neighbors[ids[i]]]) if w.neighbors[ids[i]] else np.nan for i in range(len(v))])
        e = idx.groupby("EDOCVE")[col]
        loo = ((e.transform("sum") - idx[col]) / (e.transform("count") - 1)).values
        ok = ~np.isnan(vec) & ~np.isnan(loo)
        r = lambda x: np.corrcoef(x[ok], v[ok])[0, 1] ** 2
        A = np.column_stack([np.ones(ok.sum()), vec[ok], loo[ok]]); beta, *_ = np.linalg.lstsq(A, v[ok], rcond=None)
        r2c = 1 - ((v[ok] - A @ beta).var() / v[ok].var())
        filas.append(dict(anio=y, variable=col, n=int(ok.sum()), r2_solo_entidad=r(loo), r2_solo_vecinos=r(vec), r2_ambos=r2c))
P = pd.DataFrame(filas).round(3); P.to_csv(TABLAS / "espacial_vecinos_vs_entidad.csv", index=False); print(P.to_string(index=False))

# conteo de agrupamientos y mapas (2024)
res = {}
for col, idx in lisa_res.items(): res[col] = idx.cluster.value_counts().to_dict()
json.dump(cob | {"agrupamientos_2024": res}, open(TABLAS / "espacial_lisa_resumen.json", "w"), indent=1, default=str); print(res)
COL = {"Alto-Alto": "#d1495b", "Bajo-Bajo": "#1b6ca8", "Alto-Bajo": "#e9a23b", "Bajo-Alto": "#8ab6d6", "No significativo": "#e5e5e5"}
fig, axs = plt.subplots(1, 3, figsize=(17, 5.4))
for a, (col, tt) in zip(axs, (("part", "Participación general 2024"), ("brecha_joven", "Brecha de jóvenes 2024"), ("brecha_85", "Brecha de 85+ 2024"))):
    idx = lisa_res[col]; geo = G.merge(idx[["CVEGEO", "cluster"]], on="CVEGEO", how="left")
    geo["cluster"] = geo.cluster.fillna("No significativo")
    for k_, c in COL.items():
        s = geo[geo.cluster == k_]
        if len(s): s.plot(ax=a, color=c, linewidth=0.05, edgecolor="#888", label=f"{k_} ({len(s)})")
    a.set_title(tt, fontsize=11); a.axis("off"); a.legend(fontsize=7, loc="lower left")
fig.suptitle("Agrupamientos locales (LISA, p<0.05): Alto = valor alto rodeado de valores altos", x=0.01, ha="left", fontsize=11)
guardar(fig, "espacial_lisa_2024.png")
fig, axs = plt.subplots(1, 2, figsize=(12, 5.2))
for a, (col, tt) in zip(axs, (("brecha_joven", "Brecha de jóvenes 2024 (pts)"), ("brecha_85", "Brecha de 85+ 2024 (pts)"))):
    geo = G.merge(D[(D.AELEC == 2024)].drop_duplicates("CVEGEO")[["CVEGEO", col]], on="CVEGEO", how="left")
    geo.plot(column=col, ax=a, cmap="YlOrRd", linewidth=0.03, edgecolor="#999", legend=True, legend_kwds={"shrink": .6},
             missing_kwds={"color": "#e5e5e5"})
    a.set_title(tt, fontsize=11); a.axis("off")
guardar(fig, "espacial_mapa_brechas_2024.png")
