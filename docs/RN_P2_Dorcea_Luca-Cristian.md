# Rețele neuronale · Proiect · P2 – Datele

**UNSTPB · FIIR · Informatică industrială, anul III · 2026–2027**

> **Cum se completează fișa**
>
> - Redenumiți fișierul cu numele vostru, fără diacritice și fără spații, adăugând sprintul: `RN_P2_Popescu_Ion_S1.md` pentru versiunea din sală și `RN_P2_Popescu_Ion_S2.md` pentru versiunea revizuită. În repository, în `docs/`, păstrați versiunea finală ca `RN_P2_Popescu_Ion.md`.
> - Păstrați titlurile și numerotarea. Înlocuiți textele dintre paranteze drepte `[...]` cu răspunsuri proprii. Întrebările ajutătoare din *italic* nu sunt rubrici separate; vă ajută să nu omiteți nimic.
> - Răspundeți la toate cele trei întrebări **pe același exemplu concret**.
> - Pentru ce nu știți încă scrieți **„de verificat”**. Nu prezentați presupunerile drept fapte verificate.
> - **Sprintul 1** (în sală): completați secțiunile 0–4 și încărcați fișierul `_S1` în activitatea Moodle „P2 · Datele” **înainte de finalul ședinței**. **Sprintul 2** (până înainte de P3): faceți o copie `_S2`, completați secțiunile 5–6, corectați secțiunile 1–4 unde e nevoie și încărcați-o în aceeași activitate, **fără să ștergeți fișierul `_S1`**; adăugați legătura către repository în câmpul de text.

---

## 0. Identificare

| Câmp | Răspuns |
|---|---|
| Nume și prenume | Dorcea Luca-Cristian |
| Grupa | 633AB |
| Titlul proiectului (actualizat, dacă s-a schimbat față de P1) | Recunoașterea automată a tipului și dimensiunii șuruburilor, piulițelor și șaibelor din fotografii, pentru sortarea pieselor de asamblare (neschimbat față de P1) |
| Tema este o temă propusă de partener? | nu |
| Repository-ul proiectului | https://github.com/FIIR-RN2026/633ab-dorcea-luca-cristian |
| Versiunea fișei și data | Sprintul 2 · 28.10.2026 |

## 1. Ce vreau să decid?

**1.1. Decizia.** Rezultatul îl folosește persoana care sortează piesele de asamblare amestecate dintr-un atelier; în acest proiect, eu, în garajul meu. Astăzi identific fiecare piesă după ochi. Pe baza rezultatului, citesc tipul și dimensiunea afișate pe fiecare piesă și decid în ce compartiment o pun și ce cantitate înregistrez în inventar. Decizia finală îmi aparține; aplicația nu acționează singură.

**1.2. Exemplul și momentul deciziei.** Exemplul este o singură piesă: imaginea decupată a piesei din fotografia făcută la postul fix, rotită astfel încât axa ei lungă să fie orizontală, împreună cu lungimea și lățimea ei măsurate în mm din imagine. Modelul dă un singur răspuns pentru fiecare piesă: clasa ei (tip și dimensiune). Răspunsul trebuie dat după ce fotografia este făcută și înainte ca piesele să fie luate de pe masă și puse în compartimente.

**1.3. Intrarea și ieșirea.**

| | Răspuns |
|---|---|
| Ce date am în momentul deciziei (format, sursă) | O fotografie color (fișier imagine de la camera telefonului), luată de sus, perpendicular pe masă, cu camera pe trepied la distanță constantă, pe fundal mat, uniform, închis la culoare, cu piesele așezate separat; factorul de scară mm/pixel, calibrat o singură dată cu o riglă. În pilot nu am avut trepied și fundal închis: am ținut telefonul în mână, piesele au stat pe hârtie milimetrică, iar scara mm/pixel s-a calculat din caroiajul hârtiei, separat pentru fiecare fotografie. |
| Ce ajunge efectiv la model (de exemplu: 4 valori; o imagine 224×224; o fereastră de 200 de eșantioane) | Pentru fiecare piesă: o imagine decupată de 256×256 pixeli, obținută prin prelucrare clasică (prag, operații morfologice, contururi, dreptunghiul minim rotit), fără redimensionarea piesei, ca să se păstreze informația de mărime; plus 2 valori: lungimea și lățimea piesei în mm. |
| Ce produce modelul (clasele, mărimea și unitatea sau casetele) | Clasa piesei dintr-o listă fixă de aproximativ 6 clase de tip și dimensiune (de exemplu „șurub M4×16”, „piuliță M5”, „șaibă M6”), cu probabilitatea fiecărei clase. |
| Ce face restul aplicației cu rezultatul (o propoziție) | Afișează eticheta clasei pe fiecare piesă din fotografie și un tabel cu numărul de piese din fiecare clasă. |

