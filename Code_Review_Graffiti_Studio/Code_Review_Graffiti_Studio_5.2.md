# Unabhängige Code-Prüfung – Graffiti Studio 5.2 (native macOS-App)

Prüfdatum: 2026-10-04 · Prüfgegenstand: Übergabe „Graffiti Studio – kompletter eigener Code zur unabhängigen Prüfung“ (Export 2026-10-04T09:15:15+02:00)

## 1. Ergebnis in Kürze

Die App ist sauber gegliedert. Viele Grundfunktionen arbeiten korrekt: 10-%-Raster, neutrale Nullregler, Abbruch des KI-Kindprozesses, Fingerabdruck-Zuordnung der Rezepte, Sonderzeichen in Dateinamen, Maskendeckung bei 0/90/180/270° mit Perspektive. Die Prüfung hat aber **mehrere bestätigte Fehler** gefunden, die genau die bereits beanstandeten Fälle wieder auslösen.

1. **IMG_4363/4373 werden auf zwei Wegen wieder seitlich samt Tisch und Nachbarabzügen ausgegeben:**
   - **Weg 1:** Beim Ordnerexport gelten „Automatische Papierkanten“ und „Bekannte Einzelretuschen“ des gerade gewählten Fotos für alle Fotos (R1).
   - **Weg 2:** „Ecken & Maske“ ersetzt das Rezept durch Vollbild-Ecken, wenn der Editor vor Ende der ersten Analyse geöffnet wird (R2).
   - Beides ist ausgeführt reproduziert.
2. **Masken treffen die falsche Bildstelle oder gehen verloren:**
   - Maskenbild und Export sind unterschiedlich gedreht (R3).
   - Ein einzelner Klick im Ecken-Werkzeug löscht alle Masken (R4).
   - „Einstellungen laden…“ ersetzt den gesamten Fotozustand (R5).
   - Alle Einzelwerte und Masken leben nur im Arbeitsspeicher. Das Fenster schließt ohne Rückfrage (R6).
3. **Die Oberfläche kann dauerhaft gesperrt bleiben:** „Exportieren“ gefolgt von „Abbrechen“, während noch ein abgebrochener Vorschauprozess läuft, hinterlässt `exportRunning=true` für immer (R7).
4. **Ein einziger ungültiger Eintrag blockiert jeden Ordnerexport:** gekreuzte Ecken oder ein Rezept mit 15 % reichen. Das gilt auch, wenn der Eintrag aus einem früher geöffneten Ordner stammt. Die Fehlermeldung zeigt nur „Traceback (most recent call last)“ (R8).
5. **Falsche Bildbearbeitung:**
   - Unbekannte Wand- und Zugfotos werden automatisch als „Papierabzug“ zugeschnitten (R9).
   - Eingebettete Farbprofile (iPhone = Display P3) werden ignoriert und gehen je nach Regler verloren. Das ist eine plausible Mitursache für „Farben zu schwach“ (R10).
   - Der Weißabgleich ist mathematisch wirkungslos (R14).
   - Belichtung wirkt etwa doppelt so stark wie dokumentiert und entsättigt (R15).
   - Die Vorschau entspricht nicht dem Export (R16).
6. **Laufzeit und Umgebung:**
   - Ohne `python-tk@3.14` scheitert jede Vorschau und jeder Export, weil `photo_prepare.py` beim Laden `PIL.ImageTk` importiert (R11). Ausgeführt nachgewiesen.
7. **Prüfnachweise:**
   - Die mitgelieferten Prüfberichte können von den mitgelieferten Testprogrammen nicht erzeugt worden sein.
   - Der Test „bekannter Abzug gedreht und zugeschnitten“ würde einen Abzug mit Tisch als bestanden werten (R34).

**Zählung:** 123 Einzelbefunde aus 7 Prüfbereichen plus Vollständigkeitskritik. Nach Zusammenfassen gleicher Ursachen bleiben **53 eigenständige Befunde**:

| Schweregrad | Anzahl | davon bestätigt | davon Hypothese/plausibel |
|---|---:|---:|---:|
| hoch | 11 | 11 | 0 |
| mittel | 23 | 22 | 1 |
| niedrig | 19 | 15 | 4 |

Kein Befund ist als „kritisch“ eingestuft, weil jeder eine bestimmte Bedienfolge oder Umgebung braucht. R1, R2 und R11 kommen dieser Stufe aber nahe: Sie verletzen ausdrücklich formulierte Anforderungen bzw. legen die App ganz lahm.

## 2. Methode, Nachweisart und Grenzen

**Rekonstruktion:**
- Alle 28 Textdateien wurden aus der Übergabe byte-genau wiederhergestellt. Ihre SHA-256-Werte stimmen mit dem Dateiindex überein.
- Datenfluss, Bildkoordinaten, Prozessprotokoll und Dateiausgabe wurden zuerst rekonstruiert (siehe `repro/PRUEFKONTEXT.md`).

**Ablauf:**
- 7 unabhängige Prüfbereiche:
  - A Swift-Zustand/Nebenläufigkeit
  - B Masken/Geometrie/EXIF
  - C Export/Zuordnung pro Foto
  - D Bildverarbeitung
  - E Analyse-Heuristiken
  - F Prozess/Umgebung/Build
  - G Doku/Tests
- Je Bereich ein eigener **Gegenprüfer**, der jeden Befund zu widerlegen versuchte, mit eigener Reproduktion.
- Zum Schluss ein **Vollständigkeitskritiker** (Befunde K1–K6).

**Ausgeführt:**
- Python-Teil mit Python 3.12, NumPy 2.x, OpenCV 4.14 und Pillow 12.3 unter Linux.
- Synthetische Bilder; Stubs für `engine/orientation` (Vision-OCR) und `realesrgan-ncnn-vulkan`.
- `native_bridge.py` wurde als echter Unterprozess mit den JSON-Anfragen betrieben, die Swift erzeugt, einschließlich SIGTERM-Tests.
- Die wiederholbaren Skripte liegen unter `repro/`. Die Pfade darin zeigen auf die Prüfumgebung und müssen angepasst werden.

**Nur statisch geprüft:**
- Der gesamte Swift-Code. Ein Swift-Compiler und macOS waren nicht verfügbar.
- Die Befunde wurden gegen die reale Foundation-, SwiftUI- und AppKit-Semantik nachvollzogen. Bei A6 wurde zusätzlich ein zeilengetreues Thread-Modell ausgeführt.
- Swift-Befunde mit „bestätigt (statisch)“ folgen eindeutig aus dem Code. „Plausibel“ heißt: abhängig von Laufzeitdetails, die hier nicht prüfbar waren.

**Nicht verfügbar:**
- Die 23 Fotos, die Referenz-PNGs, die vendorten Bibliotheken, das echte Modell und die echte OCR-Engine.
- Aussagen über IMG_4363/4373 beruhen deshalb auf nachgebildeten Rezepten mit derselben Struktur (z. B. `rotate: 90`, Eckpunkte, `glare_strength 0.62`).

**Gespeicherte Erfolgsberichte** (`Pruefung.json`, `Backend_Pruefung.json`) wurden nicht als Beweis gewertet, siehe R34.

### Legende

- **Status:**
  - **B-A** = bestätigt, ausgeführt reproduziert
  - **B-S** = bestätigt, statisch eindeutig
  - **P** = plausibel / Hypothese
- **Quell-IDs** verweisen auf die Einzelbefunde in `repro/workflow_rohdaten.json`. Dort stehen auch die vollständigen Belege und Ausgaben.
- Zeilen beziehen sich auf die Originaldateien:
  - `GraffitiStudio.swift` = `Quellcode/GraffitiStudio.swift`
  - Python-Dateien = `Graffiti Studio.app/Contents/Resources/…`

---

## 3. Befunde – Schweregrad hoch

### R1 · Ordnerexport überträgt „Automatische Papierkanten“ und „Bekannte Einzelretuschen“ des gewählten Fotos auf alle Fotos
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung · **Quell-IDs:** A2, C1, E2, G1

**Ort:**
- `GraffitiStudio.swift:147-150` `exportLibrary`:
  - `base=knobs` stammt vom ausgewählten Foto.
  - `merged.geometry` wird nie aus `saved` übernommen.
  - `merged.references` wird nur auf `false` gesetzt, nie auf `true`.
- `:173` `closeMask` setzt `references=false`.

**Auslöser:**
- (a) Bei einem Wandfoto „Automatische Papierkanten“ ausschalten, das Foto ausgewählt lassen und „Ordner exportieren“ klicken.
- (b) Bei irgendeinem Foto „Ecken & Maske…“ und dann „Übernehmen“ klicken (das setzt `references=false`) und mit diesem Foto ausgewählt „Ordner exportieren“ klicken.

**Wirkung:**
- (a) Alle Fotos laufen mit `geometry='aus'`. IMG_4363/4373 verlieren Entzerrung, Zuschnitt und 90°-Drehung und kommen **seitlich samt Tisch und Nachbarabzügen** heraus. Reproduziert: Rezeptabzug 1800×2400 hochkant statt 2112×1440 quer.
- (b) Die bekannten Referenzkorrekturen (Gekritzel und H auf IMG_20190701_182034, Blitz WFTPXN…) fehlen im **gesamten** Ordnerexport.
- Umgekehrt geht ein bewusst für ein Einzelfoto gesetztes „aus“ verloren.
- Das widerspricht LIES_MICH („gespeicherte Einzelwerte und Masken bleiben ihrem jeweiligen Foto zugeordnet“).

**Korrektur:**
- Nur Regler, Profil, Modus, Skalierung und Exportart bilden die gemeinsame Basis.
- `geometry` und `references` sind fotospezifisch:
  - für besuchte Fotos `merged.geometry=saved.geometry; merged.references=saved.references`
  - für nicht besuchte Fotos `geometry="auto"`, `references=true`
```swift
var common=KnobState(); common.values=knobs.values; common.profile=knobs.profile
common.mode=knobs.mode; common.scale=knobs.scale; common.export=knobs.export
for (path,saved) in perPhoto where paths.contains(path) { var m=common; m.values.merge(saved.values){_,n in n}
  m.geometry=saved.geometry; m.references=saved.references; m.corners=saved.corners; m.rotation=saved.rotation
  m.regions=saved.regions; m.strokes=saved.strokes; … specific[path]=m.json }
```

**Regressionstest:** Den Request von `exportLibrary` für (Rezeptfoto, Referenzfoto) erzeugen, mit ausgewähltem Foto `geometry='aus'` bzw. `references=false`. Erwartet: Das Rezeptfoto kommt quer und zugeschnitten heraus, die Referenz ist angewendet. Vorlage: `repro/A/r5_batch_base_leak.py`.

### R2 · „Ecken & Maske“ + „Übernehmen“ ohne Änderung verwirft Rezept, OCR-Drehung, Randbeschnitt und Referenzkorrektur – ohne Weg zurück
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung · **Quell-IDs:** A3, B2, B3, E13, K2, D9(a)

**Ort:**
- `GraffitiStudio.swift:171` `openMask`:
  - ruft `cancel()` auf
  - liest nur `plans[sel]["preparation"]`
  - setzt sonst Vollbild-Ecken; `rotation` bleibt `nil`
- `:173` `closeMask` setzt `references=false` ohne Bedingung.
- `adjustments.py:94-102` `prepare_plan`: Sobald `corners` oder `rotation` gesetzt sind, werden `cached_correction`, `rotation` (OCR) und `border_crop` entfernt.

