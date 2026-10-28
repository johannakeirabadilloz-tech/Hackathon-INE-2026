"""Tensor bayesiano de participación (versión simplificada inspirada en Zens, arXiv 2502.09255):
entidad × sexo × edad simple × elección, verosimilitud normal sobre el logit de la tasa, efectos principales con caminata
aleatoria en edad y elección, e interacciones de bajo rango con encogimiento (ARD). Solo datos del INE.
NO es el modelo de Zens (que usa procesos gaussianos, priors global-local sobre los modos y otro muestreador)."""
import os, sys, json, warnings
os.environ["XLA_FLAGS"] = "--xla_force_host_platform_device_count=2"
import numpy as np, pandas as pd
import jax, jax.numpy as jnp
import numpyro, numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, init_to_median
import matplotlib.pyplot as plt
from config import PROC, TABLAS, GRAFICAS, ANIOS
from estilo import guardar, PAL
warnings.filterwarnings("ignore"); numpyro.set_host_device_count(2)
RAPIDO = len(sys.argv) > 1 and sys.argv[1] == "rapido"
NW, NS, RMAX, SEED = (150, 150, 3, 0) if RAPIDO else (1500, 1500, 3, 0)

d = pd.read_parquet(PROC / "conteos_seccion_sexo_edad.parquet", columns=["AELEC", "EDOCVE", "SEXO", "EDAD", "SV", "NV"])
d = d[(d.SEXO != 2) & d.EDAD.between(18, 99)]
g = d.groupby(["EDOCVE", "SEXO", "EDAD", "AELEC"], observed=True)[["SV", "NV"]].sum().reset_index(); del d
# SUPUESTO: bandas de edad (18-19, 20-24, ..., 80-84, 85-89, 90-99) para reducir el tensor y estabilizar el muestreo
BORDES = [18, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100]
ETQ = [f"{a}-{b-1}" for a, b in zip(BORDES[:-1], BORDES[1:])]
g["banda"] = np.digitize(g.EDAD.values, BORDES) - 1
g = g.groupby(["EDOCVE", "SEXO", "banda", "AELEC"], observed=True)[["SV", "NV"]].sum().reset_index()
ents = np.sort(g.EDOCVE.unique()); E, A, T = len(ents), len(ETQ), len(ANIOS)
ix = (np.searchsorted(ents, g.EDOCVE.values), g.SEXO.values.astype(int), g.banda.values.astype(int), np.searchsorted(ANIOS, g.AELEC.values))
n = np.zeros((E, 2, A, T)); k = np.zeros((E, 2, A, T)); n[ix] = (g.SV + g.NV).values; k[ix] = g.SV.values
valid = n > 0
rng = np.random.default_rng(SEED); held = valid & (rng.random(n.shape) < 0.10)
train = valid & ~held
print("celdas", valid.sum(), "entrenamiento", train.sum(), "retenidas", held.sum())

def rw(name, size, scale):
    z = numpyro.sample(name + "_z", dist.Normal(0, 1).expand([size - 1]).to_event(1))
    x = jnp.concatenate([jnp.zeros(1), jnp.cumsum(z * scale)])
    return x - x.mean()