*Verificați: am fiecare intrare în momentul deciziei? Nicio intrare nu vine din viitor și nu conține deja răspunsul.*

Toate intrările provin din fotografie și din calibrare. Măsurătoarea directă a piesei (cu rigla sau cu șublerul), din care rezultă răspunsul corect, nu intră în model.

## 2. Cum știu răspunsul corect?

**2.1. Sursa răspunsului corect.** Răspunsul corect îl stabilesc eu, prin măsurarea directă a piesei și printr-o condiție creată la colectare. Plănuiesc să măsor cu șublerul; până am acces la unul, măsor cu rigla, cu o eroare de ±1 mm. Pentru antrenare, într-o fotografie pun doar piese din aceeași clasă, măsurate înainte, deci toate decupajele din acea fotografie primesc eticheta clasei respective. Pentru test, fac fotografii separate cu piese amestecate și etichetez manual fiecare decupaj, verificând clasa prin măsurare. Măsurarea directă are în plus față de model dimensiunile fizice ale piesei (diametrul tijei, lungimea), fără erorile de segmentare, umbre, reflexii sau scară din fotografie. Răspunsul este disponibil în momentul colectării și se leagă de exemplu prin numele fișierului fotografiei, notat în manifest împreună cu clasa. Marcajul de pe capul șurubului (de exemplu „8.8”, clasa de rezistență) nu face parte din clasă; îl folosesc doar ca să știu ce piesă fizică este în fotografie (coloana `grup` din manifest).

O parte din răspuns se poate calcula din intrări printr-o regulă cunoscută: dimensiunea, din lungimea și lățimea în mm comparate cu valorile nominale. Această regulă face parte din reperul S1 (secțiunea 3.2). Rețeaua poate aduce în plus trăsături de aspect (forma și mărimea capului, filetul, reflexiile), greu de exprimat prin praguri fixe, utile când piesele au dimensiuni apropiate sau sunt așezate pe o parte. Pilotul a arătat un astfel de caz: două clase de șuruburi lungi, de 102 mm și de 106 mm, nu se pot separa după lungimea măsurată în fotografie, dar se deosebesc după cap (secțiunea 5.3).

*Dacă răspunsul vine dintr-un set public: cum l-au stabilit autorii setului? Dacă răspunsul se calculează din intrări printr-o regulă cunoscută: regula devine reperul S1; ce ar aduce rețeaua în plus? Dacă depinde de judecata cuiva: care este regula și ce faceți cu un caz neclar?*

**2.2. Exemplul real examinat.**

| | Răspuns |
|---|---|
| Ce exemplu am examinat (descriere sau cale către fișier) | `data/pilot/20261028_184249.jpg`: un șurub scurt cu cap hexagonal, marcat pe cap „Z.M 8.8”, culcat pe hârtie milimetrică și fotografiat de sus. Decupajul lui, produs de programul de citire, este `L2_184249_02`. |
| De unde provine (sursa; aceeași cu cea din care va veni testul?) | Fotografie făcută de mine cu telefonul (Samsung Galaxy S26 Ultra), ținut în mână. Testul va veni din aceeași sursă (telefonul meu și piesele mele), dar de la postul fix, cu trepied; deci fotografiile din pilot diferă de cele de test prin poziția camerei și prin fundal. |
| Grupul: obiectul, persoana, locul sau sesiunea din care provine | Piesa fizică: șurubul Z.M 8.8 (grupul `ZM_8.8`). Sesiunea: 28.10.2026, lotul 2 (28 de fotografii pe hârtie milimetrică). |
| Momentul în care a fost obținut | 28.10.2026, ora 18:42:49 (din datele fotografiei originale). |
| Răspunsul corect pentru acest exemplu (sau „încă indisponibil”, cu motivul) | `surub_hex_d7_L24`: lungimea 24 mm cu cap, diametrul tijei 7 mm, diametrul capului 12 mm, pasul filetului 1 mm, măsurate cu rigla (±1 mm). |
| Ce am observat (caz clar, caz neclar, problemă) | Caz clar ca etichetă: în fotografie este o singură piesă. Problemă: programul măsoară piesa 29,3 × 15,8 mm, deci cu aproximativ 5 mm mai lungă decât cu rigla, pentru că umbra piesei intră în contur. Pe lângă piesă, programul a găsit 3 linii subțiri și 3 obiecte tăiate de marginea zonei de lucru, pe care le-a ignorat. |