**Auslöser:**
- (1) App starten (IMG_4363 ist vorgewählt) und noch während „Vorschau wird berechnet…“ den Editor öffnen. „Übernehmen“ wird freigegeben, sobald das `cancelled` der abgebrochenen Vorschau eintrifft.
- (2) Foto mit OCR-Drehung oder schwarzen Balken, oder Referenzfoto: Editor öffnen und sofort „Übernehmen“.
- (3) Variante ohne Editor: Ausgabe → Drehung „0°“ wählen.

**Wirkung:**
- (1) `openMask` bricht die eigene Erstanalyse ab, `plans` bleibt leer, Vollbild-Ecken ersetzen die Rezeptecken. Der **Abzug wird mit Tisch und Nachbarabzug ausgegeben**. Reproduziert: Tischanteil 0 % → 40 %.
- (2) Balken kehren zurück (1440×324 → 1440×420), die OCR-Drehung entfällt (1200×800 → 667×1000), statt der Referenz kommt das unretuschierte Original.
- Danach wirken weder „Bekannte Einzelretuschen = an“ noch „Automatische Papierkanten = aus“, weil `corners` gesetzt bleibt (K2).
- Es gibt keinen Bedienweg, `corners` wieder auf `nil` zu setzen. „Alle Regler auf Auto“ setzt nur `values` zurück.
- Zusätzlich schaltet jede manuelle Geometrie bei explizit gesetztem Reflexregler eine **globale** Schleierminderung auf Wandfotos ein (D9: Mittelwert 174 → 155, ohne Warnung).

**Korrektur:**
- Editor und Menüpunkt deaktivieren, bis `plans[selected]` vorliegt; die Analyse nicht per `cancel()` abbrechen.
- Die automatische Geometrie in einem Editor-Zustand halten und `knobs.corners` nur setzen, wenn der Nutzer Ecken tatsächlich verschoben hat.
- `closeMask` fasst `references` nicht an.
- Schaltfläche „Zuschnitt auf Automatik“ (`corners=nil, rotation=nil`, Masken leeren).
- In `prepare_plan`:
  - eine reine Drehung auf die Automatik aufsetzen, statt sie zu ersetzen
  - `cached_correction` nur verwerfen, wenn Ecken oder Masken wirklich vom Automatikwert abweichen
  - globale Schleierminderung nur bei Rezept, sicherer Papiererkennung oder echten Nutzer-Ecken

**Regressionstest:** Für drei synthetische Fälle (Balken, OCR-Stub-Drehung, `cached_correction`) muss `render_one` mit den Knobs nach „Editor öffnen + Übernehmen“ pixelgleich zur Automatik sein. Swift-Unit-Test: `openMask(); closeMask()` ändert `knobs` nicht. Vorlagen: `repro/B/t2_uebernehmen_ohne_aenderung.py`, `repro/B/t9_maskenrahmen.py`, `repro/K/k2_geometry_toggle.py`.

### R3 · Maskenbild und Export verwenden bei `rotation=nil` verschiedene Drehungen – Retusche und Reflexminderung treffen eine falsche Stelle
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung · **Quell-IDs:** A4, B4

**Ort:**
- `native_bridge.py:36`: `prepare` mit `rotate=settings.rotation or 0`, ohne Blick auf den Plan.
- `adjustments.py:97-101`: Beim Rendern bleibt das `rotate` des Rezepts (90) erhalten.
- `GraffitiStudio.swift:309`: Der Picker zeigt `nil` als „0°“.
- `:216`/`:172`: „Automatisch“ setzt `rotation=nil`, die Ecken bleiben.

**Auslöser:**
- IMG_4363 (Rezept `rotate: 90`): Editor wie in R2 (1) öffnen.
- Oder nach einer Bearbeitung „Ausgabe → Drehung: Automatisch“ wählen und den Editor erneut öffnen.
- Dann mit „Retuschpinsel“ oder „Reflexbereich“ eine Stelle markieren und „Übernehmen“ klicken.

**Wirkung:**
- Der Nutzer malt auf dem ungedrehten Bild, der Export dreht um 90°. Die normierten Masken landen auf anderem Inhalt.
- Das Inpainting zerstört dort möglicherweise **Originalbuchstaben oder Outlines**, der übermalte Fleck bleibt stehen. Reproduziert: Strich wirkt bei (0,14/0,09) statt (0,09/0,86).
- Eine erneute Auswahl von „0°“ löst keinen Setter aus, der Fehler ist im Editor also nicht behebbar.
- Zusätzlich erben neue Ecken alte `glare_regions`/`retouch_strokes` eines gespeicherten Rezepts.

**Korrektur:**
- `openMask` setzt `rotation` immer explizit (`preparation.rotate ?? plan.rotation ?? 0`).
- „Automatisch“ ist bei gesetzten Ecken gesperrt oder setzt Ecken und Masken mit zurück.
- `prepare` und `prepare_plan` lösen die Geometrie über **eine** gemeinsame Funktion auf.
- Im manuellen Zweig keine Rezeptmasken erben.

**Regressionstest:** Für ein Rezeptfoto mit `corners` gesetzt und `rotation=None` müssen `prepare` und `preview` dieselbe Orientierung liefern. Ein Strich bei (x,y) im Maskenbild muss im Export an der transformierten Stelle wirken. Vorlage: `repro/A/r3_mask_before_analysis.py` (Teil b).

### R4 · Ecken-Werkzeug: Jeder Klick verschiebt die nächste Ecke und löscht alle Masken
**Status:** B-S · **Kategorie:** Datenverlust · **Quell-IDs:** A16, B1

**Ort:** `GraffitiStudio.swift:330-339`.
- `DragGesture(minimumDistance:0)` wählt in `:334` die nächste Ecke ohne Trefferradius und setzt sie in `:335` auf den Klickpunkt.
- `:339` leert `regions`/`strokes` bei **jedem** `onEnded` im Ecken-Modus.
- Im Ecken-Modus werden Masken nicht gezeichnet (`:321`), der Verlust ist unsichtbar. Der Editor startet immer in „Vier Ecken“ (`:171`).

**Auslöser:** Masken zeichnen, Editor später erneut öffnen oder auf „Vier Ecken“ wechseln, einmal ins Bild oder auf den grauen Rand klicken, „Übernehmen“.

**Wirkung:**
- Ecke springt, der Ausschnitt verschiebt sich und kann konkav werden (dann R8).
- **Alle Reflexrechtecke und Retuschstriche sind endgültig weg.** Ein gezieltes Rückgängig gibt es nicht; „Abbrechen“ verwirft alles.

**Korrektur:**
- Ziehen nur starten, wenn `startLocation` höchstens etwa 20 pt vom Bildschirmpunkt `position(c[i],rect)` einer Ecke entfernt ist.
- Ecken zu Beginn merken und Masken nur löschen, wenn sich die Ecken tatsächlich geändert haben (mit Rückgängig-Schritt).

**Regressionstest:** UI-Test: Strich malen → „Vier Ecken“ → Klick ohne Ziehen fern von Ecken → „Übernehmen“. Erwartet: Ecken und Striche unverändert.

### R5 · „Einstellungen laden…“ ersetzt den ganzen Fotozustand und verwirft passende Geometrie, solange die Analyse läuft
**Status:** B-S · **Kategorie:** Datenverlust · **Quell-IDs:** B5, C10

**Ort:** `GraffitiStudio.swift:161-170`. Ein vollständig neuer `KnobState` (`:165`) ersetzt in `:167` alle Knobs. Der Hashvergleich in `:166` läuft gegen `plans[selected]`, das während der ersten Vorschau `nil` ist.

**Auslöser:**
- (a) Foto mit Ecken und Masken, dann mitgeliefertes `Rezepte/Nacht.json` laden. `Automatik.json` (`{}`) löscht sogar alle Reglerwerte.
- (b) Ein eigenes Rezept genau dieses Fotos laden, bevor die Vorschau fertig ist.

**Wirkung:**
- (a) Ecken, Drehung und Masken sind ohne Warnung weg; `geometry`, `references` und `export` stehen auf Standard.
- (b) „Rezept für ein anderes Original: nur Farbwerte übernommen.“ erscheint, obwohl es dasselbe Original ist, und auch dabei werden die bisherigen Masken gelöscht.

**Korrektur:**
- Selektiv zusammenführen: nur Schlüssel übernehmen, die das Rezept enthält.
- Geometrie nur nach erfolgreichem Hashvergleich übernehmen. Läuft die Analyse noch, zurückstellen („wird nach der Analyse geprüft“) oder den Hash per eigenem Python-Befehl ermitteln.
- Werte beim Laden auf 10er-Raster und Bereich prüfen.

**Regressionstest:** Swift-Unit-Test: `knobs` mit Ecken und Strichen, dann `Nacht.json` laden. Erwartet: Ecken und Striche erhalten, `values` und `profile` aus dem Rezept.

### R6 · Einzelwerte, Ecken und Masken nur im Speicher; Fenster schließen beendet ohne Rückfrage und bricht laufende Exporte ab
**Status:** B-A · **Kategorie:** Datenverlust · **Quell-IDs:** A1, G5, F6

**Ort:**
- `GraffitiStudio.swift:49`: `perPhoto` ist nur ein Dictionary.
- `:356-360` `StudioDelegate`: `applicationShouldTerminateAfterLastWindowClosed` liefert `true`, ein `applicationShouldTerminate` gibt es nicht.
- `studio_backend.py:86/103`: Ein Abbruch kommt vor Protokoll und ZIP.

**Auslöser:** Mehrere Fotos bearbeiten und das Fenster schließen oder Cmd+Q drücken. Ein erzwungener Neustart nach R7 hat dieselbe Wirkung. Variante: während „Ordner exportieren“ schließen.

**Wirkung:**
- Alle Einzelwerte, Ecken, Drehungen und Masken aller Fotos gehen ohne Warnung verloren.
- Ein laufender Ordnerexport wird per SIGTERM abgebrochen. Übrig bleibt ein Ordner mit den bis dahin fertigen Bildern (beim ersten Foto nur `Einstellungen.json`), aber ohne `Protokoll.csv`, Prüfbericht und ZIP.
- Chat_Korrekturen verspricht: „Neue individuelle Masken werden erst nach deiner Prüfung zu wiederverwendbaren Fotorezepten“. Die native App speichert sie nirgends.
- Der Temp-Ordner `GraffitiStudio-<UUID>` wird nie gelöscht.

**Korrektur:**
- `perPhoto` laufend sichern, z. B. in `~/Library/Application Support/Graffiti Studio/Sitzung.json`, geschlüsselt nach `image_sha256` und Pfad, und beim Öffnen wiederherstellen.
- `applicationShouldTerminate` mit Rückfrage bei laufendem Export oder ungesicherten Masken.
- Temp-Ordner beim Beenden löschen.

**Regressionstest:**
- XCUITest: Ecke verschieben, App beenden, neu starten → Ecke ist vorhanden.
- Export starten, Fenster schließen → Bestätigungsdialog erscheint.

### R7 · „Abbrechen“ eines noch wartenden Exports sperrt die Oberfläche dauerhaft
**Status:** B-A (Python-Latenz) + B-S/Modell (Swift) · **Kategorie:** Blockierte Oberfläche · **Quell-IDs:** A6, F2

