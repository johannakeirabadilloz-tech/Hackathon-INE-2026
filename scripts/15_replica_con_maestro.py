"""Repite el análisis territorial (05) con el dataset maestro y lo compara con el hecho desde los originales."""
import numpy as np, pandas as pd
from config import RAIZ, TABLAS, ANIOS
MIN_ESP = 100
M = pd.read_csv(RAIZ / "data/civia_dataset/civia_dataset_maestro_municipal_2009_2024_con_region.csv", encoding="utf-8-sig")
M = M[M.sexo_codigo != 2]
M["g"] = M.grupo_edad.map({"18-24": "18-34", "25-34": "18-34", "35-44": "35-64", "45-54": "35-64", "55-64": "35-64",
                           "65-74": "65-84", "75-84": "65-84", "85+": "85+"})
m = M.groupby(["anio", "entidad_clave", "municipio_clave", "g"])[["si_votaron", "no_votaron"]].sum().reset_index()
m["esp"] = m.si_votaron + m.no_votaron; m["part"] = 100 * m.si_votaron / m.esp.where(m.esp > 0)
res = []
for y in ANIOS:
    w = m[m.anio == y].pivot_table(index=["entidad_clave", "municipio_clave"], columns="g", values=["part", "esp"])
    w = w[(w["esp"][["18-34", "35-64", "85+"]] >= MIN_ESP).all(axis=1)]; p = w["part"]
    t = pd.DataFrame({"brecha_joven": p["35-64"] - p["18-34"], "brecha_85": p["35-64"] - p["85+"]}).reset_index()
    t["AELEC"] = y; res.append(t)
mm = pd.concat(res).rename(columns={"entidad_clave": "EDOCVE", "municipio_clave": "MPIOCVE"})
o = pd.read_csv(TABLAS / "territorial_municipio_brechas.csv")
j = o.merge(mm, on=["AELEC", "EDOCVE", "MPIOCVE"], how="outer", suffixes=("_orig", "_maestro"), indicator=True)
print("municipios-elección: originales", len(o), "maestro", len(mm), "| en ambos", int((j._merge == "both").sum()),
      "| solo orig", int((j._merge == "left_only").sum()), "| solo maestro", int((j._merge == "right_only").sum()))
b = j[j._merge == "both"]
for c in ("brecha_joven", "brecha_85"):
    d = (b[f"{c}_orig"] - b[f"{c}_maestro"]).abs()
    print(c, "dif abs máxima", round(d.max(), 4), "| media", round(d.mean(), 5), "| celdas con dif > 0.01 pts:", int((d > 0.01).sum()))
def eta2(df, col):
    tot = ((df[col] - df[col].mean()) ** 2).sum(); e = df.groupby("EDOCVE")[col].transform("mean")
    return ((e - df[col].mean()) ** 2).sum() / tot
for y in (2021, 2024):
    for nombre, t in (("orig", o[o.AELEC == y]), ("maestro", mm[mm.AELEC == y])):
        print(y, nombre, "media joven", round(t.brecha_joven.mean(), 3), "media 85+", round(t.brecha_85.mean(), 3),
              "eta2 joven", round(eta2(t, "brecha_joven"), 3), "eta2 85+", round(eta2(t, "brecha_85"), 3), "n", len(t))
