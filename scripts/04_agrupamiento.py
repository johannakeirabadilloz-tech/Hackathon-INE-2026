"""Fase 3: ¿hay tipos naturales de entidad según su trayectoria de participación?
Se prueba con escepticismo: 4 definiciones de métrica, 2 métodos por distancia,
2 por densidad, k=2..6, retiro de entidades y elecciones, referencia por mediana
y un nulo gaussiano (misma media y covarianza, sin grupos)."""
import json, warnings, numpy as np, pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, HDBSCAN
from sklearn.metrics import silhouette_score, adjusted_rand_score as ARI
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from utils import *; from estilo import *
warnings.filterwarnings("ignore"); rng = np.random.default_rng(2026)
SEMILLA, KS, NNULO = 2026, [2, 3, 4, 5, 6], 300
ent = pd.read_csv(TABLAS/"eda_05_entidades_por_eleccion.csv")
nac = agg(cubo(), ["AELEC"]).set_index("AELEC").p_esp
V = {  # definiciones alternativas de la métrica
    "p_esp (sobre situación conocida)": ent.pivot(index="entidad", columns="AELEC", values="p_esp"),
    "p_ln (sobre lista nominal)":       ent.pivot(index="entidad", columns="AELEC", values="p_ln"),
    "estandarizada sexo×edad":          ent.pivot(index="entidad", columns="AELEC", values="est"),
}
V["desvío vs nacional (pts)"] = V["p_esp (sobre situación conocida)"].sub(nac, axis=1)
def z(X): return (X - X.mean())/X.std(ddof=0)
def ajusta(X, metodo, k):
    if metodo == "kmeans": return KMeans(k, n_init=20, random_state=SEMILLA).fit_predict(X)
    return AgglomerativeClustering(k, linkage="ward").fit_predict(X)
def ss_entre(X, lab):
    mu = X.mean(0); tot = ((X-mu)**2).sum(); 
    ent_ = sum(((X[lab==c].mean(0)-mu)**2).sum()*(lab==c).sum() for c in np.unique(lab)); return ent_/tot
Xs = {k: z(v).values for k, v in V.items()}; unidades = V["p_esp (sobre situación conocida)"].index
base = "p_esp (sobre situación conocida)"; X0 = Xs[base]

# ---- A. separación por método y k (con cautela: silhouette)
filas = []
for v, X in Xs.items():
    for m in ("kmeans", "ward"):
        for k in KS:
            l = ajusta(X, m, k); filas.append(dict(metrica=v, metodo=m, k=k, silhouette=silhouette_score(X, l), varianza_entre=ss_entre(X, l), tam_min=np.bincount(l).min()))
# densidad
dens = []
d_k = NearestNeighbors(n_neighbors=4).fit(X0).kneighbors(X0)[0][:, -1]
for eps in np.round(np.quantile(d_k, [.5, .75, .9, 1.0]), 2):
    l = DBSCAN(eps=eps, min_samples=3).fit_predict(X0)
    dens.append(dict(metodo="dbscan", parametro=f"eps={eps}, min=3", grupos=len(set(l))-(-1 in l), ruido=int((l==-1).sum())))
for mcs in (3, 4, 5):
    l = HDBSCAN(min_cluster_size=mcs).fit_predict(X0)
    dens.append(dict(metodo="hdbscan", parametro=f"min_cluster_size={mcs}", grupos=len(set(l))-(-1 in l), ruido=int((l==-1).sum())))
A = pd.DataFrame(filas); D = pd.DataFrame(dens)
A.round(3).to_csv(TABLAS/"agr_01_separacion.csv", index=False); D.to_csv(TABLAS/"agr_02_densidad.csv", index=False)

# ---- B. nulo gaussiano: mejor silhouette (kmeans, k=2..6) con misma cov, sin grupos
cov = np.cov(X0.T); mu = X0.mean(0)
def mejor_sil(X): return max(silhouette_score(X, KMeans(k, n_init=5, random_state=0).fit_predict(X)) for k in KS)
obs = mejor_sil(X0); nulo = np.array([mejor_sil(rng.multivariate_normal(mu, cov, len(X0))) for _ in range(NNULO)])
pnulo = float((nulo >= obs).mean())
pd.DataFrame({"silhouette_nulo": nulo}).to_csv(TABLAS/"agr_03_nulo.csv", index=False)

