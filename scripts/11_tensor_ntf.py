"""Factorización no negativa de tensores (CP-NTF ponderada) de la participación:
municipio × sexo × edad simple (18-99) × elección. Solo datos del INE.
Cada componente = patrón de municipios ⊗ sexo ⊗ edad ⊗ elección; la participación es la suma de componentes."""
import json, warnings
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS, ANIOS
from estilo import guardar, PAL
warnings.filterwarnings("ignore")
SEED, TOPE, MIN_ESP = 42, 99, 20   # SUPUESTOS: edades >=100 fuera; celdas con <20 especificados no pesan
RANGOS = range(1, 9)

d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet",
                    columns=["AELEC", "EDOCVE", "MPIOCVE", "SEXO", "EDAD", "SV", "NV"])
d = d[(d.SEXO != 2) & d.EDAD.between(18, TOPE)]
d["mp"] = d.EDOCVE.astype("int32") * 1000 + d.MPIOCVE.astype("int32")
g = d.groupby(["mp", "SEXO", "EDAD", "AELEC"], observed=True)[["SV", "NV"]].sum().reset_index(); del d
mps = np.sort(g.mp.unique()); edades = np.arange(18, TOPE + 1)
ix = (np.searchsorted(mps, g.mp.values), g.SEXO.values.astype(int), (g.EDAD.values - 18).astype(int),
      np.searchsorted(ANIOS, g.AELEC.values))
shape = (len(mps), 2, len(edades), len(ANIOS))
esp = np.zeros(shape); sv = np.zeros(shape)
esp[ix] = (g.SV + g.NV).values; sv[ix] = g.SV.values
X = np.divide(sv, esp, out=np.zeros(shape), where=esp > 0)
W = np.where(esp >= MIN_ESP, np.sqrt(esp), 0.0); W /= W[W > 0].mean()
print("tensor", shape, "celdas con peso:", int((W > 0).sum()), f"({100*(W>0).mean():.1f}%)")

def mttkrp(T, F, k):
    # contrae T con todas las matrices menos la k-ésima
    ops, subs = [T], ["ijkl"]
    letras = "ijkl"; out = letras[k] + "r"
    for m in range(4):
        if m != k: ops.append(F[m]); subs.append(letras[m] + "r")
    return np.einsum(",".join(subs) + "->" + out, *ops, optimize=True)

def recon(F): return np.einsum("ir,jr,kr,lr->ijkl", *F, optimize=True)

def ajusta(R, mask_train, seed, it=300):
    rng = np.random.default_rng(seed)
    F = [rng.uniform(.2, 1, (n, R)) * (.5 / 1) ** .25 for n in shape]
    Wt = W * mask_train; WX = Wt * X; eps = 1e-9
    for _ in range(it):
        for k in range(4):
            num = mttkrp(WX, F, k); den = mttkrp(Wt * recon(F), F, k) + eps
            F[k] *= num / den
            # normaliza columnas y deja la escala en el modo 0 (municipios)
            if k != 0:
                s = F[k].max(0) + eps; F[k] /= s; F[0] *= s
    return F

def rmse(F, mask):
    Wm = W * mask; Xh = np.clip(recon(F), 0, 1)
    return float(np.sqrt((Wm * (X - Xh) ** 2).sum() / Wm.sum()))

rng = np.random.default_rng(SEED)
test = (rng.random(shape) < 0.10); tr = (~test).astype(float); te = test.astype(float)
filas = []
for R in RANGOS:
    for s in (0, 1):
        F = ajusta(R, tr, SEED + s)
        filas.append(dict(rango=R, semilla=s, rmse_entrenamiento=rmse(F, tr), rmse_prueba=rmse(F, te)))
        print(filas[-1], flush=True)
sel = pd.DataFrame(filas).groupby("rango")[["rmse_entrenamiento", "rmse_prueba"]].mean().round(4)
sel.to_csv(TABLAS / "tensor_ntf_seleccion_rango.csv"); print(sel)
# referencia: media ponderada por edad × sexo × elección (sin estructura de municipio)
ref = (W * X).sum(0, keepdims=True) / W.sum(0, keepdims=True).clip(1e-9)
print("ref rmse prueba (media por sexo×edad×elección):", round(float(np.sqrt((W * te * (X - ref) ** 2).sum() / (W * te).sum())), 4))
np.savez_compressed(PROC / "tensor_participacion.npz", X=X.astype("float32"), W=W.astype("float32"), mps=mps)
