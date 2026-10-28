"""Citirea și inspecția lotului pilot (P2 · Datele).

Programul:
1. citește `data/pilot/manifest.csv` și verifică coloanele și fișierele;
2. deschide fiecare fotografie și găsește piesele prin prelucrare clasică
   (tonuri de gri, prag Otsu, operații morfologice, contururi, dreptunghiul minim rotit);
3. rotește fiecare piesă cu axa lungă orizontală și o pune, fără redimensionare,
   pe un decupaj de dimensiune fixă;
4. afișează forma datelor care ajung la model (X, F, y) și problemele găsite;
5. salvează imagini de inspecție (contururile pe fotografie și o planșă cu decupaje).

Coloana opțională `numar_piese` din manifest (câte piese a pus autorul în fotografie) se compară
cu numărul de obiecte găsite, ca să se vadă detecțiile false sau ratate.

Fotografiile de antrenare conțin o singură clasă, deci fiecare decupaj primește
`raspuns_corect` din rândul fotografiei. Pentru fotografiile amestecate sau fără
răspuns, eticheta decupajelor rămâne „lipsă”.

În repository sunt doar câteva fotografii (data/pilot/); restul lotului se păstrează local,
de exemplu în data/raw/pilot/ (ignorat de git), și se indică cu --originale.

Rulare (din rădăcina repository-ului):
    python src/data/citire_pilot.py --canal hartie --scara-imagine 0.25
    python src/data/citire_pilot.py --canal hartie --scara-imagine 0.25 --originale data/raw/pilot
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
    if cale.suffix.lower() in (".heic", ".heif"):
        # OpenCV nu citește HEIC (formatul implicit al telefonului); se folosește pillow-heif
        from PIL import Image, ImageOps
        import pillow_heif

        pillow_heif.register_heif_opener()
        with Image.open(cale) as im:
            rgb = np.array(ImageOps.exif_transpose(im).convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    # np.fromfile + imdecode merge și cu căi cu diacritice pe Windows
    date = np.fromfile(str(cale), dtype=np.uint8)
    return cv2.imdecode(date, cv2.IMREAD_COLOR) if date.size else None


def zona_hartie(imagine):
    """Zona cu caroiaj albastru a hârtiei milimetrice, ca dreptunghi rotit micșorat spre interior."""
    b = cv2.GaussianBlur(cv2.cvtColor(imagine, cv2.COLOR_BGR2LAB)[:, :, 2], (5, 5), 0)
    # hârtia albastră are componenta b (galben–albastru) mai mică decât lemnul și marginea albă
    _, masca = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contururi, _ = cv2.findContours(masca, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contururi:
        return None
    colturi = cv2.boxPoints(cv2.minAreaRect(cv2.convexHull(max(contururi, key=cv2.contourArea))))
    zona = np.zeros(masca.shape, np.uint8)
    cv2.drawContours(zona, [colturi.astype(np.int32)], 0, 255, -1)
    # se scot marginile hârtiei și rigla de deasupra
    margine = impar(imagine.shape[1] * 0.025)
    return cv2.erode(zona, np.ones((margine, margine), np.uint8))


def mm_per_px_din_caroiaj(gri, zona, latura=512):
    """Factorul de scară din caroiajul de 1 mm: perioada dominantă din spectrul 2D, pe 4 ferestre."""
    x, y, w, h = cv2.boundingRect(zona)
    perioade = []
    for fx, fy in [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)]:
        cx, cy = int(x + fx * w), int(y + fy * h)
        bucata = gri[cy - latura // 2:cy + latura // 2, cx - latura // 2:cx + latura // 2].astype(float)
        if bucata.shape != (latura, latura):
            continue
        bucata -= cv2.GaussianBlur(bucata, (0, 0), 15)
        fereastra = np.outer(np.hanning(latura), np.hanning(latura))
        spectru = np.abs(np.fft.fftshift(np.fft.fft2(bucata * fereastra)))
        yy, xx = np.indices(spectru.shape)
        raza = np.hypot(yy - latura // 2, xx - latura // 2)
        # liniile de 1 mm au perioada căutată între 4 și 20 px
        spectru[(raza < latura / 20) | (raza > latura / 4)] = 0
        varf = np.unravel_index(np.argmax(spectru), spectru.shape)
        perioade.append(latura / raza[varf])
    return 1.0 / float(np.median(perioade)) if perioade else None


def impar(valoare):
    return max(3, int(valoare) // 2 * 2 + 1)


def gaseste_piese(imagine, arie_minima, canal="gri", zona=None):
    """Întoarce, pentru fiecare piesă, conturul exterior, dreptunghiul rotit și numărul de găuri."""
    if canal == "hartie":
        # pe caroiaj, piesa diferă de fundalul local (mediana pe o fereastră mare) mai mult decât liniile subțiri
        gri = cv2.medianBlur(cv2.cvtColor(imagine, cv2.COLOR_BGR2GRAY), 5)
        diferenta = cv2.absdiff(gri, cv2.medianBlur(gri, impar(imagine.shape[1] * 0.06)))
        valori = diferenta[zona > 0]
        mediana = np.median(valori)
        prag = max(18, mediana + 8 * np.median(np.abs(valori - mediana)))
        masca = np.where((diferenta > prag) & (zona > 0), 255, 0).astype(np.uint8)
        nucleu = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        masca = cv2.morphologyEx(masca, cv2.MORPH_CLOSE, nucleu)
        masca = cv2.morphologyEx(masca, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        return piese_din_masca(masca, arie_minima), masca
    if canal == "saturatie":
        # fundal deschis de lemn: oțelul zincat are saturația mai mare decât lemnul
        plan = cv2.cvtColor(imagine, cv2.COLOR_BGR2HSV)[:, :, 1]
    else:
        # fundal închis, piese metalice mai deschise
        plan = cv2.cvtColor(imagine, cv2.COLOR_BGR2GRAY)
    plan = cv2.GaussianBlur(plan, (5, 5), 0)
    _, masca = cv2.threshold(plan, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    nucleu = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    masca = cv2.morphologyEx(masca, cv2.MORPH_OPEN, nucleu)
    masca = cv2.morphologyEx(masca, cv2.MORPH_CLOSE, nucleu)
    return piese_din_masca(masca, arie_minima), masca


def piese_din_masca(masca, arie_minima):
    contururi, ierarhie = cv2.findContours(masca, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if ierarhie is None:
        return []
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
    return piese


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


def atinge_marginea(contur, forma, zona=None):
    if zona is not None:
        piesa = np.zeros(forma[:2], np.uint8)
        cv2.drawContours(piesa, [contur], 0, 255, -1)
        return bool((cv2.dilate(piesa, np.ones((5, 5), np.uint8)) & cv2.bitwise_not(zona)).any())
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
    p.add_argument("--canal", choices=["gri", "saturatie", "hartie"], default="gri",
                   help="gri: fundal închis (postul fix); saturatie: fundal deschis de lemn; "
                        "hartie: hârtie milimetrică, cu scara calculată din caroiaj pentru fiecare fotografie")
    p.add_argument("--latime-minima-mm", type=float, default=2.0,
                   help="obiectele mai înguste sunt ignorate (de exemplu gradațiile riglei); doar când scara e cunoscută")
    p.add_argument("--alungire-maxima", type=float, default=15.0,
                   help="obiectele cu lungime/lățime mai mare sunt ignorate, ca linii subțiri")
    p.add_argument("--scara-imagine", type=float, default=1.0,
                   help="micșorează toate fotografiile cu același factor înainte de prelucrare")
    p.add_argument("--arie-minima", type=float, default=0.0005, help="aria minimă a unei piese, ca fracție din fotografie")
    p.add_argument("--originale", nargs="*", default=[],
                   help="foldere locale în care se caută fotografiile care nu sunt în repository")
    p.add_argument("--iesire", default=None, help="folderul pentru imaginile de inspecție (implicit <pilot>/inspectie)")
    a = p.parse_args()

    pilot = Path(a.pilot)
    iesire = Path(a.iesire) if a.iesire else pilot / "inspectie"
    iesire.mkdir(parents=True, exist_ok=True)
    randuri = citeste_manifest(pilot / "manifest.csv")
    unitate = "mm" if a.mm_per_px or a.canal == "hartie" else "px"

    print(f"Manifest: {len(randuri)} rânduri")
    print("  pe grup:", dict(Counter(r["grup"] for r in randuri)))
    print("  pe răspuns corect:", dict(Counter(r["raspuns_corect"] for r in randuri)))

    probleme, lipsa = [], []
    X, F, y, id_uri = [], [], [], []
    for r in randuri:
        cale = next((d / r["fisier"] for d in [pilot, *map(Path, a.originale)] if (d / r["fisier"]).exists()), None)
        if cale is None:
            lipsa.append(r["id_exemplu"])
            continue
        imagine = citeste_imagine(cale)
        if imagine is None:
            probleme.append(f"{r['id_exemplu']}: fișierul {r['fisier']} nu se poate citi ca imagine")
            continue
        scara = a.mm_per_px
        zona = None
        if a.canal == "hartie":
            mica = cv2.resize(imagine, None, fx=a.scara_imagine, fy=a.scara_imagine, interpolation=cv2.INTER_AREA)
            zona = zona_hartie(mica)
            if zona is None:
                probleme.append(f"{r['id_exemplu']}: hârtia milimetrică nu a fost găsită")
                continue
            # caroiajul de 1 mm se vede doar la rezoluția completă
            zona_mare = cv2.resize(zona, (imagine.shape[1], imagine.shape[0]), interpolation=cv2.INTER_NEAREST)
            scara = mm_per_px_din_caroiaj(cv2.cvtColor(imagine, cv2.COLOR_BGR2GRAY), zona_mare)
            if scara is None:
                probleme.append(f"{r['id_exemplu']}: scara nu a putut fi calculată din caroiaj")
                continue
            scara /= a.scara_imagine
            imagine = mica
        elif a.scara_imagine != 1.0:
            imagine = cv2.resize(imagine, None, fx=a.scara_imagine, fy=a.scara_imagine, interpolation=cv2.INTER_AREA)
            if scara:
                scara /= a.scara_imagine
        arie_minima = a.arie_minima * imagine.shape[0] * imagine.shape[1]
        piese, _ = gaseste_piese(imagine, arie_minima, a.canal, zona)
        # linii subțiri (gradațiile riglei, marginea hârtiei): prea înguste sau prea alungite pentru o piesă
        def linie(pi):
            lung, lat = max(pi["dreptunghi"][1]), max(min(pi["dreptunghi"][1]), 1e-6)
            return lung / lat > a.alungire_maxima or (scara is not None and lat * scara < a.latime_minima_mm)
        linii = [pi for pi in piese if linie(pi)]
        piese = [pi for pi in piese if not linie(pi)]
        if linii:
            probleme.append(f"{r['id_exemplu']}: {len(linii)} linii subțiri ignorate")
        eticheta = r["raspuns_corect"].strip()
        if eticheta.lower() in FARA_RASPUNS:
            eticheta = "lipsă"
        text_scara = f", {scara:.4f} mm/px" if scara else ""
        print(f"{r['id_exemplu']}: {imagine.shape[1]}×{imagine.shape[0]} px{text_scara}, {len(piese)} obiecte găsite, răspuns: {eticheta}")
        if not piese:
            probleme.append(f"{r['id_exemplu']}: nicio piesă găsită (prag sau fundal nepotrivit?)")

        taiate = 0
        desen = imagine.copy()
        if zona is not None:
            contur_zona, _ = cv2.findContours(zona, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(desen, contur_zona, -1, (255, 0, 0), 1)
        for k, piesa in enumerate(piese, start=1):
            (_, _), (w, h), _ = piesa["dreptunghi"]
            lungime, latime = max(w, h) * (scara or 1.0), min(w, h) * (scara or 1.0)
            cutie = cv2.boxPoints(piesa["dreptunghi"]).astype(np.int32)
            id_piesa = f"{r['id_exemplu']}_{k:02d}"
            if atinge_marginea(piesa["contur"], imagine.shape, zona):
                # o piesă tăiată de margine nu se poate măsura întreagă
                cv2.drawContours(desen, [cutie], 0, (0, 0, 255), 1)
                taiate += 1
                continue
            cv2.drawContours(desen, [cutie], 0, (0, 255, 0), 2)
            cv2.putText(desen, str(k), tuple(cutie[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            decupaj = decupeaza(imagine, piesa["dreptunghi"], a.latura)
            if decupaj is None:
                probleme.append(f"{id_piesa}: piesa ({max(w, h):.0f}×{min(w, h):.0f} px) nu încape în {a.latura}×{a.latura}")
                continue
            print(f"    {id_piesa}: {lungime:.1f}×{latime:.1f} {unitate}, găuri: {piesa['gauri']}")
            X.append(decupaj)
            F.append([lungime, latime])
            y.append(eticheta)
            id_uri.append(id_piesa)
        if taiate:
            loc = "zonei de lucru" if zona is not None else "fotografiei"
            probleme.append(f"{r['id_exemplu']}: {taiate} obiecte tăiate de marginea {loc} ignorate")
        pastrate = sum(1 for i in id_uri if i.startswith(r["id_exemplu"] + "_"))
        asteptate = (r.get("numar_piese") or "").strip()
        if asteptate.isdigit() and int(asteptate) != pastrate:
            probleme.append(f"{r['id_exemplu']}: {pastrate} obiecte păstrate, dar în fotografie sunt {asteptate} piese")
        cv2.imwrite(str(iesire / f"{r['id_exemplu']}_contururi.jpg"), desen)

    X = np.array(X, dtype=np.uint8).reshape(-1, a.latura, a.latura, 3)
    F = np.array(F, dtype=np.float32).reshape(-1, 2)
    y = np.array(y)
    print()
    print(f"X.shape = {X.shape}  (decupaje {a.latura}×{a.latura}, color)")
    print(f"F.shape = {F.shape}  (lungime, lățime în {unitate})")
    print(f"y.shape = {y.shape}")
    print("Decupaje pe clasă:", dict(Counter(y.tolist())))
    if unitate == "px":
        print("Atenție: fără --mm-per-px, dimensiunile sunt în pixeli, nu în mm.")
    plansa(list(X), [f"{i}\n{e}" for i, e in zip(id_uri, y)], iesire / "decupaje.png")
    print(f"Imaginile de inspecție sunt în {iesire}/")

    if lipsa:
        print(f"{len(lipsa)} fotografii din manifest nu au fost găsite (nu sunt în repository; indicați folderul cu --originale).")
    print()
    if probleme:
        print(f"Probleme găsite ({len(probleme)}):")
        for pr in probleme:
            print("  -", pr)
    else:
        print("Nicio problemă găsită.")


if __name__ == "__main__":
    main()
