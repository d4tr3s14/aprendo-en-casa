"""Arma el PowerPoint de «Flora y fauna de Chile» (Ciencias Naturales, 1° básico).

Lee las diapositivas del bloque <script id="datos"> de flora-fauna-presentacion.html,
así el PowerPoint dice exactamente lo mismo que la página. Las imágenes salen de
img-flora-fauna/ (cualquier .jpg, .jpeg, .png o .webp); si falta alguna, pone un
recuadro con el emoji para que se note qué falta.

Requisitos (una sola vez):
    pip install python-pptx pillow

Uso (desde la raíz del repositorio):
    python herramientas/generar-pptx-flora-fauna.py
        → 1-basico/semestre-2/ciencias-naturales/flora-fauna-presentacion.pptx
          (sin nombre, va al repositorio)

    python herramientas/generar-pptx-flora-fauna.py --nombre "Nombre"
        → privado/flora-fauna-<nombre>.pptx (con su nombre en la portada y en el
          guion; la carpeta privado/ está en .gitignore y NO se sube a GitHub)

Las imágenes se recortan al tamaño del recuadro y se achican a 1000 px dentro del
archivo, para que el PowerPoint pese poco y corra fluido en el computador del colegio.
El guion de cada diapositiva queda en las notas del orador.
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
CARPETA = RAIZ / "1-basico" / "semestre-2" / "ciencias-naturales"
HTML = CARPETA / "flora-fauna-presentacion.html"
IMG = CARPETA / "img-flora-fauna"
EXT = (".jpg", ".jpeg", ".png", ".webp")
DATOS_RE = re.compile(r'<script type="application/json" id="datos">(.*?)</script>', re.S)
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]\\s*")

FUENTE = "Calibri"            # está en cualquier computador con Office
NEGRO = RGBColor(0x00, 0x00, 0x00)
TEXTO = RGBColor(0x19, 0x19, 0x19)
GRIS = RGBColor(0x8C, 0x8C, 0x8C)
BORDE = RGBColor(0xE6, 0xE6, 0xE6)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)


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


def emoji_png(emoji, lado, fondo=(248, 248, 248, 255)):
    """Emoji dibujado como imagen (PowerPoint no siempre muestra emojis a color)."""
    im = Image.new("RGBA", (lado, lado), fondo)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("seguiemj.ttf", int(lado * 0.42 if fondo[3] else lado * 0.8))
        d.text((lado / 2, lado / 2), emoji, font=f, anchor="mm", embedded_color=True)
    except OSError:
        d.text((lado / 2, lado / 2), "?", fill=(140, 140, 140, 255), anchor="mm")
    return im


def foto(nombre, emoji, ancho, alto, lado_max=1000):
    """Devuelve la imagen recortada al tamaño pedido (como object-fit: cover)."""
    f = busca(nombre)
    if f:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    else:
        im = emoji_png(emoji, 800).convert("RGB")
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


def pastilla(sl, x, y, w, h, contenido, tam):
    s = caja(sl, x, y, w, h, BLANCO, BORDE, radio=h / 2)
    tf = s.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = contenido
    r.font.name, r.font.size, r.font.color.rgb = FUENTE, pt(tam), TEXTO
    return s


def imagen(sl, im, x, y, w, h, formato="JPEG"):
    return sl.shapes.add_picture(a_bytes(im, formato), px(x), px(y), px(w), px(h))


def icono(sl, emoji, x, y, lado):
    imagen(sl, emoji_png(emoji, 160, (0, 0, 0, 0)), x, y, lado, lado, "PNG")


def numero(sl, n):
    texto(sl, 1480, 860, 64, 28, str(n), 22, GRIS, alinear=PP_ALIGN.RIGHT)


def sin_emoji(t):
    return EMOJI_RE.sub("", t).strip()


def guion(d, nombre):
    return " ".join((f"{nombre}." if nombre else "___.") if x.get("pausa") else x["t"] for x in d["partes"])


def notas(sl, d, nombre):
    sl.notes_slide.notes_text_frame.text = f"DIGO: {guion(d, nombre)}\n\nCONSEJO: {d['consejo']}"


def foto_derecha(prs, d, emoji, faltan):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    im, ok = foto(d["img"], emoji, 900, 900)
    faltan += [] if ok else [d["img"]]
    imagen(sl, im, 700, 0, 900, 900)
    return sl


# ---------------------------------------------------------------- diapositivas
def d_portada(prs, d, nombre, faltan):
    sl = foto_derecha(prs, d, "🌿", faltan)
    texto(sl, 88, 230, 590, 40, "Ciencias Naturales · 1° Básico", 28, GRIS)
    texto(sl, 88, 282, 590, 230, ["Flora y fauna", "de Chile"], 104, NEGRO, negrita=True, interlineado=0.92)
    x = 88
    for etiqueta, ancho in (("Copihue", 190), ("Pudú", 140)):
        pastilla(sl, x, 548, ancho, 64, etiqueta, 32)
        x += ancho + 14
    if nombre:
        texto(sl, 88, 650, 590, 60, f"por {nombre}", 40, GRIS)
    notas(sl, d, nombre)


def d_ficha(prs, d, nombre, faltan):
    sl = foto_derecha(prs, d, d["e"], faltan)
    grupo = sin_emoji(d["grupo"])
    pastilla(sl, 88, 190, 34 + len(grupo) * 16, 64, grupo, 30)
    texto(sl, 88, 276, 600, 170, d["rotulo"], 150, NEGRO, negrita=True, vertical=MSO_ANCHOR.MIDDLE)
    y = 478
    for f in d["filas"]:
        caja(sl, 88, y, 580, 116, BLANCO, BORDE, radio=20)
        icono(sl, f["e"], 110, y + 26, 64)
        texto(sl, 196, y + 8, 456, 100, f["rotulo"], 38, TEXTO, vertical=MSO_ANCHOR.MIDDLE)
        y += 116 + 18
    numero(sl, len(prs.slides._sldIdLst))
    notas(sl, d, nombre)


def d_cuidado(prs, d, nombre, faltan):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    icono(sl, d["e"], 64, 52, 120)
    texto(sl, 212, 52, 1300, 130, d["rotulo"], 104, NEGRO, negrita=True, vertical=MSO_ANCHOR.MIDDLE)
    ancho, alto_img, rotulo, gap = 632, 474, 100, 48
    x0 = (1600 - (2 * ancho + gap)) // 2
    y0 = 222
    for k, a in enumerate(d["acciones"]):
        x = x0 + k * (ancho + gap)
        caja(sl, x, y0, ancho, alto_img + rotulo, BLANCO, BORDE, radio=20)
        im, ok = foto(a["img"], a["e"], ancho - 2, alto_img)
        faltan += [] if ok else [a["img"]]
        imagen(sl, im, x + 1, y0 + 1, ancho - 2, alto_img)
        circulo = sl.shapes.add_shape(MSO_SHAPE.OVAL, px(x + 28), px(y0 + alto_img + 24), px(52), px(52))
        circulo.fill.background()
        circulo.line.color.rgb = BORDE
        circulo.shadow.inherit = False
        tf = circulo.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = str(k + 1)
        r.font.name, r.font.size, r.font.color.rgb = FUENTE, pt(30), GRIS
        texto(sl, x + 96, y0 + alto_img + 6, ancho - 120, rotulo - 12, a["rotulo"], 42, NEGRO,
              negrita=True, vertical=MSO_ANCHOR.MIDDLE)
    numero(sl, len(prs.slides._sldIdLst))
    notas(sl, d, nombre)


def d_cierre(prs, d, nombre, faltan):
    sl = foto_derecha(prs, d, d["e"], faltan)
    texto(sl, 88, 200, 590, 500, ["¡Muchas", "gracias!"], 110, NEGRO, negrita=True,
          vertical=MSO_ANCHOR.MIDDLE, interlineado=0.95)
    notas(sl, d, nombre)


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
        sys.exit("No encontré el bloque de datos en flora-fauna-presentacion.html")
    datos = json.loads(m.group(1))

    prs = Presentation()
    prs.slide_width, prs.slide_height = px(1600), px(900)
    prs.core_properties.title = "Flora y fauna de Chile"
    prs.core_properties.author = "Aprendo en casa"

    faltan = []
    hacer = {"portada": d_portada, "ficha": d_ficha, "cuidado": d_cuidado, "cierre": d_cierre}
    for d in datos["diapos"]:
        hacer[d["tipo"]](prs, d, args.nombre, faltan)

    if args.salida:
        salida = Path(args.salida)
    elif args.nombre:
        salida = RAIZ / "privado" / f"flora-fauna-{seguro(args.nombre)}.pptx"
    else:
        salida = CARPETA / "flora-fauna-presentacion.pptx"
    salida.parent.mkdir(parents=True, exist_ok=True)
    prs.save(salida)

    faltan = sorted(set(faltan))
    print(f"listo: {salida.relative_to(RAIZ).as_posix() if salida.is_relative_to(RAIZ) else salida} "
          f"({salida.stat().st_size / 1e6:.1f} MB, {len(prs.slides._sldIdLst)} diapositivas)")
    if faltan:
        print(f"faltan {len(faltan)} imágenes (van con emoji): {' '.join(faltan)}")


if __name__ == "__main__":
    main()
