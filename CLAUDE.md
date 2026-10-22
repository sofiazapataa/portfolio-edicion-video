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
