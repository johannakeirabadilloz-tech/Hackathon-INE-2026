"""Fichas de perfil (infografías): una por perfil y una hoja de panorama. PNG a 250 dpi y un PDF vectorial.
Datos: reports/perfiles_sexo_edad/trayectorias_perfiles.csv (resto de cifras: las del documento técnico).
Uso: python3 23_fichas_perfil.py   (python del sistema, con matplotlib)"""
from pathlib import Path
import textwrap  # noqa: F401  (el ajuste de línea se hace midiendo con el renderizador)

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "reports/fichas_perfil"
OUT.mkdir(parents=True, exist_ok=True)
for f in Path("/usr/share/fonts/google-crosextra-carlito").glob("*.ttf"):
    fm.fontManager.addfont(str(f))
plt.rcParams["font.family"] = "Carlito"

W, H, DPI = 8.5, 13.0, 250
NAVY, GRIS, CLARO, BORDE, ACENTO = "#16233B", "#5B6470", "#F6F4EE", "#E3DFD3", "#B8472F"
HOMBRE, MUJER = "#1B6CA8", "#B8472F"
COL = {1: "#1B6CA8", 2: "#2A9D8F", 3: "#E9A23B", 4: "#D1495B"}
COL_OSC = {1: "#14507C", 2: "#1B7468", 3: "#E9A23B", 4: "#B53A4B"}
TXT_CAB = {1: "#FFFFFF", 2: "#FFFFFF", 3: NAVY, 4: "#FFFFFF"}
ANIOS = [2009, 2012, 2015, 2018, 2021, 2024]
TRAY = pd.read_csv(RAIZ / "reports/perfiles_sexo_edad/trayectorias_perfiles.csv").set_index("perfil_n")

