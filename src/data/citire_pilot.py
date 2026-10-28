"""Citirea și inspecția lotului pilot (P2 · Datele).

Programul:
1. citește `data/pilot/manifest.csv` și verifică coloanele și fișierele;
2. deschide fiecare fotografie și găsește piesele prin prelucrare clasică
   (tonuri de gri, prag Otsu, operații morfologice, contururi, dreptunghiul minim rotit);
3. rotește fiecare piesă cu axa lungă orizontală și o pune, fără redimensionare,
   pe un decupaj de dimensiune fixă;
4. afișează forma datelor care ajung la model (X, F, y) și problemele găsite;
5. salvează imagini de inspecție (contururile pe fotografie și o planșă cu decupaje).

Fotografiile de antrenare conțin o singură clasă, deci fiecare decupaj primește
`raspuns_corect` din rândul fotografiei. Pentru fotografiile amestecate sau fără
răspuns, eticheta decupajelor rămâne „lipsă”.

Rulare (din rădăcina repository-ului):
    python src/data/citire_pilot.py
    python src/data/citire_pilot.py --mm-per-px 0.12 --latura 256
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

COLOANE = ["id_exemplu", "fisier", "sursa", "grup", "moment", "raspuns_corect", "observatii"]
FARA_RASPUNS = {"", "lipsă", "lipsa", "amestecat"}


def citeste_manifest(cale):
    with open(cale, newline="", encoding="utf-8-sig") as f:
        cititor = csv.DictReader(f)
        lipsa = [c for c in COLOANE if c not in (cititor.fieldnames or [])]
        if lipsa:
            sys.exit(f"Manifestul nu are coloanele: {', '.join(lipsa)}")
        return list(cititor)


def citeste_imagine(cale):
    # np.fromfile + imdecode merge și cu căi cu diacritice pe Windows
    date = np.fromfile(str(cale), dtype=np.uint8)
    return cv2.imdecode(date, cv2.IMREAD_COLOR) if date.size else None


def gaseste_piese(imagine, arie_minima):
    """Întoarce, pentru fiecare piesă, conturul exterior, dreptunghiul rotit și numărul de găuri."""
    gri = cv2.cvtColor(imagine, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (5, 5), 0)
    # fundal închis, piese metalice mai deschise
    _, masca = cv2.threshold(gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    nucleu = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    masca = cv2.morphologyEx(masca, cv2.MORPH_OPEN, nucleu)
    masca = cv2.morphologyEx(masca, cv2.MORPH_CLOSE, nucleu)

    contururi, ierarhie = cv2.findContours(masca, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if ierarhie is None:
        return [], masca
    ierarhie = ierarhie[0]
    piese = []
    for i, contur in enumerate(contururi):
        if ierarhie[i][3] != -1 or cv2.contourArea(contur) < arie_minima:
            continue  # gaură sau zgomot
        gauri = 0
        copil = ierarhie[i][2]
        while copil != -1:
            if cv2.contourArea(contururi[copil]) >= arie_minima * 0.05:
                gauri += 1
            copil = ierarhie[copil][0]
        piese.append({"contur": contur, "dreptunghi": cv2.minAreaRect(contur), "gauri": gauri})
    return piese, masca


def decupeaza(imagine, dreptunghi, latura):
    """Rotește piesa cu axa lungă orizontală și o centrează pe un pătrat latura×latura, fără scalare."""
    (cx, cy), (w, h), unghi = dreptunghi
    if w < h:
        w, h = h, w
        unghi += 90
    rotatie = cv2.getRotationMatrix2D((cx, cy), unghi, 1.0)
    rotita = cv2.warpAffine(imagine, rotatie, (imagine.shape[1], imagine.shape[0]))
    lung, lat = int(round(w)), int(round(h))
    if lung > latura or lat > latura:
        return None
    x0, y0 = int(round(cx - lung / 2)), int(round(cy - lat / 2))
    bucata = rotita[max(y0, 0):y0 + lat, max(x0, 0):x0 + lung]
    canvas = np.zeros((latura, latura, 3), dtype=np.uint8)
    oy, ox = (latura - bucata.shape[0]) // 2, (latura - bucata.shape[1]) // 2
    canvas[oy:oy + bucata.shape[0], ox:ox + bucata.shape[1]] = bucata
    return canvas


def atinge_marginea(contur, forma):
    x, y, w, h = cv2.boundingRect(contur)
    return x <= 1 or y <= 1 or x + w >= forma[1] - 1 or y + h >= forma[0] - 1


def plansa(decupaje, etichete, cale, coloane=6, maxim=24):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = min(len(decupaje), maxim)
    if n == 0:
        return
    randuri = (n + coloane - 1) // coloane
    fig, axe = plt.subplots(randuri, coloane, figsize=(2 * coloane, 2.2 * randuri))
    for k, ax in enumerate(np.atleast_1d(axe).ravel()):
        ax.axis("off")
        if k < n:
            ax.imshow(cv2.cvtColor(decupaje[k], cv2.COLOR_BGR2RGB))
            ax.set_title(etichete[k], fontsize=7)
    fig.tight_layout()
    fig.savefig(cale, dpi=120)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pilot", default="data/pilot", help="folderul cu manifest.csv și fotografii")
    p.add_argument("--mm-per-px", type=float, default=None, help="factorul de scară de la calibrarea cu rigla")
    p.add_argument("--latura", type=int, default=256, help="latura decupajului fix, în pixeli")
    p.add_argument("--arie-minima", type=float, default=0.0005, help="aria minimă a unei piese, ca fracție din fotografie")
    p.add_argument("--iesire", default=None, help="folderul pentru imaginile de inspecție (implicit <pilot>/inspectie)")
    a = p.parse_args()

    pilot = Path(a.pilot)
    iesire = Path(a.iesire) if a.iesire else pilot / "inspectie"
    iesire.mkdir(parents=True, exist_ok=True)
    randuri = citeste_manifest(pilot / "manifest.csv")
    unitate = "mm" if a.mm_per_px else "px"
    scara = a.mm_per_px or 1.0

    print(f"Manifest: {len(randuri)} rânduri")
    print("  pe grup:", dict(Counter(r["grup"] for r in randuri)))
    print("  pe răspuns corect:", dict(Counter(r["raspuns_corect"] for r in randuri)))

    probleme = []
    X, F, y, id_uri = [], [], [], []
    for r in randuri:
        cale = pilot / r["fisier"]
        if not cale.exists():
            probleme.append(f"{r['id_exemplu']}: lipsește fișierul {r['fisier']}")
            continue
        imagine = citeste_imagine(cale)
        if imagine is None:
            probleme.append(f"{r['id_exemplu']}: fișierul {r['fisier']} nu se poate citi ca imagine")
            continue
        arie_minima = a.arie_minima * imagine.shape[0] * imagine.shape[1]
        piese, _ = gaseste_piese(imagine, arie_minima)
        eticheta = r["raspuns_corect"].strip()
        if eticheta.lower() in FARA_RASPUNS:
            eticheta = "lipsă"
        print(f"{r['id_exemplu']}: {imagine.shape[1]}×{imagine.shape[0]} px, {len(piese)} piese găsite, răspuns: {eticheta}")
        if not piese:
            probleme.append(f"{r['id_exemplu']}: nicio piesă găsită (prag sau fundal nepotrivit?)")

        desen = imagine.copy()
        for k, piesa in enumerate(piese, start=1):
            (_, _), (w, h), _ = piesa["dreptunghi"]
            lungime, latime = max(w, h) * scara, min(w, h) * scara
            cutie = cv2.boxPoints(piesa["dreptunghi"]).astype(np.int32)
            cv2.drawContours(desen, [cutie], 0, (0, 255, 0), 2)
            cv2.putText(desen, str(k), tuple(cutie[1]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            id_piesa = f"{r['id_exemplu']}_{k:02d}"
            if atinge_marginea(piesa["contur"], imagine.shape):
                probleme.append(f"{id_piesa}: piesa atinge marginea fotografiei")
            decupaj = decupeaza(imagine, piesa["dreptunghi"], a.latura)
            if decupaj is None:
                probleme.append(f"{id_piesa}: piesa ({max(w, h):.0f}×{min(w, h):.0f} px) nu încape în {a.latura}×{a.latura}")
                continue
            print(f"    {id_piesa}: {lungime:.1f}×{latime:.1f} {unitate}, găuri: {piesa['gauri']}")
            X.append(decupaj)
            F.append([lungime, latime])
            y.append(eticheta)
            id_uri.append(id_piesa)
        cv2.imwrite(str(iesire / f"{r['id_exemplu']}_contururi.jpg"), desen)

    X = np.array(X, dtype=np.uint8).reshape(-1, a.latura, a.latura, 3)
    F = np.array(F, dtype=np.float32).reshape(-1, 2)
    y = np.array(y)
    print()
    print(f"X.shape = {X.shape}  (decupaje {a.latura}×{a.latura}, color)")
    print(f"F.shape = {F.shape}  (lungime, lățime în {unitate})")
    print(f"y.shape = {y.shape}")
    print("Decupaje pe clasă:", dict(Counter(y.tolist())))
    if not a.mm_per_px:
        print("Atenție: fără --mm-per-px, dimensiunile sunt în pixeli, nu în mm.")
    plansa(list(X), [f"{i}\n{e}" for i, e in zip(id_uri, y)], iesire / "decupaje.png")
    print(f"Imaginile de inspecție sunt în {iesire}/")

    print()
    if probleme:
        print(f"Probleme găsite ({len(probleme)}):")
        for pr in probleme:
            print("  -", pr)
    else:
        print("Nicio problemă găsită.")


if __name__ == "__main__":
    main()