*Dacă nu aveți încă acces la date reale, descrieți demersul concret: documentație, format de export, cerere de acces, captură demonstrată. Nu inventați un exemplu.*

## 3. Pot construi o primă soluție?

**3.1. Datele pe care le pot strânge.** Piesele sunt ale mele, în garajul meu. Pentru antrenare, o fotografie conține aproximativ 5–10 piese din aceeași clasă, deci eticheta se obține o singură dată pentru toată fotografia. Situațiile diferite sunt piesele fizice distincte, aranjările și orientările lor și sesiunile de fotografiere (sesiune separată pentru test). În pilot, o fotografie mi-a luat aproximativ 6–7 s, iar o măsurătoare cu rigla 3–4 s. Am folosit 5 șuruburi distincte, din 4 clase; doar clasa de 106 mm are două piese distincte (SUN 6.8 și SFC 8.8). Câte piese distincte am în fiecare clasă, inclusiv piulițe și șaibe, stabilesc la inventar (secțiunea 4).

**3.2. Reperul simplu și greșeala importantă.** Reperul S1 este un program bazat pe reguli, aplicat pe aceleași contururi ca rețeaua:
- contur cu gaură interioară și margine exterioară rotundă → șaibă;
- contur cu gaură interioară și margine exterioară hexagonală → piuliță;
- contur alungit, fără gaură → șurub;
- dimensiunea se alege după lățimea și lungimea măsurate în mm, cu factorul de scară de la calibrare, prin comparare cu valorile nominale.

Cea mai costisitoare greșeală este o dimensiune greșită (de exemplu un șurub M4 clasificat ca M5): piesa ajunge în compartimentul greșit, iar greșeala se descoperă abia la montaj, când piesa nu se potrivește. O piesă nerecunoscută costă mai puțin, pentru că se vede că nu are etichetă și o identific singur.

**3.3. Tipul datelor și o familie posibilă de rețea.** Fotografia este o imagine cu mai multe obiecte, dar prelucrarea clasică (prag și contururi) o împarte în imagini cu câte un singur obiect. Datele care ajung la model sunt deci o imagine cu un singur obiect, plus două valori numerice (lungimea și lățimea în mm); o familie posibilă este o rețea convoluțională (CNN), proiectată și antrenată de mine. Nu am nevoie de un număr mare de piese de același fel: fotografiez aceleași piese de mai multe ori, rearanjate, întoarse și rotite, iar fiecare fotografie dă decupaje noi. Din fiecare clasă păstrez câteva piese distincte doar pentru test, ca rețeaua să fie verificată pe piese pe care nu le-a văzut la antrenare. Câte piese distincte am în fiecare clasă stabilesc la inventar (secțiunea 4).

## 4. Următorul pas

| | Răspuns |
|---|---|
| Ce fac în prima săptămână | Inventariez piesele disponibile în fiecare clasă, ca să știu dacă pot păstra piese distincte doar pentru test. Montez postul fix (trepied, fundal mat, lampă în poziție fixă) și calibrez scara mm/pixel cu o riglă. Fac primele fotografii pilot, inclusiv cu două clase apropiate (de exemplu M4 și M5), și compar diferența de lățime măsurată în mm cu diferența nominală. |
| Ce îmi lipsește sau ce mă blochează (acces, permisiuni, echipament) | Nu am încă acces la un trepied și la un fundal închis la culoare, de aceea pilotul l-am făcut din mână, pe hârtie milimetrică. Nu am șubler, de aceea măsor deocamdată cu rigla. |
| De ce ajutor am nevoie de la îndrumător | Deocamdată nu am nevoie de ajutor. |

---

*Secțiunile 5–6 se completează în sprintul 2.*

## 5. Pilotul

**5.1. Ce am strâns.**

