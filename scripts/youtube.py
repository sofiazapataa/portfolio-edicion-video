#!/usr/bin/env python3
"""Sacar o volver a poner un video de la sección YouTube del portfolio.

Uso:
    python3 scripts/youtube.py sacar <nombre>
    python3 scripts/youtube.py integrar <nombre>
    python3 scripts/youtube.py estado
    python3 scripts/youtube.py sacar <nombre> --push      # además commit + push

"Sacar" mueve los videos y pósters FUERA del repo (no se publican) y cambia el
bloque `yt-media` de index.html: la sección sigue en la página, con los mismos
recuadros (crudo y editado) y las herramientas, pero cada recuadro muestra un
candado y el HTML no referencia ningún archivo. "Integrar" hace lo inverso.

Sin --push solo edita archivos (sirve para probar en local antes de publicar).
Con --push, si la sección todavía no estaba publicada en GitHub, no sube nada.
"""
import json
import os
import re
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV = os.path.dirname(REPO)
INDEX = os.path.join(REPO, "index.html")
# Fuera del repo a propósito: lo que se saca no se sube a GitHub ni se publica.
PAUSADAS = os.path.join(CV, "portfolio-edicion-video-pausadas")
# Nombres de personas: NO van en el repo (es público).
ALIAS_PRIVADOS = os.path.join(PAUSADAS, "alias-youtube.json")

PIEZAS = {
    "vlog-glamping": {
        "nombre": "Vlog de glamping",
        "alias": ["glamping"],
        "archivos": [
            "assets/youtube/vlog-glamping-crudo.mp4",
            "assets/youtube/vlog-glamping-editado.mp4",
            "assets/youtube/vlog-glamping-crudo.jpg",
            "assets/youtube/vlog-glamping-editado.jpg",
        ],
    },
}

LOCK_SVG = (
    '<svg class="yt-lock" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V8a4 4 0 018 0v3"></path></svg>'
)
BLOQUEADO = (
    '          <div class="yt-tile yt-tile--edited"><span class="yt-tag" data-i18n="y2">Editado</span><div class="yt-frame">'
    '<div class="yt-lockbox" role="img">' + LOCK_SVG +
    '<strong data-i18n="y9">Video no disponible por ahora</strong>'
    '<small data-i18n="y10">Lo vuelvo a publicar apenas pueda.</small></div></div></div>\n'
    '          <div class="yt-tile yt-tile--raw"><span class="yt-tag" data-i18n="y3">Crudo</span><div class="yt-frame">'
    '<div class="yt-lockbox" role="img">' + LOCK_SVG +
    '<span class="yt-sr" data-i18n="y11">Video no disponible</span></div></div></div>\n'
)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, cwd=REPO, **kw)


def clave_de(texto):
    t = texto.strip().lower()
    privados = {}
    if os.path.exists(ALIAS_PRIVADOS):
        privados = json.load(open(ALIAS_PRIVADOS, encoding="utf-8"))
    for clave, p in PIEZAS.items():
        if t == clave or t in p["alias"] or t in [a.lower() for a in privados.get(clave, [])]:
            return clave
    sys.exit("No conozco '%s'. Piezas: %s" % (texto, ", ".join(PIEZAS)))


def patron(clave):
    return re.compile(
        r"(<!-- yt-media:%s )(visible|locked)( -->)(.*?)(<!-- /yt-media:%s -->)" % (re.escape(clave), re.escape(clave)),
        re.S,
    )


def leer():
    return open(INDEX, encoding="utf-8").read()


def escribir(s):
    open(INDEX, "w", encoding="utf-8").write(s)


def estado_de(clave):
    m = patron(clave).search(leer())
    if not m:
        sys.exit("No encuentro el bloque 'yt-media:%s' en index.html." % clave)
    return m.group(2)


def mover(origen, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.move(origen, destino)


def sacar(clave):
    p = PIEZAS[clave]
    if estado_de(clave) == "locked":
        sys.exit("%s ya está sacada." % p["nombre"])
    s = leer()
    m = patron(clave).search(s)
    destino = os.path.join(PAUSADAS, "youtube-" + clave)
    os.makedirs(destino, exist_ok=True)
    open(os.path.join(destino, "bloque.html"), "w", encoding="utf-8").write(m.group(4))
    s = s[:m.start()] + m.group(1) + "locked" + m.group(3) + "\n" + BLOQUEADO + "          " + m.group(5) + s[m.end():]
    for rel in p["archivos"]:
        if os.path.basename(rel) in s:
            sys.exit("Quedó una referencia a %s en index.html; no la saco." % os.path.basename(rel))
    for rel in p["archivos"]:
        src = os.path.join(REPO, rel)
        if os.path.exists(src):
            mover(src, os.path.join(destino, rel))
    escribir(s)
    print("Sacada: %s. Archivos guardados en %s" % (p["nombre"], destino))


def integrar(clave):
    p = PIEZAS[clave]
    if estado_de(clave) == "visible":
        sys.exit("%s ya está integrada." % p["nombre"])
    origen = os.path.join(PAUSADAS, "youtube-" + clave)
    bloque = os.path.join(origen, "bloque.html")
    faltan = [r for r in p["archivos"] if not os.path.exists(os.path.join(origen, r))]
    if faltan or not os.path.exists(bloque):
        sys.exit("Faltan archivos en %s: %s" % (origen, ", ".join(faltan) or "bloque.html"))
    s = leer()
    m = patron(clave).search(s)
    s = s[:m.start()] + m.group(1) + "visible" + m.group(3) + open(bloque, encoding="utf-8").read() + m.group(5) + s[m.end():]
    for rel in p["archivos"]:
        mover(os.path.join(origen, rel), os.path.join(REPO, rel))
    escribir(s)
    print("Integrada: %s." % p["nombre"])


def ya_publicada(clave):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "assets/youtube"],
                         cwd=REPO, capture_output=True, text=True).stdout.strip()
    return bool(out)


def publicar(clave, accion):
    if not ya_publicada(clave):
        print("La sección YouTube todavía NO está publicada en GitHub: no hago push (nada de esto salió a internet).")
        return
    sucios = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout
    ajenos = [l for l in sucios.splitlines() if "assets/youtube" not in l and not l.endswith("index.html")]
    if ajenos:
        print("OJO: hay otros cambios sin commitear que se van a publicar:\n  " + "\n  ".join(ajenos))
    run(["git", "add", "-A", "--", "index.html", "assets/youtube"])
    msg = "Sacar un video de la sección YouTube por ahora" if accion == "sacar" else "Volver a mostrar un video en la sección YouTube"
    run(["git", "commit", "-q", "-m", msg + "\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"])
    run(["git", "push", "-q", "origin", "main"])
    print("Subido a GitHub; Vercel lo publica en un minuto.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    push = "--push" in sys.argv
    if not args or args[0] not in ("sacar", "integrar", "estado"):
        sys.exit(__doc__)
    if args[0] == "estado":
        for clave, p in PIEZAS.items():
            print("%-14s %s  (%s)" % (clave, "visible" if estado_de(clave) == "visible" else "SACADO ", p["nombre"]))
        return
    if len(args) < 2:
        sys.exit("Falta el nombre de la pieza. Ej: python3 scripts/youtube.py %s <nombre>" % args[0])
    clave = clave_de(" ".join(args[1:]))
    (sacar if args[0] == "sacar" else integrar)(clave)
    if push:
        publicar(clave, args[0])
    else:
        print("(Sin --push: solo cambió en local, no se publicó.)")


if __name__ == "__main__":
    main()