PERFILES = {
    1: dict(nombre="Participación alta", lema="El núcleo adulto", dif=12.7,
            clave="4 de cada 10 personas de la lista nominal están en este perfil.",
            bloques=[("M", "Mujeres de 39 a 77 años", 26.9, 71.0), ("H", "Hombres de 52 a 81 años", 13.4, 70.3),
                     ("M", "Mujeres de 18 años", 0.8, 65.1)],
            edades={"M": [(18, 18), (39, 77)], "H": [(52, 81)]},
            caracteriza=["Es el nivel más alto: 70 a 72 % en presidenciales y 55 a 63 % en intermedias.",
                         "Reúne a 4 de cada 10 personas de la lista nominal.",
                         "Las mujeres llegan a este nivel unos 13 años antes que los hombres (a los 39 frente a los 52)."],
            no_decir="No es un grupo “comprometido” por naturaleza: es un corte de edad. Las mujeres de 18 años están aquí por un salto aislado de la curva.",
            estrategia=["Recordar fecha y lugar de votación, sobre todo en elecciones intermedias.",
                        "Documentar qué acciones locales funcionan antes de llevarlas a otros grupos."],
            medir="Participación en la intermedia de 2027 frente a su trayectoria en intermedias anteriores."),
    2: dict(nombre="Participación intermedia", lema="La transición", dif=14.1,
            bloques=[("M", "Mujeres de 19 a 38 años", 22.2, 56.8), ("H", "Hombres de 37 a 51 años", 13.3, 55.5),
                     ("H", "Hombres de 18 a 19 años", 1.8, 52.7), ("M", "Mujeres de 78 a 83 años", 1.1, 63.7),
                     ("H", "Hombres de 82 a 87 años", 0.6, 62.8)],
            edades={"M": [(19, 38), (78, 83)], "H": [(18, 19), (37, 51), (82, 87)]},
            caracteriza=["Reúne a mujeres jóvenes y a hombres de mediana edad.",
                         "Su participación sube unos 14 puntos de las intermedias a las presidenciales.",
                         "Cayó 4.2 puntos en 2024 frente a 2018."],
            no_decir="Su distancia con el perfil 1 no significa “falta de interés”: el perfil junta dos grupos de naturaleza distinta.",
            estrategia=["Explicar qué se decide en las elecciones intermedias.",
                        "Mensajes distintos para mujeres de 19 a 38 años y hombres de 37 a 51.",
                        "Facilitar el acceso a la casilla con información práctica."],
            medir="Diferencia entre presidencial e intermedia del perfil en 2027 frente a 2021."),
    3: dict(nombre="Participación baja", lema="Sobre todo hombres jóvenes", dif=13.6,
            clave="Casi 1 de cada 5 personas de la lista nominal es un hombre de 20 a 36 años.",
            bloques=[("H", "Hombres de 20 a 36 años", 18.7, 43.3), ("M", "Mujeres de 84 a 89 años", 0.6, 49.6),
                     ("H", "Hombres de 88 a 92 años", 0.2, 48.0)],
            edades={"M": [(84, 89)], "H": [(20, 36), (88, 92)]},
            caracteriza=["Los hombres de 20 a 36 años son casi todo el perfil (18.7 % de la lista nominal).",
                         "Su participación baja de 57.9 % a los 18 años a 45.6 % a los 20.",
                         "Las mujeres de su edad participan hasta 14 puntos más."],
            no_decir="Las personas de 84 a 92 años solo se parecen en el nivel: no hay evidencia de que compartan las razones con los jóvenes.",
            estrategia=["Educación cívica que acompañe la transición del primer voto (hasta los 20 a 22 años).",
                        "Canales y formatos propios; contacto donde ya se relacionan con la institución."],
            medir="Participación de hombres de 18 a 24 años en secciones piloto frente a secciones de comparación."),
    4: dict(nombre="Edades muy avanzadas (90+)", lema="El perfil más pequeño", dif=9.6,
            clave="Solo 4 de cada 1,000 personas de la lista nominal están en este perfil; por eso se lee con reserva.",
            bloques=[("M", "Mujeres de 90 a 99 años", 0.3, 30.9), ("H", "Hombres de 93 a 99 años", 0.1, 31.8)],
            edades={"M": [(90, 99)], "H": [(93, 99)]},
            caracteriza=["Participación de 11 % a 31 % según la elección.",
                         "Representa solo 0.4 % de la lista nominal.",
                         "Es el perfil que menos reacciona al ciclo electoral."],
            no_decir="Puede estar mal medido: el padrón podría incluir personas fallecidas o que ya no viven ahí. No se verificó.",
            estrategia=["Verificar el padrón antes de actuar.",
                        "Si la baja participación es real: información accesible y apoyo de movilidad."],
            medir="Cambio en la participación solo en secciones donde el padrón se verificó."),
}


# ------------------------------------------------------------------ utilidades de dibujo
class Lienzo:
    def __init__(self):
        self.fig = plt.figure(figsize=(W, H), dpi=100, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.axis("off")
        self.rend = self.fig.canvas.get_renderer()

    def ancho(self, texto, tam, peso="normal"):
        t = self.ax.text(0, 0, texto, fontsize=tam, fontweight=peso)
        w = t.get_window_extent(self.rend).width / self.fig.dpi
        t.remove()
        return w

    def envolver(self, texto, tam, ancho, peso="normal"):
        lineas, actual = [], ""
        for pal in texto.split():
            prueba = (actual + " " + pal).strip()
            if self.ancho(prueba, tam, peso) <= ancho or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = pal
        if actual:
            lineas.append(actual)
        return lineas

    def parrafo(self, x, y, texto, tam, ancho, color=NAVY, peso="normal", interlinea=1.28, estilo="normal"):
        """Dibuja texto envuelto desde y hacia abajo; devuelve la y final."""
        paso = tam / 72 * interlinea
        for ln in self.envolver(texto, tam, ancho, peso):
            self.ax.text(x, y, ln, fontsize=tam, color=color, fontweight=peso, fontstyle=estilo, va="top", ha="left")
            y -= paso
        return y

    def vinetas(self, x, y, items, tam, ancho, color=NAVY, marca=NAVY, sep=0.07):
        for it in items:
            self.ax.add_patch(Circle((x + 0.05, y - tam / 72 * 0.62), 0.045, color=marca, lw=0))
            y = self.parrafo(x + 0.2, y, it, tam, ancho - 0.2, color=color) - sep
        return y

    def caja(self, x, y, w, h, relleno="#FFFFFF", borde=BORDE, radio=0.08, lw=1.0):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radio}", fc=relleno, ec=borde, lw=lw))

    def eje(self, x, y, w, h, **kw):
        return self.fig.add_axes([x / W, y / H, w / W, h / H], **kw)

    def guardar(self, ruta_png):
        self.fig.savefig(ruta_png, dpi=DPI, facecolor="white")

    def cerrar(self):
        plt.close(self.fig)


