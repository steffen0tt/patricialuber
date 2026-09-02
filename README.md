# Patricia Luber – Malerei (Website-Nachbau)

Dies ist ein 1:1-Nachbau der Wix-Seite `patricialuber.wixsite.com/malerei` als
statische Website (reines HTML/CSS/JavaScript, ohne Wix, ohne Baukasten-Kosten).
Sie kann kostenlos über **GitHub Pages** gehostet werden.

## Inhalt

- `index.html` – Startseite (Hero, "Alle Produkte"-Galerie, Über-mich-Teaser)
- `oel-acryl.html` – Übersicht der Öl-&-Acryl-Unterkategorien
- `abstrakt.html`, `landschaften.html`, `menschen.html`,
  `pflanzen-stillleben.html`, `tiermotive.html` – die 5 Unterkategorien
- `aquarell.html` – Aquarell-Galerie
- `ueber-mich.html` – Über-mich-Seite mit Porträtfoto
- `kontakt.html` – Kontaktformular
- `assets/css/style.css` – gesamtes Design (Farben, Schrift, Layout)
- `assets/js/main.js` – mobiles Menü, Bilder-Lightbox, Kontaktformular-Logik
- `assets/images/` – alle 79 heruntergeladenen Gemälde-Fotos plus Hero- und
  Porträtbild, in reduzierter, aber websitetauglicher Auflösung

Alle Texte, Bildtitel und die Galerie-Struktur wurden von der Original-Wix-Seite
übernommen. Die einzelnen "Produktseiten" von Wix (z. B. `/product-page/obsteller`)
waren auf der Original-Seite technisch leer (der Wix-Shop war nicht aktiv) –
stattdessen öffnet ein Klick auf ein Bild hier eine große Vorschau (Lightbox)
direkt auf der Galerieseite.

## Kontaktformular

GitHub Pages kann keine Formulardaten selbst verarbeiten (rein statisches
Hosting, kein Server). Das Formular auf `kontakt.html` öffnet daher beim Klick
auf "Senden" automatisch das E-Mail-Programm des Besuchers mit einer
vorausgefüllten Nachricht (Name, E-Mail, Betreff, Nachricht) – ganz ohne
Konto bei einem Formular-Dienst.

**Wichtig:** Trage vor der Veröffentlichung die echte E-Mail-Adresse ein, an die
die Nachrichten gehen sollen. Öffne dazu `assets/js/main.js` und ersetze
`CONTACT_EMAIL` (suche danach) durch z. B. `patricia@example.com`.

Falls später ein "richtiges" Formular ohne E-Mail-Programm gewünscht ist, kann
man z. B. [Formspree](https://formspree.io) (kostenloses Konto) einbinden –
dazu einfach im `<form>`-Tag in `kontakt.html` `action="https://formspree.io/f/DEINE-FORM-ID"`
und `method="POST"` ergänzen und das JavaScript im Kontaktformular-Teil aus
`main.js` entfernen.

## Lokal ansehen

Einfach `index.html` per Doppelklick im Browser öffnen – die Seite funktioniert
auch ohne Internetverbindung und ohne lokalen Server.

## Veröffentlichen mit GitHub Pages

1. **GitHub-Konto & Repository anlegen** (falls noch nicht vorhanden):
   - Auf [github.com](https://github.com) registrieren/einloggen.
   - Oben rechts auf **+ → New repository** klicken.
   - Name z. B. `patricia-luber-malerei`, auf **Public** stellen, dann
     **Create repository**.

2. **Git auf dem Mac einrichten** (Terminal öffnen):
   ```bash
   cd ~/Documents/patricia-luber-website
   git init
   git add .
   git commit -m "Website von Patricia Luber – Erstveröffentlichung"
   git branch -M main
   git remote add origin https://github.com/DEIN-BENUTZERNAME/patricia-luber-malerei.git
   git push -u origin main
   ```
   (Bei `git push` ggf. einmalig im Browser bei GitHub anmelden.)

3. **GitHub Pages aktivieren**:
   - Im Repository auf GitHub: **Settings → Pages** (linkes Menü).
   - Unter "Build and deployment" → **Source**: `Deploy from a branch` wählen.
   - Branch: `main`, Ordner: `/ (root)` auswählen, **Save** klicken.
   - Nach ca. 1–2 Minuten ist die Seite erreichbar unter:
     `https://DEIN-BENUTZERNAME.github.io/patricia-luber-malerei/`

4. **Eigene Domain (optional)**: Falls du z. B. `patricia-luber.de` besitzt,
   kannst du sie unter **Settings → Pages → Custom domain** eintragen und bei
   deinem Domain-Anbieter einen CNAME/A-Record auf GitHub Pages setzen
   (Details: [GitHub-Doku zu Custom Domains](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site)).

## Später Inhalte ändern

- **Neues Bild hinzufügen**: Datei in `assets/images/` legen, dann in der
  passenden `.html`-Datei einen neuen Block nach dem Muster
  ```html
  <figure class="art-card" data-full="assets/images/DATEINAME.jpg" data-title="Bildtitel">
    <img src="assets/images/DATEINAME.jpg" alt="Bildtitel" loading="lazy">
    <figcaption>Bildtitel</figcaption>
  </figure>
  ```
  in `<div class="art-grid"> … </div>` einfügen.
- **Text ändern**: einfach die entsprechende `.html`-Datei in einem
  Text-Editor öffnen und den Text anpassen.
- Änderungen lokal speichern, dann im Terminal im Projektordner:
  ```bash
  git add .
  git commit -m "Beschreibung der Änderung"
  git push
  ```
  GitHub Pages aktualisiert die Seite automatisch nach dem Push.
