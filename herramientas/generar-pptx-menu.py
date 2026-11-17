"""Arma el PowerPoint de «My Menu» (Inglés, 1° básico) a partir de la presentación web.

Lee las diapositivas del bloque <script id="datos"> de my-menu-presentacion.html,
así el PowerPoint dice exactamente lo mismo que la página. Las imágenes salen de
img-menu/ (cualquier .jpg, .jpeg, .png o .webp); si falta alguna, pone un
recuadro con el emoji para que se note qué falta.

Requisitos (una sola vez):
    pip install python-pptx pillow

Uso (desde la raíz del repositorio):
    python herramientas/generar-pptx-menu.py
        → 1-basico/semestre-2/ingles/my-menu-presentacion.pptx (sin nombre, va al repositorio)

    python herramientas/generar-pptx-menu.py --nombre "Nombre"
        → privado/my-menu-<nombre>.pptx (con su nombre en la portada; la carpeta
          privado/ está en .gitignore y NO se sube a GitHub)

Las imágenes se recortan cuadradas y se achican a 1000 px dentro del archivo,
para que el PowerPoint pese poco y corra fluido en el computador del colegio.
"""
from pathlib import Path
import argparse
import io
import json
import re
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont, ImageOps
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "1-basico" / "semestre-2" / "ingles"
HTML = CARPETA / "my-menu-presentacion.html"
IMG = CARPETA / "img-menu"
EXT = (".jpg", ".jpeg", ".png", ".webp")
DATOS_RE = re.compile(r'<script type="application/json" id="datos">(.*?)</script>', re.S)

FUENTE = "Calibri"            # está en cualquier computador con Office
NEGRO = RGBColor(0x00, 0x00, 0x00)
TEXTO = RGBColor(0x19, 0x19, 0x19)
GRIS = RGBColor(0x8C, 0x8C, 0x8C)
BORDE = RGBColor(0xE6, 0xE6, 0xE6)
LAVADO = RGBColor(0xF8, 0xF8, 0xF8)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
ACENTO = RGBColor(0x31, 0x7C, 0xFF)


# El diseño está hecho en un lienzo de 1600x900 (igual que la página web).
# 1 px del lienzo = 7620 EMU → 13,333 x 7,5 pulgadas (16:9).
def px(v):
    return Emu(int(round(v * 7620)))


def pt(v):
    """Tamaño de letra en px del lienzo → puntos."""
    return Pt(round(v * 0.6, 1))


# ---------------------------------------------------------------- imágenes
def busca(nombre):
    for e in EXT:
        f = IMG / f"{nombre}{e}"
        if f.exists():
            return f
    return None


def emoji_png(emoji, lado, fondo=(248, 248, 248)):
    """Recuadro de respaldo con el emoji (para ver qué imagen falta)."""
    im = Image.new("RGB", (lado, lado), fondo)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("seguiemj.ttf", int(lado * 0.42))
        d.text((lado / 2, lado / 2), emoji, font=f, anchor="mm", embedded_color=True)
    except OSError:
        d.text((lado / 2, lado / 2), "?", fill=(140, 140, 140), anchor="mm")
    return im


def foto(nombre, emoji, ancho, alto, lado_max=1000):
    """Devuelve la imagen recortada al tamaño pedido (como object-fit: cover)."""
    f = busca(nombre)
    if f:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    else:
        im = emoji_png(emoji, 800)
    factor = lado_max / max(ancho, alto)
    tam = (round(ancho * factor), round(alto * factor))
    im = ImageOps.fit(im, tam, Image.LANCZOS, centering=(0.5, 0.5))
    return im, f is not None


def a_bytes(im, formato="JPEG"):
    b = io.BytesIO()
    if formato == "JPEG":
        im.save(b, "JPEG", quality=84, optimize=True, progressive=True)
    else:
        im.save(b, "PNG", optimize=True)
    b.seek(0)
    return b


def redonda(im):
    """Recorta en círculo (PNG con transparencia), para el ícono de cada comida."""
    lado = min(im.size)
    im = ImageOps.fit(im, (lado, lado))
    mascara = Image.new("L", (lado * 4, lado * 4), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, lado * 4, lado * 4), fill=255)
    mascara = mascara.resize((lado, lado), Image.LANCZOS)
    out = im.convert("RGBA")
    out.putalpha(mascara)
    return out


