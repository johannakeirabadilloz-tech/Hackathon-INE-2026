"""Ajuste final de la CP-NTF (rango 4) sobre todo el tensor guardado por 11_tensor_ntf.py, con estabilidad entre semillas."""
import warnings
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS, ANIOS
from estilo import guardar, PAL
warnings.filterwarnings("ignore")
R, SEMILLAS = 4, (0, 1, 2)
z = np.load(PROC / "tensor_participacion.npz"); X, W, mps = z["X"].astype(float), z["W"].astype(float), z["mps"]
shape = X.shape; edades = np.arange(18, 100); WX = W * X
L = "ijkl"
def mt(T, F, k):
    ops, subs = [T], [L]
    for m in range(4):
        if m != k: ops.append(F[m]); subs.append(L[m] + "r")
    return np.einsum(",".join(subs) + "->" + L[k] + "r", *ops, optimize=True)
def recon(F): return np.einsum("ir,jr,kr,lr->ijkl", *F, optimize=True)
def ajusta(seed, it=400):
    rng = np.random.default_rng(seed); F = [rng.uniform(.2, 1, (n, R)) * .84 for n in shape]
    for _ in range(it):
        for k in range(4):
            F[k] *= mt(WX, F, k) / (mt(W * recon(F), F, k) + 1e-9)
            if k:
                s = F[k].max(0) + 1e-9; F[k] /= s; F[0] *= s
    return F
fits = [ajusta(s) for s in SEMILLAS]
def rm(F): return float(np.sqrt((W * (X - np.clip(recon(F), 0, 1)) ** 2).sum() / W.sum()))
# orden: por contribución media (carga municipal × escala); alinear semillas por similitud coseno del perfil de edad
def orden(F): return np.argsort(-(F[0].mean(0)))
base = [f[2][:, orden(f)] for f in fits[:1]][0]
al = []
for F in fits:
    cos = (F[2] / np.linalg.norm(F[2], axis=0)).T @ (base / np.linalg.norm(base, axis=0))
    perm = cos.argmax(0); al.append(([f[:, perm] for f in F], float(cos.max(0).min())))
print("rmse ajuste:", [round(rm(F), 4) for F in fits])
print("coseno mínimo del perfil de edad frente a la semilla 0 (alineado):", [round(c, 3) for _, c in al])
F = [f[:, orden(fits[0])] for f in fits[0]]
etiq = []
# gráficas
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
cols = [PAL[0], PAL[1], PAL[2], PAL[3]]
for r in range(R):
    ax[0].plot(edades, F[2][:, r], color=cols[r], lw=2, label=f"Componente {r+1}")
    ax[1].plot(ANIOS, F[3][:, r], color=cols[r], lw=2, marker="o")
    ax[2].bar(np.arange(2) + (r - 1.5) * .2, F[1][:, r], .2, color=cols[r])
ax[0].axvspan(85, 99, color="#999", alpha=.15); ax[0].set_xlabel("Edad"); ax[0].set_title("Perfil por edad"); ax[0].legend(fontsize=9)
ax[1].set_xticks(ANIOS); ax[1].set_title("Perfil por elección"); ax[2].set_xticks([0, 1]); ax[2].set_xticklabels(["Hombres", "Mujeres"]); ax[2].set_title("Perfil por sexo")
fig.suptitle("Componentes de la factorización no negativa de tensores (rango 4; cada perfil normalizado a máximo 1)", x=.01, ha="left", fontsize=11)
guardar(fig, "tensor_ntf_componentes.png")
pd.DataFrame({"edad": edades, **{f"c{r+1}": F[2][:, r] for r in range(R)}}).round(4).to_csv(TABLAS / "tensor_ntf_perfil_edad.csv", index=False)
pd.DataFrame({"anio": ANIOS, **{f"c{r+1}": F[3][:, r] for r in range(R)}}).round(4).to_csv(TABLAS / "tensor_ntf_perfil_eleccion.csv", index=False)
pd.DataFrame({"sexo": ["hombres", "mujeres"], **{f"c{r+1}": F[1][:, r] for r in range(R)}}).round(4).to_csv(TABLAS / "tensor_ntf_perfil_sexo.csv", index=False)
# municipios: cargas, componente dominante y estabilidad de las cargas
A = F[0]; share = A / A.sum(1, keepdims=True)
m = pd.DataFrame(A, columns=[f"carga_c{r+1}" for r in range(R)]); m["entidad"] = mps // 1000; m["municipio"] = mps % 1000
m["dominante"] = share.argmax(1) + 1
m.round(4).to_csv(TABLAS / "tensor_ntf_municipios.csv", index=False)
print("municipios por componente dominante:\n", m.dominante.value_counts().sort_index())
print("carga media por componente:", A.mean(0).round(3))
ent = m.groupby("entidad")[[f"carga_c{r+1}" for r in range(R)]].mean()
ent.round(3).to_csv(TABLAS / "tensor_ntf_entidades.csv")
fig, ax = plt.subplots(figsize=(9, 5))
sh = ent.div(ent.sum(1), axis=0).sort_values("carga_c1")
b = np.zeros(len(sh))
for r in range(R):
    ax.barh(sh.index.astype(str), sh[f"carga_c{r+1}"], left=b, color=cols[r], label=f"Componente {r+1}"); b += sh[f"carga_c{r+1}"].values
ax.set_xlabel("Proporción de la carga media municipal"); ax.set_ylabel("Clave de entidad"); ax.legend(ncol=4, fontsize=8, loc="lower center", bbox_to_anchor=(.5, 1.0))
ax.set_title("Mezcla de componentes por entidad", pad=28)
guardar(fig, "tensor_ntf_entidades.png")
# participación reconstruida en dos tipos de municipio: dominante 1 frente al resto
Xh = np.clip(recon(F), 0, 1)
print("ejemplo, participación ponderada 2024 a los 25 y 85 años (hombres) por componente dominante:")
for c in range(1, R + 1):
    sel = np.where(m.dominante.values == c)[0]
    if len(sel):
        w = W[sel][:, 0, :, 5]; x = X[sel][:, 0, :, 5]
        print(c, len(sel), [round(float((w[:, a - 18] * x[:, a - 18]).sum() / max(w[:, a - 18].sum(), 1e-9)), 3) for a in (25, 50, 70, 85)])
