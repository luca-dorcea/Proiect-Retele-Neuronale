# Rețele neuronale · Proiect · P3 – Primul experiment

**UNSTPB · FIIR · Informatică industrială, anul III · 2026–2027**

> **Cum se completează fișa**
>
> - Redenumiți fișierul cu numele vostru, fără diacritice și fără spații, adăugând sprintul: `RN_P3_Popescu_Ion_S1.md` pentru versiunea din sală și `RN_P3_Popescu_Ion_S2.md` pentru versiunea revizuită. În repository, în `docs/`, păstrați versiunea finală ca `RN_P3_Popescu_Ion.md`.
> - Păstrați titlurile și numerotarea. Înlocuiți textele dintre paranteze drepte `[...]` cu răspunsuri proprii; ștergeți întrebările ajutătoare după ce ați răspuns.
> - Cifrele din secțiunea 3 se copiază din `results/p3.json`, generat de cod; nu se scriu de mână.
> - Pentru ce nu știți încă scrieți **„de verificat”**.
> - **Sprintul 1** (în sală): completați secțiunile 0–2, 3.1 și primele două rânduri din 3.3 (familia modelului și motivul) și încărcați fișierul `_S1` în activitatea Moodle „P3 · Primul experiment” **înainte de finalul ședinței**. **Sprintul 2** (până la termen): faceți o copie `_S2`, completați restul, corectați ce e nevoie și încărcați-o în aceeași activitate, **fără să ștergeți fișierul `_S1`**; în câmpul de text puneți legătura către repository și SHA-ul commit-ului.

---

## 0. Identificare

| Câmp | Răspuns |
|---|---|
| Nume și prenume | Dorcea Luca-Cristian |
| Grupa | 633AB |
| Titlul proiectului (actualizat, dacă s-a schimbat) | Recunoașterea automată a tipului și dimensiunii șuruburilor, piulițelor și șaibelor din fotografii, pentru sortarea pieselor de asamblare (neschimbat) |
| Tema s-a schimbat față de P2? | nu |
| Situația de pornire | pilot care necesită adaptare |
| Repository-ul proiectului | https://github.com/FIIR-RN2026/633ab-dorcea-luca-cristian |
| Versiunea fișei și data | Sprintul 1 · 05.11.2026 |

## 1. Ce va învăța rețeaua și cum ajung datele la model?

**1.1. Sarcina.** Modelul primește decupajul unei singure piese, tăiat din fotografie prin prelucrare clasică (prag, operații morfologice, contururi, dreptunghiul minim rotit), plus lungimea și lățimea piesei măsurate în mm. Modelul trebuie să producă o singură clasă (tipul și dimensiunea piesei), cu probabilitatea fiecărei clase. Sarcina este restrânsă față de aplicația completă: toate cele trei soluții (S0, S1 și rețeaua) primesc aceleași decupaje. Experimentul arată cât de bine se clasifică o piesă deja izolată; nu arată cât de bine găsește programul piesele în fotografia completă (piese care se ating, obiecte care nu sunt piese). În pilot există doar șuruburi, în 4 clase: `surub_hex_d7_L24`, `surub_hex_d4_L43`, `surub_hex_d8_L106` și `surub_hex_d9_L102`; piulițele și șaibele nu au fost încă fotografiate.

**1.2. Organizarea datelor.** Datele pornesc de la manifestul din P2 (`data/pilot/manifest.csv`, câte un rând pe fotografie, cu clasa și grupul). Programul `src/data/citire_pilot.py` citește fotografiile, găsește piesele și produce pentru fiecare piesă decupajul, lungimea și lățimea în mm și eticheta fotografiei. În repository sunt manifestul și 5 fotografii; celelalte 23 de fotografii le păstrez local, ca repository-ul să conțină doar câteva exemple. Față de P2 trebuie completate:
- etichetele: programul a dat eticheta fotografiei și unor obiecte care nu sunt piese (8 obiecte: bucăți din mâna din fotografia 184411 și gradații ale riglei); păstrez doar decupajul piesei din fiecare fotografie cu o singură piesă, verificat cu coloana `numar_piese`;
- grupurile: coloana `grup` din P2 arată piesa fizică doar parțial; în clasa de 106 mm sunt două șuruburi distincte (SUN 6.8 și SFC 8.8), dar nu am notat în ce fotografie apare fiecare;
- fotografiile amestecate (4 fotografii, 15 piese) nu au încă clasa pe fiecare decupaj, deci nu intră în experiment.

**1.3. Ce ajunge la model.**

