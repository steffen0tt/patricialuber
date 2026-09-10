#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Werke-Verwaltung für patricialuber.de
======================================

Einfaches Kommandozeilen-Tool, um neue Werke hinzuzufügen oder bestehende
zu entfernen, ohne Programmierkenntnisse zu benötigen.

Benutzung (im Terminal, in diesem "source"-Ordner):

    python3 manage.py add       Neues Werk hinzufügen
    python3 manage.py remove    Werk entfernen
    python3 manage.py list      Alle aktuellen Werke anzeigen
    python3 manage.py build     Seite nur neu bauen (ohne etwas zu ändern)

Nach jedem "add" oder "remove" wird die Website automatisch neu gebaut
(build.py läuft mit). Du musst danach nur noch die Änderungen hochladen:

    cd ..
    git add -A
    git commit -m "Werk hinzugefügt: <Name>"
    git push

Bilder werden automatisch komprimiert (Originalgröße + kleine Vorschau)
und an der richtigen Stelle abgelegt.
"""
import json
import os
import re
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
DATA_PATH = os.path.join(BASE, "data.json")
IMAGES_DIR = os.path.join(REPO_ROOT, "assets", "images")
THUMBS_DIR = os.path.join(IMAGES_DIR, "thumbs")

CATEGORIES = [
    ("abstrakt", "Abstrakt (Öl & Acryl)"),
    ("landschaften", "Landschaften (Öl & Acryl)"),
    ("menschen", "Menschen (Öl & Acryl)"),
    ("pflanzen-stillleben", "Früchte, Pflanzen & Stillleben (Öl & Acryl)"),
    ("tiermotive", "Tiermotive (Öl & Acryl)"),
    ("aquarell", "Aquarell"),
]

UMLAUT_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss",
})

MAX_FULL_EDGE = 1600
FULL_QUALITY = 85
THUMB_MAX_EDGE = 480
THUMB_QUALITY = 72


def slugify(name):
    s = name.translate(UMLAUT_MAP).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s or "werk"


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def run_build():
    print("\n→ Baue Website neu ...")
    result = subprocess.run([sys.executable, os.path.join(BASE, "build.py")], cwd=BASE)
    if result.returncode != 0:
        print("  ✗ build.py ist mit einem Fehler abgebrochen. Bitte oben nachsehen.")
        sys.exit(1)
    print("  ✓ Website neu gebaut.")


def ask(prompt, default=None, required=False):
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        if not val and required:
            print("  (Pflichtfeld, bitte etwas eingeben)")
            continue
        return val


def ask_yesno(prompt, default=False):
    d = "J/n" if default else "j/N"
    val = input(f"{prompt} ({d}): ").strip().lower()
    if not val:
        return default
    return val in ("j", "ja", "y", "yes")


def ask_choice(prompt, options):
    print(f"\n{prompt}")
    for i, (slug, label) in enumerate(options, 1):
        print(f"  {i}) {label}")
    while True:
        val = input(f"Nummer (1-{len(options)}): ").strip()
        if val.isdigit() and 1 <= int(val) <= len(options):
            return options[int(val) - 1][0]
        print("  Ungültige Auswahl, bitte nochmal.")


def process_image(src_path, dest_name):
    """Kopiert + komprimiert ein Bild nach assets/images/<dest_name>
    und erzeugt die passende Vorschau in assets/images/thumbs/."""
    from PIL import Image

    im = Image.open(src_path)
    if im.mode != "RGB":
        im = im.convert("RGB")

    w, h = im.size
    if max(w, h) > MAX_FULL_EDGE:
        scale = MAX_FULL_EDGE / max(w, h)
        im_full = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    else:
        im_full = im
    os.makedirs(IMAGES_DIR, exist_ok=True)
    im_full.save(os.path.join(IMAGES_DIR, dest_name), "JPEG",
                 quality=FULL_QUALITY, optimize=True, progressive=True)

    w, h = im_full.size
    scale = THUMB_MAX_EDGE / max(w, h)
    im_thumb = im_full.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS) if scale < 1 else im_full
    os.makedirs(THUMBS_DIR, exist_ok=True)
    im_thumb.save(os.path.join(THUMBS_DIR, dest_name), "JPEG",
                  quality=THUMB_QUALITY, optimize=True, progressive=True)


def collect_image_paths():
    print("\nBilder hinzufügen: Ziehe eine Bilddatei aus dem Finder in dieses")
    print("Terminal-Fenster (das trägt automatisch den Dateipfad ein) und")
    print("drücke Enter. Leere Eingabe = fertig. Das erste Bild wird das")
    print("Hauptbild (Titelbild).")
    paths = []
    while True:
        raw = input(f"  Bild {len(paths) + 1} (oder Enter zum Beenden): ").strip()
        if not raw:
            if paths:
                break
            print("  Mindestens ein Bild wird benötigt.")
            continue
        # Terminal-Drag-and-drop umgibt Pfade manchmal mit Anführungszeichen
        # oder escaped Leerzeichen mit Backslash.
        path = raw.strip("'\"")
        path = path.replace("\\ ", " ")
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            print(f"  ✗ Datei nicht gefunden: {path}")
            continue
        paths.append(path)
    return paths


def cmd_list():
    data = load_data()
    artworks = data["artworks"]
    print(f"\n{len(artworks)} Werke:\n")
    for a in sorted(artworks, key=lambda a: a["name"]):
        cats = ", ".join(c for c in a["cats"] if c != "home")
        home = " ★" if "home" in a["cats"] else ""
        print(f"  {a['slug']:<28} {a['name']:<30} [{cats}]{home}")
    print()


def cmd_add():
    data = load_data()
    existing_slugs = {a["slug"] for a in data["artworks"]}

    print("=== Neues Werk hinzufügen ===\n")
    name = ask("Titel des Werks", required=True)

    default_slug = slugify(name)
    slug = default_slug
    if slug in existing_slugs:
        print(f"  Hinweis: Der Titel ergibt den internen Namen '{slug}', der schon vergeben ist.")
        slug = ask("Bitte einen anderen internen Namen (nur Kleinbuchstaben, Bindestriche)", required=True)
        slug = slugify(slug)
    while slug in existing_slugs:
        slug = slugify(ask(f"'{slug}' ist auch schon vergeben. Anderer interner Name", required=True))

    cat = ask_choice("Kategorie:", CATEGORIES)
    cats = [cat]
    if ask_yesno("Auf der Startseite im Karussell zeigen?"):
        cats.insert(0, "home")

    print("\nTechnik/Größe, z. B. 'Öl auf Leinwand, 60x80cm'.")
    print("Mehrere Zeilen möglich, leere Zeile = fertig.")
    medium_lines = []
    while True:
        line = input(f"  Zeile {len(medium_lines) + 1} (oder Enter für fertig): ").strip()
        if not line:
            break
        medium_lines.append(line)

    price = ask("Preis (leer = 'Preis auf Anfrage', oder 'verkauft', oder eigener Text)", default="")
    if not price:
        price = "Preis auf Anfrage"
    elif price.strip().lower() in ("verkauft", "sold"):
        price = "VERKAUFT"

    is_new = ask_yesno("Mit 'Neu'-Markierung versehen?")

    image_paths = collect_image_paths()

    # Bilddateinamen bestimmen, Kollisionen mit bestehenden Slugs vermeiden
    gallery_files = []
    for i, _ in enumerate(image_paths):
        if i == 0:
            candidate = f"{slug}.jpg"
        else:
            candidate = f"{slug}-{i + 1}.jpg"
            candidate_slug = f"{slug}-{i + 1}"
            if candidate_slug in existing_slugs:
                candidate = f"{slug}-img{i + 1}.jpg"
        gallery_files.append(candidate)

    print("\n→ Verarbeite Bilder (komprimieren + Vorschau erzeugen) ...")
    for src, dest_name in zip(image_paths, gallery_files):
        process_image(src, dest_name)
        print(f"  ✓ {dest_name}")

    artwork = {
        "slug": slug,
        "name": name,
        "media": "",
        "cats": cats,
        "medium_size": medium_lines,
        "price": price,
        "media_all": [],
        "gallery_files": gallery_files,
        "is_new": is_new,
    }
    data["artworks"].append(artwork)
    save_data(data)
    print(f"\n✓ '{name}' wurde zu data.json hinzugefügt (intern: {slug}).")

    run_build()

    print("\nFertig! Nächster Schritt zum Veröffentlichen:")
    print("  cd ..")
    print(f'  git add -A && git commit -m "Werk hinzugefügt: {name}" && git push')


def cmd_remove():
    data = load_data()
    artworks = data["artworks"]
    ordered = sorted(artworks, key=lambda a: a["name"])

    print("=== Werk entfernen ===\n")
    for i, a in enumerate(ordered, 1):
        print(f"  {i}) {a['name']}  ({a['slug']})")

    val = input(f"\nNummer (1-{len(ordered)}) oder interner Name: ").strip()
    target = None
    if val.isdigit() and 1 <= int(val) <= len(ordered):
        target = ordered[int(val) - 1]
    else:
        target = next((a for a in artworks if a["slug"] == val), None)

    if not target:
        print("  ✗ Nicht gefunden, nichts geändert.")
        return

    print(f"\nDu willst entfernen: '{target['name']}' ({target['slug']})")
    if not ask_yesno("Bist du sicher?"):
        print("  Abgebrochen.")
        return

    delete_images = ask_yesno("Auch die zugehörigen Bilddateien löschen?", default=True)

    artworks.remove(target)
    save_data(data)
    print(f"✓ '{target['name']}' wurde aus data.json entfernt.")

    if delete_images:
        removed = 0
        for fn in target.get("gallery_files", []):
            for folder in (IMAGES_DIR, THUMBS_DIR):
                p = os.path.join(folder, fn)
                if os.path.isfile(p):
                    os.remove(p)
                    removed += 1
        print(f"✓ {removed} Bilddatei(en) gelöscht.")

    # build.py erzeugt nur neue/geänderte Seiten, löscht aber keine alten.
    # Die Werk-Seite des entfernten Bilds bliebe sonst als Karteileiche stehen.
    stale_page = os.path.join(REPO_ROOT, "werke", f"{target['slug']}.html")
    if os.path.isfile(stale_page):
        os.remove(stale_page)

    run_build()

    print("\nFertig! Nächster Schritt zum Veröffentlichen:")
    print("  cd ..")
    print(f'  git add -A && git commit -m "Werk entfernt: {target["name"]}" && git push')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("add", "remove", "list", "build"):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "add":
        cmd_add()
    elif cmd == "remove":
        cmd_remove()
    elif cmd == "build":
        run_build()


if __name__ == "__main__":
    main()