| | Răspuns |
|---|---|
| Număr de exemple | 39 de piese în 28 de fotografii (lotul 2, pe hârtie milimetrică, 28.10.2026). Lotul 1 (17 fotografii pe podea de lemn, fără hârtie) nu l-am păstrat, pentru că programul nu a putut separa piesele de fundal. |
| Număr de situații diferite (obiecte, locuri, persoane, sesiuni, zile) | 5 șuruburi distincte (Z.M 8.8, unul subțire, SUN 6.8, SFC 8.8, CW 8.8), din 4 clase, fotografiate într-o singură sesiune, în același loc; între fotografii am mutat și rotit piesele. |
| Câte au deja răspunsul corect | 24 de piese: cele din cele 24 de fotografii cu o singură piesă. Cele 15 piese din cele 4 fotografii amestecate nu au încă răspunsul pe fiecare decupaj. |
| Timp real pe exemplu (captură + răspuns corect) | Captură: aproximativ 6–7 s pe fotografie (28 de fotografii între 18:42:49 și 18:45:47). Răspuns corect: 3–4 s pe fiecare măsurătoare cu rigla. |
| Unde sunt datele (repository / local, cu motivul) | În repository (`data/pilot/`): manifestul și 5 fotografii, câte una din fiecare clasă și una amestecată. Le-am convertit în JPG fără metadate (`src/data/heic_in_jpg.py`), pentru că fotografiile originale (HEIC) conțin coordonatele GPS ale locului unde au fost făcute. Celelalte 23 de fotografii le păstrez local, pe calculatorul meu, ca repository-ul să conțină doar câteva exemple. |

**5.2. Fișierele din repository.**

| Fișier | Rol |
|---|---|
| `data/pilot/manifest.csv` | câte un rând pe fotografie: `id_exemplu`, `fisier`, `sursa`, `grup`, `moment`, `raspuns_corect`, `observatii`, plus `numar_piese` (câte piese am pus în fotografie). Exemplul este piesa: programul obține câte un decupaj pentru fiecare piesă, iar în fotografiile cu o singură piesă rândul corespunde unui singur exemplu. |
| `data/pilot/20261028_184249.jpg`, `20261028_184315.jpg`, `20261028_184405.jpg`, `20261028_184437.jpg`, `20261028_184548.jpg` | câte o fotografie pentru fiecare clasă (Z.M 8.8, SUN/SFC, cel subțire, CW) și una amestecată, cu cinci șuruburi |
| `src/data/citire_pilot.py` | programul de citire și inspecție; bibliotecile necesare sunt în `requirements.txt` |
| `src/data/heic_in_jpg.py` | convertește fotografiile HEIC de la telefon în JPG fără metadate (fără coordonatele GPS), înainte să le pun în repository |

**5.3. Ce a arătat programul de citire.** Pe tot lotul (`python src/data/citire_pilot.py --canal hartie --scara-imagine 0.25 --originale data/raw/pilot`), programul dă `X.shape = (43, 256, 256, 3)` (decupaje color de 256×256 pixeli), `F.shape = (43, 2)` (lungimea și lățimea în mm) și `y.shape = (43,)`. Decupaje pe clasă: `surub_hex_d7_L24` 7, `surub_hex_d4_L43` 11, `surub_hex_d8_L106` 9, `surub_hex_d9_L102` 4, fără răspuns 12. Doar cu cele 5 fotografii din repository, formele sunt `(7, 256, 256, 3)`, `(7, 2)` și `(7,)`.

Am comparat dimensiunile măsurate de program cu cele măsurate cu rigla:

| Piesa (clasa) | Rigla: lungime, diametrul capului | Programul: lungime × lățime |
|---|---|---|
| Z.M 8.8 (`surub_hex_d7_L24`) | 24 mm, 12 mm | 27,1–30,4 × 14,9–15,9 mm (5 fotografii) |
| subțire (`surub_hex_d4_L43`) | 43 mm, 9 mm | 44,2–47,0 × 9,4–12,3 mm (5 fotografii; în a șasea, 184411, mâna acoperă șurubul) |
| SUN 6.8 / SFC 8.8 (`surub_hex_d8_L106`) | 106 mm, 16 mm | 107,6–113,3 × 18,7–23,0 mm (9 fotografii) |
| CW 8.8 (`surub_hex_d9_L102`) | 102 mm, 19 mm | 104,9–107,9 × 22,8–25,4 mm (4 fotografii) |

Ce s-a verificat fără probleme: hârtia milimetrică este găsită în toate cele 28 de fotografii, iar scara calculată din caroiaj variază între 0,131 și 0,142 mm/pixel, deci distanța telefonului față de hârtie s-a schimbat cu aproximativ ±4% de la o fotografie la alta; calculul scării pe fiecare fotografie corectează această variație. Din cele 24 de fotografii cu o singură piesă, 23 dau un decupaj al piesei, cu clasa corectă din manifest; în fotografia 184411 mâna acoperă șurubul.