**Ort:**
- `GraffitiStudio.swift:52`: Die DispatchQueue `worker` ist seriell. Jeder Block liest stdout bis EOF.
- `:106` `guard try next.start() else{return}` endet **ohne Ereignis**.
- `:142` `cancel`, `:284-289` `BridgeJob`.
- `native_bridge.py:9`: SIGTERM setzt nur ein Event.
- `analysis.py:41`: OCR läuft als nicht unterbrechbares `subprocess.run(timeout=45)`.

**Auslöser:** Regler bewegen (die Vorschau läuft Sekunden, mit OCR bis 45 s), sofort „Foto exportieren“ oder „Ordner exportieren“, dann „Abbrechen“, solange der abgebrochene Vorschauprozess noch rechnet.

**Wirkung:**
- Der Export-Block wartet hinter dem alten Prozess. Dann liefert `start()` `false` und der Block endet ohne `receive`. Das `cancelled` des alten Prozesses wird wegen des Tokens verworfen.
- `busy` und `exportRunning` bleiben **für immer** `true`. Dadurch sind Inspector, Liste, Filmstreifen, Exportknöpfe, Ordner/Dateien öffnen, Editor und Vorschau gesperrt; „Abbrechen“ wirkt nicht. Nur ein Neustart hilft, und der verwirft nach R6 alle Einstellungen.
- Gemessen: Ein abgebrochener Vorschauprozess mit 8-s-OCR-Stub lebt nach SIGTERM noch 7,2 s.
- Swift-Thread-Modell: nach 12 s weiterhin `{'busy': True, 'exportRunning': True, 'status': 'Wird abgebrochen…'}`.

**Korrektur:**
- (1) Bei `start()==false` trotzdem `receive(["type":"cancelled"],token:currentToken,…)` auf dem Main-Thread senden. Das allein beseitigt die Dauersperre.
- (2) Keine gemeinsame serielle Queue; pro Job `readabilityHandler` und `terminationHandler`.
- (3) Abbruch nach 2–3 s auf SIGKILL an die Prozessgruppe eskalieren (siehe R41).

**Regressionstest:** XCTest mit einer Fake-Bridge, die SIGTERM 5 s ignoriert: `run("preview")`; nach 0,5 s `run("export")`; nach 0,1 s `cancel()`. Erwartet: nach höchstens 6 s `busy==false` und `exportRunning==false`. Vorlagen: `repro/A/r1b_swift_model.py`, `repro/A-verify/v4_swift_queue_model.py`.

### R8 · Ungültige Ecken oder Werte: kein JSON-Fehler, Ursache unsichtbar – und ein ungültiger `per_photo`-Eintrag blockiert jeden Ordnerexport
**Status:** B-A · **Kategorie:** Export / Prozessfehler · **Quell-IDs:** A7, B9, C3, F4

**Ort:**
- `native_bridge.py:20`: `Settings.from_dict` steht **vor** dem `try`.
- `native_bridge.py:41`: **Alle** `per_photo`-Einträge werden vorab validiert.
- `GraffitiStudio.swift:330-341`: keine Konvexitätsprüfung beim Ziehen.
- `:57-74` `loadLocal`: `perPhoto` wird nie bereinigt.
- `:149`: Es werden alle `perPhoto`-Einträge gesendet.
- `:165`: Rezeptwerte werden ungeprüft übernommen.
- `:117`/`:264`: `stderr.suffix(2000)` mit `lineLimit(2)`.

**Auslöser:** Im Editor zwei Ecken über Kreuz ziehen (oder per R4 eine Ecke versehentlich springen lassen) und „Übernehmen“, oder ein Rezept mit `contrast: 15` laden. Später einen **anderen** Ordner öffnen und „Ordner exportieren“ klicken.

**Wirkung:**
- Vorschau und Export dieses Fotos: Exit 1, kein JSON-Ereignis. Die App zeigt nur „Traceback (most recent call last): / File …native_bridge.py, line 58“; die eigentliche Meldung steht in der abgeschnittenen letzten Zeile.
- „Ordner exportieren“ scheitert vollständig („Die vier Ecken müssen ohne Kreuzung angeordnet sein“): kein Bild, kein Ordner, kein Fotoname. Das gilt **auch, wenn das Foto zu einem früher geöffneten Ordner gehört**. Bis zum Neustart ist kein Ordnerexport möglich.

**Korrektur:**
- Python:
  - Anfrage lesen, `Settings.from_dict` und Importe in das `try` verschieben.
  - Fehlertext `f'{type(e).__name__}: {e}'`.
  - `per_photo` erst in `batch()` je Foto validieren und als FEHLER-Zeile mit Dateiname protokollieren.
- Swift:
  - Konvexität live prüfen und „Übernehmen“ sperren.
  - `specific` auf die aktuell geladenen Pfade filtern.
  - Rezeptwerte validieren.
  - Ohne Endereignis die **letzte** stderr-Zeile plus Exitstatus anzeigen.

**Regressionstest:**
- `native_bridge batch` mit einer gültigen Datei und einem ungültigen fremden `per_photo`-Eintrag: Erwartet wird `result` mit einem Bild.
- `preview` mit gekreuzten Ecken: Erwartet wird ein `error`-Ereignis mit Klartext.
- Vorlagen: `repro/C-verify/`, `repro/F-verify/v4_errors.py`.

### R9 · Unbekannte Wand- und Zugfotos werden automatisch als „Papierabzug“ zugeschnitten, entzerrt und entschleiert
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung · **Quell-IDs:** E1, G7, EX1

**Ort:**
- `analysis.py:104-113`: Bei `paper_confidence>=.86` wird `plan['preparation']` gesetzt, `glare_strength=.15`. Eine Warnung gibt es nur im OCR-Zweig bei unsicherer OCR.
- `analysis.py:73-86`: `paper_confidence` (Kriterium gleichmäßige/warme Umgebung).
- `analysis.py:169-170`: Protokolliert wird „Fotorezept ausgeführt.“
- `GraffitiStudio.swift:132`: Das Foto wird als „Abzüge“ einsortiert.

**Auslöser:** Wand- oder Zugfoto mit einem großen, kontrastreich umrandeten Rechteck (Piece mit Outline, Paneel, Hintergrundfläche), das 55–96 % der Fläche bedeckt, vor gleichmäßigem (Beton, Himmel, Nacht) oder warmem (Backstein, Natriumlicht) Umfeld. Dazu: sichere OCR bei 0°, oder Stapellauf, nachdem die OCR einmal ausfiel (R31).

**Wirkung:**
- Wandkontext wird ohne Rückfrage weggeschnitten (im Test 33 % der Bildfläche), Perspektive entzerrt, globale Schleierminderung 0,17 angewendet.
- Bei sicherer OCR bzw. im Stapel gibt es **keine Warnung**; Status OK/„Bereit“.
- Verletzt „Keine ungeprüfte automatische Beschneidung unbekannter Züge“ (Chat_Korrekturen.md) und „Reflexschleier nur bei bestätigtem Abzug/Rezept mindern“ (`flash.py:34`).

**Korrektur:**
- Automatisch erkannte Kanten nur als `candidate_preparation` mit Warnung ablegen. Ausführen nur bei Rezept mit passendem `image_sha256` oder nach Bestätigung im Editor.
- Warnung unabhängig von der OCR.
- In `apply_plan` zwischen „gespeichertes Rezept“ und „automatischer Vorschlag“ unterscheiden.

**Regressionstest:** Synthetische Betonwand mit umrandetem Piece. Erwartet: `analyze()` liefert kein `preparation`, der Export hat die Originalmaße, und es gibt eine Warnung „Möglicher Papierabzug“. Vorlage: `repro/E/`, `repro/E-verify/v_ocr.py`.

### R10 · Farbmanagement: Eingebettete ICC-Profile (Display P3) werden ignoriert und gehen je nach Codepfad verloren
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung · **Quell-IDs:** D1, E7, B12 (Teil)

**Ort:**
- `graffiti.py:43-44` `read_image`: keine Profilumrechnung.
- `graffiti.py:125`: `result.save(…,format='PNG')` ohne `icc_profile=`.
- Verlustpfade: `adjustments.py:129` (Kontrast über `Image.blend` mit neuem Bild ohne `info`), `:120` (Wärme/Tönung, `fromarray`), `photo_prepare.py:43/62` (jede Geometrie inkl. Drehung 0° und Vollbild-Ecken), `analysis.py:176`.
- Swift zeigt das Original farbverwaltet an (`GraffitiStudio.swift:76`, `:290-292`), das Ergebnis-PNG ohne Profil gilt als sRGB.

**Auslöser:** iPhone-Foto (Display P3), Startprofil „Automatisch“ (ergibt „kräftig“ mit Kontrast 10), jeder Abzug bzw. jedes Rezept, Wärme/Tönung ≠ 0. Ansicht „Vergleich“ oder Export.

**Wirkung:**
- P3-Zahlen werden als sRGB angezeigt, kräftige Farben verlieren Chroma (Rot ΔE76 ≈ 19, Chroma 98 → 81).
- Der Vergleich in der App zeigt das Original korrekt, das Ergebnis aber blasser. Das ist eine **plausible Mitursache der Beschwerde „Farben zu schwach“**.
- Ob das Profil erhalten bleibt, hängt zufällig vom Pfad ab: „Originalnah“ und „Nacht“ behalten P3, „Kräftig/Automatik“ verliert es. Die kräftige Einstellung erscheint dadurch blasser als die originalnahe.

**Korrektur:**
- Entweder (A) das Profil in `read_image` merken und an **allen** Ausgaben explizit setzen (PNG, Vergleich.jpg, Instagram, Panorama),
- oder (B) beim Lesen per `ImageCms.profileToProfile(…, RELATIVE_COLORIMETRIC)` nach sRGB umrechnen und alle Ausgaben als sRGB markieren. B ist für Instagram robuster, clippt aber P3-Farben außerhalb von sRGB.
- Das Profil nie implizit über `Image.info` weiterreichen.

**Regressionstest:** JPEG mit eingebettetem Nicht-sRGB-Profil durch alle Profile, Rezept- und Reglerpfade schicken. Erwartet: Jede Ausgabe trägt ein Profil, und die farbverwalteten Lab-Werte weichen bei neutralen Reglern um ΔE < 2 ab.

### R11 · tkinter ist Pflicht: Ohne `python-tk@3.14` scheitern alle Vorschauen, Masken und Exporte
**Status:** B-A · **Kategorie:** Portabilität / Prozessfehler · **Quell-IDs:** F1, G12

**Ort:** `photo_prepare.py:6` `from PIL import Image,ImageTk`. `PIL.ImageTk` importiert tkinter beim Laden. Importkette: `graffiti.py` → `analysis.py` → `photo_prepare.py`. Gebraucht wird ImageTk nur im Alt-Dialog `review()` (`:74-130`).

**Auslöser:** `brew install python@3.14` ohne die separate Formel `python-tk@3.14` (Homebrew-Standard).

**Wirkung:**
- Jede Vorschau, jede Maskenvorbereitung und jeder Export endet mit „No module named '_tkinter'“; die App erzeugt kein einziges Bild.
- Nirgends dokumentiert. Die Übergabe nennt die Tk-Pfade sogar „optional“.
- Ausgeführt: ohne tk `rc=1`, Ereignis `error`; mit tk `result`.

**Korrektur:** In `photo_prepare.py:6` nur `from PIL import Image` importieren und `from PIL import ImageTk` in `review()` verschieben. Besser: die Tk- und AppleScript-Altpfade aus dem Bundle entfernen. Laufzeitvoraussetzungen in LIES_MICH vollständig nennen.