# ---- C. estabilidad: (i) cambio de métrica, (ii) retirar entidades, (iii) retirar elecciones
est = []
for m in ("kmeans", "ward"):
    for k in KS:
        ref = ajusta(X0, m, k)
        ari_met = [ARI(ref, ajusta(Xs[v], m, k)) for v in Xs if v != base]
        loo = []
        for i in range(len(X0)):
            keep = np.arange(len(X0)) != i
            Xi = z(V[base].iloc[keep]).values; loo.append(ARI(ref[keep], ajusta(Xi, m, k)))
        col = []
        for j in range(X0.shape[1]):
            cols = [c for c in range(X0.shape[1]) if c != j]; col.append(ARI(ref, ajusta(X0[:, cols], m, k)))
        # referencia simple: corte por mediana/terciles del nivel medio
        nivel = X0.mean(1); q = np.quantile(nivel, np.linspace(0, 1, k+1)[1:-1]); basel = np.digitize(nivel, q)
        est.append(dict(metodo=m, k=k, ari_cambio_metrica_min=min(ari_met), ari_cambio_metrica_media=np.mean(ari_met),
                        ari_sin_entidad_media=np.mean(loo), ari_sin_entidad_min=np.min(loo),
                        ari_sin_eleccion_media=np.mean(col), ari_sin_eleccion_min=np.min(col),
                        var_entre_agrupamiento=ss_entre(X0, ref), var_entre_corte_nivel=ss_entre(X0, basel),
                        ari_vs_corte_nivel=ARI(ref, basel)))
E = pd.DataFrame(est); E.round(3).to_csv(TABLAS/"agr_04_estabilidad.csv", index=False)

# ---- D. alternativa continua: PCA de la trayectoria
pca = PCA().fit(X0); sc = pca.transform(X0)
carg = pd.DataFrame(pca.components_[:2].T, index=V[base].columns, columns=["PC1", "PC2"])
carg.round(3).to_csv(TABLAS/"agr_05_pca_cargas.csv")
pd.DataFrame(sc[:, :2], index=unidades, columns=["PC1","PC2"]).assign(region_A=[mapa(REGIONES_A)[int(ent[ent.entidad==u].EDOCVE.iloc[0])] for u in unidades]).round(3).to_csv(TABLAS/"agr_06_pca_entidades.csv")
varexp = pca.explained_variance_ratio_.round(3).tolist()
# ¿la región A explica la posición? (η² sobre PC1)
reg = pd.Series([mapa(REGIONES_A)[int(ent[ent.entidad==u].EDOCVE.iloc[0])] for u in unidades], index=unidades)

# ---- E. repetir en municipios (más puntos; relevante para densidad)
g = cubo(); gm = g.groupby(["AELEC","EDOCVE","MPIOCVE"], observed=True)[["LN","SV","NV","NS"]].sum().reset_index()
gm["p"] = 100*gm.SV/(gm.SV+gm.NV)
ln_min = gm.groupby(["EDOCVE","MPIOCVE"]).LN.min(); ok = ln_min[ln_min >= 500].index  # SUPUESTO: LN>=500 en las 6 elecciones
P = gm.pivot_table(index=["EDOCVE","MPIOCVE"], columns="AELEC", values="p").loc[ok].dropna()
XM = z(P).values; mfil = []
for m in ("kmeans", "ward"):
    for k in KS:
        l = ajusta(XM, m, k) if m == "kmeans" else AgglomerativeClustering(k, linkage="ward").fit_predict(XM)
        nivel = XM.mean(1); q = np.quantile(nivel, np.linspace(0, 1, k+1)[1:-1])
        mfil.append(dict(metodo=m, k=k, silhouette=silhouette_score(XM, l, sample_size=1500, random_state=0), var_entre=ss_entre(XM, l), var_entre_corte_nivel=ss_entre(XM, np.digitize(nivel, q))))
dm = NearestNeighbors(n_neighbors=10).fit(XM).kneighbors(XM)[0][:, -1]
for mcs in (20, 50):
    l = HDBSCAN(min_cluster_size=mcs).fit_predict(XM)
    mfil.append(dict(metodo=f"hdbscan mcs={mcs}", k=len(set(l))-(-1 in l), silhouette=np.nan, var_entre=np.nan, var_entre_corte_nivel=np.nan, ruido_pct=100*(l==-1).mean()))
M = pd.DataFrame(mfil); M.round(3).to_csv(TABLAS/"agr_07_municipios.csv", index=False)
pca_m = PCA().fit(XM); varexp_m = pca_m.explained_variance_ratio_.round(3).tolist()

# ---- resumen para el informe
k_best = A[A.metrica == base].sort_values("silhouette", ascending=False).iloc[0]
R = dict(n_entidades=len(X0), n_municipios=len(XM), sil_obs_mejor=round(obs, 3), sil_nulo_p50=round(float(np.median(nulo)), 3), sil_nulo_p95=round(float(np.quantile(nulo, .95)), 3),
         p_nulo=round(pnulo, 3), mejor_config=dict(k_best[["metodo","k"]]) | {"silhouette": round(k_best.silhouette, 3)},
         varexp_pca=varexp[:3], varexp_pca_municipios=varexp_m[:3], cargas_pc1=carg.PC1.round(2).to_dict(), cargas_pc2=carg.PC2.round(2).to_dict())
json.dump(R, open(TABLAS/"hallazgos_agrupamiento.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps(R, indent=1, ensure_ascii=False, default=float)); print(A[A.metrica==base].round(3).to_string()); print(D.to_string()); print(E.round(2).to_string()); print(M.round(3).to_string())
for nombre, f in (("A", None),):
    pass
# guardar objetos para gráficas
np.save(TABLAS/"_nulo.npy", nulo)
