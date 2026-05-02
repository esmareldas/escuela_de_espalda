#!/usr/bin/env python3
"""
Descarga de los 28 vídeos del programa Escuela de Espalda
para reproducirlos en local desde escuela_de_espalda.html.

Versión robusta: usa el binario "standalone" de yt-dlp, que no depende
de la versión de Python instalada. Compatible con Python 3.9+.

Uso:
  python3 descargar_videos.py     (Mac/Linux)
  python   descargar_videos.py    (Windows)
"""

import os
import sys
import platform
import subprocess
import urllib.request
import stat

# ----- Detectar plataforma y elegir el binario correcto -----
SYSTEM = platform.system()
if SYSTEM == "Darwin":
    BINARY_NAME = "yt-dlp_macos"
elif SYSTEM == "Windows":
    BINARY_NAME = "yt-dlp.exe"
else:
    BINARY_NAME = "yt-dlp_linux"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BINARY_PATH = os.path.join(SCRIPT_DIR, BINARY_NAME)


def asegurar_ytdlp():
    """Descarga el binario standalone de yt-dlp si no está ya en la carpeta."""
    if os.path.exists(BINARY_PATH) and os.path.getsize(BINARY_PATH) > 1_000_000:
        return BINARY_PATH

    url = f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{BINARY_NAME}"
    print(f"→ Descargando yt-dlp ({BINARY_NAME})…")
    print("  Esto solo ocurre la primera vez. Puede tardar 30-60 segundos.\n")

    try:
        urllib.request.urlretrieve(url, BINARY_PATH)
    except Exception as e:
        print(f"\n❌ No se pudo descargar yt-dlp: {e}")
        print(f"   Descárgalo manualmente desde: {url}")
        print(f"   Y guárdalo como '{BINARY_NAME}' en esta carpeta.")
        sys.exit(1)

    # Permisos de ejecución en Unix
    if SYSTEM != "Windows":
        st = os.stat(BINARY_PATH)
        os.chmod(BINARY_PATH, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    print("✓ yt-dlp descargado correctamente.\n")
    return BINARY_PATH


YTDLP = asegurar_ytdlp()

# ----- Lista de vídeos -----
VIDEOS = [
    ("GhGrQ9dVnuE", "Apertura costal con roller"),
    ("XTOIGMzhX3Y", "Báscula pélvica"),
    ("SnIx9dvkQw0", "Dorsal inferior en prono"),
    ("TODmZMq-rjY", "Dorsal medio en prono"),
    ("k_qzN8TTZUI", "Dorsal superior en prono"),
    ("Jo0Zphcvrsk", "Dorso de gato"),
    ("RUMfsWrfYL0", "Elongación en cuadrupedia"),
    ("kNE_HlL9iMU", "Elongación en prono"),
    ("9Rhx1PmHwds", "Movilidad pelvis fitball ante-retro"),
    ("_-t2Pej3ASk", "Movilidad pelvis fitball lateral"),
    ("oPAIxsmsbpI", "Movilidad pelvis fitball círculos"),
    ("2KFVPekaRLk", "Transverso roller MMII 2"),
    ("VagLLmUAsuM", "Transverso abdomen"),
    ("qBNvg3uUhrk", "Transverso roller MMII 1"),
    ("W022GlqzvcI", "Transverso roller MMSS"),
    ("HuCIYhC3FQc", "Plancha lateral sobre una rodilla"),
    ("MhCi6hTXcxo", "Oblicuo isometría con pelota"),
    ("x89vYRiXZrE", "Trabajo abdominal MMII alterno 2"),
    ("DabJilrrduY", "Trabajo abdominal con MMII"),
    ("mpDpM4kYKQ4", "Trabajo abdominal en excéntrico"),
    ("QY_tbpSYguU", "Trabajo abdominal MMII alternos 1"),
    ("nxCkOY5bdk8", "Transverso roller con pelota entre rodillas"),
    ("8YNuVB15s74", "Trabajo recto abdominal en isometría"),
    ("IgO_A_bCKHs", "Trabajo recto abdomen isometría prono"),
    ("NA5Ms11e6-M", "Plancha lateral con apoyo de rodillas"),
    ("IFmYTa2ESeQ", "Plancha anterior"),
    ("idNd2kjXotw", "Plancha anterior con apoyo en rodillas"),
    ("6KHRVjRO9LE", "Oblicuo isometría 2"),
]

OUT_DIR = os.path.join(SCRIPT_DIR, "videos")
os.makedirs(OUT_DIR, exist_ok=True)

# Formato MP4 pre-mezclado para que no haga falta ffmpeg.
# Códigos 18 (mp4 360p) y 22 (mp4 720p) son streams ya unidos audio+vídeo.
FORMATO = "18/22/best[ext=mp4][height<=720]/best[ext=mp4]/best"

print(f"📦 Descargando {len(VIDEOS)} vídeos a la carpeta '{OUT_DIR}/'\n")

ok = saltados = errores = 0
errores_detalle = []

for i, (vid, nombre) in enumerate(VIDEOS, 1):
    destino = os.path.join(OUT_DIR, f"{vid}.mp4")
    prefijo = f"[{i:>2}/{len(VIDEOS)}]"

    if os.path.exists(destino) and os.path.getsize(destino) > 100_000:
        print(f"{prefijo} ✓ {nombre}  (ya descargado)")
        saltados += 1
        continue

    print(f"{prefijo} ⬇ {nombre}…", end="", flush=True)

    cmd = [
        YTDLP,
        "-f", FORMATO,
        "-o", destino,
        "--no-warnings",
        "--quiet",
        "--no-playlist",
        f"https://www.youtube.com/watch?v={vid}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and os.path.exists(destino) and os.path.getsize(destino) > 100_000:
            size_mb = os.path.getsize(destino) / (1024 * 1024)
            print(f" ✓ ({size_mb:.1f} MB)")
            ok += 1
        else:
            err = (result.stderr or result.stdout or "(sin mensaje)").strip().split("\n")[-1]
            print(" ✗")
            errores += 1
            errores_detalle.append((nombre, err))
            # Limpia ficheros parciales
            if os.path.exists(destino) and os.path.getsize(destino) < 100_000:
                os.remove(destino)
    except subprocess.TimeoutExpired:
        print(" ✗ (timeout)")
        errores += 1
        errores_detalle.append((nombre, "timeout (>3 min)"))
    except Exception as e:
        print(f" ✗ ({e})")
        errores += 1
        errores_detalle.append((nombre, str(e)))

print(f"\n📊 Resumen: {ok} descargados, {saltados} ya estaban, {errores} con error.")

if errores_detalle:
    print("\n--- Detalle de errores ---")
    for nombre, err in errores_detalle[:5]:
        print(f"  • {nombre}: {err[:200]}")
    if len(errores_detalle) > 5:
        print(f"  … y {len(errores_detalle) - 5} más con errores similares.")

if errores == 0 and (ok > 0 or saltados == len(VIDEOS)):
    print("\n✅ Todo listo. Abre escuela_de_espalda.html y los vídeos se reproducirán dentro de la página.")
elif errores > 0:
    print("\n⚠ Vuelve a lanzar el script para reintentar los que faltan.")