**Regressionstest:** `native_bridge preview/prepare/export` mit einem Python-Shim, der `_tkinter` unimportierbar macht. Erwartet: `result`. Vorlage: `repro/F-verify/v1_tk.py`.

---

## 4. Befunde – Schweregrad mittel

### R12 · Veraltete Vorschauantwort wird nach einem Fotowechsel dem neuen Foto zugeschrieben
**Status:** B-S · **Quell-IDs:** A5, C11

**Ort:**
- `GraffitiStudio.swift:75` `selectionChanged`: kein `job?.cancel()`, kein neuer Token.
- `:89` Debounce 0,32 s.
- `:122-133` `receive` schreibt unter dem **aktuellen** `selected`.

**Auslöser:** Beim Start oder nach Reglerbewegung schnell durch die Liste wechseln (Pfeiltasten, schneller als 0,32 s je Schritt). Dann beim gewählten Foto X vor dessen Vorschau den Editor öffnen oder „Einstellungen speichern“.

**Wirkung:**
- Ergebnisbild, Plan (`preparation`, `image_sha256`), Status, Typ „Abzüge“, `resolved` und Warnung von Foto A erscheinen unter X.
- `openMask` übernimmt A's Rezeptecken und 90°-Drehung für X.
- `saveRecipe` speichert X's Masken mit A's Fingerabdruck.
- Dauerhaft, wenn X's Vorschau abgebrochen wird oder scheitert.

**Korrektur:**
- In `selectionChanged`: `task?.cancel(); job?.cancel(); token=UUID()`.
- Quellpfad mit dem Job führen. `receive` speichert unter diesem Pfad und zeigt nur an, wenn er `selected` entspricht.

**Regressionstest:** Swift-Unit-Test mit Fake-Bridge: Ein Ergebnis für A trifft nach dem Wechsel zu X ein. Erwartet: `plans[X]` bleibt `nil` und `result` bleibt `nil`.

### R13 · 16-Bit-Graustufen werden weiß, Float schwarz, Transparenz meist schwarz, CMYK naiv umgerechnet – ohne Warnung als „OK“
**Status:** B-A · **Quell-IDs:** D2, E6, B12

**Ort:** `graffiti.py:43-44` `read_image`: nur `convert('RGB')`.

**Auslöser:** 16-Bit-Graustufen-Scan (PNG/TIFF `I;16`), Float-TIFF, freigestelltes PNG, CMYK-JPEG.

**Wirkung:**
- `I;16` wird auf 255 geklemmt: Das Ergebnis ist eine reine weiße Fläche (Mittel 254,4), ohne Warnung.
- Float wird schwarz; Transparenz nimmt die verborgene RGB-Farbe an (häufig Schwarz); CMYK ergibt Farbabweichungen.
- 48-Bit-RGB wird dagegen korrekt reduziert.

**Korrektur:**
- `I;16*` durch 257 teilen (nach Bittiefe, nicht über `a.max()` erraten).
- Float skalieren.
- Alpha auf Weiß oder neutral komponieren und Warnung ausgeben.
- CMYK mit Profil über ImageCms umrechnen.

**Regressionstest:** Rampenbilder in jedem Modus. Erwartet: Mittelwert und Spaltenwerte bleiben innerhalb ±2 erhalten. Vorlage: `repro/D/t2_formats.py`.

### R14 · Automatischer Weißabgleich und Regler „Weißabgleich“ sind praktisch immer wirkungslos
**Status:** B-A · **Quell-IDs:** D6

**Ort:** `analysis.py:19-24` `scan_features`, `adjustments.py:84`, `adjustments.py:108`.

**Ursache (mathematisch):**
- Als neutral gelten nur Pixel mit HSV-S < 40. Für sie gilt max/min ≤ 1/(1−40/255) ≈ 1,183, also auch für die Kanalmittel.
- Die Schwelle `> 1.18` liegt nur im schmalen Band 1,18–1,183 und ist praktisch unerreichbar. Stärkere Farbstiche fallen ganz aus der Neutralmaske.

**Wirkung:**
- `cast_suspected` bleibt `False`, die Verstärkungen bleiben `[1,1,1]`.
- Der vom Nutzer geforderte Weißabgleich-Regler multipliziert mit 0. Ein toter Regler, im Test für R/B 1,08–1,67 nie ausgelöst.

**Korrektur:**
- Neutralkandidaten in Lab bestimmen (niedrige Chroma relativ zur Verteilung, 35 < L < 90) und daraus Gray-World- bzw. Graukarten-Schätzung.
- Verstärkungen immer berechnen und vom Regler skalieren lassen; `cast_suspected` nur für den Automatikvorschlag.
- Dämpfung (×0,45, Clip 0,93–1,08) vom Regler steuern lassen.

**Regressionstest:** Graue Wand unter Natriumlicht (R/B 1,4). Bei Regler 100 % muss der Abstand zu Neutralgrau um mindestens 50 % sinken. Vorlage: `repro/D/t7b_wb_sweep.py`.

### R15 · Belichtung und Schatten wirken auf gamma-kodierte Luma bei fester Chroma: etwa doppelt so stark wie dokumentiert, mit Ausbrennen und Entsättigung
**Status:** B-A · **Quell-IDs:** D7

**Ort:** `adjustments.py:123-131` `render` (LUT `x*2**(e/50)` auf Y, Cb/Cr bleiben); die Dokumentation in `:10` verspricht ±2 Blendenstufen.

**Wirkung:**
- +50 % ergibt etwa +2,2 EV statt +1 EV: Ab Eingang 128 ist alles reinweiß, 18-%-Grau geht von 118 auf 236 statt 162. Weiße Farbe brennt aus.
- Dunkelrot (100,20,20) bei +100 wird (228,148,147), die Sättigung fällt von 0,80 auf 0,36.
- Gelb bei −100 kippt im Farbton von 52° auf 42°.
- Nachtprofil (Schatten 70) entsättigt dunkle Farben.

**Korrektur:**
- Belichtung in linearem Licht auf RGB anwenden (sRGB → linear × 2^(2e/100) → sRGB, optional weiche Schulter).
- Schatten und Lichter als Luminanzverhältnis auf alle Kanäle anwenden.

**Regressionstest:** Belichtung +50 auf 18-%-Grau ergibt sRGB ≈ 162 ± 3. Farbton- und Sättigungsänderung gesättigter Farben bei ±100 kleiner als 3° bzw. 0,1.

### R16 · Vorschau ≠ Export: feste Pixelradien nach dem Skalieren; „200 %“ vergrößert nur das Vorschaubild
**Status:** B-A · **Quell-IDs:** D4

**Ort:**
- `adjustments.py:115-117` (bilateral d=5, Median 3), `:137` (UnsharpMask r=0,8).
- `graffiti.py:82-85`/`:118-122` (`render` nach der Skalierung).
- `GraffitiStudio.swift:236/264`.

**Wirkung:**
- Gemessen (12 MP, Rauschen σ=9), Detailenergie in der Vorschau gegenüber dem Export:

  | Regler | Vorschau | Export 1× | Export 2× |
  |---|---:|---:|---:|
  | Rauschminderung | −35 % | −11 % | −2 % |
  | Artefaktglättung | −19 % | −2 % | −1 % |

- Schärfe wirkt je nach Rauschen schwächer oder stärker als in der Vorschau.
- Die Vorschau ist damit **keine kontrollierbare Vorschau** des Exports. „200 % Vorschau“ vergrößert nur das ≤1440 px große Vorschaubild und erlaubt kein Urteil über Schärfe und Rauschen.

**Korrektur:**
- Radien in Quellpixeln definieren und mit dem tatsächlichen Maßstab skalieren (`px_scale`).
- Oder Glättung immer in Quellauflösung vor der Skalierung rechnen.
- Für 200 % einen Ausschnitt in Exportauflösung rendern.

**Regressionstest:** Für jeden Regler muss die verkleinerte Exportausgabe von der Vorschau um weniger als 3 % Detailenergie bzw. weniger als 2 Tonwertstufen abweichen. Vorlage: `repro/D/`.

### R17 · Jede Reglerstufe kostet einen neuen Prozess mit Vollanalyse, OCR, Vollauflösungs-Transform, KI-Neustart und Bytecode-Übersetzung
**Status:** B-A · **Kategorie:** Leistung · **Quell-IDs:** A19, D5, D12, E9, G13, F9

**Ort:**
- `GraffitiStudio.swift:89-93`: neuer Prozess je Wert.
- `graffiti.py:50-51`: `read_image` und `analyze` jedes Mal.
- `analysis.py:11`: SHA über alle Pixel.
- `analysis.py:41`: OCR.
- `photo_prepare.py:41-71`: Transform in Vollauflösung.
- `graffiti.py:86`: `use_ai` ignoriert `preview_size`.
- `graffiti.py:12`: `SESSION` gilt nur pro Prozess.
- `GraffitiStudio.swift:98` `PYTHONDONTWRITEBYTECODE` und `zip_native.py:6` ohne `.pyc`.

**Wirkung:**
- Gemessen ohne echte OCR: 2–3,7 s (12 MP), 5,4 s (12 MP mit Masken), 28,7 s (48 MP mit Masken) je Reglerschritt. Auf dem Mac kommt jedes Mal die Vision-OCR hinzu.
- Im Automatikmodus startet jede Vorschau Real-ESRGAN neu, obwohl das Vorschaubild kleiner als die Quelle ist. Ein hängendes Modell blockiert bis zu 600 s je Schritt.
- „Einmaliger KI-Versuch, danach in diesem Lauf klassisch“ stimmt nur im Stapel.
- Etwa +0,22 s Importzeit je Prozess durch fehlenden Bytecode.

**Korrektur:**
- Analyseplan (inkl. OCR) einmal je Fingerabdruck berechnen und cachen.
- Vorschau nach der Analyse aus einer verkleinerten Arbeitskopie rechnen (Ecken und Masken sind normiert).
- Keine KI in der Vorschau, oder nur in einem Ausschnitt; KI-Ausfall prozessübergreifend merken (Flag in der Anfrage).
- `PYTHONPYCACHEPREFIX` nach `~/Library/Caches/…` statt `PYTHONDONTWRITEBYTECODE`.
- Langfristig ein langlebiger Worker-Prozess statt eines Prozesses je Vorschau.

**Regressionstest:** Zweite Vorschau desselben Fotos mit anderem Regler: unter 1 s bei 12 MP und ohne OCR- oder Modellaufruf (Zähler in Stubs).

### R18 · Abbruch wirkt nur an groben Checkpoints und eskaliert nicht (OCR bis 45 s, Rendern/Speichern ~20 s bei 60 MP, Panorama und ZIP gar nicht)
**Status:** B-A · **Kategorie:** Blockierte Oberfläche / Prozessfehler · **Quell-IDs:** E10, F3, G10, C6 (Teil), F12

**Ort:**
- `analysis.py:41` (zweimal aufgerufen: `:111`, `:120`): `subprocess.run(timeout=45)` ohne Abbruch.
- `graffiti.py:49-58` und `:118-128`: Checkpoints nur grob.
- `studio_backend.py:106-121` und `native_bridge.py:44-54`: Panorama, Instagram und ZIP ohne Abbruchprüfung.
- `native_bridge.py:9`: Der Handler setzt nur das Event.

