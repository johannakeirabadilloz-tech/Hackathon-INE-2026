"""Fase 2: descripción. Estandarización directa con pesos = distribución de la
lista nominal agregada (todas las elecciones, entidades) por estrato (supuesto)."""
import json, numpy as np, pandas as pd
from utils import *; from estilo import *
g = cubo(); H = {}
ANIOS_ = ANIOS
# ---------- 1. tiempo y denominadores
t = agg(g, ["AELEC"]); t["tipo"] = t.AELEC.map(PRES)
t.round(3).to_csv(TABLAS/"eda_01_nacional_por_eleccion.csv", index=False)
H["nacional"] = t.set_index("AELEC")[["p_esp","p_ln","p_ns"]].round(2).to_dict("index")
fig, ax = plt.subplots(figsize=(8, 4.3))
ax.plot(t.AELEC, t.p_esp, "o-", lw=2.2, color=PAL[0]); ax.plot(t.AELEC, t.p_ln, "s--", lw=1.8, color=PAL[3])
for _, r in t.iterrows():
    ax.annotate(f"{r.p_esp:.1f}", (r.AELEC, r.p_esp), (0, 8), textcoords="offset points", ha="center", color=PAL[0], fontsize=9.5)
    ax.annotate(f"{r.p_ln:.1f}", (r.AELEC, r.p_ln), (0, -15), textcoords="offset points", ha="center", color=PAL[3], fontsize=9.5)
ax.text(2024.3, t.p_esp.iloc[-1], "sobre registros\ncon situación\nconocida", color=PAL[0], va="center", fontsize=9)
ax.text(2024.3, t.p_ln.iloc[-1]-1.5, "sobre toda la\nlista nominal", color=PAL[3], va="center", fontsize=9)
ax.set_xlim(2008, 2027.3); ax.set_xticks(ANIOS_); ax.set_ylabel("% de participación"); ax.set_ylim(38, 68)
ax.set_title(f"La participación sube en las elecciones presidenciales (2012, 2018, 2024) y cae en las intermedias")
guardar(fig, "01_participacion_nacional.png")

# ---------- pesos de estandarización
w_edad = g.groupby("gedad")["LN"].sum(); w_edad = w_edad/w_edad.sum()
w_es = g.groupby(["sexo","gedad"])["LN"].sum(); w_es = w_es/w_es.sum()
w_es24 = g[g.AELEC==2024].groupby(["sexo","gedad"])["LN"].sum(); w_es24 = w_es24/w_es24.sum()
w_ess = g.groupby(["sexo","gedad","TIPOSEC"])["LN"].sum(); w_ess = w_ess/w_ess.sum()

# ---------- 2. sexo: cruda vs estandarizada por edad
c = agg(g, ["AELEC","sexo"]).pivot(index="AELEC", columns="sexo", values="p_esp")
e = estandarizada(g, ["AELEC","sexo"], ["gedad"], w_edad).pivot(index="AELEC", columns="sexo", values="est")
s = pd.DataFrame({"cruda_H": c.Hombres, "cruda_M": c.Mujeres, "brecha_cruda": c.Mujeres-c.Hombres,
                  "est_H": e.Hombres, "est_M": e.Mujeres, "brecha_est_edad": e.Mujeres-e.Hombres})
s.round(3).to_csv(TABLAS/"eda_02_sexo_cruda_vs_estandarizada.csv"); H["sexo"] = s.round(2).to_dict("index")
fig, ax = plt.subplots(figsize=(8, 4.2)); x = np.arange(6); w = .38
b1 = ax.bar(x-w/2, s.brecha_cruda, w, color=PAL[5], label="Diferencia observada")
b2 = ax.bar(x+w/2, s.brecha_est_edad, w, color=PAL[1], label="Diferencia con la misma estructura de edad")
for bs in (b1, b2):
    for b in bs: ax.annotate(f"{b.get_height():.1f}", (b.get_x()+b.get_width()/2, b.get_height()), (0, 3), textcoords="offset points", ha="center", fontsize=9)
ax.set_xticks(x, ANIOS_); ax.set_ylabel("puntos porcentuales (mujeres − hombres)"); ax.set_ylim(0, 11)
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.12), ncol=2, frameon=False, fontsize=9.5)
ax.set_title(f"Las mujeres votan más que los hombres en todas las elecciones: {s.brecha_est_edad.min():.1f} a {s.brecha_est_edad.max():.1f} puntos")
guardar(fig, "02_brecha_sexo.png")

# ---------- 3. brecha por edad (el promedio oculta la inversión)
a = agg(g, ["AELEC","gedad","sexo"]).pivot_table(index=["AELEC","gedad"], columns="sexo", values="p_esp")
a["brecha"] = a.Mujeres - a.Hombres; br = a.brecha.unstack(0)
br = br.reindex(ETIQ_EDAD); br.round(3).to_csv(TABLAS/"eda_03_brecha_sexo_por_edad.csv"); H["brecha_edad"] = br.round(2).to_dict()
fig, ax = plt.subplots(figsize=(8, 4.4))
for i, y in enumerate(ANIOS_):
    ax.plot(ETIQ_EDAD, br[y], "o-", lw=2.4 if y == 2024 else 1.2, alpha=1 if y == 2024 else .55, color=PAL[i % 6])
