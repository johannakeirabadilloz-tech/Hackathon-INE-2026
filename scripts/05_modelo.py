"""Fase 4: regresión logística binomial sobre conteos (SV éxitos, NV fracasos).
Celdas: elección × entidad × tipo de sección × sexo × grupo de edad. Errores
robustos agrupados por entidad (32 grupos: pocos; interpretar con cautela)."""
import json, warnings, numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from utils import *
warnings.filterwarnings("ignore"); rng = np.random.default_rng(2026)
g = cubo()
c = g.groupby(["AELEC","EDOCVE","TIPOSEC","sexo","gedad"], observed=True)[["SV","NV"]].sum().reset_index()
c["n"] = c.SV+c.NV; c = c[c.n > 0].copy(); c["anio"] = c.AELEC.astype(str); c["ent"] = c.EDOCVE.astype(str); c["tipo"] = c.TIPOSEC
for k, v in (("anio","2021"),("sexo","Hombres"),("gedad","30-39"),("tipo","U")): pass
Y = "SV + NV ~ "     # no se usa; endog explícito abajo
def fit(rhs, d=c, robusto=True):
    m = smf.glm(f"I(SV/n) ~ {rhs}", d, family=sm.families.Binomial(), freq_weights=d.n) if False else None
    X = smf.glm(f"SV + NV ~ {rhs}", d, family=sm.families.Binomial())
    if robusto: return X.fit(cov_type="cluster", cov_kwds={"groups": d.ent.astype("category").cat.codes})
    return X.fit()
def d2(m): return 1 - m.deviance/m.null_deviance
# ---- 1. factores de uno en uno: solos, secuenciales, y aporte al final
F = {"elección": "C(anio)", "sexo": "C(sexo)", "edad": "C(gedad)", "tipo de sección": "C(tipo)", "entidad": "C(ent)"}
solo = {k: d2(fit(v, robusto=False)) for k, v in F.items()}
orden = ["elección", "edad", "sexo", "tipo de sección", "entidad"]; acum, prev, rows = [], 0, []
for i, k in enumerate(orden):
    m = fit(" + ".join(F[o] for o in orden[:i+1]), robusto=False); r = d2(m); rows.append((k, solo[k], r-prev, r)); prev = r
full = fit(" + ".join(F.values()), robusto=False)
T = pd.DataFrame(rows, columns=["factor","explica_solo","incremento_secuencial","acumulado"])
T["aporte_al_final"] = [d2(full) - d2(fit(" + ".join(F[o] for o in F if o != k), robusto=False)) for k in T.factor]
T.round(4).to_csv(TABLAS/"mod_01_factores.csv", index=False)
# ---- 2. interacciones (Wald robusto por bloque) sobre el modelo de efectos principales
base_rhs = " + ".join(F.values()); mb = fit(base_rhs); out = []
for nombre, term in {"sexo×edad": "C(sexo):C(gedad)", "elección×edad": "C(anio):C(gedad)", "elección×sexo": "C(anio):C(sexo)",
                     "elección×tipo": "C(anio):C(tipo)", "elección×entidad": "C(anio):C(ent)", "sexo×tipo": "C(sexo):C(tipo)", "edad×tipo": "C(gedad):C(tipo)"}.items():
    mi = fit(base_rhs + " + " + term); nuevos = [p for p in mi.params.index if p not in mb.params.index]
    nuevos = [p for p in nuevos if np.isfinite(mi.params[p]) and mi.bse[p] > 0]
    try: w = mi.wald_test(np.eye(len(mi.params))[[list(mi.params.index).index(p) for p in nuevos]], scalar=True); pv = float(w.pvalue)
    except Exception: pv = np.nan
    out.append(dict(interaccion=nombre, parametros=len(nuevos), ganancia_D2=d2(mi)-d2(mb), p_wald_robusto=pv))
