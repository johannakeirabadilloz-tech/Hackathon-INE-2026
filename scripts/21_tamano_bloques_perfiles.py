"""Tamaño y participación 2024 de cada bloque (perfil × sexo × rango de edad) de `perfiles_sexo_edad`.
Sirve para saber cuánta lista nominal hay detrás de cada parte de un perfil (p. ej. en el perfil 3).
Lee la composición publicada y los conteos originales de 2024; no recalcula los perfiles."""
import re, zipfile
import pandas as pd
from config import RAW, RAIZ

CARPETA = RAIZ / "reports" / "perfiles_sexo_edad"
z = zipfile.ZipFile(RAW / "DatosAbiertos_DECEyEC_ConteosCensales2024.zip")
partes = []
for n in z.namelist():
    if n.endswith(".csv"):
        d = pd.read_csv(z.open(n), encoding="utf-8-sig", usecols=["SEXO", "EDAD", "LN", "SV", "NV"], dtype=str)
        d = d.apply(pd.to_numeric, errors="coerce")
        partes.append(d[(d.SEXO != 2) & d.EDAD.between(18, 99)].groupby(["SEXO", "EDAD"])[["LN", "SV", "NV"]].sum())
a = pd.concat(partes).groupby(level=[0, 1]).sum()
total = a.LN.sum()

filas = []
for _, r in pd.read_csv(CARPETA / "composicion_perfiles.csv").iterrows():
    sexo = 0 if r.sexo == "hombres" else 1
    for tramo in re.split(r",\s*", r.edades):
        lo, _, hi = tramo.partition("-")
        lo, hi = int(lo), int(hi or lo)
        m = a.loc[sexo].loc[lo:hi]
        filas.append(dict(perfil=r.perfil, sexo=r.sexo, edades=tramo, lista_nominal_2024=int(m.LN.sum()),
                          pct_lista_2024=round(100 * m.LN.sum() / total, 2),
                          participacion_2024=round(100 * m.SV.sum() / (m.SV.sum() + m.NV.sum()), 1)))
T = pd.DataFrame(filas)
T.to_csv(CARPETA / "tamano_bloques_perfiles_2024.csv", index=False)
print(T.to_string(index=False))
print(T.groupby("perfil").pct_lista_2024.sum().round(1))