ax.axhline(0, color="k", lw=1)
ax.text(6.1, br[2024].iloc[-1], "2024", color=PAL[5 % 6], fontsize=9, va="center")
ax.set_ylabel("puntos (mujeres − hombres)"); ax.set_xlabel("grupo de edad")
ax.set_title("La brecha cambia de signo con la edad: a partir de 70 años los hombres participan más")
ax.legend(ANIOS_, ncol=6, loc="upper center", bbox_to_anchor=(.5, -.2), frameon=False, fontsize=9)
guardar(fig, "03_brecha_sexo_edad.png")

# ---------- 4. edad: curvas y cambio 2018→2024
ed = agg(g, ["AELEC","gedad"]).pivot(index="gedad", columns="AELEC", values="p_esp").reindex(ETIQ_EDAD)
ed.round(3).to_csv(TABLAS/"eda_04_participacion_por_edad.csv"); H["edad"] = ed.round(1).to_dict()
d = pd.DataFrame({"cambio_2018_2024": ed[2024]-ed[2018], "cambio_2012_2024": ed[2024]-ed[2012], "cambio_2021_2024": ed[2024]-ed[2021]})
d.round(3).to_csv(TABLAS/"eda_04b_cambio_por_edad.csv"); H["cambio_edad"] = d.round(1).to_dict()
fig, ax = plt.subplots(figsize=(8, 4.2))
cols = [PAL[1] if v < 0 else PAL[0] for v in d.cambio_2018_2024]
bars = ax.bar(ETIQ_EDAD, d.cambio_2018_2024, color=cols)
for b in bars: ax.annotate(f"{b.get_height():+.1f}", (b.get_x()+b.get_width()/2, b.get_height()), (0, 3 if b.get_height() > 0 else -12), textcoords="offset points", ha="center", fontsize=9.5)
ax.axhline(0, color="k", lw=1); ax.set_ylabel("puntos porcentuales"); ax.set_xlabel("grupo de edad")
tot = t.set_index("AELEC").p_esp
ax.set_title(f"De 2018 a 2024 la participación bajó en menores de 60 años y subió en mayores de 60 (total: {tot[2024]-tot[2018]:+.1f} puntos)")
ax.set_ylim(min(d.cambio_2018_2024.min()-1.5, -1), d.cambio_2018_2024.max()+1.5)
guardar(fig, "04_cambio_edad_2018_2024.png")

# ---------- 5. territorio: entidad (2024) cruda vs estandarizada por sexo×edad
nombres = {1:"Aguascalientes",2:"Baja California",3:"Baja California Sur",4:"Campeche",5:"Coahuila",6:"Colima",7:"Chiapas",8:"Chihuahua",9:"Ciudad de México",10:"Durango",11:"Guanajuato",12:"Guerrero",13:"Hidalgo",14:"Jalisco",15:"Estado de México",16:"Michoacán",17:"Morelos",18:"Nayarit",19:"Nuevo León",20:"Oaxaca",21:"Puebla",22:"Querétaro",23:"Quintana Roo",24:"San Luis Potosí",25:"Sinaloa",26:"Sonora",27:"Tabasco",28:"Tamaulipas",29:"Tlaxcala",30:"Veracruz",31:"Yucatán",32:"Zacatecas"}
pd.Series(nombres, name="entidad").rename_axis("EDOCVE").to_csv(TABLAS/"catalogo_entidades.csv")
ent = agg(g, ["AELEC","EDOCVE"]); ent = ent.merge(estandarizada(g, ["AELEC","EDOCVE"], ["sexo","gedad"], w_es)[["AELEC","EDOCVE","est"]], on=["AELEC","EDOCVE"])
ent["entidad"] = ent.EDOCVE.map(nombres); ent["reg_a"] = ent.EDOCVE.map(mapa(REGIONES_A)); ent["reg_b"] = ent.EDOCVE.map(mapa(REGIONES_B))
ent.round(3).to_csv(TABLAS/"eda_05_entidades_por_eleccion.csv", index=False)
e24 = ent[ent.AELEC == 2024].sort_values("est")
H["entidad24"] = {"max": [e24.iloc[-1].entidad, round(e24.iloc[-1].est,1)], "min": [e24.iloc[0].entidad, round(e24.iloc[0].est,1)],
                  "rango_puntos": round(e24.est.max()-e24.est.min(), 1)}
