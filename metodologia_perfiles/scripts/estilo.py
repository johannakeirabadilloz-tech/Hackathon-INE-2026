import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import GRAFICAS
PAL = ["#1b6ca8", "#d1495b", "#2a9d8f", "#e9a23b", "#6a4c93", "#6b7280"]
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "figure.dpi": 110, "axes.grid": True, "grid.alpha": .25, "axes.axisbelow": True,
    "axes.prop_cycle": plt.cycler(color=PAL)})
def guardar(fig, nombre):
    fig.savefig(GRAFICAS/nombre, dpi=140, bbox_inches="tight", facecolor="white"); plt.close(fig)
PRES = {2009:"intermedia", 2012:"presidencial", 2015:"intermedia", 2018:"presidencial", 2021:"intermedia", 2024:"presidencial"}