def modelo(R, n, k, mask):
    mu = numpyro.sample("mu", dist.Normal(0, 2))
    se = numpyro.sample("sd_ent", dist.HalfNormal(1)); sa = numpyro.sample("sd_edad", dist.HalfNormal(.3)); st = numpyro.sample("sd_elec", dist.HalfNormal(.5))
    ent = numpyro.sample("ent", dist.Normal(0, 1).expand([E])) * se
    sex = numpyro.sample("sexo", dist.Normal(0, 1)) * 0.5
    edad = rw("edad", A, sa); elec = rw("elec", T, st)
    eta = mu + ent[:, None, None, None] + jnp.array([-1, 1])[None, :, None, None] * sex + edad[None, None, :, None] + elec[None, None, None, :]
    if R > 0:
        tau = numpyro.sample("tau", dist.HalfCauchy(1))
        lam = numpyro.sample("lam", dist.HalfNormal(1).expand([R])) * tau * 0.3     # ARD: encoge componentes sobrantes
        u = numpyro.sample("u", dist.Normal(0, 1).expand([E, R]))
        s = numpyro.sample("s", dist.Normal(0, 1).expand([2, R]))
        sv = numpyro.sample("sv", dist.Normal(0, 1).expand([A, R]))
        v = jnp.cumsum(sv * 0.15, axis=0); v = (v - v.mean(0)) / (v.std(0) + 1e-6)         # suave en edad
        sw = numpyro.sample("sw", dist.Normal(0, 1).expand([T, R]))
        w = (sw - sw.mean(0)) / (sw.std(0) + 1e-6)
        eta = eta + jnp.einsum("r,er,sr,ar,tr->esat", lam, u, s, v, w)
    # verosimilitud normal sobre el logit de la tasa observada: varianza muestral (delta) + dispersión libre sigma
    # (la beta-binomial sobre conteos de 1e5-1e6 dejó al NUTS sin poder explorar: paso de 1e-6)
    sigma = numpyro.sample("sigma", dist.HalfNormal(.2))
    po = jnp.clip(k / jnp.maximum(n, 1.), 1e-4, 1 - 1e-4)
    yl = jnp.log(po / (1 - po)); var = 1. / (jnp.maximum(n, 1.) * po * (1 - po)) + sigma ** 2
    with numpyro.handlers.mask(mask=mask):
        numpyro.sample("obs", dist.Normal(eta, jnp.sqrt(var)), obs=jnp.where(mask, yl, 0.))
    p = jax.nn.sigmoid(eta)
    numpyro.deterministic("p", p)

def ajusta(R, tag):
    mc = MCMC(NUTS(lambda **kw: modelo(R, **kw), target_accept_prob=.9, max_tree_depth=8, init_strategy=init_to_median), num_warmup=NW, num_samples=NS, num_chains=2, chain_method="parallel", progress_bar=False)
    mc.run(jax.random.PRNGKey(SEED), n=jnp.array(n), k=jnp.array(k), mask=jnp.array(train))
    s = mc.get_samples(group_by_chain=True)
    return mc, s

def evalua(s, nombre):
    p = np.asarray(s["p"]).reshape(-1, *n.shape)[::10].mean(0)
    w = np.sqrt(n[held]); y = (k / np.maximum(n, 1))[held]; ph = p[held]
    return dict(modelo=nombre, rmse_pond_retenidas=float(np.sqrt(np.average((y - ph) ** 2, weights=w))),
                mae_pts=float(100 * np.average(np.abs(y - ph), weights=w)))

res, out = [], {}
for R, nombre in ((0, "solo efectos principales"), (RMAX, f"con interacciones de rango {RMAX}")):
    mc, s = ajusta(R, nombre)
    from numpyro.diagnostics import summary
    dd = {kk_: v for kk_, v in s.items() if kk_ in ("mu", "sigma", "sd_ent", "sd_edad", "sd_elec")}
    if R > 0:   # solo el producto tau·lam está identificado; se ordena por tamaño para evitar el cambio de etiquetas
        le = np.sort(np.asarray(s["lam"]) * np.asarray(s["tau"])[..., None] * 0.3, axis=-1)[..., ::-1]
        dd.update({f"lam_eff{j+1}": le[..., j] for j in range(R)})
    sm = summary(dd, group_by_chain=True)
    rh = max(float(np.max(v["r_hat"])) for v in sm.values())
    print("r_hat por cantidad:", {k_: round(float(np.max(v["r_hat"])), 3) for k_, v in sm.items()}, flush=True)
    div = int(mc.get_extra_fields()["diverging"].sum())
    r = evalua(s, nombre); r.update(max_rhat_hiperparametros=round(rh, 3), divergencias=div, sigma_residual_logit=float(np.mean(s["sigma"]))); res.append(r); out[R] = s
    print(r, flush=True)
pd.DataFrame(res).round(4).to_csv(TABLAS / "tensor_bayes_comparacion.csv", index=False)

