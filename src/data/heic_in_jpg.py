"""Convertește fotografiile HEIC de la telefon în JPG fără metadate.

Originalele HEIC conțin datele EXIF, inclusiv coordonatele GPS ale locului unde au fost făcute,
deci nu se pun în repository. JPG-ul păstrează imaginea (cu orientarea aplicată), fără EXIF, GPS
sau XMP. Momentul fotografiei se notează înainte în manifest, din originale.

Rulare (din rădăcina repository-ului):
    python src/data/heic_in_jpg.py data/raw/pilot data/pilot 20261028_184249 20261028_184315
    python src/data/heic_in_jpg.py data/raw/pilot data/raw/pilot_jpg
"""

import argparse
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sursa", help="folderul cu fotografiile HEIC")
    p.add_argument("destinatie", help="folderul în care se scriu fișierele JPG")
    p.add_argument("nume", nargs="*", help="doar aceste fotografii (numele fără extensie); implicit toate")
    p.add_argument("--calitate", type=int, default=90, help="calitatea JPG (1–95)")
    a = p.parse_args()

    pillow_heif.register_heif_opener()
    sursa, destinatie = Path(a.sursa), Path(a.destinatie)
    destinatie.mkdir(parents=True, exist_ok=True)
    fisiere = sorted(f for f in sursa.iterdir() if f.suffix.lower() in (".heic", ".heif"))
    if a.nume:
        fisiere = [f for f in fisiere if f.stem in a.nume]
    for f in fisiere:
        with Image.open(f) as im:
            rgb = ImageOps.exif_transpose(im).convert("RGB")
        iesire = destinatie / (f.stem + ".jpg")
        # fără argumentul exif, Pillow nu scrie metadatele originalului
        rgb.save(iesire, "JPEG", quality=a.calitate)
        print(f"{f.name} -> {iesire} ({iesire.stat().st_size // 1024} KB)")
    print(f"{len(fisiere)} fotografii convertite.")


if __name__ == "__main__":
    main()