# ------------------------------------------------------------------ íconos (formas simples)
def persona(ax, x, y, h, sexo):
    c = MUJER if sexo == "M" else HOMBRE
    ax.add_patch(Circle((x, y + h * 0.86), h * 0.13, color=c, lw=0))
    if sexo == "M":
        ax.add_patch(Polygon([(x - h * 0.24, y), (x + h * 0.24, y), (x, y + h * 0.68)], closed=True, color=c, lw=0))
    else:
        ax.add_patch(FancyBboxPatch((x - h * 0.15, y), h * 0.30, h * 0.66, boxstyle=f"round,pad=0,rounding_size={h * 0.08}", color=c, lw=0))


def urna(ax, x, y, s, c="#FFFFFF"):
    """Urna con boleta: x,y = esquina inferior izquierda."""
    ax.add_patch(Rectangle((x + s * 0.30, y + s * 0.55), s * 0.40, s * 0.38, fc=c, ec=c, lw=0))
    ax.plot([x + s * 0.38, x + s * 0.47, x + s * 0.64], [y + s * 0.72, y + s * 0.62, y + s * 0.84], color=NAVY, lw=1.4, solid_capstyle="round", zorder=5)
    ax.add_patch(FancyBboxPatch((x, y), s, s * 0.62, boxstyle=f"round,pad=0,rounding_size={s * 0.06}", fc=c, ec=c, lw=0))
    ax.add_patch(Rectangle((x + s * 0.25, y + s * 0.44), s * 0.5, s * 0.06, fc=NAVY, lw=0, zorder=6))


def calendario(ax, x, y, s, c):
    ax.add_patch(FancyBboxPatch((x, y), s, s * 0.9, boxstyle=f"round,pad=0,rounding_size={s * 0.08}", fc="#FFFFFF", ec=c, lw=1.6))
    ax.add_patch(Rectangle((x, y + s * 0.62), s, s * 0.28, fc=c, lw=0))
    for i in range(3):
        for j in range(2):
            ax.add_patch(Rectangle((x + s * (0.15 + 0.27 * i), y + s * (0.12 + 0.2 * j)), s * 0.16, s * 0.12, fc=c, lw=0, alpha=.8))


def foco(ax, x, y, s, c):
    ax.add_patch(Circle((x, y + s * 0.62), s * 0.34, fc=c, ec=c, lw=0))
    ax.add_patch(Rectangle((x - s * 0.16, y + s * 0.06), s * 0.32, s * 0.12, fc=c, lw=0))
    ax.add_patch(Rectangle((x - s * 0.12, y + s * 0.20), s * 0.24, s * 0.08, fc=c, lw=0))


def aviso(ax, x, y, s, c):
    ax.add_patch(Polygon([(x - s * 0.5, y), (x + s * 0.5, y), (x, y + s * 0.88)], closed=True, fc=c, ec=c, lw=0))
    ax.text(x, y + s * 0.10, "!", ha="center", va="bottom", fontsize=s * 38, color="#FFFFFF", fontweight="bold")


# ------------------------------------------------------------------ gráficas
def franja_edades(L, x, y, w, h, perfil, d):
    ax = L.eje(x, y, w, h)
    ax.set_xlim(18, 100)
    ax.set_ylim(0, 2)
    for fila, sexo, etq in ((1, "M", "Mujeres"), (0, "H", "Hombres")):
        ax.add_patch(Rectangle((18, fila + 0.1), 82, 0.8, fc="#EFEBE1", lw=0))
        for lo, hi in d["edades"].get(sexo, []):
            ax.add_patch(Rectangle((lo, fila + 0.1), hi - lo + 1, 0.8, fc=COL[perfil], lw=0))
            if hi - lo >= 6:
                ax.text((lo + hi + 1) / 2, fila + 0.5, f"{lo} a {hi}", ha="center", va="center", fontsize=10, fontweight="bold",
                        color=TXT_CAB[perfil])
        ax.text(17, fila + 0.5, etq, ha="right", va="center", fontsize=10.5, color=NAVY)
    ax.set_yticks([])
    ax.set_xticks([20, 40, 60, 80, 99])
    ax.tick_params(axis="x", labelsize=10, colors=GRIS, length=3)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BORDE)
    return ax


