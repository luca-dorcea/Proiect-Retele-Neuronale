# Rețele neuronale · Proiect · P1 – Propunerea de proiect

**UNSTPB · FIIR · Informatică industrială, anul III · 2026–2027**

> **Cum se completează fișa**
>
> - Redenumiți fișierul `RN_P1_Nume_Prenume.md` cu numele vostru, fără diacritice și fără spații (de exemplu `RN_P1_Popescu_Ion.md`).
> - Păstrați titlurile și numerotarea. Înlocuiți textele dintre paranteze drepte `[...]` cu răspunsuri proprii.
> - Scrieți concis, dar suficient de concret încât altă persoană să poată înțelege și verifica propunerea.
> - Pentru informațiile pe care nu le cunoașteți încă scrieți **„de verificat”** și treceți-le la secțiunea 7. Nu prezentați presupunerile drept fapte verificate.
> - La P1 se predă o **propunere argumentată**: nu se cer cod, model antrenat, date colectate sau rezultate.

---

## 0. Identificare

| Câmp | Răspuns |
|---|---|
| Nume și prenume | Dorcea Luca-Cristian |
| Grupa | 633AB |
| Versiunea fișei și data | 1 · 08.10.2026 |
| Titlul provizoriu al proiectului | Recunoașterea automată a tipului și dimensiunii șuruburilor, piulițelor și șaibelor din fotografii, pentru sortarea pieselor de asamblare |
| Username GitHub | luca-dorcea |
| Repository-ul proiectului | https://github.com/FIIR-RN2026/633ab-dorcea-luca-cristian |
| Invitația GitHub este acceptată | da |

## 1. Nevoia și utilizatorul

**1.1. Situația concretă.** În garajul meu am piese de asamblare (șuruburi, piulițe, șaibe) amestecate, pe care le sortez pe o masă. Astăzi le identific vizual, după ochi, ceea ce face sortarea plictisitoare și consumatoare de timp.

**1.2. Utilizatorul sau sistemul beneficiar.** Utilizatorul este persoana care sortează piesele de asamblare amestecate dintr-un atelier; în cazul acestui proiect, eu, în garajul propriu. Astăzi sortez piesele pe o masă, identificându-le vizual.

**1.3. Dovada nevoii.** Observație proprie: în garajul meu, sortarea pieselor amestecate se face vizual și durează mult. Atelierele au adesea cutii cu piese amestecate a căror sortare este plictisitoare și consumatoare de timp.

## 2. Decizia sprijinită și costul erorilor

**2.1. Decizia sau acțiunea.** Aplicația indică, pentru fiecare piesă din fotografie, tipul și dimensiunea (de exemplu „șurub M4×16”, „piuliță M5”, „șaibă M6”) și numărul de piese din fiecare clasă. Pe baza acestui rezultat, utilizatorul decide în ce compartiment pune fiecare piesă sau ce cantitate înregistrează în inventar. Decizia finală aparține utilizatorului; aplicația nu acționează singură.

**2.2. Costul erorilor.** Mai gravă este o dimensiune greșită (de exemplu, un șurub M4 clasificat ca M5): piesa ajunge în compartimentul greșit, iar greșeala se descoperă abia la montaj, când piesa nu se potrivește. O piesă nerecunoscută este mai puțin gravă, deoarece utilizatorul vede că nu are etichetă și o identifică singur.

**2.3. Beneficiul urmărit.** Sortarea și numărarea pieselor devin mai rapide și mai consecvente decât prin soluția actuală (secțiunea 4.1). Beneficiul se verifică pe același set de fotografii de test prin: (1) acuratețea pe fiecare clasă și matricea de confuzie, comparate cu reperul automat bazat pe reguli (secțiunea 4.3); (2) timpul necesar pentru a identifica piesele dintr-o fotografie, comparat cu timpul necesar prin soluția actuală.

## 3. Formularea problemei

| Element | Răspuns |
|---|---|
| Intrarea aplicației | O fotografie color, luată de sus, perpendicular pe masă, cu camera fixată pe un trepied la distanță constantă, pe un fundal mat, uniform, de culoare închisă. Piesele sunt așezate separat (se pot atinge, dar nu sunt suprapuse). Din fotografie, aplicația decupează automat câte o imagine pentru fiecare piesă și îi măsoară lungimea și lățimea în mm. |
| Ieșirea rețelei neuronale | Clasa fiecărei piese decupate (tip și dimensiune, de exemplu „șurub M4×16”), cu probabilitatea asociată. |
| Rezultatul pentru utilizator | Fotografia cu eticheta clasei afișată pe fiecare piesă și un tabel cu numărul de piese din fiecare clasă. |
| Tipul sarcinii | Clasificare de imagini: pentru fiecare piesă decupată, rețeaua alege o clasă dintr-o mulțime fixă de tipuri și dimensiuni. Găsirea pieselor în imagine se face prin prelucrare clasică (prag și contururi), deci rețeaua nu trebuie să rezolve și detecția. |
| Un exemplu | Exemplu ipotetic: o fotografie cu 5 șuruburi M4×16, 3 piulițe M5 și 7 șaibe M6. Rezultatul corect așteptat este o etichetă corectă pe fiecare dintre cele 15 piese și tabelul „șurub M4×16: 5, piuliță M5: 3, șaibă M6: 7”. |

