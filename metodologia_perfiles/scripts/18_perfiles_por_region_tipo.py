"""¿Los perfiles de sexo × edad cambian por región o por tipo de sección, o todos se comportan igual?
Regiones: propuesta del proyecto (config.REGIONES_A), no oficial. Datos del INE. Exploratorio."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score
from config import PROC, TABLAS, GRAFICAS, ANIOS, REGIONES_A, mapa
from estilo import guardar, PAL
SEED, K = 42, 4
d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", columns=["AELEC", "EDOCVE", "TIPOSEC", "SEXO", "EDAD", "SV", "NV"])
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)]
d["region"] = d.EDOCVE.map(mapa(REGIONES_A)).str.lower(); d["tipo"] = d.TIPOSEC.map({"U": "urbana", "M": "mixta", "R": "rural"})
for c in ("SV", "NV"): d[c] = d[c].astype("int64")
def tabla(by):
    a = d.groupby(by + ["SEXO", "EDAD", "AELEC"])[["SV", "NV"]].sum(); a["esp"] = a.SV + a.NV; a["p"] = 100 * a.SV / a.esp
    return a
nac = tabla([]); 
P0 = nac.p.unstack("AELEC")[ANIOS]
Z0 = StandardScaler().fit(P0.values)
lab0 = KMeans(K, n_init=50, random_state=SEED).fit(Z0.transform(P0.values))
orden = np.argsort(-pd.Series(Z0.inverse_transform(lab0.cluster_centers_)[:, 5]).values)   # perfiles de mayor a menor 2024
rank = {c: i + 1 for i, c in enumerate(orden)}; L0 = pd.Series([rank[x] for x in lab0.labels_], index=P0.index, name="perfil_nac")
filas, curvas = [], {}
for nombre, by in (("region", ["region"]), ("tipo", ["tipo"]), ("region_x_tipo", ["region", "tipo"])):
    a = tabla(by)
    for g, sub in a.groupby(level=by if len(by) > 1 else by[0]):
        gk = g if isinstance(g, tuple) else (g,)
        P = sub.p.unstack("AELEC")[ANIOS].droplevel(list(range(len(by)))).dropna(); N = sub.esp.unstack("AELEC")[ANIOS].droplevel(list(range(len(by)))).loc[P.index]
        idx = P.index.intersection(P0.index); P, N = P.loc[idx], N.loc[idx]; W = N.sum(axis=1)
        b = P0.loc[idx]
        # nivel y forma frente al nacional (ponderado por tamaño)
        dif = (P - b); nivel = float(np.average(dif.mean(axis=1), weights=W)); rmse = float(np.sqrt(np.average((dif ** 2).mean(axis=1), weights=W)))
        # error que queda al quitar el nivel del grupo (diferencia de forma por edad y de una elección a otra); descomposición exacta: rmse² = nivel² + varianza
        rmse_forma = float(np.sqrt(max(rmse ** 2 - nivel ** 2, 0.0)))
        # perfil propio (k=4) frente al nacional
        lab = KMeans(K, n_init=30, random_state=SEED).fit_predict(StandardScaler().fit_transform(P.values))
        ari = adjusted_rand_score(L0.loc[idx], lab)
        # perfil nacional asignado por centroides nacionales -> participación del grupo por perfil nacional
        pp = {f"perfil{k}_2024": float(np.average(P.loc[L0.loc[idx] == k, 2024], weights=W[L0.loc[idx] == k])) for k in range(1, K + 1)}
        filas.append(dict(corte=nombre, grupo=" / ".join(gk), nivel_vs_nacional_pts=nivel, rmse_total_pts=rmse, rmse_sin_nivel_pts=rmse_forma,
                          ari_perfiles_propios_vs_nacional=ari, **pp))
        curvas[(nombre, " / ".join(gk))] = P[2024]
R = pd.DataFrame(filas).round(2); R.to_csv(TABLAS / "perfiles_region_tipo_comparacion.csv", index=False); print(R.to_string(index=False))
# cuánto explica agregar región o tipo a edad×sexo×elección (R² ponderado sobre celdas municipales-sexo-edad no necesario: sobre celdas del corte)
nac_p = P0.stack().rename("p0")
for nombre, by in (("region", ["region"]), ("tipo", ["tipo"]), ("region_x_tipo", ["region", "tipo"])):
    a = tabla(by).reset_index().merge(nac_p.reset_index().rename(columns={"level_2": "AELEC", 0: "p0"}), on=["SEXO", "EDAD", "AELEC"])
    w = a.esp; mu = np.average(a.p, weights=w)
    sst = np.average((a.p - mu) ** 2, weights=w)
    r2_nac = 1 - np.average((a.p - a.p0) ** 2, weights=w) / sst
    off = a.assign(r=a.p - a.p0).groupby(by + ["AELEC"]).apply(lambda x: np.average(x.r, weights=x.esp), include_groups=False).rename("off").reset_index()
    a = a.merge(off, on=by + ["AELEC"]); r2_off = 1 - np.average((a.p - a.p0 - a.off) ** 2, weights=w) / sst
    print(f"{nombre}: R² con curva nacional {r2_nac:.3f}; sumando un nivel propio por grupo y elección {r2_off:.3f}")
# gráfica: curvas 2024 por región y por tipo (hombres y mujeres)
fig, axs = plt.subplots(2, 2, figsize=(12, 7.5), sharey=True)
for j, (corte, cols) in enumerate((("region", {"norte": PAL[0], "centro": PAL[3], "sur": PAL[1]}), ("tipo", {"urbana": PAL[0], "mixta": PAL[3], "rural": PAL[2]}))):
    for i, (sx, st) in enumerate(((0, "Hombres"), (1, "Mujeres"))):
        ax = axs[i, j]
        for g, c in cols.items():
            s = curvas[(corte, g)]; s = s.xs(sx, level="SEXO"); ax.plot(s.index, s.values, color=c, lw=2, label=g)
        ax.set_title(f"{st}, por {'región' if corte == 'region' else 'tipo de sección'} (2024)", fontsize=11); ax.legend(fontsize=8)
        if i == 1: ax.set_xlabel("Edad")
        if j == 0: ax.set_ylabel("Participación (%)")
guardar(fig, "perfiles_region_tipo_curvas_2024.png")
