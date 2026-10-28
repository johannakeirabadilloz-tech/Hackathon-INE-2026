"""Boosting + SHAP con edad simple (18-99) a nivel entidad × tipo de sección × sexo × edad.
Permite ver a 85+ por separado. Prueba temporal: entrenar 2009-2021, predecir 2024. Solo datos del INE."""
import json, warnings
import numpy as np, pandas as pd, lightgbm as lgb, shap
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS
from estilo import guardar, PAL
warnings.filterwarnings("ignore")
SEED, TOPE = 42, 99      # SUPUESTO: edades >= 100 se excluyen (ver calidad abajo)

d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet",
                    columns=["AELEC", "EDOCVE", "TIPOSEC", "SEXO", "EDAD", "LN", "SV", "NV"])
d = d[(d.SEXO != 2) & (d.EDAD >= 18)]
cal = d.assign(c100=d.EDAD >= 100).groupby(["AELEC", "c100"]).LN.sum().unstack()
cal["pct_ln_100mas"] = (100 * cal[True] / (cal[True] + cal[False])).round(3)
cal[["pct_ln_100mas"]].to_csv(TABLAS / "boosting_edad_calidad_100mas.csv")
print(cal[["pct_ln_100mas"]].T)
d = d[d.EDAD <= TOPE]
g = d.groupby(["AELEC", "EDOCVE", "TIPOSEC", "SEXO", "EDAD"], observed=True)[["SV", "NV"]].sum().reset_index()
del d
g["esp"] = g.SV + g.NV
g = g[g.esp > 0].copy()
g["y"] = 100 * g.SV / g.esp
g["edad"] = g.EDAD.astype(int); g["mujer"] = g.SEXO.astype(int)
g["tipo"] = g.TIPOSEC.map({"U": 0, "M": 1, "R": 2})
g["pres"] = g.AELEC.isin([2012, 2018, 2024]).astype(int)
g["entidad"] = g.EDOCVE.astype("category")
F = ["entidad", "edad", "mujer", "tipo", "pres"]
te = g[g.AELEC == 2024]; trv = g[g.AELEC <= 2021]
va = trv.sample(frac=0.1, random_state=SEED); tr = trv.drop(va.index)
P = dict(objective="regression", learning_rate=0.05, num_leaves=31, min_child_samples=30, subsample=0.8,
         subsample_freq=1, colsample_bytree=0.9, reg_lambda=5, cat_smooth=20, random_state=SEED, n_jobs=8, verbose=-1)
m = lgb.LGBMRegressor(n_estimators=3000, **P).fit(tr[F], tr.y, sample_weight=tr.esp, eval_set=[(va[F], va.y)],
        eval_sample_weight=[va.esp], callbacks=[lgb.early_stopping(80, verbose=False)])
k = m.best_iteration_
m = lgb.LGBMRegressor(n_estimators=k, **P).fit(trv[F], trv.y, sample_weight=trv.esp)

def metr(y, p, w):
    mu = np.average(y, weights=w)
    return dict(r2_pond=round(1 - np.average((y - p) ** 2, weights=w) / np.average((y - mu) ** 2, weights=w), 3),
                mae_pts_pond=round(np.average(np.abs(y - p), weights=w), 2))
kk = ["EDOCVE", "TIPOSEC", "SEXO", "EDAD", "pres"]
tabla = trv.groupby(kk, observed=True).apply(lambda x: np.average(x.y, weights=x.esp), include_groups=False).rename("p")
b_tab = te.join(tabla, on=kk).p
b_tab = b_tab.fillna(trv.y.mean())
ant = g[g.AELEC == 2018].set_index(["EDOCVE", "TIPOSEC", "SEXO", "EDAD"]).y
b_ant = pd.Series(te.set_index(["EDOCVE", "TIPOSEC", "SEXO", "EDAD"]).index.map(ant), index=te.index).fillna(b_tab)
te = te.assign(pred=m.predict(te[F]))
res = {"lgbm": {**metr(te.y, te.pred, te.esp), "arboles": int(k)},
       "ref_tabla_medias_con_edad_simple": metr(te.y, b_tab, te.esp),
       "ref_misma_celda_2018": metr(te.y, b_ant, te.esp),
       "n": dict(entrenamiento=len(trv), prueba_2024=len(te))}
# error por tramo de edad
te["tramo"] = pd.cut(te.edad, [17, 34, 64, 84, 99], labels=["18-34", "35-64", "65-84", "85-99"])
res["mae_pts_por_tramo"] = te.groupby("tramo", observed=True).apply(
    lambda x: round(np.average(np.abs(x.y - x.pred), weights=x.esp), 2), include_groups=False).to_dict()
json.dump(res, open(TABLAS / "boosting_edad_metricas.json", "w"), indent=1, default=float); print(json.dumps(res, indent=1, default=float))

