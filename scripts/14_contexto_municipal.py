"""¿Se asocian las brechas municipales con variables de contexto derivadas del propio padrón (INE)?
Variables: número y tamaño de secciones, % de lista nominal en sección urbana/rural, estructura de edad y sexo, % no especificado.
Asociación entre municipios, no causa."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS
from estilo import guardar, PAL
ANIOS_Y = [2021, 2024]

filas = []
for y in ANIOS_Y:
    d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", filters=[("AELEC", "==", y)],
                        columns=["EDOCVE", "MPIOCVE", "SECCION", "TIPOSEC", "SEXO", "EDAD", "LN", "NS"])
    d = d[(d.EDAD >= 18) & (d.SEXO != 2)]
    k = ["EDOCVE", "MPIOCVE"]
    t = d.groupby(k).agg(LN=("LN", "sum"), NS=("NS", "sum"), secciones=("SECCION", "nunique")).reset_index()
    for nm, cond in (("urbana", d.TIPOSEC == "U"), ("rural", d.TIPOSEC == "R"), ("jov18_29", d.EDAD < 30), ("mayor65", d.EDAD >= 65),
                     ("mayor85", d.EDAD >= 85), ("mujer", d.SEXO == 1)):
        t = t.merge(d[cond].groupby(k).LN.sum().rename(f"ln_{nm}").reset_index(), on=k, how="left")
    t = t.fillna(0)
    out = pd.DataFrame({"AELEC": y, "EDOCVE": t.EDOCVE, "MPIOCVE": t.MPIOCVE,
        "log_tamano": np.log10(t.LN), "ln_por_seccion": t.LN / t.secciones,
        "urbana_pct": 100 * t.ln_urbana / t.LN, "rural_pct": 100 * t.ln_rural / t.LN,
        "jov18_29_pct": 100 * t.ln_jov18_29 / t.LN, "mayor65_pct": 100 * t.ln_mayor65 / t.LN,
        "mayor85_pct": 100 * t.ln_mayor85 / t.LN, "mujer_pct": 100 * t.ln_mujer / t.LN, "ns_pct": 100 * t.NS / t.LN})
    filas.append(out); del d
C = pd.concat(filas)
b = pd.read_csv(TABLAS / "territorial_municipio_brechas.csv")
VARS = [c for c in C.columns if c not in ("AELEC", "EDOCVE", "MPIOCVE")]
res = []
for y in ANIOS_Y:
    t = b[b.AELEC == y].merge(C[C.AELEC == y], on=["AELEC", "EDOCVE", "MPIOCVE"]).dropna(subset=VARS)
    X = (t[VARS] - t[VARS].mean()) / t[VARS].std()
    for brecha in ("brecha_joven", "brecha_85"):
        yv = t[brecha].values
        for nombre, M in (("sin_entidad", X.values), ("con_entidad", np.column_stack([X.values, pd.get_dummies(t.EDOCVE, dtype=float).values]))):
            A = np.column_stack([np.ones(len(t)), M]); beta, *_ = np.linalg.lstsq(A, yv, rcond=None)
            r = yv - A @ beta; r2 = 1 - r.var() / yv.var()
            br = np.linalg.pinv(A.T @ A)
            meat = sum(np.outer(A[i].T @ r[i], A[i].T @ r[i]) for i in [np.where(t.EDOCVE.values == e)[0] for e in t.EDOCVE.unique()])
            se = np.sqrt(np.diag(br @ meat @ br))
            for j, v in enumerate(VARS):
                res.append(dict(anio=y, brecha=brecha, modelo=nombre, variable=v, coef_pts_por_1sd=beta[j + 1], se_cluster=se[j + 1],
                                t=beta[j + 1] / se[j + 1], r2=r2, n=len(t)))
R = pd.DataFrame(res).round(3); R.to_csv(TABLAS / "contexto_municipal_regresion.csv", index=False)
for y in ANIOS_Y:
    for br in ("brecha_joven", "brecha_85"):
        q = R[(R.anio == y) & (R.brecha == br)]
        print(y, br, "n", q.n.iloc[0], "R2 sin/con entidad:", q[q.modelo == "sin_entidad"].r2.iloc[0], q[q.modelo == "con_entidad"].r2.iloc[0])
        print(q[q.modelo == "sin_entidad"].set_index("variable")[["coef_pts_por_1sd", "t"]].join(
            q[q.modelo == "con_entidad"].set_index("variable")[["coef_pts_por_1sd", "t"]], rsuffix="_ef").to_string())
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
for a, br, tt, c in zip(ax, ("brecha_joven", "brecha_85"), ("Brecha de jóvenes", "Brecha de 85+"), (PAL[0], PAL[3])):
    q = R[(R.anio == 2024) & (R.brecha == br) & (R.modelo == "con_entidad")].set_index("variable")
    a.barh(q.index, q.coef_pts_por_1sd, xerr=1.96 * q.se_cluster, color=c); a.axvline(0, color="k", lw=.5)
    a.set_title(tt + " 2024", fontsize=11); a.set_xlabel("Puntos por desviación estándar (con entidad; IC 95%)")
guardar(fig, "contexto_municipal_coeficientes.png")
