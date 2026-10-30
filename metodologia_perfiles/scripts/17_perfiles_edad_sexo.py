"""Perfiles por sexo × edad simple (18-99) según su trayectoria de participación en las seis elecciones.
Nacional; datos del INE. Exploratorio: compara k=2..6 y su estabilidad."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from config import PROC, TABLAS, GRAFICAS, ANIOS
from estilo import guardar, PAL
SEED = 42
d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", columns=["AELEC", "SEXO", "EDAD", "SV", "NV"])
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)]
a = d.groupby(["SEXO", "EDAD", "AELEC"])[["SV", "NV"]].sum(); del d
a["esp"] = a.SV + a.NV; a["p"] = 100 * a.SV / a.esp
P = a.p.unstack("AELEC")[ANIOS]; N = a.esp.unstack("AELEC")[ANIOS]
P = P.dropna(); N = N.loc[P.index]
Z = StandardScaler().fit_transform(P.values)
rng = np.random.default_rng(SEED); filas = []
for k in range(2, 7):
    for nom, mk in (("kmeans", lambda k: KMeans(k, n_init=30, random_state=SEED)), ("ward", lambda k: AgglomerativeClustering(k))):
        lab = mk(k).fit_predict(Z); sil = silhouette_score(Z, lab)
        aris = []
        for _ in range(20):
            s = rng.choice(len(Z), int(.8 * len(Z)), replace=False)
            l2 = mk(k).fit_predict(Z[s]); aris.append(adjusted_rand_score(lab[s], l2))
        filas.append(dict(k=k, algoritmo=nom, silhouette=sil, tamano_min_pct=100 * np.bincount(lab).min() / len(lab), ari_medio=np.mean(aris), ari_min=np.min(aris)))
S = pd.DataFrame(filas).round(3); S.to_csv(TABLAS / "perfiles_edad_sexo_comparacion.csv", index=False); print(S.to_string(index=False))
for K in (2, 3, 4, 5):
    lab = KMeans(K, n_init=50, random_state=SEED).fit_predict(Z)
    T = P.copy(); T["perfil"] = lab
    w = N.mul(P).div(100)   # votos aproximados para ponderar
    print(f"\n=== k={K} ===")
    res = []
    for c in range(K):
        m = T.perfil == c; idx = T.index[m]
        edad = idx.get_level_values("EDAD"); sexo = idx.get_level_values("SEXO")
        part = (w[m].sum() / (N[m].sum()) * 100).round(1)
        res.append(dict(perfil=c, segmentos=int(m.sum()), edades=f"{edad.min()}-{edad.max()}", pct_mujeres=round(100 * (sexo == 1).mean()), **{str(y): part[y] for y in ANIOS}))
    R = pd.DataFrame(res).sort_values("2024"); print(R.to_string(index=False))
    # detalle por sexo: rangos de edad
    for c in R.perfil:
        idx = T.index[T.perfil == c]
        s = {sx: sorted(idx[idx.get_level_values("SEXO") == sx].get_level_values("EDAD")) for sx in (0, 1)}
        rg = lambda l: "-" if not l else ", ".join(f"{x[0]}-{x[-1]}" for x in np.split(np.array(l), np.where(np.diff(l) > 1)[0] + 1))
        print(f"  perfil {c}: hombres {rg(s[0])} | mujeres {rg(s[1])}")
    if K == 4: lab4, R4 = lab, R
# gráfica k=4: curvas por edad coloreadas por perfil, por sexo
K = 4; T = P.copy(); T["perfil"] = lab4
orden = {c: i for i, c in enumerate(R4.perfil)}; cols = [PAL[0], PAL[2], PAL[3], PAL[1]]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
for a_, sx, tt in zip(ax, (0, 1), ("Hombres", "Mujeres")):
    q = T.xs(sx, level="SEXO")
    for c in range(K): 
        s = q[q.perfil == c]; a_.scatter(s.index, s[2024], s=22, color=cols[orden[c]], label=f"Perfil {orden[c]+1}")
    a_.set_title(f"{tt}: participación 2024 por edad"); a_.set_xlabel("Edad")
ax[0].set_ylabel("Participación (%)"); ax[0].legend(fontsize=8)
guardar(fig, "perfiles_edad_sexo_k4.png")
T.to_csv(TABLAS / "perfiles_edad_sexo_k4_asignacion.csv")
