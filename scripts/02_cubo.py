"""Fase 1b: cubo agregado (suma de conteos) año × entidad × municipio × tipo de
sección × sexo × grupo de edad. Los datos originales no se tocan."""
import pandas as pd, numpy as np
from config import *
t = pd.read_parquet(PROC/"conteos_seccion_sexo_edad.parquet").astype({c: "int64" for c in ["LN","SV","NV","NS"]})
t["gedad"] = pd.cut(t.EDAD, CORTES_EDAD, right=False, labels=ETIQ_EDAD)
# edad única (para revisar extremos)
ed = t.groupby(["AELEC","EDAD"], observed=True)[["LN","SV","NV","NS"]].sum().reset_index()
ed.to_parquet(PROC/"cubo_edad_unica.parquet")
g = t.groupby(["AELEC","EDOCVE","MPIOCVE","TIPOSEC","SEXO","gedad"], observed=True)[["LN","SV","NV","NS"]].sum().reset_index()
g.to_parquet(PROC/"cubo.parquet")
print(g.shape)
# revisión de edades extremas
tot = ed.groupby("AELEC")[["LN","SV","NV"]].sum()
e100 = ed[ed.EDAD > 100].groupby("AELEC")[["LN","SV","NV"]].sum()
r = pd.DataFrame({"LN_edad_gt100": e100.LN, "pct_de_LN": 100*e100.LN/tot.LN,
                  "particip_gt100": 100*e100.SV/(e100.SV+e100.NV),
                  "particip_total": 100*tot.SV/(tot.SV+tot.NV)})
r.round(3).to_csv(TABLAS/"calidad_edades_extremas.csv"); print(r.round(3))