**Wirkung:**
- Nach SIGTERM rechnet Python bis zum nächsten Checkpoint weiter. Gemessen:
  - 19,7 s bei einem OCR-Stub von 20 s
  - 44,8 s bei hängender OCR
  - 17–18 s Rendern bei 60 MP
  - 23 s Speichern einer PNG mit 60 MP
  - Panorama mit 23 Fotos: etwa 120 s ohne Abbruch; „Abbrechen“ endet trotzdem mit „Export fertig“
- In dieser Zeit blockiert der Prozess die serielle Swift-Queue (siehe R7).
- ZIP mit Deflate auf PNG/JPG: 2,5 s statt 0,13 s für 86 MiB, ohne Größenvorteil.

**Korrektur:**
- OCR wie `run_model` per `Popen` mit Abbruchschleife starten.
- `cancel` an `analyze`, `transform`, `stitch` und die ZIP-Schleife durchreichen.
- Swift: SIGTERM, nach 2–3 s SIGKILL an die Prozessgruppe.
- ZIP mit `ZIP_STORED` für Bilddateien.

**Regressionstest:** `native_bridge` mit OCR-Stub (20 s), SIGTERM nach 1 s. Erwartet: `cancelled` und Prozessende innerhalb von 1,5 s. Dasselbe in der Panorama- und ZIP-Phase. Vorlagen: `repro/F/`, `repro/E-verify/`.

### R19 · Reflexbereich-Werkzeug: Ohne Reglerwert wirkungslos, auf Abzügen schaltet es die automatische Minderung ab, und die Weichzeichnung ist zu breit
**Status:** B-A · **Quell-IDs:** A15, B6, G14, D8, D9(b)

**Ort:**
- `adjustments.py:86`: Auto-Glare kommt nur aus `preparation`.
- `adjustments.py:103-107`.
- `photo_prepare.py:53-61`: `mask[:]=0`, nur die Rechtecke werden 1; danach `GaussianBlur` mit σ = 2 % der Bildgröße in Vollauflösung.
- `GraffitiStudio.swift:307`: Der Hinweistext erwähnt den Regler nicht.

**Wirkung:**
- (1) Wand- oder Zugfoto, Rechteck gezogen, Regler „Auto (0 %)“: Änderung 0,00, keine Warnung.
- (2) Kleines Rechteck auf einem Abzug mit Automatik 70 %: Außerhalb wird die Minderung abgeschaltet (Mittel 83 → 125 = Original).
- (3) Ein Bereich von 3 % × 3 % erreicht nur 31 % der Sollwirkung und wirkt über 100 px über den Rand hinaus, wo möglicherweise nicht markierte weiße Farbe liegt. Bei 48 MP kostet das etwa 15 s.

**Korrektur:**
- Bereiche bekommen eine eigene Stärke (Standard z. B. 50 %), oder es erscheint ein Hinweis „Bereich markiert, Regler steht auf 0 %“.
- Auf Abzügen `np.maximum(global, region)` statt `mask[:]=0`, oder dokumentieren.
- Weiche Kante relativ zur Bereichsgröße und nach innen (Abstandstransformation), in Arbeitsauflösung.

**Regressionstest:** Rechteck 3 % auf einem 12-MP-Schleierbild. Erwartet: mindestens 90 % Sollwirkung im Bereich und weniger als 5 % Wirkung 2 % außerhalb.

### R20 · Generative Referenzkorrekturen: Ausgabe ungekennzeichnet, Verfahren „klassisch“, Warnungen veraltet oder falsch
**Status:** B-A · **Kategorie:** Falsche Bildbearbeitung (Kennzeichnung) · **Quell-IDs:** E3, G6, E4, B14, C9, C16 (Teil)

**Ort:**
- `analysis.py:116-118`: Der Hinweis ist fest codiert; `generative_reconstruction` wird ignoriert.
- `analysis.py:142-149`: Blitzwarnungen werden unterdrückt, sobald `cached_correction` im Plan steht.
- `graffiti.py:89-90/126`: `effective_backend='klassisch'`.
- `graffiti.py:125`: PNG ohne Metadaten.
- `adjustments.py:91/96`: entfernt `cached_correction`, ohne die Warnungen anzupassen.
- `studio_backend.py:101`: CSV-Spalte.

**Wirkung:**
- Die ausgegebenen PNGs, Instagram-Slides und Panorama-Basen tragen keinerlei Kennzeichnung (weder Name noch Text-Chunk).
- Statuszeile und CSV melden „Klassisch“ für ein generativ rekonstruiertes Bild; der Ordnerexport zeigt den KI-Hinweis nicht in der App.
- Wird die Referenz abgeschaltet (Schalter oder R2), bleibt der Hinweis „enthält KI-rekonstruierte Details“ stehen, die drei Warnungen zum tatsächlich vorhandenen Blitz fehlen.
- Damit wird der Requirement-Fall „nicht als dokumentarisch sichere Rekonstruktion ausgeben“ nicht verlässlich erfüllt.

**Korrektur:**
- Bei Referenz: `effective_backend='gespeicherte_KI_referenz'`, Dateinamen-Suffix `_KI-Referenz`, PNG-tEXt-Eintrag, Hinweisdatei im Instagram-Ordner, Hinweis immer an erster Stelle.
- Warnungen erst nach `prepare_plan` aus dem tatsächlich wirksamen Zustand erzeugen (`finalize_warnings`).

**Regressionstest:** Referenzfoto (Testeintrag) exportieren: Dateiname/tEXt markiert, `effective_backend` ≠ klassisch. Mit `use_saved_retouches=False`: kein KI-Hinweis, Blitzwarnungen vorhanden.

### R21 · `black_border()` schneidet dunkle Nachtbereiche ab, auch stark asymmetrisch
**Status:** B-A · **Quell-IDs:** E5

**Ort:** `analysis.py:51-60`. Geprüft wird nur `top>0 and bottom>0` und eine Summe unter 60 % bzw. 30 %. Symmetrie und Gleichmäßigkeit werden nicht geprüft, obwohl der Kommentar „Preserve asymmetric dark night edges“ das Gegenteil verspricht.

**Wirkung:** Eine Nachtaufnahme mit einer schwarzen Zeile oben und 550 unten wird von 1500×1000 auf 1500×449 beschnitten. Echter (dunkler) Bildinhalt geht ohne Warnung verloren.

**Korrektur:** Nur echtes Letterboxing entfernen: `|top−bottom| ≤ max(2, 1 %)`, Bandzeilen exakt konstant, harte Kante zum Inhalt, Anteil höchstens etwa 25 %. Sonst nur ein Vorschlag mit Warnung.

**Regressionstest:** 2 schwarze Zeilen oben und 500 unten (Werte 0..3) ergeben keinen Zuschnitt. Symmetrische 40/40-px-Balken werden entfernt.

### R22 · KI-Modus bei Fotos über 3,5 MP: Das Modell sieht nur ein verkleinertes Bild, das Ergebnis wird trotzdem zu 60 % beigemischt; unplausible Ausgaben gelten als Erfolg
**Status:** B-A (mit Stub-Modell) · **Quell-IDs:** D3, D14

**Ort:**
- `graffiti.py:94-97`: Eingabe auf 3,5 MP verkleinert.
- `:103`: Die Ausgabe wird auf die Zielgröße skaliert.
- `:105-108`: Beimischung.
- `:102`: Geprüft werden nur Exit-Code und Dateiexistenz.

**Wirkung:**
- Bei 12 MP sieht die KI nur 0,54× der Auflösung, ihre Ausgabe hat weniger echte Auflösung als die Basis. Detailenergie −72 %, an Schriftkanten bis 73 Tonwertstufen Abweichung.
- Ein echtes Real-ESRGAN erfindet die verlorenen Strichdetails. Das widerspricht „Keine generative Neuzeichnung“ und dem Schutz der Originalbuchstaben.
- Eine schwarze oder 1×1-Ausgabe des Modells (bekanntes ncnn-Vulkan-Fehlerbild) wird beigemischt: Das Bild wird stark dunkler (Mittel 123 → 62), gemeldet als „lokale_ki“.

**Korrektur:**
- KI nur einsetzen, wenn die effektive Auflösung die Zielgröße erreicht. Andernfalls kachelweise ohne Verkleinerung bzw. mit `-s 2`; dabei die Pillow-Pixelgrenze beachten (R45).
- Ausgabe prüfen (Größe = Eingabe×4, Standardabweichung > 1, mittlere Abweichung zur LANCZOS-Basis < Schwelle), sonst Fallback.

**Regressionstest:** Stub-Modell mit Schwarz-Ausgabe ergibt `backend=klassisch` und eine Warnung. Ein 12-MP-Bild im KI-Modus darf die Laplace-Varianz nicht unter die klassische Variante senken.

### R23 · „Ordner öffnen“ lädt frühere Ergebnisse als neue Fotos
**Status:** B-S · **Quell-IDs:** A11, C8, G11

**Ort:**
- `GraffitiStudio.swift:58`: Die Ausschlussliste enthält weder Instagram, Panorama noch Bildvorschlaege.
- `:62`: Nur die Präfixe `Ergebnisse_` und `Vorschau_` werden erkannt.
- `:60`: kein `.skipsPackageDescendants`.
- `:47`: Standardausgabe `~/Downloads/Graffiti_Studio_Ergebnisse`.
- Der Python-Filter `list_sources` wird von der App gar nicht benutzt; der Test prüft genau diesen.

**Auslöser:** Nach einem Export `~/Downloads` öffnen (so in `Pruefung.json` beschrieben) und „Ordner exportieren“ klicken.

**Wirkung:**
- `01_*.png`, `*_Vergleich.jpg`, Instagram-Slides und Panorama-Basen werden als Graffiti „restauriert“, dazu die Fotos im App-Paket.
- Jeder Lauf wird größer; Ergebnisse von Ergebnissen entstehen.

**Korrektur:**
- Eine gemeinsame Filterlogik (Swift ruft `native_bridge.py list` mit `out=Ausgabeordner` auf).
- Ausgabeordner, `Foto_*`/`Ordner_*` (bzw. eine Markerdatei), Instagram, Panorama, Bildvorschlaege und Pakete ausschließen.

**Regressionstest:** Testordner mit einem vorherigen Exportordner darin. Erwartet: nur die Originalfotos werden geladen.

### R24 · Ordnersuche, Thumbnails und Original werden synchron auf dem Main-Thread erzeugt; Filmstreifen zeigt still nur 30 Fotos
**Status:** B-S · **Kategorie:** Blockierte Oberfläche · **Quell-IDs:** A12

**Ort:** `GraffitiStudio.swift:60-66`, `:83`, `:76`, `:291` (`FromImageAlways` ignoriert eingebettete Vorschaubilder), `:276` `prefix(30)`.

**Wirkung:** Ordner mit Tausenden Fotos oder großen TIFF/PNG-Scans frieren die App ohne Fortschritt und Abbruch ein. Jeder Fotowechsel dekodiert synchron. Der Filmstreifen ignoriert Suche und Filter.

**Korrektur:** Enumeration und Thumbnails im Hintergrund mit Fortschritt; Thumbnails lazy und gecacht; `loadOriginal` asynchron mit Token; Filmstreifen auf `visiblePhotos` und lazy.

**Regressionstest:** UI-Test mit 5 000 Dummy-JPEGs: Hauptthread-Hänger unter 250 ms, Fortschritt sichtbar.

### R25 · Fehlermeldungen unlesbar: zwei Zeilen Traceback-Anfang, Protokoll gelöscht, endloser Spinner im Masken-Editor
**Status:** B-A · **Kategorie:** Fehler nicht sichtbar · **Quell-IDs:** A13, B8, F4

