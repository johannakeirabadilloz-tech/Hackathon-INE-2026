"""Genera el documento técnico (Word y PDF) a partir de documento_tecnico_contenido.py.
Formato pedido: Calibri 11, interlineado 1.5, hoja carta, márgenes de 2.5 cm.
El PDF incrusta Carlito (fuente con las mismas medidas que Calibri); el Word usa Calibri.
Uso: python3 22_documento_tecnico.py  (python del sistema con python-docx y fpdf2)"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import documento_tecnico_contenido as C

OUT = C.RAIZ / "reports/documento_tecnico"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, ACCENT, GRAY = (22, 35, 59), (184, 71, 47), (90, 100, 112)
FUENTE = "Carlito"
RUTA_FUENTE = Path("/usr/share/fonts/google-crosextra-carlito")


def partes(texto):
    """Divide 'a **b** c' en [(a, False), (b, True), (c, False)]."""
    out = []
    for i, p in enumerate(re.split(r"\*\*", texto)):
        if p:
            out.append((p, i % 2 == 1))
    return out


# =============================================================== PDF
def construir_pdf(ruta):
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fpdf.fonts import FontFace
    from PIL import Image

    class Doc(FPDF):
        def footer(self):
            self.set_y(-42)
            self.set_font(FUENTE, "", 9)
            self.set_text_color(*GRAY)
            self.cell(0, 12, f"Perfiles ciudadanos de participación electoral · Página {self.page_no()}", align="C")

    pdf = Doc(orientation="P", unit="pt", format="Letter")
    for est, f in (("", "Regular"), ("B", "Bold"), ("I", "Italic"), ("BI", "BoldItalic")):
        pdf.add_font(FUENTE, est, str(RUTA_FUENTE / f"Carlito-{f}.ttf"))
    pdf.set_margins(70.9, 64, 70.9)
    pdf.set_auto_page_break(True, 58)
    pdf.set_title(C.TITULO)
    pdf.set_author("Equipo del proyecto")
    pdf.add_page()
    W = pdf.w - pdf.l_margin - pdf.r_margin
    LH = 20  # 11 pt × 1.22 (alto natural de Calibri) × 1.5 ≈ 20 pt

    def libre():
        return pdf.h - pdf.b_margin - pdf.get_y()

    def md(texto, ancho=None, alto=LH, **kw):
        pdf.multi_cell(ancho or W, alto, texto, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT, **kw)

    def cuerpo():
        pdf.set_font(FUENTE, "", 11)
        pdf.set_text_color(25, 25, 25)

    # --- portada compacta
    pdf.set_font(FUENTE, "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(W, 27, C.TITULO, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_font(FUENTE, "", 12)
    pdf.set_text_color(*GRAY)
    pdf.multi_cell(W, 16, C.SUBTITULO, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FUENTE, "B", 11)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(W, 16, C.PROYECTO, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FUENTE, "I", 10.5)
    pdf.set_text_color(*GRAY)
    pdf.multi_cell(W, 15, C.EQUIPO, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(1.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 90, pdf.get_y())
    pdf.ln(8)

    def encabezado(nivel, texto):
        tam, alto, antes = {1: (15, 20, 12), 2: (12.5, 18, 8), 3: (11.5, 16, 5)}[nivel]
        if libre() < 95:
            pdf.add_page()
        pdf.ln(antes)
        pdf.set_font(FUENTE, "B", tam)
        pdf.set_text_color(*(NAVY if nivel < 3 else ACCENT))
        pdf.multi_cell(W, alto, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        cuerpo()

    def nota(texto):
        pdf.set_font(FUENTE, "I", 9.5)
        pdf.set_text_color(*GRAY)
        pdf.multi_cell(W, 12, texto, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        cuerpo()

    def altura_tabla(d):
        cols = [w * W for w in d["widths"]]
        alto = 0
        for fila in [d["header"]] + d["rows"]:
            lin = max(-(-len(c.replace("**", "")) * 4.9 // max(cols[k] - 9, 20)) for k, c in enumerate(fila))
            alto += lin * 13 + 5.5
        return alto

    def altura_min(b):
        """Altura mínima que debe caber junto a un título para no dejarlo solo al final de la página."""
        t = b[0]
        if t in ("h1", "h2", "h3"):
            return 40
        if t == "p":
            return 3 * LH
        if t in ("bullets", "numbered"):
            return 3 * LH
        if t == "table":
            return altura_tabla(b[1]) + 14
        if t == "image":
            im = Image.open(b[1])
            return b[2] * 28.3465 * im.height / im.width + 50
        if t == "callout":
            return 110
        return 40

    def tabla(d):
        cols = [w * W for w in d["widths"]]
        al = {"L": "LEFT", "C": "CENTER"}
        pdf.set_font(FUENTE, "", 10)
        pdf.set_text_color(25, 25, 25)
        alto_t = altura_tabla(d)
        if libre() < alto_t + 14:
            pdf.add_page()
        pdf.ln(2)
        pdf.set_fill_color(255, 255, 255)
        enc = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=NAVY)
        with pdf.table(col_widths=cols, text_align=tuple(al[a] for a in d["align"]), line_height=13, width=W,
                       headings_style=enc, borders_layout="HORIZONTAL_LINES", padding=(2.5, 4)) as t:
            fila = t.row()
            for h in d["header"]:
                fila.cell(h)
            for r in d["rows"]:
                fila = t.row()
                for c in r:
                    if c.startswith("**") and c.endswith("**") and c.count("**") == 2:
                        fila.cell(c[2:-2], style=FontFace(emphasis="BOLD"))
                    else:
                        fila.cell(c.replace("**", ""))
        pdf.ln(5)
        cuerpo()
        if d.get("note"):
            nota(d["note"])
        else:
            pdf.ln(2)

    def imagen(ruta, ancho_cm, pie):
        w = ancho_cm * 28.3465
        im = Image.open(ruta)
        h = w * im.height / im.width
        if libre() < h + 50:
            pdf.add_page()
        pdf.image(str(ruta), x=pdf.l_margin + (W - w) / 2, y=pdf.get_y(), w=w)
        pdf.set_y(pdf.get_y() + h + 4)
        nota(pie)

    def callout(titulo, texto):
        pdf.set_font(FUENTE, "", 11)
        lineas = pdf.multi_cell(W - 28, LH - 2, texto, dry_run=True, output="LINES")
        alto = 20 + len(lineas) * (LH - 2) + 16
        if libre() < alto + 10:
            pdf.add_page()
        x, y = pdf.l_margin, pdf.get_y()
        pdf.set_fill_color(245, 239, 230)
        pdf.rect(x, y, W, alto, style="F")
        pdf.set_fill_color(*ACCENT)
        pdf.rect(x, y, 5, alto, style="F")
        pdf.set_xy(x + 16, y + 8)
        pdf.set_font(FUENTE, "B", 11)
        pdf.set_text_color(*ACCENT)
        pdf.cell(W - 28, 16, titulo, new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_x(x + 16)
        pdf.set_font(FUENTE, "", 11)
        pdf.set_text_color(25, 25, 25)
        pdf.multi_cell(W - 28, LH - 2, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_y(y + alto + 10)
        cuerpo()

    cuerpo()
    for idx, b in enumerate(C.BLOQUES):
        t = b[0]
        if t in ("h1", "h2", "h3"):
            # título + (otros títulos seguidos) + el primer bloque de contenido deben caber juntos
            need, k = 0, idx
            while k < len(C.BLOQUES) and C.BLOQUES[k][0] in ("h1", "h2", "h3"):
                need += {"h1": 44, "h2": 36, "h3": 30}[C.BLOQUES[k][0]]
                k += 1
            if k < len(C.BLOQUES):
                need += altura_min(C.BLOQUES[k])
            if libre() < need:
                pdf.add_page()
        if t == "h1":
            encabezado(1, b[1])
        elif t == "h2":
            encabezado(2, b[1])
        elif t == "h3":
            encabezado(3, b[1])
        elif t == "p":
            cuerpo()
            md(b[1])
            pdf.ln(5)
        elif t in ("bullets", "numbered"):
            cuerpo()
            for i, item in enumerate(b[1], 1):
                marca = "•" if t == "bullets" else f"{i}."
                pdf.set_x(pdf.l_margin + 4)
                pdf.cell(20, LH, marca)
                pdf.multi_cell(W - 24, LH, item, markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(2)
            pdf.ln(3)
        elif t == "table":
            tabla(b[1])
        elif t == "image":
            imagen(b[1], b[2], b[3])
        elif t == "callout":
            callout(b[1], b[2])
    pdf.output(str(ruta))
    return pdf.page_no()


# =============================================================== WORD
def construir_docx(ruta):
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
    sec.left_margin = sec.right_margin = Cm(2.5)
    sec.top_margin = Cm(2.3)
    sec.bottom_margin = Cm(2.3)
    ancho_cm = 21.59 - 5.0

    def fuente(estilo, nombre="Calibri", tam=None, negrita=None, color=None, cursiva=None):
        estilo.font.name = nombre
        rpr = estilo.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(a), nombre)
        if tam:
            estilo.font.size = Pt(tam)
        if negrita is not None:
            estilo.font.bold = negrita
        if cursiva is not None:
            estilo.font.italic = cursiva
        if color:
            estilo.font.color.rgb = RGBColor(*color)

    normal = doc.styles["Normal"]
    fuente(normal, tam=11)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    for nombre, tam, color, antes in (("Heading 1", 15, NAVY, 14), ("Heading 2", 12.5, NAVY, 10), ("Heading 3", 11.5, ACCENT, 6)):
        e = doc.styles[nombre]
        fuente(e, tam=tam, negrita=True, color=color, cursiva=False)
        e.paragraph_format.line_spacing = 1.15
        e.paragraph_format.space_before = Pt(antes)
        e.paragraph_format.space_after = Pt(4)
        e.paragraph_format.keep_with_next = True
    fuente(doc.styles["List Bullet"], tam=11)
    doc.styles["List Bullet"].paragraph_format.line_spacing = 1.5
    doc.styles["List Bullet"].paragraph_format.space_after = Pt(3)

    def runs(p, texto, tam=None, cursiva=None, color=None, negrita_total=False):
        for t, neg in partes(texto):
            r = p.add_run(t)
            r.bold = True if (neg or negrita_total) else None
            if tam:
                r.font.size = Pt(tam)
            if cursiva:
                r.italic = True
            if color:
                r.font.color.rgb = RGBColor(*color)
            r.font.name = "Calibri"

    def insertar(padre, hijo, sucesores):
        """Inserta `hijo` antes del primer elemento de `sucesores` que exista (respeta el orden del esquema)."""
        for tag in sucesores:
            e = padre.find(qn(tag))
            if e is not None:
                e.addprevious(hijo)
                return
        padre.append(hijo)

    def sombrear(celda, hexa):
        tcpr = celda._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hexa)
        tcpr.append(shd)

    def bordes(tabla, color="D9D4C7"):
        tblpr = tabla._tbl.tblPr
        b = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), color)
            b.append(e)
        insertar(tblpr, b, ["w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription"])

    def compacto(p, tam=10):
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_after = Pt(1)
        pf.space_before = Pt(1)

    # --- portada compacta
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.1
    runs(p, C.TITULO, tam=22, color=NAVY, negrita_total=True)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    runs(p, C.SUBTITULO, tam=12, color=GRAY)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    runs(p, C.PROYECTO, tam=11, color=ACCENT, negrita_total=True)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    runs(p, C.EQUIPO, tam=10.5, color=GRAY, cursiva=True)
    pb = OxmlElement("w:pBdr")
    bt = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "12"), ("w:space", "4"), ("w:color", "B8472F")):
        bt.set(qn(k), v)
    pb.append(bt)
    insertar(p._p.get_or_add_pPr(), pb, ["w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
             "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
             "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
             "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"])

    def pie_nota(texto):
        p = doc.add_paragraph()
        compacto(p)
        p.paragraph_format.space_after = Pt(8)
        runs(p, texto, tam=9.5, cursiva=True, color=GRAY)

    def tabla(d):
        n = len(d["header"])
        t = doc.add_table(rows=1 + len(d["rows"]), cols=n)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        bordes(t)
        total = ancho_cm
        anchos = [Cm(total * w) for w in d["widths"]]
        al = {"L": WD_ALIGN_PARAGRAPH.LEFT, "C": WD_ALIGN_PARAGRAPH.CENTER}
        for i, h in enumerate(d["header"]):
            c = t.rows[0].cells[i]
            c.width = anchos[i]
            sombrear(c, "16233B")
            p = c.paragraphs[0]
            compacto(p)
            p.alignment = al[d["align"][i]]
            runs(p, h, tam=10, color=(255, 255, 255), negrita_total=True)
        for ri, fila in enumerate(d["rows"], 1):
            for i, txt in enumerate(fila):
                c = t.rows[ri].cells[i]
                c.width = anchos[i]
                p = c.paragraphs[0]
                compacto(p)
                p.alignment = al[d["align"][i]]
                runs(p, txt, tam=10)
        # evita que una fila se parta entre páginas
        for r in t.rows:
            trpr = r._tr.get_or_add_trPr()
            e = OxmlElement("w:cantSplit")
            trpr.append(e)
        if d.get("note"):
            pie_nota(d["note"])
        else:
            sp = doc.add_paragraph()
            compacto(sp)
            sp.paragraph_format.space_after = Pt(4)

    def callout(titulo, texto):
        t = doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t.rows[0].cells[0]
        c.width = Cm(ancho_cm)
        sombrear(c, "F5EFE6")
        p = c.paragraphs[0]
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(2)
        runs(p, titulo, color=ACCENT, negrita_total=True)
        p2 = c.add_paragraph()
        p2.paragraph_format.line_spacing = 1.3
        runs(p2, texto)
        sp = doc.add_paragraph()
        compacto(sp)

    for b in C.BLOQUES:
        t = b[0]
        if t in ("h1", "h2", "h3"):
            doc.add_heading(b[1], level=int(t[1]))
        elif t == "p":
            runs(doc.add_paragraph(), b[1])
        elif t == "bullets":
            for item in b[1]:
                runs(doc.add_paragraph(style="List Bullet"), item)
        elif t == "numbered":
            for i, item in enumerate(b[1], 1):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.9)
                p.paragraph_format.first_line_indent = Cm(-0.6)
                p.paragraph_format.space_after = Pt(3)
                runs(p, f"{i}.  " + item)
        elif t == "table":
            tabla(b[1])
        elif t == "image":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.0
            p.add_run().add_picture(str(b[1]), width=Cm(b[2]))
            pie_nota(b[3])
        elif t == "callout":
            callout(b[1], b[2])

    # número de página en el pie
    pf = sec.footer.paragraphs[0]
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = pf.add_run("Perfiles ciudadanos de participación electoral · Página ")
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(*GRAY)
    r2 = pf.add_run()
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(*GRAY)
    for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        r2._r.append(e)
    for z in doc.settings.element.findall(qn("w:zoom")):
        if z.get(qn("w:percent")) is None:
            z.set(qn("w:percent"), "100")
    doc.core_properties.title = C.TITULO
    doc.core_properties.author = "Equipo del proyecto"
    doc.save(str(ruta))


if __name__ == "__main__":
    n = construir_pdf(OUT / "Documento_tecnico_perfiles.pdf")
    construir_docx(OUT / "Documento_tecnico_perfiles.docx")
    print("páginas del PDF:", n)
