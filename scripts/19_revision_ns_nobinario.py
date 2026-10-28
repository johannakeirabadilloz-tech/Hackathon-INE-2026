"""Revisión de los perfiles por sexo × edad: peso de los no especificados (NS), sensibilidad a contarlos como no voto,
y personas no binarias. Datos del INE."""
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score
from config import PROC, TABLAS, ANIOS
SEED = 42
d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", columns=["AELEC", "SEXO", "EDAD", "LN", "SV", "NV", "NS"])
for c in ("LN", "SV", "NV", "NS"): d[c] = d[c].astype("int64")
# --- no binarios
nb = d[d.SEXO == 2]
print("NO BINARIO: filas por elección", nb.groupby("AELEC").size().to_dict())
print(nb.groupby("AELEC")[["LN", "SV", "NV", "NS"]].sum().assign(part=lambda x: (100 * x.SV / (x.SV + x.NV)).round(1)).to_string())
tot = d.groupby("AELEC").LN.sum(); print("% de la lista nominal 2024 que es no binaria:", round(100 * nb.LN.sum() / tot[2024], 5))
# --- NS: peso por elección, por sexo y por tramo de edad
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)]
print("\nNS % de LN por elección:", (100 * d.groupby("AELEC").NS.sum() / d.groupby("AELEC").LN.sum()).round(2).to_dict())
d["tramo"] = pd.cut(d.EDAD, [17, 29, 44, 64, 84, 99], labels=["18-29", "30-44", "45-64", "65-84", "85-99"])
t = d.groupby(["AELEC", "tramo"], observed=True)[["NS", "LN"]].sum(); t["ns_pct"] = (100 * t.NS / t.LN).round(2)
print(t.ns_pct.unstack("tramo").to_string())
s = d.groupby(["AELEC", "SEXO"])[["NS", "LN"]].sum(); s["ns_pct"] = (100 * s.NS / s.LN).round(2); print(s.ns_pct.unstack("SEXO").rename(columns={0: "hombres", 1: "mujeres"}).to_string())
# --- sensibilidad: perfiles recalculados contando NS como "no votó" (SV/LN) y comparados con los principales (SV/(SV+NV))
a = d.groupby(["SEXO", "EDAD", "AELEC"])[["SV", "NV", "NS", "LN"]].sum()
Pa = (100 * a.SV / (a.SV + a.NV)).unstack("AELEC")[ANIOS].dropna(); Pb = (100 * a.SV / a.LN).unstack("AELEC")[ANIOS].loc[Pa.index]
def perfiles(P):
    Z = StandardScaler().fit(P.values); km = KMeans(4, n_init=50, random_state=SEED).fit(Z.transform(P.values))
    ord_ = np.argsort(-Z.inverse_transform(km.cluster_centers_)[:, 5]); r = {c: i + 1 for i, c in enumerate(ord_)}
    return pd.Series([r[x] for x in km.labels_], index=P.index)
la, lb = perfiles(Pa), perfiles(Pb)
print("\nARI perfiles principales vs. NS contados como no voto:", round(adjusted_rand_score(la, lb), 3), "| segmentos que cambian de perfil:", int((la != lb).sum()), "de", len(la))
print("segmentos que cambian (sexo, edad, perfil principal -> sensibilidad):")
ch = pd.DataFrame({"principal": la, "sin_NS_en_denominador": lb})[la != lb]; print(ch.to_string()); ch.to_csv(TABLAS / "perfiles_sensibilidad_ns.csv")
# --- sensibilidad: solo 2012-2024 (sin 2009 y 2015 con más NS) y solo presidenciales
for nom, ys in (("sin 2009", [2012, 2015, 2018, 2021, 2024]), ("solo presidenciales", [2012, 2018, 2024])):
    Pc = Pa[ys]; Z = StandardScaler().fit(Pc.values); km = KMeans(4, n_init=50, random_state=SEED).fit(Z.transform(Pc.values))
    print(f"ARI con perfiles principales usando {nom}:", round(adjusted_rand_score(la, km.labels_), 3))