**Formularea sintetică.** „Pentru persoana care sortează piesele de asamblare amestecate dintr-un atelier, aplicația primește o fotografie luată de sus, de la distanță fixă, cu piese de asamblare așezate separat pe un fundal uniform și produce tipul și dimensiunea fiecărei piese, plus numărul de piese din fiecare clasă, pentru a sprijini sortarea și inventarierea lor, în condițiile unui post fix de fotografiere (trepied, fundal și iluminare constante), cu piese nesuprapuse și o listă fixă de clase.”

## 4. Soluția actuală și reperul de comparație

Rețeaua neuronală se compară cu soluția folosită astăzi pentru aceeași nevoie, adusă într-o formă automată și comparabilă.

**4.1. Cum se rezolvă problema astăzi.** Eu sortez piesele manual, pe o masă, identificându-le vizual, după ochi. [Cât durează și ce greșeli apar.]

**4.2. Limita soluției actuale.** Ipoteză: regulile simple de formă și dimensiune funcționează când piesele sunt clar separate și au dimensiuni bine distanțate. Ele devin nesigure când piesele se ating, au reflexii puternice, sunt așezate pe o parte sau au dimensiuni apropiate (de exemplu M4 față de M5). O rețea neuronală convoluțională ar putea învăța din exemple trăsături de aspect (forma capului, filetul, reflexiile) care sunt greu de exprimat prin praguri fixe.

**4.3. Reperul automat.** Un program bazat pe reguli, care primește aceleași fotografii și folosește aceleași contururi ca rețeaua:
- un contur cu gaură interioară și margine exterioară rotundă este clasificat ca șaibă;
- un contur cu gaură interioară și margine exterioară hexagonală este clasificat ca piuliță;
- un contur alungit, fără gaură, este clasificat ca șurub;
- dimensiunea (de exemplu M4 sau M5, lungimea șurubului) se alege după lățimea și lungimea măsurate în mm, folosind factorul de scară obținut la calibrare, prin comparare cu valorile nominale.

## 5. Datele

Temele pot fi asemănătoare cu ale colegilor; **datele și dezvoltarea trebuie să fie proprii**. Un set public poate fi un punct de pornire, cu sursa declarată. Augmentarea și datele generate cu instrumente AI nu înlocuiesc datele proprii.

**5.1. Unitatea de date și răspunsul corect.** Un exemplu este imaginea decupată a unei singure piese, rotită astfel încât axa ei lungă să fie orizontală, împreună cu lungimea și lățimea măsurate în mm. Pentru datele de antrenare, eticheta se stabilește prin protocolul de fotografiere: într-o fotografie se pun doar piese din aceeași clasă, deci toate decupajele din acea fotografie primesc eticheta clasei respective. Pentru datele de test se fac fotografii cu piese amestecate, iar decupajele se etichetează manual. Clasa fiecărei piese se validează prin măsurare cu șublerul.

**5.2. Sursele de date.**

| Sursa | Accesul (link, dispozitiv disponibil sau „de verificat”) | Contribuția proprie (colectare, etichetare, măsurare, protocol) |
|---|---|---|
| Fotografii proprii ale pieselor, la postul fix cu trepied | Telefonul mobil (varianta cea mai probabilă), montat pe trepied; șubler pentru măsurarea de referință | Toată colectarea: protocolul de fotografiere, calibrarea scării (mm/pixel), fotografierea, etichetarea pe clase și verificarea prin măsurare |

**5.3. Planul de obținere.** Fotografiile se fac la un post fix: camera pe trepied, orientată perpendicular în jos, la distanță constantă, cu fundal mat uniform și o lampă în poziție fixă. Scara se calibrează o singură dată, fotografiind o riglă. Pentru antrenare se fotografiază câte o clasă pe rând (aproximativ 15–25 de piese pe fotografie), cu piesele rearanjate între fotografii, cu poziții și orientări variate și cu mici variații de iluminare. Pentru test se face o sesiune separată, cu fotografii cu piese amestecate.