def trayectoria(L, x, y, w, h, perfil=None, todos=False):
    ax = L.eje(x, y, w, h)
    for a in (2012, 2018, 2024):
        ax.axvspan(a - 1.3, a + 1.3, color="#EEEAE0", lw=0)
    for p in (1, 2, 3, 4):
        v = TRAY.loc[p, [str(a) for a in ANIOS]].values.astype(float)
        if todos or p == perfil:
            ax.plot(ANIOS, v, color=COL[p], lw=2.6, marker="o", ms=5, zorder=4)
            if todos:
                ax.text(2024.9, v[-1], f"{p}", color=COL[p], fontsize=11, fontweight="bold", va="center")
            else:
                for a, val in zip(ANIOS, v):
                    ax.text(a, val + 3.2, f"{val:.0f}", ha="center", fontsize=9.5, color=NAVY)
        else:
            ax.plot(ANIOS, v, color="#C9C4B6", lw=1.3, zorder=2)
    ax.set_ylim(0, 85)
    ax.set_xlim(2007.5, 2025.8)
    ax.set_xticks(ANIOS)
    ax.tick_params(labelsize=9.5, colors=GRIS, length=3)
    ax.set_yticks([0, 25, 50, 75])
    ax.set_yticklabels(["0 %", "25 %", "50 %", "75 %"])
    ax.grid(axis="y", color=BORDE, lw=.7)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BORDE)
    return ax