# SHAP en 2021 (intermedia) y 2024 (presidencial); contribución conjunta edad + sexo + interacción
ex = g[g.AELEC.isin([2021, 2024])].reset_index(drop=True)
expl = shap.TreeExplainer(m)
iv = expl.shap_interaction_values(ex[F])
ie, im = F.index("edad"), F.index("mujer")
ex["c_edad_sexo"] = iv[:, ie, ie] + iv[:, im, im] + 2 * iv[:, ie, im]
ex["c_edad"] = iv[:, ie, ie] + iv[:, ie, im] + iv[:, ie, F.index("pres")] + iv[:, ie, F.index("tipo")] + iv[:, ie, F.index("entidad")]
imp = pd.Series(np.abs(iv.sum(2)).mean(0), index=F).sort_values(ascending=False)
imp.round(2).rename("shap_abs_media_pts").to_csv(TABLAS / "boosting_edad_importancia.csv"); print(imp.round(2))
curva = ex.groupby(["AELEC", "mujer", "edad"]).apply(lambda x: pd.Series({
    "participacion_obs": np.average(x.y, weights=x.esp), "shap_edad": np.average(x.c_edad, weights=x.esp),
    "shap_edad_sexo": np.average(x.c_edad_sexo, weights=x.esp)}), include_groups=False).reset_index()
curva.round(2).to_csv(TABLAS / "boosting_edad_curvas.csv", index=False)
tr85 = te.assign(g85=np.where(te.edad >= 85, "85-99", np.where(te.edad >= 65, "65-84", "18-64"))).groupby(["mujer", "g85"]).apply(
    lambda x: pd.Series({"obs": np.average(x.y, weights=x.esp), "pred": np.average(x.pred, weights=x.esp)}), include_groups=False)
print(tr85.round(1))

# --- gráficas
SX = {0: ("Hombres", PAL[0]), 1: ("Mujeres", PAL[1])}
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
for a, y, t in zip(ax, (2021, 2024), ("2021 (intermedia)", "2024 (presidencial)")):
    for s, (n, c) in SX.items():
        q = curva[(curva.AELEC == y) & (curva.mujer == s)]
        a.plot(q.edad, q.participacion_obs, color=c, label=n, lw=2)
    a.axvspan(85, 99, color="#999", alpha=.15); a.set_title(f"Participación por edad, {t}", fontsize=11); a.set_xlabel("Edad")
ax[0].set_ylabel("Participación entre especificados (%)"); ax[0].legend()
guardar(fig, "boosting_edad_participacion_observada.png")

fig, ax = plt.subplots(figsize=(8, 4.4))
for s_, (n, c) in SX.items():
    q = curva[(curva.AELEC == 2024) & (curva.mujer == s_)]
    ax.plot(q.edad, q.shap_edad_sexo, color=c, label=n, lw=2)
ax.axhline(0, color="k", lw=.6); ax.axvspan(85, 99, color="#999", alpha=.15)
ax.set_title("Contribución de edad y sexo a la predicción (SHAP, 2024)"); ax.set_xlabel("Edad")
ax.set_ylabel("Puntos vs. promedio del modelo"); ax.legend()
guardar(fig, "boosting_edad_shap_sexo.png")

fig, ax = plt.subplots(figsize=(8, 4.4))
q = te.groupby("edad").apply(lambda x: pd.Series({"obs": np.average(x.y, weights=x.esp), "pred": np.average(x.pred, weights=x.esp)}), include_groups=False)
ax.plot(q.index, q.obs, color=PAL[0], lw=2, label="Observada 2024"); ax.plot(q.index, q.pred, color=PAL[3], lw=2, ls="--", label="Predicha (entrenado hasta 2021)")
ax.axvspan(85, 99, color="#999", alpha=.15); ax.set_xlabel("Edad"); ax.set_ylabel("Participación (%)"); ax.legend()
ax.set_title("Predicción 2024 frente a lo observado, por edad")
guardar(fig, "boosting_edad_prediccion_vs_observado.png")

fig, ax = plt.subplots(figsize=(8, 4.4))
dl = curva[curva.AELEC == 2024].groupby("edad").apply(lambda x: np.average(x.participacion_obs), include_groups=False)
dd = (curva[(curva.AELEC == 2024)].pivot(index="edad", columns="mujer", values="participacion_obs"))
ax.plot(dd.index, dd[1] - dd[0], color=PAL[4], lw=2); ax.axhline(0, color="k", lw=.6); ax.axvspan(85, 99, color="#999", alpha=.15)
ax.set_xlabel("Edad"); ax.set_ylabel("Mujeres menos hombres (puntos)"); ax.set_title("Brecha de participación por sexo y edad, 2024")
guardar(fig, "boosting_edad_brecha_sexo.png")
dd.assign(brecha_m_menos_h=dd[1] - dd[0]).round(2).rename(columns={0: "hombres", 1: "mujeres"}).to_csv(TABLAS / "boosting_edad_brecha_sexo_2024.csv")
print(dd.assign(b=dd[1] - dd[0]).loc[[18, 25, 35, 50, 65, 75, 84, 85, 90, 95, 99]].round(1))