| | Răspuns |
|---|---|
| Forma unui exemplu la intrare (de exemplu 64 × 64 × 3, 42 de valori, 499 × 3) | un decupaj color de 256 × 256 × 3 pixeli și 2 valori (lungimea și lățimea în mm) |
| Pregătirea intrării (redimensionare, standardizare cu valori învățate pe antrenare, extractor preantrenat declarat) | Piesa este rotită cu axa lungă orizontală și decupată fără redimensionare, ca să se păstreze informația de mărime. Pixelii se împart la 255. Lungimea și lățimea se standardizează cu media și abaterea standard calculate pe antrenare. Nu folosesc extractor preantrenat. |
| Verificarea că informația relevantă rămâne vizibilă după pregătire (de exemplu obiectul sau defectul, după redimensionare) | Am verificat vizual decupajele din pilot (P2, secțiunea 5.3): piesa întreagă, cu capul, rămâne vizibilă în decupaj. Dimensiunile măsurate de program sunt mai mari cu 1–7 mm decât cele măsurate cu rigla, din cauza umbrei și a telefonului ținut în mână. |
| Forma ieșirii | 4 probabilități, câte una pentru fiecare clasă din pilot |

**1.4. Distribuția.**

| Clasa (sau intervalul valorii țintă) | Exemple | Grupuri din care provin |
|---|---|---|
| `surub_hex_d7_L24` | 5 | 1 (șurubul Z.M 8.8) |
| `surub_hex_d4_L43` | 5 | 1 (șurubul subțire) |
| `surub_hex_d8_L106` | 9 | 2 piese fizice (SUN 6.8 și SFC 8.8), dar nu știu în ce fotografie apare fiecare, deci 1 grup utilizabil (`SUN_SFC`) |
| `surub_hex_d9_L102` | 4 | 1 (șurubul CW 8.8) |

Exemplele sunt piesele din cele 23 de fotografii cu o singură piesă, în care programul a găsit piesa (în fotografia 184411 mâna acoperă șurubul). Clasa `surub_hex_d9_L102` are cele mai puține exemple, dar problema principală nu este numărul de exemple, ci numărul de piese fizice: fiecare clasă are o singură piesă identificabilă. Ce fac: colectare țintită, cu mai multe piese distincte în fiecare clasă, fotografiate de la postul fix.

**1.5. Proveniența.** Toate cele 23 de exemple vin din fotografiile mele, cu piesele mele, făcute cu telefonul (Samsung Galaxy S26 Ultra) pe hârtie milimetrică, la 28.10.2026. Nu folosesc niciun set public. Condițiile diferă de cele de utilizare: telefonul a fost ținut în mână, iar postul fix (trepied, fundal, lampă) nu este încă montat.

## 2. Cum separ datele?

**2.1. Regula de separare.** Separ pe grupuri. În utilizare, modelul va întâlni piese pe care nu le-a văzut la antrenare, deci un grup este o piesă fizică: toate decupajele aceleiași piese (din toate fotografiile și orientările ei) intră în același set. Fotografiile aceleiași piese, făcute la câteva secunde distanță, sunt aproape identice, deci nu le despart între seturi. Pilotul nu permite încă o separare relevantă: în fiecare clasă am o singură piesă fizică identificabilă, deci nu pot pune piese diferite din aceeași clasă în antrenare, validare și test. Trebuie completate: mai multe piese distincte în fiecare clasă (cel puțin trei, ca fiecare set să aibă o piesă proprie), fiecare notată în manifest cu propriul grup, plus piulițele și șaibele. O rulare pe pilot va verifica doar că antrenarea funcționează; nu va arăta cât de bine generalizează modelul pe piese noi.

**2.2. Seturile.**

| Set | Exemple | Grupuri | Distribuția pe clase (sau intervalul țintei) |
|---|---|---|---|
| antrenare | nu există încă o separare relevantă | 1 piesă fizică pe clasă, insuficient | — |
| validare | nu există încă o separare relevantă | — | — |
| test (pus deoparte) | de colectat | — | — |

Separarea se va păstra în `data/split.csv`, câte un rând pe exemplu, cu setul lui.

**2.3. Testul.**

| | Răspuns |
|---|---|
| Starea testului | de colectat: piese distincte din fiecare clasă, care nu apar deloc în antrenare și validare, fotografiate într-o sesiune separată, în fotografii cu piese amestecate; clasa fiecărui decupaj o stabilesc prin măsurare directă |
| Din ce condiții vine și de ce reprezintă utilizarea reală | De la postul fix (telefon pe trepied, de sus), cu piese amestecate, așezate separat. Aceasta este situația din utilizare: un lot de piese amestecate, fotografiate o dată, din care fiecare piesă trebuie pusă în compartimentul ei. |
| Confirmare că nu a fost folosit la P3 | în `results/p3.json`: `"test_evaluat": false`; codul de antrenare și de evaluare nu citește exemplele de test |

**2.4. Augmentarea.** Nu folosesc încă augmentare. Variația o obțin fotografiind aceleași piese de mai multe ori, rearanjate, întoarse și rotite. Dacă adaug augmentare, o aplic doar pe antrenare, după separare.

## 3. Ce arată primul experiment?

