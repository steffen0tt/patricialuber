# Patricia Luber – Malerei (Website)

Statischer Nachbau der Wix-Seite `patricialuber.wixsite.com/malerei` als reine
HTML/CSS/JavaScript-Website, ohne Wix, ohne laufende Kosten. Gehostet kostenlos
über **GitHub Pages**.

## Aufbau des Ordners

```
patricia-luber-website/
├── index.html, *.html, werke/*.html   ← die fertige Website (wird automatisch erzeugt)
├── assets/
│   ├── css/style.css                  ← Design (Farben, Schrift, Layout) – von Hand gepflegt
│   ├── js/main.js                     ← Menü, Bildergalerie, Sortierung, Kontaktformular
│   ├── images/ + images/thumbs/       ← alle Werk-Fotos (Original + kleine Vorschau)
│   ├── icons/                         ← Favicon
│   └── fonts/                         ← selbst gehostete Schriftart
├── sitemap.xml, robots.txt, 404.html
└── source/                            ← die "Quelle": hieraus wird die Website gebaut
    ├── data.json                      ← alle Werke, Kategorien, Kontaktdaten
    ├── build.py                       ← erzeugt aus data.json die *.html-Seiten
    └── manage.py                      ← Werkzeug zum Hinzufügen/Entfernen von Werken
```

**Wichtig:** Die `.html`-Dateien im Hauptordner und in `werke/` werden von
`build.py` automatisch erzeugt. Sie sollten nicht von Hand bearbeitet werden –
Änderungen gehen beim nächsten Bauen wieder verloren. Bearbeitet wird stattdessen
`source/data.json` (am einfachsten über `manage.py`, siehe unten).

`assets/css/style.css` und `assets/js/main.js` sind dagegen **nicht**
automatisch erzeugt und dürfen normal von Hand bearbeitet werden.

## Neue Werke hinzufügen oder entfernen

Dafür gibt es `source/manage.py` – ein kleines Kommandozeilen-Werkzeug, das
Bilder automatisch komprimiert, Vorschaubilder erzeugt, `data.json` anpasst
und die Website neu baut.

Im Terminal:

```bash
cd ~/Documents/patricia-luber-website/source
python3 manage.py add       # neues Werk hinzufügen (fragt Titel, Kategorie, Preis, Bilder ab)
python3 manage.py remove    # Werk entfernen (aus einer Liste auswählen)
python3 manage.py list      # alle aktuellen Werke anzeigen
python3 manage.py build     # Website nur neu bauen, ohne etwas zu ändern
```

Bei `add` fragt das Programm nacheinander alles Nötige ab, unter anderem die
Bilddatei(en) – dafür einfach die Bilddatei(en) aus dem Finder in das
Terminal-Fenster ziehen (das trägt automatisch den Dateipfad ein).

Nach `add` oder `remove` ist die Website lokal fertig aktualisiert. Um sie
online zu veröffentlichen, im Terminal (im Hauptordner, nicht in `source/`):

```bash
cd ~/Documents/patricia-luber-website
git add -A
git commit -m "Werk hinzugefügt: <Titel>"
git push
```

GitHub Pages aktualisiert die Seite automatisch innerhalb weniger Minuten
nach dem Push.

## Kontaktformular

GitHub Pages kann keine Formulardaten selbst verarbeiten (rein statisches
Hosting, kein Server). Das Formular auf `kontakt.html` öffnet daher beim Klick
auf "Senden" automatisch das E-Mail-Programm des Besuchers mit einer
vorausgefüllten Nachricht an die in `source/data.json` hinterlegte
E-Mail-Adresse.

## Lokal ansehen

Einfach `index.html` per Doppelklick im Browser öffnen – die Seite funktioniert
auch ohne Internetverbindung und ohne lokalen Server.

## Veröffentlichen mit GitHub Pages

1. **GitHub-Konto & Repository anlegen** (falls noch nicht vorhanden):
   - Auf [github.com](https://github.com) registrieren/einloggen.
   - Oben rechts auf **+ → New repository** klicken.
   - Name z. B. `patricia-luber-malerei`, auf **Public** stellen, dann
     **Create repository** (nichts initialisieren – das Repo existiert lokal
     schon).

2. **Mit GitHub verbinden und hochladen** (Terminal, im Hauptordner):
   ```bash
   cd ~/Documents/patricia-luber-website
   git remote add origin https://github.com/DEIN-BENUTZERNAME/patricia-luber-malerei.git
   git push -u origin main
   ```
   (Bei `git push` ggf. einmalig im Browser bei GitHub anmelden – am
   einfachsten über [GitHub Desktop](https://desktop.github.com).)

3. **GitHub Pages aktivieren**:
   - Im Repository auf GitHub: **Settings → Pages** (linkes Menü).
   - Unter "Build and deployment" → **Source**: `Deploy from a branch` wählen.
   - Branch: `main`, Ordner: `/ (root)` auswählen, **Save** klicken.
   - Nach ca. 1–2 Minuten ist die Seite erreichbar unter:
     `https://DEIN-BENUTZERNAME.github.io/patricia-luber-malerei/`

4. **Domain in der Website eintragen**: Sobald die GitHub-Pages-Adresse (oder
   eine eigene Domain) feststeht, trage sie in `source/data.json` unter
   `"url"` ein und führe `python3 source/manage.py build` einmal aus – das
   sorgt dafür, dass Sitemap und Vorschaubilder bei geteilten Links (z. B. in
   WhatsApp) korrekt funktionieren.

5. **Eigene Domain (optional)**: Falls du z. B. `patricia-luber.de` besitzt,
   kannst du sie unter **Settings → Pages → Custom domain** eintragen und bei
   deinem Domain-Anbieter einen CNAME/A-Record auf GitHub Pages setzen
   (Details: [GitHub-Doku zu Custom Domains](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site)).