**Ort:**
- `GraffitiStudio.swift:117` (`errors.suffix(2000)`).
- `:104`: Die Logdatei wird gelöscht.
- `:264`: `lineLimit(2)`, nicht auswählbar.
- `:133`: nur `warnings.first`.
- `:141`: `fail` lässt das alte Ergebnis stehen.
- `:312/:328`: Der Editor zeigt bei Fehler weiter die ProgressView.
- `native_bridge.py:35-37` und `photo_prepare.py:40`: Die Mindestgröße wird auf dem 1800-px-Thumbnail geprüft.

**Wirkung:**
- Die Ursache bleibt unsichtbar (siehe R8).
- Schlägt `prepare` fehl (ungültige Ecken, „Ausschnitt zu klein.“), zeigt das Sheet endlos „Ausschnitt wird vorbereitet…“.
- Schmale, aber gültige Ausschnitte (2,5 % eines 4000-px-Fotos = 100 px, im Thumbnail 45 px) lassen sich nie maskieren, obwohl der Export sie verarbeitet.

**Korrektur:**
- Alle Fehler als JSON melden. Swift zeigt die letzte stderr-Zeile, den vollen Text in einem kopierbaren Alert, das Log unter `~/Library/Logs/Graffiti Studio`.
- `maskError` im Editor mit „Zu den Ecken“.
- Die Mindestgröße in Vollauflösung prüfen.
- Alle Warnungen als Liste zeigen.

**Regressionstest:** `prepare` mit schmalem Streifen (101×3000 voll) ergibt `result`. `prepare` mit gekreuzten Ecken ergibt ein `error`-Ereignis, das Sheet zeigt die Meldung.

### R26 · HEIC/HEIF/DNG und Symlink-Dateien werden beim Ordnerimport still übersprungen
**Status:** B-S · **Quell-IDs:** A14

**Ort:** `GraffitiStudio.swift:58` (Endungen), `:63` (`isRegularFileKey` ist für Symlinks `false`), `:73` (Meldung nur bei 0 Fotos).

**Wirkung:** iPhone-Standardfotos (HEIC) und verlinkte Dateien fehlen in Liste und Export, ohne Hinweis oder Zählung. Der Ordnerexport wirkt vollständig. Python würde Symlinks dagegen einbeziehen.

**Korrektur:**
- Übersprungene Bilddateien (`UTType.conforms(to:.image)`) zählen und melden.
- HEIC über ImageIO in temporäre PNG/TIFF wandeln. Nur „heic“ in die Endungsliste aufnehmen reicht nicht, weil Pillow ohne pillow-heif scheitert.
- Symlinks auflösen und dedupen.

**Regressionstest:** Ordner mit 2 JPG, 1 HEIC und 1 Symlink. Erwartet: 4 Fotos, oder 3 Fotos plus die Meldung „1 HEIC übersprungen“.

### R27 · `resolved` gilt global statt pro Foto, Startwerte fehlen: +/− rechnet vor der Vorschau mit falscher Basis
**Status:** B-S · **Quell-IDs:** A8

**Ort:** `GraffitiStudio.swift:44` (es fehlen `glare`, `clarity`, `denoise`, `white_balance`), `:85`, `:183/185`, `:75`.

**Wirkung:**
- Beim Start (IMG_4363, Reflexschleier automatisch 70 %) wird „+“ zu **10 %**: Die Reflexminderung sinkt drastisch.
- Nach einem Nachtfoto wird bei einem anderen Foto „Schatten −“ zu 60 statt 30.
- Falsche Werte werden als Nutzerentscheidung gespeichert und exportiert.

**Korrektur:** `resolved` pro Foto; +/− und Zahl deaktivieren, solange kein Plan vorliegt; Startwerte aus Python (`schema`/`resolve`).

**Regressionstest:** Swift-Unit-Test: Fotowechsel, dann sofort `set` über +. Erwartet: deaktiviert, oder Basis = Plan des neuen Fotos.

### R28 · Menübefehle bleiben bei offenem Masken-Editor aktiv: Masken von Foto A landen auf Foto B, „Abbrechen“ stoppt einen Export
**Status:** P (Swift-Laufzeit: Wirken Menüs bei offenem Sheet?) · **Quell-IDs:** A10, B11, C18, F7

**Ort:** `GraffitiStudio.swift:366` (`CommandGroup`/`CommandMenu` ohne `.disabled`), `:77-84` (nicht-modales `panel.begin`), `:344` („Abbrechen“ setzt `knobs=saved` ohne Fotobezug), `:146`.

**Auslöser:** Editor für A offen, Cmd+O bzw. Cmd+Shift+O wählt B, dann „Abbrechen“ im Sheet. Oder Cmd+E bei offenem Sheet.

**Wirkung:**
- A's Ecken und Masken werden auf B angewendet und in `perPhoto[B]` gespeichert.
- A's unbestätigte Editoränderungen werden aktiv.
- Cmd+E exportiert mit unbestätigten Masken; „Abbrechen“ im Sheet bricht dann den Export ab.

**Korrektur:** Menübefehle mit `.disabled(model.maskEditor || model.exportRunning)` versehen; Guards in `chooseFolder`, `addFiles`, `exportPhoto`, `reset`; `MaskView` merkt sich den Fotopfad.

**Regressionstest:** UI-Test der Folge. Erwartet: Menüpunkte bei offenem Editor deaktiviert.

### R29 · Instagram-Karussell: falsche Slide-Anzahl, äußere Slides bis zu 67 % schwarz
**Status:** B-A · **Quell-IDs:** C7

**Ort:** `exports.py:10-15` (`count=ceil(ratio)` für 1080er-Quadrate, ab ratio > 2,6 aber Höhe 720; `contain` statt passender Aufteilung).

**Wirkung:**
- 2,1:1 ergibt 3 Slides, die äußeren 45 % schwarz.
- 4:1 ergibt 4 Slides, die äußeren 66,7 % schwarz.
- 4:5- und 3:2-Bilder landen mit Balken in einem Quadrat.
- Widerspricht der Zusage „nahtlose Slides“.

**Korrektur:** `count=max(1,ceil(ratio/1.91))`, `slide_h=round(1080*count/ratio)` begrenzt auf 566…1350, ohne Obergrenze 4. Einzelbilder als 4:5 bzw. 1,91:1.

**Regressionstest:** Für ratio 0,8–8 liegt der Schwarzanteil je Slide bei höchstens 2 %.

### R30 · Panorama im Ordnerexport: quadratischer Paarvergleich, SIFT je Paar neu, ohne Fortschritt, Abbruch oder Speichergrenze
**Status:** B-A (Laufzeit) / P (Speicher) · **Kategorie:** Leistung / Blockiert · **Quell-IDs:** C6, K4

**Ort:** `exports.py:43-61` (`overlap` für alle n(n−1)/2 Paare, SIFT jedes Mal neu), `studio_backend.py:95-96/106-110`.

**Wirkung:**
- 12 Fotos brauchen 30,6 s, 23 Fotos 119,8 s; es wächst quadratisch. Die App zeigt währenddessen „Fertig“ und reagiert nicht auf Abbrechen.
- Bei 200 Fotos werden etwa 5 GB im Speicher gehalten, bevor der Stitcher startet.

**Korrektur:** SIFT je Bild einmal; `cancel`/`progress` an `stitch`; Bildanzahl begrenzen (z. B. ≤ 30) mit klarer Meldung; für das Panorama nur Pfade sammeln.

**Regressionstest:** 23 Bilder: Abbruch innerhalb von 1 s; Merkmalsberechnung je Bild genau einmal (Zähler).

### R31 · Ein einzelner OCR- oder KI-Ausfall im Ordnerexport schaltet die Funktion für alle folgenden Fotos ab – ohne Warnung
**Status:** B-A · **Quell-IDs:** K1, K3

**Ort:** `graffiti.py:12/51-55` (`SESSION['ocr_available']=False` nach einem Fehlschlag), `graffiti.py:111-117` (`SESSION['ai_available']=False`; nur das erste Foto erhält eine Warnung), `studio_backend.py:101`.

**Wirkung:**
- Nach einem OCR-Timeout (über 45 s) werden folgende Abzüge mit `rotate=0` und damit **seitlich** exportiert. Fotos bleiben ungedreht; Status „OK“ ohne Warnung, obwohl die Einzelvorschau sie dreht.
- Mit „Lokale KI“ laufen nach einem Ausfall alle weiteren Fotos klassisch, aber mit Status „OK“.

**Korrektur:**
- Funktion nur bei dauerhaftem Fehlen abschalten (Engine fehlt, wiederholter Startfehler); Einzelfehler nur am Foto markieren.
- Bei `ocr=False` für Abzüge dieselbe Warnung wie bei unsicherer OCR setzen.
- Lauf-Warnung „N Fotos ohne angeforderte KI“.

**Regressionstest:** OCR-Stub, der beim 1. Foto in den Timeout läuft. Erwartet: Foto 2 (Abzug) wird gedreht oder trägt eine Warnung. Vorlage: `repro/K/`.

### R32 · Blitz-Markierungen und Mehrfach-Scan-Vorschläge existieren in der nativen App nicht; Warnungen verweisen auf nicht vorhandene Bedienung
**Status:** B-A · **Kategorie:** Dokumentation / Fehler nicht sichtbar · **Quell-IDs:** E11, G8, G9, G15

**Ort:**
- `analysis.py:140-153`: `review_regions` und `panel_candidates` werden nur ins JSON geschrieben.
- `studio_backend.py:97-100`: Vergleich ohne Markierungen, kein `split_panels`.
- Die Warnungen in `analysis.py` nennen „Abzüge prüfen“ und „markierte Bereiche“.

**Wirkung:**
- „Möglicher Kamerablitz/Reflex: markierte Bereiche prüfen“: Es gibt keine Markierung (0 gelbe Pixel im Vergleichsbild).
- Für Mehrfach-Scans entstehen keine „zusätzlichen Bildvorschläge“, anders als in Chat_Korrekturen beschrieben.
- „Abzüge prüfen“ gibt es in der nativen App nicht. Erkannte Kandidaten-Ecken (`candidate_preparation`) bietet der Editor nicht an.

**Korrektur:** `review_regions` als Overlay in Original/Vergleich und im Vergleichsbild des Stapels zeichnen; `split_panels` im nativen Stapel aufrufen; Warntexte an die native Bedienung anpassen; `candidate_preparation` als Startecken im Editor.

**Regressionstest:** Scan 2000×600 mit zwei Stegen und Blitzfleck. Erwartet: Vergleichsbild mit Markierung und Ordner `Bildvorschlaege` mit 3 Dateien.

### R33 · Exporte verlieren Aufnahmedatum, Kamera und GPS (EXIF)
**Status:** B-A · **Quell-IDs:** C17, D13

**Ort:** `graffiti.py:125`, `exports.py:16-17` (speichern ohne `exif=`).

**Wirkung:** Kein `DateTimeOriginal` in PNG und Slides; die Dateizeit ist die Exportzeit. Sortierung und dokumentarischer Erhalt nach Aufnahmedatum gehen verloren.

**Korrektur:** EXIF der Quelle übernehmen (Orientation auf 1, ohne Vorschaubild), Dateizeit setzen, GPS optional entfernen.

**Regressionstest:** Quelle mit `DateTimeOriginal`. Erwartet: in PNG, Slides und Vergleich vorhanden, Orientation = 1.