# ------------------------------------------------------------------ ficha
def ficha(p):
    d = PERFILES[p]
    L = Lienzo()
    ax, c, co = L.ax, COL[p], COL_OSC[p]
    tc = TXT_CAB[p]
    # cabecera
    ax.add_patch(Rectangle((0, 11.55), W, 1.45, fc=co, lw=0))
    ax.text(0.55, 12.62, f"PERFIL {p}", fontsize=13, color=tc, fontweight="bold", va="top", alpha=.9)
    ax.text(0.55, 12.28, d["nombre"], fontsize=29, color=tc, fontweight="bold", va="top")
    ax.text(0.55, 11.72, d["lema"], fontsize=15, color=tc, va="bottom", fontstyle="italic")
    ax.add_patch(Circle((7.55, 12.28), 0.52, fc="#FFFFFF", lw=0, alpha=.95))
    urna(ax, 7.55 - 0.3, 12.28 - 0.28, 0.6, c=co)
    # indicadores
    kp = [(f"{TRAY.loc[p, '2024']:.1f} %", "participó en 2024"), (f"{TRAY.loc[p, 'pct_lista_2024']:.1f} %", "de la lista nominal"),
          (f"+{d['dif']:.1f}", "puntos en presidenciales frente a intermedias")]
    xs = [0.55, 3.0, 5.45]
    for (v, etq), x0 in zip(kp, xs):
        L.caja(x0, 10.15, 2.4, 1.1, relleno=CLARO)
        ax.text(x0 + 0.2, 11.02, v, fontsize=26, color=co if p != 3 else "#9A5F00", fontweight="bold", va="top")
        L.parrafo(x0 + 0.2, 10.5, etq, 10.5, 2.05, color=GRIS, interlinea=1.15)
    # quiénes son
    ax.text(0.55, 9.9, "Quiénes son", fontsize=15, color=NAVY, fontweight="bold", va="top")
    ax.add_patch(Rectangle((0.55, 9.58), 0.5, 0.04, fc=c, lw=0))
    y = 9.38
    for sexo, txt, lista, part in d["bloques"]:
        persona(ax, 0.82, y - 0.33, 0.30, sexo)
        ax.text(1.2, y - 0.17, txt, fontsize=12.5, color=NAVY, fontweight="bold", va="center")
        ax.text(7.95, y - 0.17, f"{lista:.1f} % de la lista · {part:.1f} % participó", fontsize=11, color=GRIS, ha="right", va="center")
        y -= 0.37
    if d.get("clave"):
        tope, fondo = y + 0.02, 7.5
        L.caja(0.55, fondo, 7.4, tope - fondo, relleno=CLARO, borde=BORDE)
        ax.add_patch(Rectangle((0.55, fondo), 0.09, tope - fondo, fc=c, lw=0))
        lin = L.envolver(d["clave"], 13, 6.7, "bold")
        paso = 13 / 72 * 1.3
        y0 = (tope + fondo) / 2 + paso * (len(lin) - 1) / 2
        for k, ln in enumerate(lin):
            ax.text(0.9, y0 - k * paso, ln, fontsize=13, color=NAVY, fontweight="bold", va="center")
    # edades del perfil
    ax.text(0.55, 7.28, "Edades del perfil", fontsize=15, color=NAVY, fontweight="bold", va="top")
    ax.add_patch(Rectangle((0.55, 6.96), 0.5, 0.04, fc=c, lw=0))
    franja_edades(L, 1.75, 5.95, 6.2, 0.92, p, d)
    # trayectoria + características
    ax.text(0.55, 5.72, "Su participación, 2009 a 2024", fontsize=15, color=NAVY, fontweight="bold", va="top")
    ax.add_patch(Rectangle((0.55, 5.4), 0.5, 0.04, fc=c, lw=0))
    trayectoria(L, 0.55, 3.72, 3.75, 1.62, perfil=p)
    ax.text(0.6, 3.36, "Sombreado: elecciones presidenciales. En gris, los otros perfiles.", fontsize=8.8, color=GRIS, va="top", fontstyle="italic")
    ax.text(4.6, 5.72, "Qué lo caracteriza", fontsize=15, color=NAVY, fontweight="bold", va="top")
    ax.add_patch(Rectangle((4.6, 5.4), 0.5, 0.04, fc=c, lw=0))
    L.vinetas(4.6, 5.25, d["caracteriza"], 11.5, 3.35, marca=c)
    # qué no se puede decir
    L.caja(0.55, 2.35, 7.4, 0.85, relleno="#FBF3E4", borde="#E9D6A8")
    aviso(ax, 0.95, 2.62, 0.38, "#C8821A")
    ax.text(1.4, 3.08, "Qué no se puede decir", fontsize=11.5, color="#8A5A0C", fontweight="bold", va="top")
    L.parrafo(1.4, 2.84, d["no_decir"], 11, 6.4, color=NAVY, interlinea=1.2)
    # estrategia
    L.caja(0.55, 0.62, 7.4, 1.55, relleno="#FFFFFF", borde=c, lw=2.0)
    foco(ax, 1.0, 1.55, 0.5, c)
    ax.text(1.5, 2.04, "Estrategia a probar", fontsize=13.5, color=NAVY, fontweight="bold", va="top")
    y2 = L.vinetas(1.5, 1.78, d["estrategia"], 10.8, 6.2, marca=c, sep=0.03)
    L.parrafo(1.5, y2 - 0.02, "Cómo medirlo: " + d["medir"], 9.8, 6.2, color=GRIS, estilo="italic", interlinea=1.15)
    # pie
    ax.text(0.55, 0.28, "Perfiles de participación electoral · Datos del INE, elecciones 2009 a 2024 · Describen grupos, no personas; las estrategias son hipótesis a probar.",
            fontsize=8, color=GRIS, va="center")
    return L