Probleme găsite:
- programul măsoară piesele mai lungi cu 1–7 mm decât rigla, pentru că umbra intră în contur și telefonul ținut în mână nu este perfect paralel cu hârtia;
- clasele de 102 mm (CW) și 106 mm (SUN/SFC) se suprapun ca lungime măsurată, deci regula după lungime nu le poate separa; le separă capul, care în fotografie are aproximativ 21,5 mm la CW și 19,4 mm la SUN/SFC;
- 8 obiecte care nu sunt piese (bucăți din mâna din fotografia 184411 și gradații ale riglei) au primit eticheta fotografiei; verificarea cu `numar_piese` le semnalează;
- piesele care se ating (fotografia 184548) sunt unite într-un singur contur, iar o piesă lipită de riglă (fotografia 184501) este ignorată;
- în fotografia 184525 șuruburile stau vertical, pe cap, deci din fotografie nu li se vede lungimea; asemenea fotografii nu respectă protocolul (piese culcate).

## 6. Ce am schimbat după sprintul 1

**6.1. Corecturi.**
- 1.3: am adăugat cum au fost făcute fotografiile pilot (din mână, pe hârtie milimetrică, cu scara calculată din caroiaj pe fiecare fotografie), pentru că nu am avut trepied și fundal închis. Am înlocuit „tonuri de gri, prag Otsu” cu „prag”: pe hârtia deschisă, cu linii albastre, pragul se aplică pe diferența față de fundalul din jur, nu pe tonurile de gri.
- 2.1: răspunsul corect se măsoară deocamdată cu rigla (±1 mm), pentru că nu am șubler; am precizat că marcajul de pe cap identifică piesa fizică, nu clasa.
- 2.2: am adăugat exemplul real (fotografia 20261028_184249).
- 3.1: am adăugat timpul pe fotografie și pe măsurătoare și numărul de piese din pilot.
- 4: am actualizat ce îmi lipsește (trepied, fundal închis, șubler) și am precizat că deocamdată nu am nevoie de ajutor de la îndrumător.
- Sursa datelor: în primul lot, pe podea de lemn, programul nu a separat corect piesele de fundal și a găsit obiecte false (sigla riglei, umbre, alte obiecte din cadru), de aceea am refăcut pilotul pe hârtie milimetrică.

**6.2. Ce rămâne deschis.**
- Pilotul conține doar șuruburi; piulițele și șaibele nu au fost încă fotografiate.
- În pilot am folosit câte o singură piesă fizică din fiecare clasă, cu excepția clasei de 106 mm (SUN și SFC); deci deocamdată am piese distincte pentru test doar în această clasă. Numărul de piese disponibile îl stabilesc la inventar.
- Reperul S1 compară dimensiunile măsurate cu valorile nominale, dar în fotografie piesele ies mai lungi cu 1–7 mm, iar clasele de 102 mm și 106 mm se suprapun.
- Rigla are eroare de ±1 mm, deci nu separă sigur diametre apropiate (de exemplu tijă de 8 mm și de 9 mm).
- Postul fix (trepied, fundal, lampă) nu este încă montat, iar fundalul final (închis la culoare sau hârtie milimetrică) nu este încă ales.
- Obiectele false (mâna, gradațiile riglei) și piesele care se ating trebuie evitate la fotografiere sau eliminate din date.

## 7. Surse și utilizarea AI

**7.1. Surse.**
- *P2 · Datele* (instrucțiuni, RN_P2_Instructiuni.pdf), cadrele didactice ale disciplinei Rețele neuronale, UNSTPB FIIR, 2026: https://curs.upb.ro/2026/mod/resource/view.php?id=46386
- Fișa mea P1 (`docs/RN_P1_Dorcea_Luca-Cristian.md`), din care am preluat decizia, reperul și planul de date.
- Bibliotecile folosite de programul de citire: OpenCV, NumPy, Pillow, pillow-heif și Matplotlib (lista este în `requirements.txt`).

**7.2. Utilizarea AI.** Am folosit Claude (Anthropic) pentru redactarea acestei fișe pe baza fișei P1, a răspunsurilor mele și a măsurătorilor mele cu rigla, pentru scrierea programului de citire `src/data/citire_pilot.py` și pentru analiza fotografiilor pilot (segmentarea pieselor, scara din caroiaj, compararea cu măsurătorile mele). Fotografiile și măsurătorile sunt făcute de mine; niciun exemplu nu este generat cu AI.
