# portfolio-edicion-video — portfolio independiente de edición de video

https://github.com/sofiazapataa/portfolio-edicion-video · deploy en Vercel.

Una sola página: `index.html` con CSS y JS inline, sin build ni dependencias.

Los videos, pósters y logos **no viven en este repo**: se cargan desde
`https://portfolio-2026-phi-ecru.vercel.app/assets/...` y `/uploads/...`.
Si se renombra o borra un archivo en `portfolio 2026`, se rompe acá también.

## Piezas pausadas (sacar y volver a poner sin preguntar)

Algunas piezas se pueden sacar del sitio temporalmente y volver a integrar con
un comando. Cuando Sofía pida "integrá / volvé a poner X" o "sacá X por ahora",
correr directamente, sin pedir confirmación:

```bash
python3 scripts/piezas.py integrar raza   # o: pausar raza
python3 scripts/piezas.py estado
```

El script mueve el bloque HTML y los videos a
`~/Documents/Cv/portfolio-edicion-video-pausadas/` (fuera del repo, no se
publica), ajusta los textos que cuentan piezas en ES y EN, regenera los dos PDF
del portfolio en `~/Documents/Cv/` y hace commit + push (Vercel publica solo).

Piezas registradas: `raza` (reel de Raza Automotores, pausado desde 2026-10-22).
Para registrar otra: marcar su bloque en `index.html` con
`<!-- pieza:clave -->` … `<!-- /pieza:clave -->` y agregarla a `PIEZAS` en el
script, con sus archivos y los textos que cambian.

`.vercelignore` excluye `CLAUDE.md` y `scripts/` del sitio publicado.

## Sección YouTube (crudo vs editado) — sacar y volver a poner sin preguntar

`#youtube` (debajo de Motion graphics, antes de Edición de reels) muestra el video **editado** grande y el
**crudo** chico en blanco y negro, superpuestos sobre un fondo cálido, con las
herramientas usadas. Son loops sincronizados de 5 s (mismo tramo del crudo y del
editado, sin audio) que corren solos mientras se ven, con botón de pausa. Videos
y pósters en `assets/youtube/`. El bloque de los recuadros está entre
`<!-- yt-media:vlog-glamping visible|locked -->` y `<!-- /yt-media:vlog-glamping -->`.

Sofía puede pedir sacar un video (o volver a ponerlo) nombrando a la persona (ej. "sacá el video de <nombre>"). Pasarle esas palabras al
script, que las resuelve con
`~/Documents/Cv/portfolio-edicion-video-pausadas/alias-youtube.json` (fuera del
repo a propósito: **el repo es público**). Cuando lo pida (o pida volver a ponerlo),
correr directo, sin pedir confirmación:

```bash
python3 scripts/youtube.py sacar <nombre> --push    # lo saca y publica ya
python3 scripts/youtube.py integrar <nombre>        # SIN --push: probar en local
python3 scripts/youtube.py estado
```

"Sacar" mueve los videos y pósters a `…-pausadas/youtube-vlog-glamping/` (fuera
del repo) y deja la sección con los mismos recuadros y herramientas, pero cada
recuadro con un candado y sin referenciar ningún archivo. "Integrar" lo revierte.

- **`sacar` siempre con `--push`.** Si la sección todavía no estaba publicada, el
  script no sube nada (lo avisa).
- **`integrar`: nunca con `--push` hasta que Sofía diga "subilo/publicalo"**;
  mostrarle primero cómo queda en local.
- Los archivos tienen nombre neutro (`vlog-glamping-*`) a propósito: el nombre de
  la persona no aparece en el código, las URLs ni el texto público. No ponérselo en
  `index.html`, `scripts/`, `CLAUDE.md` ni en los mensajes de commit.
- Aunque se saque, una versión ya publicada puede seguir en el historial de git y en
  despliegues viejos de Vercel; por eso no se publica nada sin OK.