H["entidad_rank_cambia_por_ajuste"] = int((e24.p_esp.rank() - e24.est.rank()).abs().gt(3).sum())
fig, ax = plt.subplots(figsize=(7.5, 8.2)); y = np.arange(len(e24))
ax.hlines(y, e24.p_esp, e24.est, color="#bbb", lw=1.5)
ax.scatter(e24.p_esp, y, color=PAL[5], s=28, zorder=3, label="observada"); ax.scatter(e24.est, y, color=PAL[0], s=36, zorder=3, label="con misma estructura sexo-edad")
ax.set_yticks(y, e24.entidad, fontsize=9); ax.set_xlabel("% de participación 2024")
ax.legend(loc="upper center", bbox_to_anchor=(.4, -.07), ncol=2, frameon=False, fontsize=9.5)
ax.set_title(f"En 2024 la participación va de {H['entidad24']['min'][1]}% ({H['entidad24']['min'][0]}) a {H['entidad24']['max'][1]}% ({H['entidad24']['max'][0]})")
guardar(fig, "05_entidades_2024.png")

# ---------- 6. regiones y tipo de sección: cruda vs estandarizada sexo×edad en el tiempo
def serie(by, nomb, w, strata):
    cr = agg(g, ["AELEC", by]).pivot(index="AELEC", columns=by, values="p_esp")
    es = estandarizada(g, ["AELEC", by], strata, w).pivot(index="AELEC", columns=by, values="est")
    return cr, es
cra, esa = serie("reg_a", "region", w_es, ["sexo","gedad"])
pd.concat({"cruda": cra, "estandarizada": esa}, axis=1).round(3).to_csv(TABLAS/"eda_06_regiones_A.csv")
crb, esb = serie("reg_b", "region", w_es, ["sexo","gedad"])
pd.concat({"cruda": crb, "estandarizada": esb}, axis=1).round(3).to_csv(TABLAS/"eda_06_regiones_B.csv")
crt, est_ = serie("TIPOSEC", "tipo", w_es, ["sexo","gedad"])
pd.concat({"cruda": crt, "estandarizada": est_}, axis=1).round(3).to_csv(TABLAS/"eda_07_tipo_seccion.csv")
H["regionA"] = {"cruda": cra.round(1).to_dict(), "est": esa.round(1).to_dict()}
H["tiposec"] = {"cruda": crt.round(1).to_dict(), "est": est_.round(1).to_dict()}
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, df, ttl in ((axs[0], cra, "Observada"), (axs[1], esa, "Con la misma estructura de sexo y edad")):
    for i, r in enumerate(df.columns):
        ax.plot(df.index, df[r], "o-", color=PAL[i], lw=2); ax.annotate(r, (2024, df[r].iloc[-1]), (6, 0), textcoords="offset points", fontsize=9.5, color=PAL[i], va="center")
    ax.set_xticks(ANIOS_); ax.set_xlim(2008, 2027.5); ax.set_title(ttl, fontsize=11)
axs[0].set_ylabel("% de participación")
fig.suptitle("El orden de las regiones cambia entre elecciones; no hay una región siempre más participativa", x=.06, ha="left", fontweight="bold", fontsize=12.5, y=1.02)
guardar(fig, "06_regiones_tiempo.png")

fig, ax = plt.subplots(figsize=(8, 4.2)); nm = {"U":"Urbana","M":"Mixta","R":"Rural"}
for i, r in enumerate(["U","M","R"]):
    ax.plot(est_.index, est_[r], "o-", color=PAL[i], lw=2); ax.annotate(nm[r], (2024, est_[r].iloc[-1]), (6, 0), textcoords="offset points", fontsize=9.5, color=PAL[i], va="center")
ax.set_xticks(ANIOS_); ax.set_xlim(2008, 2026.5); ax.set_ylabel("% de participación (misma estructura de sexo y edad)")
dif24 = est_.loc[2024]; dif15 = est_.loc[2015]
ax.set_title(f"La ventaja rural se estrechó: de {dif15['R']-dif15['U']:+.1f} puntos frente a la urbana en 2015 a {dif24['R']-dif24['U']:+.1f} en 2024")
guardar(fig, "07_tipo_seccion.png")

# ---------- 7. NS: dónde se concentra
ns = agg(g, ["AELEC","EDOCVE"]); ns["entidad"] = ns.EDOCVE.map(nombres)
ns24 = ns[ns.AELEC == 2024].sort_values("p_ns", ascending=False)
ns[["AELEC","entidad","p_ns"]].pivot(index="entidad", columns="AELEC", values="p_ns").round(2).to_csv(TABLAS/"eda_08_ns_por_entidad.csv")
H["ns24_top"] = ns24.head(3)[["entidad","p_ns"]].round(1).values.tolist(); H["ns24_min"] = ns24.tail(1)[["entidad","p_ns"]].round(1).values.tolist()
w24 = g[g.AELEC==2024].groupby("gedad")["LN"].sum(); w24 = w24/w24.sum()
e_alt = estandarizada(g, ["AELEC","sexo"], ["gedad"], w24).pivot(index="AELEC", columns="sexo", values="est")
H["sensibilidad_pesos_brecha_sexo"] = (e_alt.Mujeres-e_alt.Hombres).round(2).to_dict()
(e_alt.Mujeres-e_alt.Hombres).round(3).to_csv(TABLAS/"eda_02b_brecha_sexo_pesos_2024.csv")
json.dump(H, open(TABLAS/"hallazgos_eda.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps(H, indent=1, ensure_ascii=False, default=float)[:6000])