# ------------------------------------------------------------------ panorama
def panorama():
    L = Lienzo()
    ax = L.ax
    ax.add_patch(Rectangle((0, 11.2), W, 1.8, fc=NAVY, lw=0))
    ax.text(0.55, 12.62, "HACKATHON INE 2026 · RETO 1", fontsize=11, color="#E9A23B", fontweight="bold", va="top")
    ax.text(0.55, 12.28, "Cuatro perfiles de participación", fontsize=27, color="#F6F4EE", fontweight="bold", va="top")
    ax.text(0.55, 11.72, "electoral en México, 2009 a 2024", fontsize=27, color="#F6F4EE", fontweight="bold", va="top")
    L.parrafo(0.55, 10.95, "La participación cambia sobre todo con la edad, y el sexo desplaza el momento. Cuatro perfiles resumen ese patrón: cada uno "
              "participa de forma distinta y conviene atenderlo con estrategias distintas.", 12.5, 7.4, color=NAVY)
    ax.text(0.55, 9.75, "Participación de cada perfil, 2009 a 2024", fontsize=14.5, color=NAVY, fontweight="bold", va="top")
    ax.add_patch(Rectangle((0.55, 9.43), 0.5, 0.04, fc=ACENTO, lw=0))
    trayectoria(L, 0.7, 7.5, 6.9, 1.8, todos=True)
    ax.text(0.7, 7.12, "Sombreado: elecciones presidenciales. Los números indican el perfil.", fontsize=9, color=GRIS, va="top", fontstyle="italic")
    # tarjetas 2x2
    pos = {1: (0.55, 4.0), 2: (4.35, 4.0), 3: (0.55, 1.1), 4: (4.35, 1.1)}
    for p, (x0, y0) in pos.items():
        d = PERFILES[p]
        L.caja(x0, y0, 3.6, 2.6, relleno="#FFFFFF", borde=BORDE)
        ax.add_patch(FancyBboxPatch((x0, y0 + 2.05), 3.6, 0.55, boxstyle="round,pad=0,rounding_size=0.08", fc=COL_OSC[p], ec=COL_OSC[p]))
        ax.text(x0 + 0.2, y0 + 2.33, f"{p}. {d['nombre']}", fontsize=13.5, color=TXT_CAB[p], fontweight="bold", va="center")
        ax.text(x0 + 0.2, y0 + 1.95, f"{TRAY.loc[p, '2024']:.1f} %", fontsize=27, color=COL_OSC[p] if p != 3 else "#9A5F00", fontweight="bold", va="top")
        ax.text(x0 + 1.75, y0 + 1.72, f"participó en 2024\n{TRAY.loc[p, 'pct_lista_2024']:.1f} % de la lista", fontsize=10.5, color=GRIS, va="top", linespacing=1.15)
        yy = y0 + 1.28
        for sexo, txt, lista, part in d["bloques"][:3 if p != 2 else 2]:
            persona(ax, x0 + 0.32, yy - 0.34, 0.27, sexo)
            ax.text(x0 + 0.6, yy - 0.2, txt, fontsize=10.6, color=NAVY, va="center")
            yy -= 0.38
        if p == 2:
            ax.text(x0 + 0.6, yy - 0.16, "y tramos pequeños", fontsize=9.6, color=GRIS, va="center", fontstyle="italic")
    L.parrafo(0.55, 0.85, "Los perfiles son cortes útiles de una curva continua, no grupos naturales: se distinguen por su nivel de participación y su "
              "trayectoria. Describen grupos de personas, no a personas ni sus motivos.", 9.8, 7.4, color=GRIS, estilo="italic", interlinea=1.2)
    ax.text(0.55, 0.28, "Datos del INE (conteos de participación ciudadana), elecciones 2009 a 2024. Participación = votaron ÷ (votaron + no votaron).",
            fontsize=8, color=GRIS, va="center")
    return L


if __name__ == "__main__":
    paginas = [("00_panorama_perfiles", panorama())]
    nombres = {1: "participacion_alta", 2: "participacion_intermedia", 3: "participacion_baja", 4: "edades_muy_avanzadas"}
    for p in (1, 2, 3, 4):
        paginas.append((f"ficha_{p}_{nombres[p]}", ficha(p)))
    with PdfPages(OUT / "Fichas_de_perfil.pdf") as pdf:
        for nombre, L in paginas:
            L.guardar(OUT / f"{nombre}.png")
            pdf.savefig(L.fig, facecolor="white")
            L.cerrar()
    print("listo:", sorted(x.name for x in OUT.iterdir()))
