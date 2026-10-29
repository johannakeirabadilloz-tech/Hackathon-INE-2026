"""Boosting (LightGBM) + SHAP sobre el cubo municipal del INE. Prueba temporal: entrenar 2009-2021, predecir 2024.
Solo variables del propio INE. SHAP explica al modelo, no causas."""
import json, warnings
import numpy as np, pandas as pd, lightgbm as lgb, shap
import matplotlib.pyplot as plt
from utils import cubo
from config import TABLAS, GRAFICAS
from estilo import guardar, PAL, PRES
warnings.filterwarnings("ignore")
SEED = 42
EDADES = ["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"]

g = cubo()
g["esp"] = g.SV + g.NV
g = g[g.esp > 0].copy()
g["y"] = 100 * g.SV / g.esp
g["edad"] = g.gedad.map({e: i for i, e in enumerate(EDADES)})
g["mujer"] = (g.sexo == "Mujeres").astype(int)
g["tipo"] = g.TIPOSEC.map({"U": 0, "M": 1, "R": 2})        # urbana, mixta, rural
g["pres"] = g.AELEC.isin([2012, 2018, 2024]).astype(int)
g["log_esp"] = np.log10(g.esp)
g["entidad"] = g.EDOCVE.astype("category")
g["mpio"] = (g.EDOCVE.astype("int32") * 1000 + g.MPIOCVE.astype("int32")).astype("category")
F0 = ["entidad", "edad", "mujer", "tipo", "pres"]
F1 = F0 + ["mpio"]

te = g[g.AELEC == 2024]
trv = g[g.AELEC <= 2021]
# SUPUESTO: el número de árboles se elige con 10% de celdas al azar de 2009-2021 (no con un año completo,
# porque el nivel de participación cambia por tipo de elección y detendría el modelo demasiado pronto)
va = trv.sample(frac=0.1, random_state=SEED); tr = trv.drop(va.index)
P = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_child_samples=50,
         subsample=0.8, subsample_freq=1, colsample_bytree=0.9, reg_lambda=5, cat_smooth=20,
         random_state=SEED, n_jobs=8, verbose=-1)

def ajusta(feats):
    m = lgb.LGBMRegressor(n_estimators=2000, **P)
    m.fit(tr[feats], tr.y, sample_weight=tr.esp, eval_set=[(va[feats], va.y)], eval_sample_weight=[va.esp],
          callbacks=[lgb.early_stopping(50, verbose=False)])
    k = m.best_iteration_
    f = lgb.LGBMRegressor(n_estimators=k, **P).fit(trv[feats], trv.y, sample_weight=trv.esp)
    return f, k

def metr(y, p, w):
    mu = np.average(y, weights=w)
    return dict(r2_pond=1 - np.average((y - p) ** 2, weights=w) / np.average((y - mu) ** 2, weights=w),
                mae_pts_pond=np.average(np.abs(y - p), weights=w), mae_pts_simple=np.abs(y - p).mean())

res = {}
# Referencias simples
k = ["EDOCVE", "edad", "mujer", "tipo", "pres"]
tabla = trv.groupby(k, observed=True).apply(lambda d: np.average(d.y, weights=d.esp), include_groups=False).rename("p")
b1 = te.join(tabla, on=k).p.fillna(trv.y.mean())
res["ref_tabla_media_entidad_edad_sexo_tipo_pres"] = metr(te.y, b1, te.esp)
ant = g[g.AELEC == 2018].set_index(["EDOCVE", "MPIOCVE", "TIPOSEC", "SEXO", "gedad"]).y
b2 = te.set_index(["EDOCVE", "MPIOCVE", "TIPOSEC", "SEXO", "gedad"]).index.map(ant)
b2 = pd.Series(b2, index=te.index).fillna(b1)
res["ref_misma_celda_2018"] = metr(te.y, b2, te.esp)

m0, k0 = ajusta(F0); res["lgbm_sin_municipio"] = {**metr(te.y, m0.predict(te[F0]), te.esp), "arboles": k0}
m1, k1 = ajusta(F1); res["lgbm_con_municipio"] = {**metr(te.y, m1.predict(te[F1]), te.esp), "arboles": k1}
res["n_celdas"] = dict(entrenamiento=len(trv), prueba_2024=len(te))
json.dump(res, open(TABLAS / "boosting_metricas.json", "w"), indent=1)
print(json.dumps(res, indent=1))

# ---- SHAP del modelo sin municipio (interpretable), muestra de prueba 2024 ponderada por tamaño
ex = te.sample(20000, weights=te.esp, replace=True, random_state=SEED)
expl = shap.TreeExplainer(m0)
sv = expl.shap_values(ex[F0])
etq = {"entidad": "Entidad", "edad": "Grupo de edad", "mujer": "Sexo (mujer)", "tipo": "Tipo de sección",
       "pres": "Elección presidencial"}
imp = pd.DataFrame({"variable": F0, "shap_abs_media_pts": np.abs(sv).mean(0)}).sort_values("shap_abs_media_pts", ascending=False)
imp.round(3).to_csv(TABLAS / "boosting_shap_importancia.csv", index=False)
print(imp.round(2).to_string(index=False))