### R34 · Prüfnachweise: Berichte nicht aus den Tests erzeugbar, falscher Prüfling, zu schwache Orakel, Lücken genau bei den Beschwerden
**Status:** B-A/B-S · **Kategorie:** Test · **Quell-IDs:** G2, G3, G4, G10, G11, G17

**Berichte:**
- `Pruefung.json` enthält `gui_checked: true`, `gui_checks`, `native_compiled`, `file_dialogs` und `photos_app_integration`. `test_native_bridge.py:45-46` schreibt aber `gui_checked=False` und keinen dieser Schlüssel.
- `Backend_Pruefung.json` enthält `backend_only`; der Test schreibt `gui_built`.
- Die ausgelieferten Berichte stammen also nicht unverändert aus den ausgelieferten Tests.

**Prüfling:**
- Die Tests prüfen `outputs/Graffiti_Studio_Mac`, gezippt wird `…_Nativ` (offen benannt).
- `test_native_engine.py:42` schreibt in das signierte App-Bundle.

**Orakel:**
- „bekannter Abzug gedreht und zugeschnitten“ prüft nur `w>h` und die Größengrenze (`test_native_engine.py:26`, `test_native_bridge.py:19`).
- Ein Ergebnis mit 19 % Tisch und 8 % Nachbarabzug besteht (ausgeführt). IMG_4373 kommt in keinem Test vor.

**Pfadabdeckung:**
- Der Ordnertest prüft Python-`list_sources`, die App nutzt aber den Swift-Filter (R23).
- Die Abbruchtests prüfen nicht den App-Weg (OCR, serielle Queue).

**Fehlende Tests:**
- `per_photo` im Stapel, Masken nach Drehung (R3), `exportLibrary`-Basis (R1), Editor ohne Analyse (R2), ICC (R10), Swift insgesamt.

**Korrektur:**
- Berichte nur maschinell erzeugen, mit Zeitstempel, Versionen und SHA-256 des Prüflings; manuelle GUI-Prüfungen getrennt ausweisen.
- Ressourcenpfad als Argument übergeben, gegen eine Kopie testen.
- Orakel für Abzüge: `'Fotorezept ausgeführt.' in executed`, Seitenverhältnis aus den Rezeptecken ±2 %, Randfarbanteil.
- Die Vorlagen `repro/G/g_mask_registration.py` und `repro/G/g_recipe_assignment.py` übernehmen und die Regressionstests dieses Berichts ergänzen.

---

## 5. Befunde – Schweregrad niedrig

| Nr. | Befund | Status | Ort | Kurzkorrektur | Quell-IDs |
|---|---|---|---|---|---|
| R35 | Freigegebene Bilder (UZO): Regler, Ecken und Masken werden kommentarlos ignoriert; der Plan meldet `controls`, der Vergleich „Mit Reglern bearbeitet“. Instagram, Panorama und Vergleich öffnen die Kopie ohne EXIF-Drehung, Hochformat erscheint seitlich. | B-A | `graffiti.py:57-63`, `studio_backend.py:93/99`, `native_bridge.py:48` | Warnung plus Regler/Editor deaktivieren; `read_image` statt `Image.open` | B15, D10, E8, C12, D11 |
| R36 | Eckreihenfolge/Umlaufsinn nicht normalisiert: Gegen den Uhrzeigersinn gezogen entsteht ein gespiegeltes (transponiertes) Bild, das keine Drehung zurückholt; zyklisch verschoben eine stille Drehung. | B-A | `photo_prepare.py:34-41`, `adjustments.py:58-61` | Shoelace-Fläche < 0 → `p[[0,3,2,1]]`, Startecke oben links | B7 |
| R37 | Abbruch im Ordnerexport: Teilergebnisse ohne Protokoll, Bericht, ZIP und Hinweis; „Ergebnisse öffnen“ fehlt. Ein Fehler nach den Bildern (z. B. Platte voll beim ZIP) meldet den ganzen Export als gescheitert und hinterlässt ein defektes ZIP unter dem Endnamen. | B-A | `studio_backend.py:85-121`, `native_bridge.py:44-57`, `GraffitiStudio.swift:136/141` | `try/finally` mit CSV/Bericht/`ABGEBROCHEN.txt`; ZIP als `.part` + `os.replace`; ZIP-Fehler nur als Warnung | C4, C5 |
| R38 | Jedes vorgeschaute Foto ohne Abzug landet unter „Abzüge“ (`NSNull != nil`). Typ und Vorauswahl richten sich nach dem Dateinamen; gleichnamige Fotos aus Unterordnern sind nicht unterscheidbar. | B-A/B-S | `GraffitiStudio.swift:132`, `:66-72`, `:255/262/277` | `plan["preparation"] is [String:Any]`; Unterordner anzeigen; Typ per Fingerabdruck | A17, G16, A20 |
| R39 | `per_photo`-Schlüssel: Swift sendet `photo.path`, Python sucht `str(source.resolve())`. Bei Symlink-Pfaden (verlinkter Ordner, `/tmp`→`/private/tmp`) gehen Ecken, Masken und Einzelwerte im Stapel still verloren. | P (ob macOS-Pfade aus `NSOpenPanel` Symlinks enthalten) | `studio_backend.py:89`, `GraffitiStudio.swift:63/149` | `by.get(str(source)) or by.get(str(source.resolve()))`; Schlüssel beidseitig normalisieren | A9, B10, C2 |
| R40 | Interpreter fest auf `/opt/homebrew/bin/python3.14`, Rückfall auf ein beliebiges `python3` trotz ABI-gebundener vendor-Erweiterungen (`cpython-314`); python.org-Installationen werden nicht gefunden. Unter einer ausdrücklich gesetzten Nicht-UTF-8-Locale wird ein erfolgreicher Export als „ohne Ergebnis“ gemeldet. | B-A | `GraffitiStudio.swift:96/98`, `native_bridge.py:5-13` | Kandidatenliste nur 3.14 plus Startprüfung (`cache_tag`, Importe); `env["PYTHONUTF8"]="1"`, `read_text(encoding='utf-8')` | F5, F8 |
| R41 | Wird die Brücke hart beendet (Aktivitätsanzeige, jetsam, künftige SIGKILL-Eskalation), läuft `realesrgan` verwaist weiter. | B-A | `studio_backend.py:13`, `GraffitiStudio.swift:287` | `os.setpgrp()` in `native_bridge`; Swift `kill(-pid,…)` | F10 |
| R42 | Lange Dateinamen: `.working.png` plus Präfix `01_` überschreitet 255 Byte (bei NFD-Umlauten schon ab etwa 80–120 Zeichen), das Foto scheitert. | B-A | `studio_backend.py:39/47/92` | Namen UTF-8-sicher kürzen + Hash; Hilfsdateien per `mkstemp` | C13 |
| R43 | ZIP, Plan-JSON und CSV enthalten absolute Pfade (`/Users/<name>/…`). Die ZIP-Prüfung besteht nur aus `assert testzip()` und entfällt bei `PYTHONOPTIMIZE`. | B-A | `studio_backend.py:46/101/117-121`, `native_bridge.py:49-53` | Relative Namen; explizite Prüfung von Namensliste und CRC mit Klartextfehler | C14 |
| R44 | Status „Export fertig · N Bild(er)“ ohne Gesamtzahl und ohne Prüf- und KI-Befunde; die Zahl der Teilfehler steht nur in der Warnzeile. | B-A | `GraffitiStudio.swift:134`, `studio_backend.py:105-122` | „N von M exportiert, K zur Prüfung, G mit KI-Referenz“ | C16 |
| R45 | Pillow-Pixelgrenze (178,9 MP) blockiert große Panoramen trotz späterer 30-MP-Begrenzung; defekte oder leere Dateien liefern rohe englische Pillow-Meldungen; extrem flache Bilder (Breite > 1800 × Höhe) stürzen in `recipe()` mit Höhe 0 ab. | B-A | `graffiti.py:43-44`, `photo_prepare.py:15` | Bewusste Grenze plus `draft()`/`reduce()` beim Lesen; deutsche Meldungen; `max(1,…)` | D15, E14, E15 |
| R46 | Rezept-Reflexstärke wird bei „Auto“ auf das 10-%-Raster gerundet: 0,62 → 0,595 (IMG_4363/4373), 0,15 → 0,17. | B-A | `adjustments.py:86/103-104` | Bei Auto den Rezeptwert unverändert lassen | D16, E16 |
| R47 | Weiße Farbe wird als „Überstrahlung mit verlorenen Details“ mit Konfidenz 0,95 gemeldet; weiße Zierstreifen gelten als Scan-Trenner. Es werden keine Pixel verändert, aber ein unsicherer Befund als Tatsache formuliert. | B-A | `flash.py:25-27`, `analysis.py:62-71/144` | Konditionale Formulierung; Farbflächen-Merkmale abwerten | E17 |
| R48 | Alt-CLI `--prepare pruefen` startet mit dem Rezept eines **anderen** gleichnamigen Fotos und überschreibt dann das geprüfte Rezept von IMG_4363 (Schlüssel = Dateiname) im App-Bundle. | B-A | `photo_prepare.py:133-142` | Rezepte nach Fingerabdruck schlüsseln; in Application Support speichern; Alt-Pfad entfernen | E18 |
| R49 | `setRotation` löscht Masken auch ohne wirksame Änderung (`nil` ↔ gleicher Wert, z. B. „0°“ bei einem Foto ohne Rezept). | B-S | `GraffitiStudio.swift:172` | Wirksame Drehung vergleichen | B13 |
| R50 | Nach Export oder Abbruch wird die verworfene Vorschau nicht neu berechnet; „Ergebnis“ zeigt einen veralteten Stand. | B-S | `GraffitiStudio.swift:92/134/136` | Nach Abschluss `schedule()` bzw. „veraltet“ kennzeichnen | A18 |
| R51 | `Bauen.command` baut nur `GraffitiStudio.swift` (kein `mkdir`, `orientation` wird nie gebaut, Ziel-macOS unbekannt); die Ad-hoc-Signatur wird nicht geprüft; `.pyc` werden nach dem Signieren entfernt; Weitergabe an andere Macs scheitert an Gatekeeper/Quarantäne. | P | `Bauen.command:3-5`, `zip_native.py:3-6` | Vollständiges Bauskript; innere Binärdateien einzeln signieren; `codesign --verify` | F11 |
| R52 | (Hypothese) Eine als „sicher“ geltende Vision-OCR dreht beliebige Nicht-Abzüge (Wagennummern, Schilder) ohne Warnung; ob Vision auf echten Graffiti-Fotos solche Werte liefert, ist ungeprüft. | P | `analysis.py:119-122` | Bei Fotos ohne Rezept nur Vorschlag plus Warnung | E12 |
| R53 | (Hypothesen) (a) Orientierung wird doppelt bestimmt (ImageIO in Swift, Pillow in Python); bei EXIF nur in ImageMagick-Textchunk oder XMP passen die Ecken nicht. (b) Bei Referenzkorrektur richtet sich die Vergrößerung nach den Originalmaßen, das Bild ist aber das Referenz-PNG, sodass der Export kleiner als das Original sein kann. (c) Ecken und Masken hängen am Pfad statt am Inhalt; eine extern ersetzte Datei erhält fremde Masken. | P | `GraffitiStudio.swift:290-293`, `graffiti.py:43-44`, `analysis.py:155-168`, `GraffitiStudio.swift:49` | (a) Orientierung nur in Python bestimmen und dem Editor liefern; (b) Skalierung nach `apply_plan` bestimmen, Warnung; (c) `source_sha256` in `KnobState` und in `prepare_plan` prüfen | B16, K5, K6 |

