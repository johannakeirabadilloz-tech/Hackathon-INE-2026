"""Fase 1a: lee los ZIP originales (sin extraer ni modificar), valida y guarda
una tabla de trabajo en data/processed/. Reporta problemas sin corregirlos."""
import io, zipfile, re
import numpy as np, pandas as pd
from config import *

COLS = ["AELEC","EDOCVE","MPIOCVE","SECCION","TIPOSEC","SEXO","EDAD","LN","SV","NV","NS"]
frames, calidad = [], []
for y in ANIOS:
    zf = zipfile.ZipFile(next(RAW.glob(f"*{y}.zip")))
    for n in sorted(x for x in zf.namelist() if x.endswith(".csv")):
        with zf.open(n) as f:
            d = pd.read_csv(f, encoding="utf-8-sig", usecols=COLS, dtype=str)
        d["archivo"] = n.rsplit("/", 1)[-1]
        frames.append(d)
    print(y, "leído", flush=True)
raw = pd.concat(frames, ignore_index=True); del frames

# ---- conversión numérica: lo no convertible se cuenta, no se corrige
num = ["AELEC","EDOCVE","MPIOCVE","SECCION","SEXO","EDAD","LN","SV","NV","NS"]
Q = {}   # hallazgos de calidad
for c in num:
    v = pd.to_numeric(raw[c], errors="coerce")
    Q[f"{c}_no_numerico_o_vacio"] = int(v.isna().sum())
    raw[c] = v
Q["filas_total"] = len(raw)
Q["TIPOSEC_valores"] = raw["TIPOSEC"].fillna("<NA>").value_counts().to_dict()
Q["SEXO_valores"] = raw["SEXO"].value_counts(dropna=False).to_dict()
raw["TIPOSEC"] = raw["TIPOSEC"].str.strip().str.upper().str[0]   # "Urbana"->U, etc.

# ---- consistencia aritmética LN = SV + NV + NS
dif = raw["LN"] - (raw["SV"] + raw["NV"] + raw["NS"])
tab = raw.assign(dif=dif).groupby("AELEC").agg(
    filas=("LN","size"), LN=("LN","sum"), SV=("SV","sum"), NV=("NV","sum"), NS=("NS","sum"),
    filas_suma_no_cuadra=("dif", lambda s: int((s != 0).sum())),
    suma_dif_total=("dif","sum"))
tab["pct_NS_de_LN"] = 100*tab.NS/tab.LN
tab["pct_sin_dato_denominador_cero"] = raw.assign(z=(raw.SV+raw.NV)==0).groupby("AELEC")["z"].mean()*100
# ---- duplicados en la llave natural
llave = ["AELEC","EDOCVE","MPIOCVE","SECCION","SEXO","EDAD"]
dup = raw.duplicated(llave, keep=False)
Q["filas_en_llave_duplicada"] = int(dup.sum())
Q["duplicados_exactos_en_todo"] = int(raw.duplicated(COLS, keep=False).sum())
Q["duplicados_por_anio"] = raw[dup].groupby("AELEC").size().to_dict()
# ---- negativos, extremos
for c in ["LN","SV","NV","NS"]:
    Q[f"{c}_negativos"] = int((raw[c] < 0).sum())
    Q[f"{c}_max"] = int(raw[c].max())
Q["SV_mayor_que_LN"] = int((raw.SV > raw.LN).sum())
Q["edad_min"], Q["edad_max"] = int(raw.EDAD.min()), int(raw.EDAD.max())
Q["filas_edad_menor_18"] = int((raw.EDAD < 18).sum())
Q["filas_edad_mayor_100"] = int((raw.EDAD > 100).sum())
Q["LN_p99.9"] = float(raw.LN.quantile(.999))
ext = raw[raw.LN > raw.LN.quantile(.9999)]
Q["filas_LN_sobre_p99.99"] = len(ext)
# ---- entidad vs archivo (coherencia)
Q["entidades_por_anio"] = raw.groupby("AELEC").EDOCVE.nunique().to_dict()
Q["secciones_por_anio"] = raw.drop_duplicates(["AELEC","EDOCVE","SECCION"]).groupby("AELEC").size().to_dict()
Q["municipios_por_anio"] = raw.drop_duplicates(["AELEC","EDOCVE","MPIOCVE"]).groupby("AELEC").size().to_dict()
# no binario
Q["filas_sexo2_por_anio"] = raw[raw.SEXO == 2].groupby("AELEC").size().to_dict()
# ---- tipo de sección de una misma sección que cambia entre elecciones
ts = raw.drop_duplicates(["AELEC","EDOCVE","SECCION"])[["AELEC","EDOCVE","SECCION","TIPOSEC"]]
Q["secciones_con_tipo_cambiante"] = int((ts.groupby(["EDOCVE","SECCION"]).TIPOSEC.nunique() > 1).sum())

import json
(TABLAS/"calidad_hallazgos.json").write_text(json.dumps(Q, indent=1, ensure_ascii=False, default=str))
tab.round(4).to_csv(TABLAS/"calidad_por_eleccion.csv")
print(tab.round(3).to_string()); print(json.dumps(Q, indent=1, ensure_ascii=False, default=str))

# ---- tabla de trabajo: tipos compactos; NO se eliminan filas
t = raw.drop(columns=["archivo"]).astype({"AELEC":"int16","EDOCVE":"int8","MPIOCVE":"int16","SECCION":"int32",
        "SEXO":"int8","EDAD":"int16","LN":"int32","SV":"int32","NV":"int32","NS":"int32"}, errors="ignore")
t.to_parquet(PROC/"conteos_seccion_sexo_edad.parquet", index=False)
print("guardado", t.shape)