# ---------------------------------------------------------------- formas
def caja(sl, x, y, w, h, relleno=BLANCO, borde=BORDE, radio=None):
    forma = MSO_SHAPE.ROUNDED_RECTANGLE if radio else MSO_SHAPE.RECTANGLE
    s = sl.shapes.add_shape(forma, px(x), px(y), px(w), px(h))
    if radio:
        s.adjustments[0] = radio / min(w, h)
    if relleno is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = relleno
    if borde is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = borde
        s.line.width = Pt(1)
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def texto(sl, x, y, w, h, contenido, tam, color=TEXTO, negrita=False, alinear=PP_ALIGN.LEFT,
          vertical=MSO_ANCHOR.TOP, interlineado=1.0):
    tb = sl.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = vertical
    lineas = contenido if isinstance(contenido, list) else [contenido]
    for i, linea in enumerate(lineas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinear
        p.line_spacing = interlineado
        r = p.add_run()
        r.text = linea
        r.font.name = FUENTE
        r.font.size = pt(tam)
        r.font.bold = negrita
        r.font.color.rgb = color
    return tb


def imagen(sl, im, x, y, w, h, formato="JPEG"):
    return sl.shapes.add_picture(a_bytes(im, formato), px(x), px(y), px(w), px(h))


def numero(sl, n):
    texto(sl, 1480, 860, 64, 28, str(n), 22, GRIS, alinear=PP_ALIGN.RIGHT)


def notas(sl, d, extra=""):
    t = sl.notes_slide.notes_text_frame
    t.text = (f"DIGO: {d['_guion']}\n"
              f"(En español: {d['_es']})\n"
              f"Se pronuncia: {d['pron']}"
              + (f"\n\n{extra}" if extra else ""))


# ---------------------------------------------------------------- diapositivas
def d_portada(prs, d, nombre, faltan):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    im, ok = foto(d["img"], "🍽️", 900, 900)
    faltan += [] if ok else [d["img"]]
    imagen(sl, im, 700, 0, 900, 900)
    texto(sl, 104, 260, 580, 40, "English · 1° Básico", 28, GRIS)
    texto(sl, 104, 310, 580, 150, "My Menu", 130, NEGRO, negrita=True)
    x = 104
    for etiqueta, ancho in (("Breakfast", 200), ("Lunch", 140), ("Tea time", 180)):
        s = caja(sl, x, 500, ancho, 64, BLANCO, BORDE, radio=32)
        tf = s.text_frame
        tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = etiqueta
        r.font.name, r.font.size, r.font.color.rgb = FUENTE, pt(30), TEXTO
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        x += ancho + 14
    if nombre:
        texto(sl, 104, 620, 580, 60, f"by {nombre}", 40, GRIS)
    guion = dict(d)
    if nombre:
        guion["_guion"] = guion["_guion"].replace("___", nombre)
    notas(sl, guion, "Saluda mirando al curso y con una sonrisa.")


def d_comida(prs, d, ali, faltan):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    # ícono redondo de la comida + título
    im, ok = foto(d["id"], d["e"], 150, 150, 300)
    faltan += [] if ok else [d["id"]]
    imagen(sl, redonda(im), 64, 52, 150, 150, "PNG")
    texto(sl, 246, 52, 1200, 150, d["en"], 112, NEGRO, negrita=True, vertical=MSO_ANCHOR.MIDDLE)
    # fila de alimentos, grandes para señalarlos con el puntero
    n = len(d["ids"])
    if n == 4:
        x0, ancho, gap = 64, 344, 32
    else:
        x0, ancho, gap = 144, 416, 32
    y0, rotulo, pad = 242, 96, 12
    for k, idn in enumerate(d["ids"]):
        a = ali[idn]
        x = x0 + k * (ancho + gap)
        caja(sl, x, y0, ancho, ancho + rotulo, BLANCO, BORDE, radio=20)
        lado = ancho - 2 * pad
        im, ok = foto(idn, a["e"], lado, lado)
        faltan += [] if ok else [idn]
        imagen(sl, im, x + pad, y0 + pad, lado, lado)
        texto(sl, x + 8, y0 + ancho, ancho - 16, rotulo - 4, a["en"], 40 if n == 4 else 44, NEGRO,
              negrita=True, alinear=PP_ALIGN.CENTER, vertical=MSO_ANCHOR.MIDDLE)
    texto(sl, 64, 770, 1472, 50, d["inicio_en"] + "…", 40, GRIS, alinear=PP_ALIGN.CENTER)
    numero(sl, len(prs.slides._sldIdLst))
    notas(sl, d, "Señala cada alimento con el puntero mientras lo nombras.")


def d_cierre(prs, d, faltan):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    im, ok = foto(d["img"], "💛", 900, 900)
    faltan += [] if ok else [d["img"]]
    imagen(sl, im, 700, 0, 900, 900)
    texto(sl, 104, 200, 570, 500, ["Thank you for", "your attention!"], 84, NEGRO, negrita=True,
          vertical=MSO_ANCHOR.MIDDLE, interlineado=0.95)
    notas(sl, d, "Dilo fuerte, con una sonrisa, y espera los aplausos.")


def seguro(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "copia"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nombre", help="nombre para la portada (genera una copia privada)")
    ap.add_argument("--salida", help="ruta del .pptx (opcional)")
    args = ap.parse_args()

    m = DATOS_RE.search(HTML.read_text(encoding="utf-8"))
    if not m:
        sys.exit("No encontré el bloque de datos en my-menu-presentacion.html")
    datos = json.loads(m.group(1))
    ali = {a["id"]: a for a in datos["alimentos"]}

    prs = Presentation()
    prs.slide_width, prs.slide_height = px(1600), px(900)
    prs.core_properties.title = "My Menu"
    prs.core_properties.author = "Aprendo en casa"

    faltan = []
    for d in datos["diapos"]:
        if d["tipo"] == "portada":
            d_portada(prs, d, args.nombre, faltan)
        elif d["tipo"] == "comida":
            d_comida(prs, d, ali, faltan)
        else:
            d_cierre(prs, d, faltan)

    if args.salida:
        salida = Path(args.salida)
    elif args.nombre:
        salida = RAIZ / "privado" / f"my-menu-{seguro(args.nombre)}.pptx"
    else:
        salida = CARPETA / "my-menu-presentacion.pptx"
    salida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(salida)

    faltan = sorted(set(faltan))
    print(f"listo: {salida.relative_to(RAIZ).as_posix() if salida.is_relative_to(RAIZ) else salida} "
          f"({salida.stat().st_size / 1e6:.1f} MB, {len(prs.slides._sldIdLst)} diapositivas)")
    if faltan:
        print(f"faltan {len(faltan)} imágenes (van con emoji): {' '.join(faltan)}")


if __name__ == "__main__":
    main()
