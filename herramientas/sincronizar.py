"""Copia el sistema de diseño Selva v2 (carpeta diseno/) dentro de cada actividad.

Regla del proyecto: cada actividad es UN solo archivo HTML que funciona sin
internet. Por eso el diseño común no se enlaza: se incrusta. Este script lo
mantiene al día en todos los archivos a la vez.

Uso (desde la raíz del repositorio):
    python herramientas/sincronizar.py

Es seguro correrlo muchas veces: reemplaza el bloque anterior, no lo duplica.
Modos (se detectan solos; se pueden fijar a mano en el comentario del bloque):
    juego         pantallas inicio / juego / final (la mayoría)
    moderno       actividades que ya nacieron con el diseño v2 (la-cama-de-mama)
    presentacion  diapositivas
"""
from pathlib import Path
import re
import sys

RAIZ = Path(__file__).resolve().parent.parent
DISENO = RAIZ / "diseno"

CSS_RE = re.compile(r"\n?<!-- selva:css modo=(\w+)[^>]*-->.*?<!-- /selva:css -->\n?", re.S)
JS_RE = re.compile(r"\n?<!-- selva:js -->.*?<!-- /selva:js -->\n?", re.S)
GFONTS_RE = re.compile(r"[ \t]*<link[^>]+fonts\.(googleapis|gstatic)\.com[^>]*>\r?\n?")
BALOO_RE = re.compile(r"@font-face\{font-family:['\"]Baloo 2['\"]")


def leer(nombre):
    return (DISENO / nombre).read_text(encoding="utf-8").strip()


def detectar_modo(html):
    m = CSS_RE.search(html)
    if m:
        return m.group(1)
    if 'id="lienzo"' in html:
        return "presentacion"
    if 'id="pInicio"' in html:
        return "moderno"
    return "juego"


def procesar(ruta):
    original = ruta.read_text(encoding="utf-8")
    modo = detectar_modo(original)
    html = JS_RE.sub("\n", CSS_RE.sub("\n", original))

    partes = []
    if not BALOO_RE.search(html):
        # la fuente venía de Google Fonts: se incrusta para que funcione sin internet
        html = GFONTS_RE.sub("", html)
        partes.append(leer("baloo-2.css"))
    partes.append(leer("selva-base.css"))
    if modo == "juego":
        partes.append(leer("selva-juego.css"))
    elif modo == "presentacion":
        partes.append(leer("selva-presentacion.css"))

    html = re.sub(
        r'(<meta name="viewport" content=")([^"]*)(")',
        lambda m: m.group(1) + (m.group(2) if "viewport-fit" in m.group(2) else m.group(2) + ",viewport-fit=cover") + m.group(3),
        html, count=1)

    css = (f"<!-- selva:css modo={modo} · generado por herramientas/sincronizar.py, no editar aquí -->\n"
           f"<style id=\"selva\">\n" + "\n".join(partes) + "\n</style>\n<!-- /selva:css -->\n")
    js = "<!-- selva:js -->\n<script id=\"selva-js\">\n" + leer("selva.js") + "\n</script>\n<!-- /selva:js -->\n"

    i = html.find("</head>")
    html = html[:i].rstrip("\n") + "\n" + css + html[i:]
    j = html.rfind("</body>")
    html = html[:j].rstrip("\n") + "\n" + js + html[j:]

    if html != original:
        ruta.write_text(html, encoding="utf-8", newline="")
        return modo, True
    return modo, False


FUENTE_RE = re.compile(r"\n?<!-- selva:fuente -->.*?<!-- /selva:fuente -->\n?", re.S)


def portada():
    """La portada tiene su propio estilo; solo se le incrusta la fuente."""
    ruta = RAIZ / "index.html"
    original = ruta.read_text(encoding="utf-8")
    html = GFONTS_RE.sub("", FUENTE_RE.sub("\n", original))
    bloque = "<!-- selva:fuente -->\n<style>\n" + leer("baloo-2.css") + "\n</style>\n<!-- /selva:fuente -->\n"
    i = html.find("<style>")
    html = html[:i] + bloque + html[i:]
    if html != original:
        ruta.write_text(html, encoding="utf-8", newline="")
    print(f"{'actualizado' if html != original else 'sin cambios':12} {'portada':13} index.html")


def main():
    portada()
    archivos = sorted(RAIZ.glob("*-basico/**/*.html")) + [RAIZ / "plantilla" / "base.html"]
    for ruta in archivos:
        modo, cambio = procesar(ruta)
        print(f"{'actualizado' if cambio else 'sin cambios':12} {modo:13} {ruta.relative_to(RAIZ).as_posix()}")


if __name__ == "__main__":
    sys.exit(main())