**3.1. Reperul S0.** S0 răspunde mereu clasa cea mai frecventă în setul de antrenare, determinată doar din antrenare. Pe pilot nu raportez un rezultat pe validare, pentru că datele nu permit încă o separare relevantă pe piese (secțiunea 2.1): în fiecare clasă am o singură piesă fizică identificabilă. Ca să pot măsura S0 pe validare trebuie completate mai multe piese distincte în fiecare clasă, fiecare cu propriul grup în manifest.

**3.2. Reperul S1.** [Soluția fără rețea din fișa P2, descrisă prin operații. Parametrii învățați din date, estimați pe antrenare; pragurile de decizie și alegerile dintre variante, stabilite pe validare.]

**3.3. Prima rețea.**

| | Răspuns |
|---|---|
| Familia modelului și motivul alegerii | O rețea convoluțională (CNN) mică, pentru că intrarea principală este o imagine cu o singură piesă, iar diferențele dintre clase sunt de formă și aspect (capul, filetul, grosimea tijei). Cele 2 valori în mm (lungimea și lățimea) se adaugă după straturile convoluționale, înaintea straturilor complet conectate, pentru că mărimea reală a piesei nu se poate deduce sigur doar din imagine. |
| De la zero sau model preantrenat adaptat? Dacă e preantrenat: ce ați preluat, ce ați antrenat și de ce | De la zero, proiectată și antrenată de mine, ca la laboratoare: sarcina are puține clase, iar imaginile sunt simple (o piesă pe fundal uniform). |
| Arhitectura, pe scurt (straturi, număr de parametri) | [ ] |
| Antrenarea: epoci, oprirea timpurie (epoca păstrată), rata de învățare | [ ] |
| Configurația folosită (în repository, calea) și modelul sau parametrii antrenați (calea; dacă fișierul e prea mare, locația și modalitatea de acces pentru îndrumător) | [ ] |

**3.4. Metrica principală.** [Ce metrică și de ce, legată de greșeala cea mai gravă din fișa P2.]

**3.5. Rezultatele pe validare** (copiate din `results/p3.json`; o valoare nemăsurată rămâne `null`, cu motivul).

| Model | Metrica principală | Măsură suplimentară, dacă este necesară |
|---|---|---|
| S0 | [ ] | [ ] |
| S1 | [ ] | [ ] |
| Rețeaua | [ ] | [ ] |

[Suficient din erori pentru a interpreta metrica: matricea de confuzie, erorile numerice sau exemple vizuale, după sarcină; figura în repository și ce arată.]

**3.6. Curbele de antrenare.** [Calea figurii în repository și ce arată: unde s-a oprit antrenarea, dacă apare supraînvățarea.]

## 4. Constatarea și următorul pas

**4.1. Ce a arătat experimentul.** [O constatare concretă, cu cifre: ce merge, ce nu, unde greșește rețeaua (câteva exemple examinate). Dacă experimentul a fost doar o rulare tehnică pe pilot, spuneți-o.]

**4.2. Ce schimbați și de ce.** [Date, separare, metrică sau model. Când rezultatul e slab, începeți cu datele.]

**4.3. Ce rămâne deschis.** [Riscuri, lucruri neverificate.]

## 5. Resurse

| | Răspuns |
|---|---|
| Unde ați antrenat (Colab, Kaggle, calculatorul propriu, laborator) | [ ] |
| Cât durează o antrenare | [ ] |
| Ajung resursele pentru pașii următori? De ce ajutor aveți nevoie? | [ ] |

## 6. Fișierele din repository

| Fișier | Rol |
|---|---|
| `data/split.csv` (sau coloana `set` în manifest) | setul fiecărui exemplu |
| `src/baseline.py` | S0 și S1 |
| `src/train.py` sau `notebooks/…` | [antrenarea rețelei] |
| `results/p3.json` | rezultatele pe validare, generate de cod |
| `results/…` | [curbele, matricea de confuzie sau exemplele de erori] |
| `models/…` sau `results/…` | [configurația folosită; modelul sau parametrii antrenați, ori locația lor dacă fișierul e prea mare] |
| `docs/RN_P3_Nume_Prenume.md` | fișa finală |

## 7. Surse și utilizarea AI

**7.1. Surse.**
- *P3 · Primul experiment* (instrucțiuni, RN_P3_Instructiuni.pdf), cadrele didactice ale disciplinei Rețele neuronale, UNSTPB FIIR, 2026: https://curs.upb.ro/2026/mod/resource/view.php?id=59291
- Fișa mea P2 (`docs/RN_P2_Dorcea_Luca-Cristian.md`), din care am preluat pilotul, manifestul și programul de citire.

**7.2. Utilizarea AI.** Am folosit Claude (Anthropic) pentru redactarea acestei fișe pe baza fișei P2, a pilotului meu și a răspunsurilor mele. Fotografiile și măsurătorile sunt făcute de mine; niciun exemplu nu este generat cu AI.
