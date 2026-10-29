import numpy as np, pandas as pd
from config import *
def cubo():
    g = pd.read_parquet(PROC/"cubo.parquet")
    g = g[g.SEXO != 2].copy()       # no binario (105 filas, solo 2024) se analiza aparte
    g["gedad"] = g.gedad.astype(str)
    g["reg_a"] = g.EDOCVE.map(mapa(REGIONES_A)); g["reg_b"] = g.EDOCVE.map(mapa(REGIONES_B))
    g["sexo"] = g.SEXO.map({0: "Hombres", 1: "Mujeres"})
    return g
def tasa(d, den="esp"):
    """Participación a partir de conteos sumados. esp=SV/(SV+NV); ln=SV/LN; ns=NS/LN"""
    if den == "esp": return 100*d.SV/(d.SV+d.NV)
    if den == "ln": return 100*d.SV/d.LN
    if den == "ns": return 100*d.NS/d.LN
    if den == "lnns": return 100*d.SV/(d.LN-d.NS)
def agg(g, by):
    a = g.groupby(by, observed=True)[["LN","SV","NV","NS"]].sum().reset_index()
    a["p_esp"], a["p_ln"], a["p_ns"] = tasa(a), tasa(a,"ln"), tasa(a,"ns")
    return a
def estandarizada(g, by, strata, peso):
    """Estandarización directa: Σ_w peso_strata × tasa_strata dentro de cada celda de `by`.
    peso: Series indexada por strata con suma 1. Tasa sobre especificados."""
    c = g.groupby(by+strata, observed=True)[["SV","NV"]].sum().reset_index()
    c["t"] = 100*c.SV/(c.SV+c.NV)
    pk = peso.reset_index(); pk.columns = strata+["w"]
    c = c.merge(pk, on=strata)
    c["tw"] = c.t*c.w
    out = c.groupby(by, observed=True).agg(est=("tw","sum"), wsum=("w","sum")).reset_index()
    out["est"] = out.est/out.wsum   # re-normaliza si faltan estratos (se reporta wsum)
    return out