I = pd.DataFrame(out); I.round(5).to_csv(TABLAS/"mod_02_interacciones.csv", index=False)
# ---- 3. modelo final y sobredispersión
final_rhs = base_rhs + " + C(sexo):C(gedad) + C(anio):C(gedad) + C(anio):C(sexo) + C(anio):C(tipo)"
mf = fit(final_rhs); mf_nr = fit(final_rhs, robusto=False)
disp = dict(pearson_chi2_sobre_gl_efectos_principales=float(full.pearson_chi2/full.df_resid), pearson_chi2_sobre_gl_final=float(mf_nr.pearson_chi2/mf_nr.df_resid),
            D2_efectos_principales=d2(full), D2_final=d2(mf), celdas=len(c), parametros_final=len(mf.params), n_entidades=c.ent.nunique())
# ---- 4. a puntos porcentuales: efectos marginales promedio (contrafactual, ponderado por n)
def pred(m, d): return m.predict(d)
def ame(m, d, var, lev, ref):
    a, b = d.copy(), d.copy(); a[var] = lev; b[var] = ref
    return 100*np.average(pred(m, a) - pred(m, b), weights=d.n)
def efectos(m, d):
    e = {}
    e["Mujeres vs Hombres"] = ame(m, d, "sexo", "Mujeres", "Hombres")
    for l in ETIQ_EDAD[:-1] + ["70+"]:
        if l != "30-39": e[f"Edad {l} vs 30-39"] = ame(m, d, "gedad", l, "30-39")
    for l in ("R", "M"): e[f"Sección {'rural' if l=='R' else 'mixta'} vs urbana"] = ame(m, d, "tipo", l, "U")
    for l in ("2009","2012","2015","2018","2021"): e[f"Elección 2024 vs {l}"] = ame(m, d.assign(anio=d.anio), "anio", "2024", l)
    # brecha por edad (viene de la interacción)
    for l in ETIQ_EDAD:
        s = d[d.gedad == l]; 
        e[f"Brecha M−H en edad {l}"] = ame(m, s, "sexo", "Mujeres", "Hombres")
    for l in ETIQ_EDAD:
        e[f"Brecha M−H 2024 en edad {l}"] = ame(m, d[(d.gedad == l) & (d.anio == "2024")], "sexo", "Mujeres", "Hombres")
    for y in ("2015", "2024"):
        e[f"Rural vs urbana, elección {y}"] = ame(m, d[d.anio == y], "tipo", "R", "U")
    return e
E0 = efectos(mf, c)
# bootstrap por entidades (remuestrea entidades completas) para IC
B = 150; boots = []
ents = c.ent.unique()
for b in range(B):
    s = rng.choice(ents, len(ents)); d = pd.concat([c[c.ent == e].assign(ent=f"{e}_{i}") for i, e in enumerate(s)], ignore_index=True)
    try:
        mb_ = smf.glm(f"SV + NV ~ {final_rhs}", d, family=sm.families.Binomial()).fit(); boots.append(efectos(mb_, d))
    except Exception: continue
Bt = pd.DataFrame(boots)
A = pd.DataFrame({"efecto_pp": pd.Series(E0), "ic95_inf": Bt.quantile(.025), "ic95_sup": Bt.quantile(.975)}); A["replicas_validas"] = len(Bt)
A.round(2).to_csv(TABLAS/"mod_03_efectos_pp.csv"); 
# ---- 5. contraste con la descripción
desc = pd.read_csv(TABLAS/"eda_03_brecha_sexo_por_edad.csv", index_col=0)[ "2024"]
comp = pd.DataFrame({"modelo": [E0[f"Brecha M−H 2024 en edad {l}"] for l in ETIQ_EDAD], "descriptiva": desc.reindex(ETIQ_EDAD).values}, index=ETIQ_EDAD).round(2); comp.to_csv(TABLAS/"mod_04_modelo_vs_descriptiva_brecha_2024.csv")
json.dump(dict(disp=disp, efectos=A.round(2).to_dict("index")), open(TABLAS/"hallazgos_modelo.json", "w"), indent=1, ensure_ascii=False, default=float)
print(T.round(4).to_string()); print(I.round(5).to_string()); print(json.dumps(disp, indent=1)); print(A.round(2).to_string()); print(comp)
