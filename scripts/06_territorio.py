"""Fase 5: ¿una regionalización recoge el efecto territorial de la entidad?
(a) captura de devianza vs particiones al azar; (b) variación entre municipios
dentro de cada región (participación ajustada por sexo×edad, estandarización indirecta)."""
import json, warnings, numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from utils import *
warnings.filterwarnings("ignore"); rng = np.random.default_rng(2026)
g = cubo()
c = g.groupby(["AELEC","EDOCVE","TIPOSEC","sexo","gedad"], observed=True)[["SV","NV"]].sum().reset_index()
c = c[(c.SV+c.NV) > 0].copy(); c["anio"] = c.AELEC.astype(str); c["ent"] = c.EDOCVE.astype(str); c["tipo"] = c.TIPOSEC
def D2(rhs, d):
    m = smf.glm(f"SV + NV ~ {rhs}", d, family=sm.families.Binomial()).fit(); return 1 - m.deviance/m.null_deviance
CTRL = "C(anio) + C(sexo) + C(gedad) + C(tipo)"
def captura(d, ctrl=CTRL, reg=None):
    d0 = D2(ctrl, d); de = D2(ctrl + " + C(ent)", d)
    return d0, de, ((D2(ctrl + f" + C({reg})", d) - d0)/(de - d0) if reg else np.nan)
ma, mb = mapa(REGIONES_A), mapa(REGIONES_B)
c["reg_a"] = c.EDOCVE.map(ma); c["reg_b"] = c.EDOCVE.map(mb)
# ---- (a) global
d0, de, ca = captura(c, reg="reg_a"); _, _, cb = captura(c, reg="reg_b")
# con efecto territorial que cambia por elección
CT = CTRL + " + C(anio):C(tipo)"
t0 = D2(CTRL, c); te = D2(CTRL + " + C(ent) + C(anio):C(ent)", c)
ta = (D2(CTRL + " + C(reg_a) + C(anio):C(reg_a)", c) - t0)/(te - t0); tb = (D2(CTRL + " + C(reg_b) + C(anio):C(reg_b)", c) - t0)/(te - t0)
# placebo: particiones al azar con los mismos tamaños
def placebo(tam, n=200, reg_name="r"):
    out = []; ents = np.arange(1, 33)
    for _ in range(n):
        p = rng.permutation(ents); lab, i = {}, 0
        for j, t in enumerate(tam):
            for e in p[i:i+t]: lab[e] = j
            i += t
        d = c.assign(r=c.EDOCVE.map(lab)); out.append((D2(CTRL + " + C(r)", d) - d0)/(de - d0))
    return np.array(out)
pa = placebo([len(v) for v in REGIONES_A.values()]); pb = placebo([len(v) for v in REGIONES_B.values()])
# por elección
fil = []
for y, d in c.groupby("anio"):
    ctrl = "C(sexo) + C(gedad) + C(tipo)"; z0, ze, za = captura(d, ctrl, "reg_a"); _, _, zb = captura(d, ctrl, "reg_b")
    fil.append(dict(eleccion=int(y), captura_A=za, captura_B=zb, D2_controles=z0, D2_con_entidad=ze))
P = pd.DataFrame(fil); P.round(4).to_csv(TABLAS/"ter_02_captura_por_eleccion.csv", index=False)
G = pd.DataFrame([dict(region="A: 3 regiones", captura_global=ca, captura_con_cambio_por_eleccion=ta, azar_mediana=np.median(pa), azar_p95=np.quantile(pa, .95)),
                  dict(region="B: 5 regiones", captura_global=cb, captura_con_cambio_por_eleccion=tb, azar_mediana=np.median(pb), azar_p95=np.quantile(pb, .95))])
