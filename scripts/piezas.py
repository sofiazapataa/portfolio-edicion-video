#!/usr/bin/env python3
"""Pausar o volver a integrar piezas del portfolio de edición de video.

Uso:
    python3 scripts/piezas.py pausar raza
    python3 scripts/piezas.py integrar raza
    python3 scripts/piezas.py estado

Pausar saca el bloque de la página, mueve los archivos fuera del repo (no se
publican), ajusta los textos que cuentan las piezas, regenera los PDF y hace
commit + push. Integrar hace exactamente lo inverso.
"""
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CV = os.path.dirname(REPO)
INDEX = os.path.join(REPO, "index.html")
CLIPS = os.path.join(REPO, "assets", "clips")
# Fuera del repo a propósito: lo pausado no se sube a GitHub ni se publica.
PAUSADAS = os.path.join(CV, "portfolio-edicion-video-pausadas")
PDF_SRC = os.path.join(CV, "pdf-portfolio-video-fuente")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PDFS = {"es": "Sofi_Zapata_Portfolio_Editora_Video_IA_ES.pdf", "en": "Sofi_Zapata_AI_Video_Editor_Portfolio_EN.pdf"}

# Cada pieza: archivos, y textos que cambian según esté integrada o pausada
# (español en el HTML, inglés en el diccionario EN del script de la página).
PIEZAS = {
    "raza": {
        "nombre": "Raza Automotores",
        "archivos": ["reel-raza.mp4", "reel-raza.jpg"],
        "textos": [
            # (integrada, pausada)
            (">Instagram · 2 reels<", ">Instagram · 1 reel<"),
            ('"r1": "Instagram · 2 reels"', '"r1": "Instagram · 1 reel"'),
            (">Dos reels para Instagram de marcas con las que trabajo: una agencia de autos y una marca de cosmética de la que hago venta mayorista.<",
             ">Reel para Instagram de una marca de cosmética con la que trabajo en venta mayorista.<"),
            ('"r2": "Two Instagram reels for brands I work with: a car dealership and a skincare brand I sell wholesale."',
             '"r2": "Instagram reel for a skincare brand I work with as a wholesale seller."'),
        ],
    },
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def leer():
    return open(INDEX, encoding="utf-8").read()


def escribir(s):
    open(INDEX, "w", encoding="utf-8").write(s)


def esta_pausada(clave):
    return ("<!-- pieza:%s pausada -->" % clave) in leer()


def pausar(clave):
    p = PIEZAS[clave]
    s = leer()
    ini, fin = "<!-- pieza:%s -->" % clave, "<!-- /pieza:%s -->" % clave
    if ini not in s:
        sys.exit("%s ya está pausada." % p["nombre"])
    a = s.index(ini)
    b = s.index(fin) + len(fin)
    destino = os.path.join(PAUSADAS, clave)
    os.makedirs(destino, exist_ok=True)
    open(os.path.join(destino, "bloque.html"), "w", encoding="utf-8").write(s[a:b])
    s = s[:a] + "<!-- pieza:%s pausada -->" % clave + s[b:]
    for integrada, pausada in p["textos"]:
        if integrada not in s:
            sys.exit("No encontré el texto a cambiar: " + integrada[:60])
        s = s.replace(integrada, pausada)
    escribir(s)
    for f in p["archivos"]:
        shutil.move(os.path.join(CLIPS, f), os.path.join(destino, f))
    return "Pausar %s" % p["nombre"]


def integrar(clave):
    p = PIEZAS[clave]
    s = leer()
    marca = "<!-- pieza:%s pausada -->" % clave
    if marca not in s:
        sys.exit("%s ya está integrada." % p["nombre"])
    origen = os.path.join(PAUSADAS, clave)
    bloque = open(os.path.join(origen, "bloque.html"), encoding="utf-8").read()
    s = s.replace(marca, bloque)
    for integrada, pausada in p["textos"]:
        if pausada not in s:
            sys.exit("No encontré el texto a cambiar: " + pausada[:60])
        s = s.replace(pausada, integrada)
    escribir(s)
    for f in p["archivos"]:
        shutil.move(os.path.join(origen, f), os.path.join(CLIPS, f))
    return "Integrar %s" % p["nombre"]


def regenerar_pdfs():
    if not os.path.exists(os.path.join(PDF_SRC, "gen_pdf_html.py")):
        print("Aviso: no encontré la fuente del PDF, no lo regeneré.")
        return
    run([sys.executable, "-I", "gen_pdf_html.py", PDF_SRC], cwd=PDF_SRC)
    for lang, nombre in PDFS.items():
        run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             "--allow-file-access-from-files", "--print-to-pdf=" + os.path.join(CV, nombre),
             "file://" + os.path.join(PDF_SRC, "portfolio_%s.html" % lang)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("PDF regenerados en", CV)


def publicar(mensaje):
    run(["git", "add", "-A"], cwd=REPO)
    run(["git", "commit", "-q", "-m", mensaje + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=REPO)
    run(["git", "push", "-q", "origin", "main"], cwd=REPO)
    print("Subido a GitHub; Vercel lo publica en un minuto.")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "estado":
        for k, p in PIEZAS.items():
            print("%-8s %s" % (k, "pausada" if esta_pausada(k) else "integrada"))
        return
    if len(sys.argv) != 3 or sys.argv[1] not in ("pausar", "integrar") or sys.argv[2] not in PIEZAS:
        sys.exit(__doc__)
    accion, clave = sys.argv[1], sys.argv[2]
    mensaje = pausar(clave) if accion == "pausar" else integrar(clave)
    regenerar_pdfs()
    publicar(mensaje)


if __name__ == "__main__":
    main()