S = pd.DataFrame(sv, columns=F0, index=ex.index)
ed = pd.DataFrame({"gedad": ex.gedad, "pres": ex.pres, "shap_edad": S.edad})
ed.groupby("gedad").shap_edad.mean().round(2).to_csv(TABLAS / "boosting_shap_edad.csv")
S["gedad"] = ex.gedad; S["tipo_n"] = ex.tipo; S["ent"] = ex.EDOCVE
S.groupby("ent").entidad.mean().round(2).to_csv(TABLAS / "boosting_shap_entidad.csv")

# interacciones (muestra menor)
ei = ex.drop_duplicates().sample(4000, random_state=SEED)
iv = expl.shap_interaction_values(ei[F0])
M = pd.DataFrame(np.abs(iv).mean(0), index=F0, columns=F0)
M.round(3).to_csv(TABLAS / "boosting_shap_interacciones.csv")

# gráficas
fig, ax = plt.subplots(figsize=(7, 3.8))
imp2 = imp.iloc[::-1]
ax.barh([etq[v] for v in imp2.variable], imp2.shap_abs_media_pts, color=PAL[0])
ax.set_xlabel("|SHAP| medio (puntos porcentuales)"); ax.set_title("Qué usa el modelo para predecir la participación")
guardar(fig, "boosting_shap_importancia.png")

fig, ax = plt.subplots(figsize=(8, 4.2))
for pres, c, n in ((0, PAL[0], "Intermedia"), (1, PAL[1], "Presidencial")):
    d = ed[ed.pres == pres].groupby("gedad").shap_edad.mean().reindex(EDADES)
    ax.plot(EDADES, d.values, marker="o", color=c, label=n)
ax.axhline(0, color="k", lw=.6); ax.legend(); ax.set_ylabel("Contribución de la edad (pts)")
ax.set_title("Efecto de la edad sobre la participación según tipo de elección (SHAP)")
guardar(fig, "boosting_shap_edad_por_eleccion.png")

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(M.values, cmap="Blues"); ax.set_xticks(range(len(F0))); ax.set_yticks(range(len(F0)))
ax.set_xticklabels([etq[v] for v in F0], rotation=45, ha="right"); ax.set_yticklabels([etq[v] for v in F0])
ax.grid(False); ax.set_title("Interacciones SHAP (|media|, pts)"); fig.colorbar(im)
guardar(fig, "boosting_shap_interacciones.png")

# efecto de edad por tipo de sección: contribución conjunta edad + interacción
J = pd.DataFrame({"gedad": ei.gedad, "tipo": ei.tipo, "j": iv[:, F0.index("edad"), F0.index("tipo")] * 2})
J.groupby(["gedad", "tipo"]).j.mean().unstack().rename(columns={0: "urbana", 1: "mixta", 2: "rural"}).reindex(EDADES).round(2)\
    .to_csv(TABLAS / "boosting_shap_edad_x_tipo.csv")
print(M.round(2).to_string()); print(pd.read_csv(TABLAS / "boosting_shap_edad_x_tipo.csv", index_col=0))
print(pd.read_csv(TABLAS / "boosting_shap_edad.csv"))

# contribución conjunta edad + sexo + su interacción, por grupo de edad (pts respecto del promedio)
ie, im = F0.index("edad"), F0.index("mujer")
C = pd.DataFrame({"gedad": ei.gedad, "mujer": ei.mujer,
                  "c": iv[:, ie, ie] + iv[:, im, im] + 2 * iv[:, ie, im]})
C.groupby(["gedad", "mujer"]).c.mean().unstack().rename(columns={0: "hombres", 1: "mujeres"}).reindex(EDADES).round(2)\
    .to_csv(TABLAS / "boosting_shap_edad_x_sexo.csv")
print(pd.read_csv(TABLAS / "boosting_shap_edad_x_sexo.csv", index_col=0))

# gráficas de las interacciones edad × sexo y edad × tipo de sección
fig, ax = plt.subplots(figsize=(8, 4.2))
q = pd.read_csv(TABLAS / "boosting_shap_edad_x_sexo.csv", index_col=0)
x = np.arange(len(q)); w = .38
ax.bar(x - w / 2, q.hombres, w, color=PAL[0], label="Hombres"); ax.bar(x + w / 2, q.mujeres, w, color=PAL[1], label="Mujeres")
ax.set_xticks(x); ax.set_xticklabels(q.index); ax.axhline(0, color="k", lw=.6); ax.legend()
ax.set_ylabel("Contribución (pts)"); ax.set_title("Edad y sexo: contribución conjunta a la participación (SHAP, 2024)")
guardar(fig, "boosting_shap_edad_x_sexo.png")

fig, ax = plt.subplots(figsize=(8, 4.2))
q = pd.read_csv(TABLAS / "boosting_shap_edad_x_tipo.csv", index_col=0)
for col, c in zip(q.columns, (PAL[0], PAL[3], PAL[2])):
    ax.plot(q.index, q[col], marker="o", color=c, label=col)
ax.axhline(0, color="k", lw=.6); ax.legend(); ax.set_ylabel("Interacción (pts)")
ax.set_title("Edad × tipo de sección: efecto adicional sobre la participación (SHAP)")
guardar(fig, "boosting_shap_edad_x_tipo.png")