Volumul inițial estimat, pentru aproximativ 6 clase:
- 300–500 de decupaje pe clasă pentru antrenare (în total 2.000–3.000), adică 100–150 de fotografii;
- 30–50 de fotografii de test (500–800 de piese);
- aproximativ 1,5–2 ore pentru fotografiile de antrenare și 1–2 ore pentru etichetarea manuală a setului de test.

Estimarea se bazează pe ordinele de mărime folosite uzual pentru antrenarea de la zero a unei rețele convoluționale mici; prima antrenare va arăta dacă sunt necesare mai multe date. Piesele disponibile: [tipurile, dimensiunile și numărul aproximativ de piese din fiecare clasă].

**5.4. Alternativa.** Dacă distingerea dimensiunilor apropiate nu se poate face sigur, scopul minim se păstrează prin restrângerea claselor la tipuri (șurub, piuliță, șaibă), cu dimensiunea estimată din măsurătoarea în mm. Dacă numărul de piese dintr-o clasă este prea mic, clasa respectivă se elimină sau se combină cu una apropiată.

## 6. Versiunea minimă și riscul principal

**6.1. Versiunea minimă demonstrabilă.** Pentru o fotografie luată la postul fix, cu piese așezate separat pe fundalul uniform, aplicația decupează automat fiecare piesă, o clasifică cu rețeaua convoluțională proprie într-una dintre aproximativ 6 clase și afișează eticheta pe fotografie, împreună cu numărul de piese din fiecare clasă. Rezultatele se compară cu reperul bazat pe reguli, pe același set de test. Rămân în afara proiectului: piesele suprapuse sau grămezile (care ar necesita detecție de obiecte, de exemplu YOLO), fotografiile făcute din mână sau din alt unghi, alte fundaluri și piesele din afara listei de clase.

**6.2. Riscul principal.** Riscul principal este distingerea dimensiunilor apropiate (de exemplu M4 față de M5), din cauza reflexiilor metalului și a erorilor de segmentare. Se verifică devreme: înainte de colectarea completă, se fac câteva fotografii de probă cu două clase apropiate și se compară diferența de lățime măsurată în mm cu diferența nominală dintre ele. Variantele de rezervă sunt ajustarea iluminării și a fundalului sau restrângerea claselor (secțiunea 5.4).

## 7. Ce nu este încă clar

| Întrebarea deschisă | Cum o verific | Până când |
|---|---|---|
| Este acceptată o rețea preantrenată de detecție (de exemplu YOLO) ca extensie, alături de rețeaua convoluțională proprie? | Discuție cu îndrumătorul în ședința P1 | Ședința P1 |
| Câte piese distincte sunt disponibile în fiecare clasă și ajung pentru a păstra câteva piese doar pentru test? | Inventarierea pieselor disponibile | Înainte de ședința P2 |

## 8. Feedback și revizuire

**8.1. Recomandările primite în ședința P1.** [Notați recomandările îndrumătorului. Dacă discuția nu a avut loc, menționați acest lucru.]

**8.2. Modificările față de versiunea anterioară.** Nu este cazul; aceasta este versiunea 1.

## 9. Surse și folosirea asistenților AI

**9.1. Surse consultate.**
- *P1 · Propunerea de proiect* (instrucțiuni), cadrele didactice ale disciplinei Rețele neuronale, UNSTPB FIIR, 2026: structura și cerințele propunerii.
- *Repository-ul GitHub al proiectului RN: pași de urmat*, cadrele didactice ale disciplinei Rețele neuronale, UNSTPB FIIR, 2026: accesul la repository.

**9.2. Folosirea asistenților AI.** Am folosit Claude (Anthropic) pentru alegerea temei dintre mai multe variante propuse, pentru discutarea abordării tehnice (post fix cu trepied, decupare automată, rețea convoluțională proprie, reper bazat pe reguli) și pentru redactarea acestei fișe pe baza răspunsurilor mele. [Ce ați verificat sau modificat personal.]

---

## Verificare înainte de predare

- [ ] Nevoia, utilizatorul și decizia sprijinită sunt concrete.
- [ ] Am argumentat costul erorilor pentru problema mea.
- [ ] Intrarea, ieșirea rețelei și rezultatul pentru utilizator sunt precizate.
- [ ] Am descris soluția actuală și ideea reperului automat.
- [ ] Sursele de date și contribuția proprie sunt indicate; ce nu știu încă este marcat „de verificat”.
- [ ] Versiunea minimă și riscul principal sunt formulate.
- [ ] Am completat sursele și declarația privind folosirea AI.
- [ ] Fișierul este redenumit corect și este încărcat atât în Moodle, cât și în repository, în `docs/`.