G.round(4).to_csv(TABLAS/"ter_01_captura.csv", index=False)
# ---- (b) municipios: participación ajustada por sexo×edad (indirecta)
nat = g.groupby(["AELEC","sexo","gedad"], observed=True)[["SV","NV"]].sum(); nat["r"] = nat.SV/(nat.SV+nat.NV)
natY = g.groupby("AELEC")[["SV","NV"]].sum(); natY["p"] = natY.SV/(natY.SV+natY.NV)
m = g.groupby(["AELEC","EDOCVE","MPIOCVE","sexo","gedad"], observed=True)[["SV","NV"]].sum().reset_index().merge(nat.r.reset_index(), on=["AELEC","sexo","gedad"])
m["n"] = m.SV+m.NV; m["E"] = m.n*m.r
M = m.groupby(["AELEC","EDOCVE","MPIOCVE"]).agg(O=("SV","sum"), E=("E","sum"), n=("n","sum")).reset_index()
M["adj"] = 100*M.AELEC.map(natY.p)*M.O/M.E; M["crudo"] = 100*M.O/M.n; M["reg_a"] = M.EDOCVE.map(ma); M["reg_b"] = M.EDOCVE.map(mb)
M = M[M.n >= 300]       # SUPUESTO: mínimo 300 registros con situación conocida
def descomp(d, y="adj"):
    w = d.n/d.n.sum(); mu = (w*d[y]).sum(); tot = (w*(d[y]-mu)**2).sum()
    out = {}
    for nombre, reg in (("A", "reg_a"), ("B", "reg_b")):
        gr = d.groupby(reg).apply(lambda s: pd.Series({"w": s.n.sum()/d.n.sum(), "mu": np.average(s[y], weights=s.n)}), include_groups=False)
        ge = d.groupby("EDOCVE").apply(lambda s: pd.Series({"w": s.n.sum()/d.n.sum(), "mu": np.average(s[y], weights=s.n), "reg": s[reg].iloc[0]}), include_groups=False)
        ent_mu = d.EDOCVE.map(ge.mu); reg_mu = d[reg].map(gr.mu)
        out[nombre] = dict(entre_regiones=(w*(reg_mu-mu)**2).sum()/tot, entre_entidades_dentro=(w*(ent_mu-reg_mu)**2).sum()/tot, entre_municipios_dentro=(w*(d[y]-ent_mu)**2).sum()/tot)
    ruido = (w*(d.crudo/100*(1-d.crudo/100)/d.n*1e4)).sum()/tot  # varianza binomial esperada (ruido de muestreo), en % de la varianza total
    return out, ruido
fil = []
for y, d in M.groupby("AELEC"):
    o, r = descomp(d)
    for k, v in o.items(): fil.append(dict(eleccion=y, regionalizacion=k, **v, ruido_muestreo_fraccion_varianza=r))
Dc = pd.DataFrame(fil); Dc.round(4).to_csv(TABLAS/"ter_03_descomposicion_municipal.csv", index=False)
# dispersión dentro de cada región (2024, y 2018)
fil = []
for y in (2018, 2024):
    d = M[M.AELEC == y]
    for nombre, reg in (("A", "reg_a"), ("B", "reg_b")):
        for r, s in d.groupby(reg):
            q = np.quantile(s.adj, [.1, .5, .9]); fil.append(dict(eleccion=y, regionalizacion=nombre, region=r, municipios=len(s), p10=q[0], mediana=q[1], p90=q[2], amplitud_p10_p90=q[2]-q[0]))
W = pd.DataFrame(fil); W.round(2).to_csv(TABLAS/"ter_04_dispersion_dentro_region.csv", index=False)
# solape: % de municipios de la región más baja que superan la mediana de la región más alta (2024, regionalización A)
d = M[M.AELEC == 2024]; med = d.groupby("reg_a").apply(lambda s: np.median(s.adj), include_groups=False)
alta, baja = med.idxmax(), med.idxmin(); solape = float((d[d.reg_a == baja].adj > med[alta]).mean())
mA = d.groupby("reg_a").apply(lambda s: np.median(s.adj), include_groups=False)
M.round(3).to_csv(PROC/"municipios_ajustados.csv", index=False)
R = dict(captura_global=G.round(3).to_dict("records"), por_eleccion=P.round(3).to_dict("records"), solape_2024=dict(alta=alta, baja=baja, pct_baja_sobre_mediana_alta=round(100*solape, 1)), n_municipios_2024=int(len(d)),
         D2_controles=round(d0, 3), D2_con_entidad=round(de, 3))
json.dump(R, open(TABLAS/"hallazgos_territorio.json", "w"), indent=1, ensure_ascii=False, default=float)
np.save(TABLAS/"_placebo_a.npy", pa); np.save(TABLAS/"_placebo_b.npy", pb)
print(G.round(3).to_string()); print(P.round(3).to_string()); print(Dc.round(3).to_string()); print(W[W.eleccion==2024].round(1).to_string()); print(R["solape_2024"])