---

## 6. Dokumentation gegen Implementierung

| Aussage | Fundstelle | Befund |
|---|---|---|
| „gespeicherte Einzelwerte und Masken bleiben ihrem jeweiligen Foto zugeordnet“ | LIES_MICH (Bedienung) | Falsch für `geometry` und `references` (R1); Masken gehen bei „Einstellungen laden“, Klick im Ecken-Werkzeug und App-Ende verloren (R4–R6) |
| „Neue individuelle Masken werden erst nach deiner Prüfung zu wiederverwendbaren Fotorezepten“ | Chat_Korrekturen.md | Die native App speichert Masken nie dauerhaft (R6) |
| „Keine ungeprüfte automatische Beschneidung unbekannter Züge“ | Chat_Korrekturen.md | Bei `paper_confidence ≥ 0,86` wird automatisch beschnitten (R9) |
| „Asymmetrische dunkle Nachtbereiche erhalten“ | Chat_Korrekturen.md, `analysis.py:56` | Asymmetrische Bereiche werden abgeschnitten (R21) |
| „Mehrere Abzüge in einem Scan: zusätzliche Bildvorschläge“ | Chat_Korrekturen.md | Nur im Alt-CLI, nicht in der nativen App (R32) |
| „Kamerablitz …: markierte Bereiche im Vergleich“ | Chat_Korrekturen.md | Keine Markierung in der nativen App (R32) |
| „Lokale KI …: Einmaliger Versuch, danach in diesem Lauf klassisch“ | Chat_Korrekturen.md | Gilt nur im Stapel; jede Vorschau versucht neu (R17). Im Stapel bleibt der Ausfall danach ungemeldet (R31) |
| „Tatsächliches Backend in jedem Plan/CSV“ | Chat_Korrekturen.md | Generative Referenz wird als „klassisch“ ausgewiesen (R20) |
| „Die bekannten generativen Referenzen sind im Ergebnisplan gekennzeichnet“ | LIES_MICH | Nur im Plan; Bilddateien ungekennzeichnet; Hinweis bleibt nach Abschalten falsch stehen (R20) |
| „±100 % entspricht ±2 Belichtungsstufen“ | `adjustments.py:10`, UI | Tatsächlich etwa ±4,4 EV-äquivalent auf Gamma-Werten (R15) |
| „Stärke der anhand neutraler Stellen vorgeschlagenen Korrektur“ (Weißabgleich) | Regler-Hilfe | Regler ist praktisch wirkungslos (R14) |
| „Vorschau“ / „200 % Vorschau“ / Vergleich | LIES_MICH, UI | Vorschau weicht systematisch vom Export ab (R16); Farbvergleich irreführend (R10) |
| „Instagram: Eine gemeinsame Basis, nahtlose Slides“ | Chat_Korrekturen.md | Äußere Slides bis zu 67 % schwarz (R29) |
| „Pillow, NumPy, OpenCV … liegen in der App“; Abhängigkeiten | LIES_MICH, Übergabe | tkinter ist zusätzlich Pflicht (R11). Die Bibliothekstabelle der Übergabe ist **leer**, es sind keine Versionen angegeben |
| „Tk-/AppleScript-Pfade optional, unverändert mitgegeben“ | Übergabe | Tk ist durch den Modul-Import Pflicht (R11); der Alt-Pfad kann das Rezept von IMG_4363 überschreiben (R48) |
| Gespeicherte Prüfberichte (GUI geprüft) | `Pruefung.json`, `Backend_Pruefung.json` | Nicht aus den mitgelieferten Testprogrammen erzeugbar (R34) |
| „Abbrechen stoppt auch einen laufenden KI-Kindprozess“ | LIES_MICH | **Stimmt** (ausgeführt: 0,1–0,5 s; ein SIGTERM ignorierendes Modell wird nach 3,5 s gekillt). OCR, Rendern, Panorama und ZIP sind aber nicht abbrechbar (R18) |

## 7. Geprüft und in Ordnung (Auswahl, ausgeführt)

- **10-%-Raster, Grenzwerte, neutrale Nullregler:**
  - `Settings` lehnt 15 % ab; Extremwerte liefern gültiges RGB in Originalgröße.
  - Alle Regler auf 0 ergeben pixelidentische Ausgabe; Retuschstärke 0 ist neutral.
- **Maskendeckung:** Gleiche normierte Ecken, Regionen und Striche treffen auf 1800-px-Maskenbild und Vollauflösung dieselbe Stelle.
  - Abweichung höchstens 2,5 Export-Pixel bei 7000 px, bei 0/90/180/270° mit Perspektive.
  - Vollbild-Ecken sind pixelgleich zur Identität.
  - Der eigentliche Fehler ist die *Drehung* (R3), nicht die Skalierung.
- **Drehrichtung:** Die Zuordnung `orientation.swift` [.up,.left,.down,.right] → [0,90,180,270] passt zu PIL `rotate` (gegen den Uhrzeigersinn) und zu EXIF 1/8/3/6.
- **Fingerabdruck:**
  - Identische SHA-256 mit Pillow 12.3, Pillow 10.0 und OpenCV/libjpeg-turbo (Baseline, progressiv, EXIF 6).
  - Ein umbenannter Abzug erhält sein Rezept per Inhalt.
  - Gleicher Name und gleiche Größe bei anderem Inhalt: Das Rezept wird mit Warnung verworfen.
- **Grenz- und Defekteingaben:**
  - 1×1, 1×5000, 49×49, schwarz, weiß, L, P, RGBA, CMYK, 48-Bit-RGB und winzige Bilder laufen durch Analyse, Vorschau und Export.
  - Der Plan ist JSON-serialisierbar.
  - Entartete Ecken (doppelt, kollinear) werden abgelehnt; die Meldung „ohne Kreuzung“ ist für doppelte Ecken aber irreführend.
- **Sonderzeichen und Kollisionen:**
  - Anführungszeichen, `<&`, Emoji, NFD-Umlaute, Zeilenumbruch, führendes `-`, `..` und Punkte im Stamm laufen samt ZIP und CSV korrekt.
  - Dateikollisionen verhindern das NN_-Präfix und Zeitstempelordner.
- **Prozessprotokoll:**
  - SIGTERM während der Importe beendet sofort und wird korrekt als „Abgebrochen“ gemeldet.
  - Nach Abbruch gibt es keine falschen Erfolgsmeldungen; ein wahrheitsgemäßes `result` kommt, wenn der Abbruch erst nach dem Speichern eintraf.
  - GUI-Start ohne `LANG` bzw. mit `LANG=C` ist dank PEP 538/540 unkritisch.
  - App Translocation: Kein Bridge-Pfad schreibt ins Bundle.
- **Weitere korrekte Teile:**
  - KI-Fallback deckt alle realistischen Fehler ab: fehlende Engine, Exit ≠ 0, Datenmüll, abgeschnittene PNG, Timeout.
  - 30- und 60-MP-Begrenzung rechnet korrekt.
  - Division im Schleiermodell ist durch die Begrenzung auf 65 abgesichert.
- **Stapel:** Kein Erfolg ohne Bild (`good==0` führt zu einem Fehler); Teilfehler erscheinen als FEHLER-Zeile und Warnung.

## 8. Nicht geprüft / offene Punkte

- Reale Swift-Laufzeit: Kompilierbarkeit, Concurrency-Isolation im Swift-5-Modus, Menüverhalten bei offenem Sheet (R28), `DateFormatter` in `stamp()` ohne `en_US_POSIX` (andere Kalender und Ziffern in Ordnernamen).
- Echte Vision-OCR und echtes Real-ESRGAN (GPU/Metal-Fehlerbilder, Laufzeiten). Simuliert wurde nur mit Stubs.
- Die Originalfotos und Referenz-PNGs: tatsächliche ICC-Profile der 23 Fotos, Auflösung von `Korrektur_01/02.png` (R53 b).
- macOS-Datenschutzfreigaben (TCC) für den Python-Kindprozess nach Ad-hoc-Neubau; Ausgabe auf exFAT/SMB (`: ? " *`), iCloud-Platzhalterdateien, schreibgeschützte Volumes, zwei App-Instanzen in denselben Ausgabeordner.

## 9. Empfohlene Reihenfolge der Korrekturen

| Schritt | Was | Befunde |
|---|---|---|
| 1 | Sofort, kleine Eingriffe:<br>- Lazy-Import ImageTk<br>- `cancelled` bei `start()==false`<br>- `Settings.from_dict` in das `try` und `per_photo` pro Foto validieren<br>- `exportLibrary` mit fotospezifischem `geometry`/`references`<br>- `closeMask` ohne `references=false`<br>- Editor erst nach Analyse<br>- Trefferradius im Ecken-Werkzeug<br>- `loadRecipe` zusammenführen statt ersetzen<br>- `NSNull`-Prüfung | R11, R7, R8, R1, R2, R4, R5, R38 |
| 2 | Geometrie und Masken: gemeinsame Geometrieauflösung für `prepare` und Render; `rotation` nie `nil` bei gesetzten Ecken; „Zuschnitt auf Automatik“; Ecken normalisieren und validieren | R3, R2, R36, R25 |
| 3 | Persistenz und Beenden: Sitzung sichern; Rückfrage beim Beenden; Stapel-Abbruch mit Protokoll | R6, R37 |
| 4 | Bildkorrektheit: Farbmanagement; Eingabemodi; Weißabgleich; lineare Belichtung; Vorschau = Export; Reflexbereich-Semantik; Auto-Papierkanten nur als Vorschlag; `black_border` | R10, R13, R14, R15, R16, R19, R9, R21 |
| 5 | Wahrhaftigkeit: generative Kennzeichnung; Warnungen am Ende berechnen; Markierungen und Bildvorschläge oder ehrliche Texte; Ausfälle im Stapel melden | R20, R32, R31, R44 |
| 6 | Leistung und Abbruch: Analyse-Cache; verkleinerte Vorschau; abbrechbare OCR; SIGKILL-Eskalation an die Prozessgruppe; Panorama O(n) | R17, R18, R30, R41 |
| 7 | Tests: die Regressionstests dieses Berichts als automatisierte Suite gegen eine Kopie des finalen Bundles; Berichte nur maschinell | R34 |

## 10. Anhang: Reproduktionen

- `repro/<Bereich>/*.py`: Skripte der Finder. `repro/<Bereich>-verify/*.py`: unabhängige Gegenproben. `repro/K/`: Vollständigkeitskritik.
- Die Bereiche sind A–G wie in Abschnitt 2.
- Die Skripte erwarten:
  - eine **Kopie** des Resources-Ordners (sie legen selbst Kopien wie `Resources_t2` an bzw. verwenden sie),
  - Python mit NumPy, OpenCV und Pillow.
- Absolute Pfade aus der Prüfumgebung (`/tmp/claude-0/…/scratchpad`) müssen angepasst werden. Die großen synthetischen Testbilder sind nicht beigelegt; die Skripte erzeugen sie neu.
- `repro/workflow_rohdaten.json`: alle 123 Einzelbefunde mit Belegtext, Ausgaben, Gegenprüfer-Urteil und Fix-Korrekturen.
- `repro/PRUEFKONTEXT.md`: Prüfumgebung und rekonstruierte Architektur.
