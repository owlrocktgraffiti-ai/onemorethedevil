# Prüfkontext Graffiti Studio 5.2 (für alle Prüf-Agenten)

## Wo liegt der Code
Basis: `/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad`
- `pkg/Quellcode/GraffitiStudio.swift` – SwiftUI/AppKit-Oberfläche (368 Zeilen, dichter Stil)
- `pkg/Graffiti Studio.app/Contents/Resources/` – Python-Unterbau: adjustments.py, analysis.py, exports.py, flash.py, graffiti.py, native_bridge.py, photo_prepare.py, studio_backend.py, engine/orientation.swift, JSON-Konfiguration, LIES_MICH.txt, Chat_Korrekturen.md
- `pkg/Graffiti Studio.app/Contents/Info.plist`, `pkg/Quellcode/Bauen.command`
- `pkg/Pruefung.json`, `pkg/workspace/work/test_native_engine.py`, `test_native_bridge.py`, `zip_native.py` – frühere Tests/Berichte
- Original-Übergabe (Markdown, inkl. Prüfsummen von Fotos/Binärdateien): `/root/.claude/uploads/6ce71caf-ac92-56ea-8654-f76e736d54cd/2cf56676-Graffiti_Studio_Code_Review.md`

Alle Dateien wurden byte-genau aus der Übergabe wiederhergestellt (SHA-256 identisch mit dem Dateiindex). Zeilennummern beziehen sich auf diese Dateien – mit dem Read-Tool lesen, um Zeilen korrekt zu zitieren.

NICHT verfügbar: die 23 Fotos, Referenz-PNGs, die Modelle/Binärdateien (realesrgan, orientation), vendor-Bibliotheken, macOS/Swift-Compiler. Swift-Befunde sind daher nur statisch prüfbar. Ausführen mit synthetischen Bildern ist für Python möglich.

## Python-Umgebung zum Ausführen
- Interpreter: `/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/venv/bin/python` (Python 3.12, numpy 2.x, opencv-python-headless 4.14, Pillow 12, tkinter vorhanden). Die App nutzt auf dem Mac Homebrew-Python 3.14 mit vendorten Bibliotheken unbekannter Version – Abweichungen beachten.
- Import: `sys.path.insert(0, '<Basis>/pkg/Graffiti Studio.app/Contents/Resources')`.
- Achtung: `native_bridge.py`/`studio_backend.py`/`graffiti.py` lesen JSON-Dateien relativ zu ihrem eigenen Ordner (ROOT). Für Tests, die etwas schreiben könnten, vorher eine KOPIE des Resources-Ordners anlegen, z. B. `cp -r "pkg/Graffiti Studio.app/Contents/Resources" repro/<dein-bereich>/Resources` und dort importieren. Die Dateien unter `pkg/` NIEMALS verändern.
- Reproduktionsskripte und Ausgaben nur unter `<Basis>/repro/<dein-bereich>/` ablegen. Skripte so schreiben, dass sie erneut ausführbar sind (Pfad im Befund nennen).
- Fehlende Laufzeiten (orientation-Engine, realesrgan) fehlen hier wirklich; das ist der Fall „Laufzeit fehlt“ und darf so getestet werden. Zum Simulieren können Stub-Programme in der KOPIE unter engine/ angelegt werden.

## Architektur (Kurz)
Swift-UI startet pro Vorschau/Export einen neuen Prozess `python3 native_bridge.py <preview|export|batch|prepare> --request <json>`; Python antwortet zeilenweise mit JSON-Ereignissen (progress/log/result/error/cancelled) auf stdout, stderr geht in eine Logdatei. Abbruch = SIGTERM → Python setzt ein threading.Event, das an Checkpoints geprüft wird; KI-Kindprozess (realesrgan) wird in run_model beendet. Swift verwaltet Reglerwerte (KnobState) pro Foto nur im Speicher (perPhoto), Ecken/Masken in normierten Koordinaten 0..1. Python: analyze() → Settings.prepare_plan() → apply_plan()/transform() → Skalierung/KI → render() → PNG.

## Nutzeranforderungen (aus dem Prüfauftrag, gekürzt)
- Eigenständige macOS-App für lokale Dateien/Ordner; keine Apple-Fotos-Integration, keine Cloud-/API-Aufrufe. KEINE Cloud- oder Apple-Fotos-Anbindung vorschlagen.
- Ordner inkl. Unterordner tatsächlich nach Fotos durchsuchen und echte Bilddateien erzeugen; Fehler sichtbar; kein Erfolg ohne ausgegebene Bilder.
- Alle Regler in 10-%-Schritten; Belichtung, Kontrast, Schatten/Lichter, Weißabgleich, Details, Rauschen, Reflexminderung; kontrollierbare Vorschau und Vergleich.
- Fotografierte Papierabzüge zuschneiden, entzerren, drehen. IMG_4363/IMG_4373 dürfen NICHT seitlich samt Tisch und Nachbarabzügen ausgegeben werden. EXIF-Orientierung und spätere Koordinaten müssen zusammenpassen.
- Blitz, Reflexe, Schleier, Clipping, Nacht, Unschärfe, Körnung beurteilen; Originalbuchstaben, weiße Farbe, Outlines, schwarze Originalformen schützen; unsichere Erkennung nicht als sichere Rekonstruktion verkaufen.
- Bekannte Referenzkorrekturen (IMG_20190701_182034 Gekritzel + H; zentraler Blitz WFTPXN…) exakt zugeordnet; generative Referenzen korrekt kennzeichnen, nicht als dokumentarisch sicher ausgeben. Neue Fälle brauchen sichere Zuordnung oder Nutzermasken.
- Originale erhalten; Fotorezepte/Masken nur auf das zugehörige Foto; Geometrieänderungen dürfen alte Masken nicht versetzen; bekannte Rezepte per Bildinhalt/Fingerabdruck statt Dateiname.
- Einzel- und Stapelverarbeitung, Fotos/Instagram/Panorama, Ausgabeordner, belastbare ZIPs, verständliche Teilfehler, Abbruch inkl. Modell-Kindprozesse.
- GUI und Python müssen dieselben Werte und Bildkoordinaten verwenden.
- Besonders prüfen: Grenzwerte, leere/defekte Eingaben, Sonderzeichen/lange Pfade, sehr große Bilder/Ordner, doppelte Namen, Symlinks, schnelle Foto-/Reglerwechsel, veraltete Vorschauantworten, Prozessbeendigung, fehlende Laufzeiten, Modellfehler, Masken nach Drehung/Perspektive, Metadaten, Dateikollisionen, wahrheitsgemäße Export-/Fehlerberichte, Dokumentation verspricht mehr als implementiert.
- Priorität: Datenverlust > falsche Bildbearbeitung > blockierte Oberfläche > nicht funktionierender Export > Prozessfehler > Stil.

## Bereits beim Einrichten bestätigt
- `photo_prepare.py` Zeile 6: `from PIL import Image,ImageTk` – PIL.ImageTk importiert tkinter beim Laden. Ohne tkinter (Homebrew: separates Paket python-tk@3.14) scheitert der Import von photo_prepare → analysis → graffiti → jede Vorschau/jeder Export. Hier ausgeführt: ModuleNotFoundError: No module named 'tkinter' (Python 3.11 ohne tk).

## Sprache und Format
Alle Texte in den Ergebnissen auf Deutsch. Zeilenangaben als `Datei:Zeile` (bzw. Bereich). Keine Stilkritik ohne funktionale Wirkung.