# ---- componentes de la versión con interacciones
s = out[RMAX]
lam = np.asarray(s["lam"]).reshape(-1, RMAX) * np.asarray(s["tau"]).reshape(-1, 1) * 0.3
u = np.asarray(s["u"]).reshape(-1, E, RMAX); sx = np.asarray(s["s"]).reshape(-1, 2, RMAX)
sv_ = np.asarray(s["sv"]).reshape(-1, A, RMAX); sw_ = np.asarray(s["sw"]).reshape(-1, T, RMAX)
v = np.cumsum(sv_ * 0.15, 1); v = (v - v.mean(1, keepdims=True)) / (v.std(1, keepdims=True) + 1e-6)
w = (sw_ - sw_.mean(1, keepdims=True)) / (sw_.std(1, keepdims=True) + 1e-6)
sel = slice(None, None, 5)
comp = np.einsum("dr,der,dsr,dar,dtr->dresat", lam[sel], u[sel], sx[sel], v[sel], w[sel])   # draws × r × e × s × a × t
varcomp = comp.reshape(comp.shape[0], RMAX, -1).var(2)            # varianza aportada por componente (invariante a signos)
orden = np.argsort(-varcomp, axis=1)
vs = np.take_along_axis(varcomp, orden, 1)
tabla = pd.DataFrame({"componente": np.arange(1, RMAX + 1), "var_logit_media": vs.mean(0), "p05": np.quantile(vs, .05, 0), "p95": np.quantile(vs, .95, 0)})
tabla["pct_de_interaccion"] = 100 * tabla.var_logit_media / tabla.var_logit_media.sum()
tabla.round(4).to_csv(TABLAS / "tensor_bayes_componentes.csv", index=False); print(tabla.round(3))
comp = np.take_along_axis(comp, orden[:, :, None, None, None, None], 1)
edades = np.arange(A)
# gráfica 1: componente principal – efecto edad × elección (media sobre entidad y sexo; el perfil de elección tiene media cero)
fig, axs = plt.subplots(1, 3, figsize=(15, 4.3), sharey=True)
for r, a in enumerate(axs):
    cr = comp[:, r].mean((1, 2))                                   # draws × a × t
    for t, an in enumerate(ANIOS):
        a.plot(edades, cr[:, :, t].mean(0), color=("#d1495b" if an in (2012, 2018, 2024) else "#1b6ca8"), lw=1.6, alpha=.9)
    a.axhline(0, color="k", lw=.5); a.axvspan(A - 2.5, A - .5, color="#999", alpha=.15)
    a.set_xticks(edades[::2]); a.set_xticklabels(ETQ[::2], rotation=45, fontsize=8)
    a.set_title(f"Componente {r+1}: {tabla.pct_de_interaccion[r]:.0f}% de la interacción", fontsize=11); a.set_xlabel("Edad")
axs[0].set_ylabel("Efecto en logit (media entidad y sexo)")
fig.suptitle("Interacciones latentes edad × elección; rojo = presidenciales, azul = intermedias", x=0.01, ha="left", fontsize=11)
guardar(fig, "tensor_bayes_componentes_edad_eleccion.png")
# gráfica 2: amplitud (raíz del promedio de cuadrados) del componente 1 por entidad
amp = np.sqrt((comp[:, 0] ** 2).mean((2, 3, 4)))                   # draws × e
q = pd.DataFrame({"entidad": ents, "media": amp.mean(0), "p05": np.quantile(amp, .05, 0), "p95": np.quantile(amp, .95, 0)}).sort_values("media")
q.round(4).to_csv(TABLAS / "tensor_bayes_entidades.csv", index=False)
fig, ax = plt.subplots(figsize=(7, 7)); ax.errorbar(q["media"], range(E), xerr=[q["media"] - q.p05, q.p95 - q["media"]], fmt="o", color=PAL[0])
ax.set_yticks(range(E)); ax.set_yticklabels(q.entidad.astype(int)); ax.set_xlabel("Amplitud del componente 1 (logit, raíz del promedio de cuadrados)")
ax.set_ylabel("Clave de entidad"); ax.set_title("Intensidad de la interacción por entidad (90% creíble)")
guardar(fig, "tensor_bayes_entidades.png")
print(q.tail(3).round(3)); print(q.head(3).round(3))
