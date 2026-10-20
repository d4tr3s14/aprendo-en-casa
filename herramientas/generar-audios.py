"""Graba con voz natural todo lo que una actividad dice en voz alta.

La voz del dispositivo (Web Speech API) suena robótica. Este script usa las voces
neuronales de Microsoft Edge (librería edge-tts, voz chilena es-CL-CatalinaNeural)
para dejar cada frase grabada como .mp3 junto a la actividad. La actividad busca
primero el audio grabado y, si no lo encuentra, usa la voz del dispositivo.

Requisitos (una sola vez):
    pip install edge-tts

Uso (desde la raíz del repositorio):
    python herramientas/generar-audios.py 1-basico/semestre-2/lenguaje/sapo-y-sepo-son-amigos.html

Opciones:
    --voz es-CL-LorenzoNeural   otra voz (ver: python -m edge_tts --list-voices)
    --velocidad -10%            más lento o más rápido (por defecto -6%)
    --rehacer                   vuelve a grabar todo, aunque ya exista
    --limpiar                   borra los audios que la actividad ya no usa

Cómo funciona: la actividad guarda sus textos en un bloque
<script type="application/json" id="datos"> con la clave "audio" (carpeta de
destino, relativa al HTML). Se graban todos los textos de ese bloque, salvo los
campos de la lista NO_SE_DICEN. Cada archivo se llama con la huella FNV-1a del
texto limpio, la misma que calcula la actividad en JavaScript. Además se guarda
tiempos.json con el momento en que se dice cada palabra, para irlas marcando.
Es seguro correrlo muchas veces: solo graba lo que falta.
"""
from pathlib import Path
import argparse
import asyncio
import json
import re
import sys
import unicodedata

RAIZ = Path(__file__).resolve().parent.parent
DATOS_RE = re.compile(r'<script type="application/json" id="datos">(.*?)</script>', re.S)
# emojis, selectores de variación y comillas angulares: no se leen (igual que limpia() en JS)
FUERA_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍«»]")
# campos que no son texto para decir: emojis, ids, abreviaturas, sílabas distractoras, atributos de dibujos
NO_SE_DICEN = {"e", "id", "tipo", "c", "d", "a", "otros", "audio", "unidad", "titulo", "nombre"}


def limpia(t):
    t = FUERA_RE.sub("", unicodedata.normalize("NFC", t))
    return re.sub(r"\s+", " ", t).strip()


def huella(t):
    h = 0x811C9DC5
    for b in t.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def textos(nodo, clave=None):
    if clave in NO_SE_DICEN:
        return
    if isinstance(nodo, str):
        t = limpia(nodo)
        if re.search(r"\w", t):
            yield t
    elif isinstance(nodo, list):
        for x in nodo:
            yield from textos(x)
    elif isinstance(nodo, dict):
        for k, v in nodo.items():
            yield from textos(v, k)


async def graba(texto, destino, voz, velocidad, sem):
    import edge_tts
    async with sem:
        for intento in range(3):
            try:
                com = edge_tts.Communicate(texto, voz, rate=velocidad, boundary="WordBoundary")
                audio, marcas = bytearray(), []
                async for trozo in com.stream():
                    if trozo["type"] == "audio":
                        audio.extend(trozo["data"])
                    elif trozo["type"] == "WordBoundary":
                        # edge-tts mide en unidades de 100 ns
                        marcas.append([round(trozo["offset"] / 1e4), round(trozo["duration"] / 1e4), trozo["text"]])
                if not audio:
                    raise RuntimeError("sin audio")
                destino.write_bytes(bytes(audio))
                return marcas
            except Exception as e:  # la conexión a veces se corta: se reintenta
                if intento == 2:
                    print(f"  ✗ no se pudo grabar: {texto[:60]}… ({e})")
                    return None
                await asyncio.sleep(1.5 * (intento + 1))


async def principal(args):
    html_ruta = (RAIZ / args.actividad).resolve() if not Path(args.actividad).is_absolute() else Path(args.actividad)
    html = html_ruta.read_text(encoding="utf-8")
    m = DATOS_RE.search(html)
    if not m:
        sys.exit('La actividad no tiene el bloque <script type="application/json" id="datos">.')
    datos = json.loads(m.group(1))
    carpeta = (html_ruta.parent / datos["audio"]).resolve()
    carpeta.mkdir(parents=True, exist_ok=True)

    lista = list(dict.fromkeys(textos(datos)))
    ruta_tiempos = carpeta / "tiempos.json"
    tiempos = json.loads(ruta_tiempos.read_text(encoding="utf-8")) if ruta_tiempos.exists() else {}

    faltan = [(t, huella(t)) for t in lista if args.rehacer or not (carpeta / f"{huella(t)}.mp3").exists()]
    print(f"{len(lista)} frases · {len(faltan)} por grabar · voz {args.voz} · velocidad {args.velocidad}")

    sem = asyncio.Semaphore(4)
    hechas = 0

    async def una(t, h):
        nonlocal hechas
        marcas = await graba(t, carpeta / f"{h}.mp3", args.voz, args.velocidad, sem)
        if marcas is not None:
            tiempos[h] = marcas
            hechas += 1
            if hechas % 25 == 0:
                print(f"  … {hechas} de {len(faltan)}")

    await asyncio.gather(*(una(t, h) for t, h in faltan))

    usadas = {huella(t) for t in lista}
    if args.limpiar:
        for f in carpeta.glob("*.mp3"):
            if f.stem not in usadas:
                f.unlink()
                print(f"  borrado {f.name}")
    tiempos = {h: v for h, v in sorted(tiempos.items()) if h in usadas or not args.limpiar}
    ruta_tiempos.write_text(json.dumps(tiempos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    peso = sum(f.stat().st_size for f in carpeta.glob("*.mp3")) / 1e6
    print(f"listo: {hechas} grabadas · {len(list(carpeta.glob('*.mp3')))} audios en {carpeta.relative_to(RAIZ).as_posix()} ({peso:.1f} MB)")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("actividad", help="ruta del .html de la actividad")
    p.add_argument("--voz", default="es-CL-CatalinaNeural")
    p.add_argument("--velocidad", default="-6%")
    p.add_argument("--rehacer", action="store_true")
    p.add_argument("--limpiar", action="store_true")
    asyncio.run(principal(p.parse_args()))


if __name__ == "__main__":
    main()
