"""Cotejo del dataset maestro (civia) contra los conteos originales (ZIP -> data/processed, sin filas eliminadas).
Reagrupa los originales al grano del maestro y compara conteo por conteo."""
import json
import numpy as np, pandas as pd
from config import PROC, RAIZ, TABLAS

M = pd.read_csv(RAIZ / "data/civia_dataset/civia_dataset_maestro_municipal_2009_2024_con_region.csv", encoding="utf-8-sig")
BORDES = [18, 25, 35, 45, 55, 65, 75, 85, 10_000]; ETQ = ["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]
raw = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet",
                      columns=["AELEC", "EDOCVE", "MPIOCVE", "TIPOSEC", "SEXO", "EDAD", "LN", "SV", "NV", "NS"])
n_raw = len(raw); fuera = {"edad_menor_18": int((raw.EDAD < 18).sum()), "edad_100_o_mas": int((raw.EDAD >= 100).sum())}
tot_raw = raw.groupby("AELEC")[["LN", "SV", "NV", "NS"]].sum()
raw = raw[raw.EDAD >= 18].copy()
raw["grupo_edad"] = pd.cut(raw.EDAD, BORDES, right=False, labels=ETQ).astype(str)
k = ["AELEC", "EDOCVE", "MPIOCVE", "SEXO", "TIPOSEC", "grupo_edad"]
A = raw.groupby(k, observed=True).agg(LN=("LN", "sum"), SV=("SV", "sum"), NV=("NV", "sum"), NS=("NS", "sum"), n=("LN", "size")).reset_index()
del raw
M2 = M.rename(columns={"anio": "AELEC", "entidad_clave": "EDOCVE", "municipio_clave": "MPIOCVE", "sexo_codigo": "SEXO", "tipo_seccion_codigo": "TIPOSEC"})
J = A.merge(M2[k + ["lista_nominal", "si_votaron", "no_votaron", "no_especificados", "registros_origen"]], on=k, how="outer", indicator=True)
res = {"filas_originales": n_raw, "filas_maestro": len(M), "fuera_del_maestro_por_diseno": fuera,
       "celdas_originales_reagrupadas": len(A), "solo_en_originales": int((J._merge == "left_only").sum()), "solo_en_maestro": int((J._merge == "right_only").sum())}
B = J[J._merge == "both"].copy()
for a, b in (("LN", "lista_nominal"), ("SV", "si_votaron"), ("NV", "no_votaron"), ("NS", "no_especificados"), ("n", "registros_origen")):
    d = B[a] - B[b]; res[f"celdas_con_diferencia_{a}"] = int((d != 0).sum()); res[f"suma_diferencia_{a}"] = int(d.sum())
# totales por elección: originales (incluye todas las edades) frente al maestro
tm = M.groupby("anio")[["lista_nominal", "si_votaron", "no_votaron", "no_especificados"]].sum()
cmp = tot_raw.join(tm); cmp.columns = ["LN_orig", "SV_orig", "NV_orig", "NS_orig", "LN_maestro", "SV_maestro", "NV_maestro", "NS_maestro"]
for c in ("LN", "SV", "NV", "NS"): cmp[f"dif_{c}"] = cmp[f"{c}_orig"] - cmp[f"{c}_maestro"]
cmp.to_csv(TABLAS / "cotejo_maestro_totales.csv")
# participación recalculada frente a la declarada
M["part_recalc"] = 100 * M.si_votaron / (M.si_votaron + M.no_votaron).replace(0, np.nan)
res["participacion_pct_max_dif_abs"] = float((M.part_recalc - M.participacion_pct).abs().max())
res["filas_participacion_nula_con_denominador_cero"] = int((M.participacion_pct.isna() & ((M.si_votaron + M.no_votaron) == 0)).sum())
res["filas_LN_distinto_de_suma"] = int((M.lista_nominal != M.si_votaron + M.no_votaron + M.no_especificados).sum())
res["llaves_duplicadas_en_maestro"] = int(M.duplicated(["anio", "entidad_clave", "municipio_clave", "sexo_codigo", "tipo_seccion_codigo", "grupo_edad"]).sum())
B[(B.LN != B.lista_nominal) | (B.SV != B.si_votaron) | (B.NV != B.no_votaron) | (B.NS != B.no_especificados)].head(500).to_csv(TABLAS / "cotejo_maestro_diferencias_muestra.csv", index=False)
J[J._merge != "both"].head(500).to_csv(TABLAS / "cotejo_maestro_celdas_sin_par.csv", index=False)
json.dump(res, open(TABLAS / "cotejo_maestro_resumen.json", "w"), indent=1)
print(json.dumps(res, indent=1)); print(cmp.to_string())
