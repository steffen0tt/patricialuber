#!/usr/bin/env python3
import json, os, html, re
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)  # Repo-Root (ein Ordner über "source")
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "assets", "images"), exist_ok=True)
os.makedirs(os.path.join(OUT, "assets", "css"), exist_ok=True)
os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
os.makedirs(os.path.join(OUT, "werke"), exist_ok=True)
os.makedirs(os.path.join(OUT, "en"), exist_ok=True)

data = json.load(open(os.path.join(BASE, "data.json"), encoding="utf-8"))
site = data["site"]
categories = data["categories"]
artworks = data["artworks"]
cat_by_slug = {c["slug"]: c for c in categories}

def person_ld_json():
    """JSON-LD (schema.org Person) fuer Startseite und Ueber-mich-Seite - staerkt die Namens-/Markensuche."""
    ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site.get("full_name", site["artist"]),
        "alternateName": "Patricia Luber",
        "jobTitle": "Malerin",
        "description": "Malerin aus Köln – Öl- und Acrylbilder sowie Aquarelle.",
        "url": site.get("url", ""),
        "image": f"{site.get('url', '')}assets/images/portrait.jpg",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": site.get("city", "Köln"),
            "addressCountry": "DE",
        },
    }
    return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'

def esc(s):
    return html.escape(s, quote=True)

def img_filename(slug):
    return f"{slug}.jpg"

def thumb_filename(filename):
    return f"thumbs/{filename}"

def cls_active(active, key):
    return ' class="active"' if active == key else ''

NAV_LABELS = {
    "de": {
        "home": "Start", "oel_acryl": "Öl &amp; Acryl", "aquarell": "Aquarell",
        "ueber_mich": "Über mich", "kontakt": "Kontakt",
        "menu": "Menü öffnen", "sub_toggle": "Unterkategorien anzeigen",
    },
    "en": {
        "home": "Home", "oel_acryl": "Oil &amp; Acrylic", "aquarell": "Watercolor",
        "ueber_mich": "About Me", "kontakt": "Contact",
        "menu": "Open menu", "sub_toggle": "Show subcategories",
    },
}

FOOTER_LABELS = {
    "de": {"impressum": "Impressum", "datenschutz": "Datenschutz"},
    "en": {"impressum": "Imprint (German)", "datenschutz": "Privacy Policy (German)"},
}

# Seiten, die es auch auf Englisch gibt (Slug ist in beiden Sprachen identisch, nur unter /en/ gespiegelt)
TRANSLATED_PAGES = {"index", "oel-acryl", "abstrakt", "landschaften", "menschen", "pflanzen-stillleben", "tiermotive", "aquarell", "ueber-mich", "kontakt"}

def lang_switch(active, prefix, lang):
    """Ziel-URL + Label fuer den DE/EN-Umschalter in der Navigation."""
    other = "en" if lang == "de" else "de"
    if active in TRANSLATED_PAGES:
        target = f"{active}.html"
        href = f"{prefix}en/{target}" if lang == "de" else f"{prefix}{target}"
    else:
        href = f"{prefix}en/index.html" if lang == "de" else f"{prefix}index.html"
    return href, other.upper()

def nav_html(active="", prefix="", lang="de", nav_prefix=None):
    if nav_prefix is None:
        nav_prefix = prefix
    L = NAV_LABELS[lang]
    sub_items = []
    for c in categories:
        if c["parent"] == "oel-acryl":
            title = c.get("title_en", c["title"]) if lang == "en" else c["title"]
            sub_items.append('          <li><a href="{p}{s}.html"{cls}>{t}</a></li>'.format(
                p=nav_prefix, s=c["slug"], cls=cls_active(active, c["slug"]), t=esc(title)))
    sub = "\n".join(sub_items)
    switch_href, switch_label = lang_switch(active, prefix, lang)
    switch_hreflang = "en" if lang == "de" else "de"
    return '''  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{np}index.html">Patricia Luber</a>
      <button class="nav-toggle" id="navToggle" aria-label="{menu}" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <nav class="site-nav" id="siteNav">
        <ul>
          <li><a href="{np}index.html"{idx}>{home}</a></li>
          <li class="has-sub">
            <a href="{np}oel-acryl.html"{oa}>{oel_acryl}</a>
            <button type="button" class="sub-toggle" aria-expanded="false" aria-label="{sub_toggle}"><span class="rot" aria-hidden="true">&#9662;</span></button>
            <ul class="sub-nav">
{sub}
            </ul>
          </li>
          <li><a href="{np}aquarell.html"{aq}>{aquarell}</a></li>
          <li><a href="{np}ueber-mich.html"{um}>{ueber_mich}</a></li>
          <li><a href="{np}kontakt.html"{kt}>{kontakt}</a></li>
          <li class="lang-switch"><a href="{sh}" hreflang="{shl}">{sl}</a></li>
        </ul>
      </nav>
    </div>
  </header>
'''.format(
        np=nav_prefix,
        idx=cls_active(active, "index"),
        oa=cls_active(active, "oel-acryl"),
        sub=sub,
        aq=cls_active(active, "aquarell"),
        um=cls_active(active, "ueber-mich"),
        kt=cls_active(active, "kontakt"),
        home=L["home"], oel_acryl=L["oel_acryl"], aquarell=L["aquarell"],
        ueber_mich=L["ueber_mich"], kontakt=L["kontakt"],
        menu=L["menu"], sub_toggle=L["sub_toggle"],
        sh=switch_href, shl=switch_hreflang, sl=switch_label,
    )

def footer_html(prefix="", lang="de"):
    L = FOOTER_LABELS[lang]
    return f'''  <footer class="site-footer">
    <div class="footer-inner">
      <p class="footer-legal"><a href="{prefix}impressum.html">{L["impressum"]}</a> &middot; <a href="{prefix}datenschutz.html">{L["datenschutz"]}</a></p>
    </div>
  </footer>
'''

def page_shell(title, description, active, body, prefix="", extra_head="", path="", image="assets/images/hero.jpg", lang="de", nav_prefix=None, alt_langs=None):
    site_url = site.get("url", "")
    canonical = f"{site_url}{path}" if site_url else ""
    og_image = f"{site_url}{image}" if site_url else f"{prefix}{image}"
    canonical_tag = f'<link rel="canonical" href="{canonical}">\n' if canonical else ""
    og_url_tag = f'<meta property="og:url" content="{canonical}">\n' if canonical else ""
    og_locale = "en_US" if lang == "en" else "de_DE"
    hreflang_tags = ""
    if alt_langs and site_url:
        for hl, p in alt_langs.items():
            hreflang_tags += f'<link rel="alternate" hreflang="{hl}" href="{esc(site_url + p)}">\n'
        default_path = alt_langs.get("de", path)
        hreflang_tags += f'<link rel="alternate" hreflang="x-default" href="{esc(site_url + default_path)}">\n'
    skip_text = "Skip to content" if lang == "en" else "Zum Inhalt springen"
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{canonical_tag}{hreflang_tags}<link rel="icon" href="{prefix}assets/icons/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="16x16" href="{prefix}assets/icons/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/icons/favicon-32x32.png">
<link rel="apple-touch-icon" href="{prefix}assets/icons/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site['artist'])}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
{og_url_tag}<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{og_image}">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
{extra_head}</head>
<body>
<a class="skip-link" href="#main-content">{skip_text}</a>
{nav_html(active, prefix, lang=lang, nav_prefix=nav_prefix)}
  <main id="main-content">
{body}
  </main>
{footer_html(prefix, lang=lang)}
  <script src="{prefix}assets/js/main.js"></script>
</body>
</html>
'''

def price_sort_value(a):
    price = a.get("price")
    if price == "VERKAUFT":
        return 1
    return 0

def gallery_grid(items, lead="", prefix="", lang="de"):
    cards = []
    for i, a in enumerate(items):
        ribbon = ''  # "Neu"-Badge deaktiviert (Kundenwunsch)
        cards.append(f'''        <a class="art-card" href="{prefix}werke/{a["slug"]}.html" data-name="{esc(a["name"])}" data-price="{price_sort_value(a)}" data-order="{i}">
          {ribbon}
          <img src="{prefix}assets/images/{thumb_filename(img_filename(a["slug"]))}" alt="{esc(a["name"])}" loading="lazy">
          <span class="art-card-caption">{esc(a["name"])}</span>
        </a>''')
    sort_label = "Sort by" if lang == "en" else "Sortieren nach"
    toolbar = f'''      <div class="gallery-toolbar">
        <select id="sortSelect" class="sort-select" aria-label="{sort_label}">
          <option value="">{sort_label}</option>
          <option value="name-asc">Name (A-Z)</option>
          <option value="name-desc">Name (Z-A)</option>
        </select>
      </div>
'''
    return f'''{lead}{toolbar}
      <div class="art-grid" id="artGrid">
{chr(10).join(cards)}
      </div>
'''

def product_slider(items, lead="", prefix="", lang="de"):
    cards = []
    for a in items:
        cards.append(f'''          <a class="slider-card" href="{prefix}werke/{a["slug"]}.html">
            <img src="{prefix}assets/images/{thumb_filename(img_filename(a["slug"]))}" alt="{esc(a["name"])}" loading="lazy">
            <span class="art-card-caption">{esc(a["name"])}</span>
          </a>''')
    prev_label = "Previous painting" if lang == "en" else "Vorheriges Produkt"
    next_label = "Next painting" if lang == "en" else "Nächstes Produkt"
    return f'''{lead}
      <div class="slider-wrap">
        <button class="slider-arrow slider-prev" type="button" aria-label="{prev_label}">&#8249;</button>
        <div class="slider" id="productSlider">
{chr(10).join(cards)}
        </div>
        <button class="slider-arrow slider-next" type="button" aria-label="{next_label}">&#8250;</button>
      </div>
      <div class="slider-dots" id="sliderDots"></div>
'''

# ---------- index.html ----------
home_items = [a for a in artworks if "home" in a["cats"]]
hero_lead = f'''    <section class="home-band home-band--muted">
      <div class="home-band-inner hero">
        <div class="hero-text">
          <h1>Malerei von {esc(site["artist"].split("-")[0])}</h1>
          <p>Bienvenue! Schön, dass Sie den Weg hierher gefunden haben. Dies ist eine Auswahl von meinen Bildern, die ich zum Verkauf oder auch für Ausstellungen zur Verfügung stelle. Alle Bilder sind Unikate und können auch gerne vor Ort bei mir in Köln besichtigt werden.</p>
          <a class="btn" href="oel-acryl.html">Jetzt entdecken</a>
        </div>
        <div class="hero-image">
          <img src="assets/images/hero.jpg" alt="Gemälde von Patricia Luber" loading="eager">
        </div>
      </div>
    </section>
    <section class="home-band home-band--light">
      <div class="home-band-inner">
        <h2>Alle Produkte</h2>
'''
home_gallery = product_slider(home_items, hero_lead) + '''      </div>
    </section>
    <section class="home-band home-band--muted">
      <div class="home-band-inner about-teaser">
        <h2>Über mich</h2>
        <p>Geboren in Deutschland, aufgewachsen in Frankreich, nach Abschluss meines Studiums der Sprachen und der Betriebswirtschaft zurück in Deutschland, zuerst in München, dann in Köln.</p>
        <p>Kunst und Malerei begleiten mich seit meiner Jugend. Anfänglich interessierte mich insbesondere die Seiden- und Aquarellmalerei. Später wandte ich mich dem Zeichnen mit Bleistift und Kohle und der Ölmalerei zu, später dem Acryl.</p>
        <div class="btn-row">
          <a class="btn" href="ueber-mich.html">Mehr erfahren</a>
        </div>
      </div>
    </section>
'''
INDEX_ALT_LANGS = {"de": "index.html", "en": "en/index.html"}

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
    page_shell("Patricia Luber – Malerei aus Köln | Öl, Acryl & Aquarell",
               "Malerei von Patricia Luber aus Köln – Öl- und Acrylbilder sowie Aquarelle, Originale zum Verkauf oder für Ausstellungen.",
               "index", home_gallery, path="index.html", image="assets/images/hero.jpg",
               extra_head=person_ld_json(), alt_langs=INDEX_ALT_LANGS)
)

# ---------- en/index.html (englische Startseite) ----------
en_hero_lead = f'''    <section class="home-band home-band--muted">
      <div class="home-band-inner hero">
        <div class="hero-text">
          <h1>Paintings by {esc(site["artist"].split("-")[0])}</h1>
          <p>Bienvenue! Welcome, and thank you for finding your way here. This is a selection of my paintings, which I offer for sale or for exhibitions. All works are one-of-a-kind originals and can also be viewed in person at my studio in Cologne.</p>
          <a class="btn" href="oel-acryl.html">Discover now</a>
        </div>
        <div class="hero-image">
          <img src="../assets/images/hero.jpg" alt="Painting by Patricia Luber" loading="eager">
        </div>
      </div>
    </section>
    <section class="home-band home-band--light">
      <div class="home-band-inner">
        <h2>All Paintings</h2>
'''
en_home_gallery = product_slider(home_items, en_hero_lead, prefix="../", lang="en") + '''      </div>
    </section>
    <section class="home-band home-band--muted">
      <div class="home-band-inner about-teaser">
        <h2>About Me</h2>
        <p>Born in Germany, raised in France, I returned to Germany after completing my studies in languages and business administration – first to Munich, then to Cologne.</p>
        <p>Art and painting have been part of my life since my youth. I was initially drawn especially to silk painting and watercolors. Later I turned to drawing with pencil and charcoal, and to oil painting, and eventually to acrylics.</p>
        <div class="btn-row">
          <a class="btn" href="ueber-mich.html">Learn more</a>
        </div>
      </div>
    </section>
'''
open(os.path.join(OUT, "en", "index.html"), "w", encoding="utf-8").write(
    page_shell("Patricia Luber – Paintings from Cologne | Oil, Acrylic & Watercolor",
               "Paintings by Patricia Luber from Cologne, Germany – original oil and acrylic works as well as watercolors, available for sale or exhibition.",
               "index", en_home_gallery, prefix="../", nav_prefix="", path="en/index.html",
               image="assets/images/hero.jpg", lang="en", extra_head=person_ld_json(),
               alt_langs=INDEX_ALT_LANGS)
)

# ---------- oel-acryl.html (alle Werke aller Öl & Acryl-Unterkategorien direkt) ----------
sub_cats = [c for c in categories if c["parent"] == "oel-acryl"]
sub_cat_slugs = {c["slug"] for c in sub_cats}
oel_acryl_items = []
_seen_slugs = set()
for a in artworks:
    if a["slug"] not in _seen_slugs and any(cat in sub_cat_slugs for cat in a["cats"]):
        oel_acryl_items.append(a)
        _seen_slugs.add(a["slug"])

lead = "    <section class=\"section\">\n      <h1>Öl &amp; Acryl</h1>\n"
body = gallery_grid(oel_acryl_items, lead) + "    </section>\n"

OEL_ACRYL_ALT_LANGS = {"de": "oel-acryl.html", "en": "en/oel-acryl.html"}

open(os.path.join(OUT, "oel-acryl.html"), "w", encoding="utf-8").write(
    page_shell("Öl & Acryl | Patricia Luber",
               "Öl- und Acrylbilder von Patricia Luber: Abstrakt, Landschaften, Menschen, Stillleben und Tiermotive – alle Werke auf einen Blick.",
               "oel-acryl", body, path="oel-acryl.html", image="assets/images/hero.jpg",
               alt_langs=OEL_ACRYL_ALT_LANGS)
)

# ---------- en/oel-acryl.html ----------
en_lead = "    <section class=\"section\">\n      <h1>Oil &amp; Acrylic</h1>\n"
en_body = gallery_grid(oel_acryl_items, en_lead, prefix="../", lang="en") + "    </section>\n"

open(os.path.join(OUT, "en", "oel-acryl.html"), "w", encoding="utf-8").write(
    page_shell("Oil & Acrylic | Patricia Luber",
               "Oil and acrylic paintings by Patricia Luber: Abstract, Landscapes, People, Still Life and Animal Motifs – all works in one gallery.",
               "oel-acryl", en_body, prefix="../", nav_prefix="", path="en/oel-acryl.html",
               image="assets/images/hero.jpg", lang="en", alt_langs=OEL_ACRYL_ALT_LANGS)
)

# ---------- category pages ----------
all_gallery_cats = sub_cats + [c for c in categories if c["slug"] == "aquarell"]
for c in all_gallery_cats:
    items = [a for a in artworks if c["slug"] in a["cats"]]
    lead = f"    <section class=\"section\">\n      <h1>{esc(c['title'])}</h1>\n"
    gallery = gallery_grid(items, lead) + "    </section>\n"
    cat_image = f"assets/images/{img_filename(items[0]['slug'])}" if items else "assets/images/hero.jpg"
    cat_alt_langs = {"de": f"{c['slug']}.html", "en": f"en/{c['slug']}.html"}
    open(os.path.join(OUT, f"{c['slug']}.html"), "w", encoding="utf-8").write(
        page_shell(f"{c['title']} | Patricia Luber",
                   f"{c['title']} – Gemälde von Patricia Luber.",
                   c["slug"], gallery, path=f"{c['slug']}.html", image=cat_image,
                   alt_langs=cat_alt_langs)
    )

    # englische Version derselben Kategorie
    title_en = c.get("title_en", c["title"])
    en_lead = f"    <section class=\"section\">\n      <h1>{esc(title_en)}</h1>\n"
    en_gallery = gallery_grid(items, en_lead, prefix="../", lang="en") + "    </section>\n"
    open(os.path.join(OUT, "en", f"{c['slug']}.html"), "w", encoding="utf-8").write(
        page_shell(f"{title_en} | Patricia Luber",
                   f"{title_en} – paintings by Patricia Luber.",
                   c["slug"], en_gallery, prefix="../", nav_prefix="", path=f"en/{c['slug']}.html",
                   image=cat_image, lang="en", alt_langs=cat_alt_langs)
    )

# ---------- ueber-mich.html ----------
about_body = '''    <section class="section about-page">
      <h1>Über mich</h1>
      <div class="about-layout">
        <img class="portrait" src="assets/images/portrait.jpg" alt="Patricia Luber-Laporte">
        <div class="about-text">
          <p><strong>Patricia Luber-Laporte</strong></p>
          <p>Geboren in Deutschland, aufgewachsen in Frankreich, nach Abschluss meines Studiums der Sprachen und der Betriebswirtschaft zurück in Deutschland, zuerst in München, dann in Köln.</p>
          <p>Kunst und Malerei begleiten mich seit meiner Jugend. Anfänglich interessierte mich insbesondere die Seiden- und Aquarellmalerei. Später wandte ich mich dem Zeichnen mit Bleistift und Kohle und der Ölmalerei zu, später dem Acryl.</p>
          <p>Hier in Köln besuche ich regelmäßig Malkurse, unter anderem bei Bettina Mauel, Imke Pitro-Riedel, Kaikaoss, Lucian.</p>
          <p>Zuletzt habe ich ein 3 jähriges Intensivstudium an der freien Kunstakademie arte fact Bonn absolviert.</p>
          <p>Meine derzeit am häufigsten angewandten Techniken sind Aquarell und Öl. Meine bevorzugte Motive sind Landschaften, Blumen, Stillleben und Menschen. Inspirieren lasse ich mich auf Fahrten in mein zweites Heimatland Frankreich, aber auch auf Reisen insbesondere in Asien. Gerne male ich auch Bilder für Kinder.</p>
          <a class="btn" href="kontakt.html">Jetzt kontaktieren</a>
        </div>
      </div>
    </section>
'''
UEBER_MICH_ALT_LANGS = {"de": "ueber-mich.html", "en": "en/ueber-mich.html"}

open(os.path.join(OUT, "ueber-mich.html"), "w", encoding="utf-8").write(
    page_shell("Über mich | Patricia Luber",
               "Patricia Luber-Laporte – Künstlerin in Köln. Über meinen Weg zur Malerei.",
               "ueber-mich", about_body, path="ueber-mich.html", image="assets/images/portrait.jpg",
               extra_head=person_ld_json(), alt_langs=UEBER_MICH_ALT_LANGS)
)

# ---------- en/ueber-mich.html ----------
en_about_body = '''    <section class="section about-page">
      <h1>About Me</h1>
      <div class="about-layout">
        <img class="portrait" src="../assets/images/portrait.jpg" alt="Patricia Luber-Laporte">
        <div class="about-text">
          <p><strong>Patricia Luber-Laporte</strong></p>
          <p>Born in Germany, raised in France, I returned to Germany after completing my studies in languages and business administration – first to Munich, then to Cologne.</p>
          <p>Art and painting have been part of my life since my youth. I was initially drawn especially to silk painting and watercolors. Later I turned to drawing with pencil and charcoal, and to oil painting, and eventually to acrylics.</p>
          <p>Here in Cologne, I regularly attend painting courses, among others with Bettina Mauel, Imke Pitro-Riedel, Kaikaoss, and Lucian.</p>
          <p>I recently completed a three-year intensive program at the independent art academy arte fact in Bonn.</p>
          <p>My most frequently used techniques at the moment are watercolor and oil. My favorite subjects are landscapes, flowers, still lifes, and people. I draw inspiration from trips to my second home country, France, as well as travels, particularly in Asia. I also enjoy painting pictures for children.</p>
          <a class="btn" href="kontakt.html">Get in touch</a>
        </div>
      </div>
    </section>
'''
open(os.path.join(OUT, "en", "ueber-mich.html"), "w", encoding="utf-8").write(
    page_shell("About Me | Patricia Luber",
               "Patricia Luber-Laporte – artist based in Cologne, Germany. About my path to painting.",
               "ueber-mich", en_about_body, prefix="../", nav_prefix="", path="en/ueber-mich.html",
               image="assets/images/portrait.jpg", lang="en", extra_head=person_ld_json(),
               alt_langs=UEBER_MICH_ALT_LANGS)
)

# ---------- kontakt.html ----------
contact_body = f'''    <section class="section contact-page">
      <h1>Kontakt</h1>
      <p>Wenn Sie an meiner Arbeit oder konkret an einem meiner Bilder interessiert sind, schreiben Sie mir doch gerne eine kurze Nachricht. Ich melde mich so schnell wie möglich bei Ihnen und freue mich über jeden Austausch zur Malerei.</p>
      <p>Viele Grüße et à bientôt,<br>Patricia Luber</p>
      <form id="contactForm" class="contact-form">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Name" required>

        <label for="email">Email</label>
        <input type="email" id="email" name="email" placeholder="Email" required>

        <label for="subject">Betreff</label>
        <input type="text" id="subject" name="subject" placeholder="Betreff">

        <label for="message">Nachricht</label>
        <textarea id="message" name="message" placeholder="Nachricht" rows="6" required></textarea>

        <button type="submit" class="btn">Senden</button>
        <p class="form-hint">Beim Klick auf &bdquo;Senden&ldquo; öffnet sich Ihr E-Mail-Programm mit einer vorausgefüllten Nachricht an {esc(site["artist"])}.</p>
        <p class="form-status" id="formStatus" role="status" hidden>Ihr E-Mail-Programm sollte sich jetzt mit der vorausgefüllten Nachricht öffnen. Falls sich nichts tut, schreiben Sie gerne direkt an <a href="mailto:{esc(site["email"])}">{esc(site["email"])}</a>.</p>
      </form>
    </section>
'''
KONTAKT_ALT_LANGS = {"de": "kontakt.html", "en": "en/kontakt.html"}

open(os.path.join(OUT, "kontakt.html"), "w", encoding="utf-8").write(
    page_shell("Kontakt | Patricia Luber",
               "Kontaktieren Sie Patricia Luber bei Interesse an ihren Bildern.",
               "kontakt", contact_body, path="kontakt.html", image="assets/images/hero.jpg",
               alt_langs=KONTAKT_ALT_LANGS)
)

# ---------- en/kontakt.html ----------
en_contact_body = f'''    <section class="section contact-page">
      <h1>Contact</h1>
      <p>If you're interested in my work, or in one of my paintings in particular, feel free to send me a short message. I'll get back to you as soon as possible, and I always enjoy an exchange about painting.</p>
      <p>Warm regards et à bientôt,<br>Patricia Luber</p>
      <form id="contactForm" class="contact-form">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Name" required>

        <label for="email">Email</label>
        <input type="email" id="email" name="email" placeholder="Email" required>

        <label for="subject">Subject</label>
        <input type="text" id="subject" name="subject" placeholder="Subject">

        <label for="message">Message</label>
        <textarea id="message" name="message" placeholder="Message" rows="6" required></textarea>

        <button type="submit" class="btn">Send</button>
        <p class="form-hint">Clicking &ldquo;Send&rdquo; will open your email program with a pre-filled message to {esc(site["artist"])}.</p>
        <p class="form-status" id="formStatus" role="status" hidden>Your email program should now open with the pre-filled message. If nothing happens, feel free to write directly to <a href="mailto:{esc(site["email"])}">{esc(site["email"])}</a>.</p>
      </form>
    </section>
'''
open(os.path.join(OUT, "en", "kontakt.html"), "w", encoding="utf-8").write(
    page_shell("Contact | Patricia Luber",
               "Get in touch with Patricia Luber if you're interested in her paintings.",
               "kontakt", en_contact_body, prefix="../", nav_prefix="", path="en/kontakt.html",
               image="assets/images/hero.jpg", lang="en", alt_langs=KONTAKT_ALT_LANGS)
)

# ---------- impressum.html ----------
full_name = esc(site.get("full_name", site["artist"]))
addr_street = esc(site.get("address_street", ""))
addr_zip = esc(site.get("address_zip", ""))
addr_city = esc(site.get("address_city", ""))
phone = esc(site.get("phone", ""))
email_addr = esc(site["email"])

impressum_body = f'''    <section class="section legal-page">
      <h1>Impressum</h1>
      <p><strong>Angaben gemäß § 5 DDG (Digitale-Dienste-Gesetz)</strong></p>
      <p>
        {full_name}<br>
        {addr_street}<br>
        {addr_zip} {addr_city}<br>
        Deutschland
      </p>
      <p><strong>Kontakt</strong></p>
      <p>
        Telefon: {phone}<br>
        E-Mail: <a href="mailto:{email_addr}">{email_addr}</a>
      </p>
      <p><strong>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</strong></p>
      <p>{full_name}, Anschrift wie oben.</p>
      <p><strong>Hinweis</strong></p>
      <p>Diese Website wird als private bzw. nebenberufliche Präsentation eigener Kunstwerke betrieben, ohne Gewerbeanmeldung.</p>
      <p><strong>Haftung für Inhalte</strong></p>
      <p>Als Diensteanbieterin bin ich gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Eine Verpflichtung zur Überwachung übermittelter oder gespeicherter fremder Informationen besteht nach §§ 8 bis 10 DDG nicht.</p>
      <p><strong>Haftung für Links</strong></p>
      <p>Diese Website enthält keine Links zu externen Websites Dritter, auf deren Inhalte kein Einfluss besteht.</p>
      <p><strong>Urheberrecht</strong></p>
      <p>Die auf dieser Website gezeigten Bilder und Texte sind urheberrechtlich geschützt. Eine Vervielfältigung, Bearbeitung oder Verwertung außerhalb der Grenzen des Urheberrechts bedarf der vorherigen schriftlichen Zustimmung.</p>
    </section>
'''
open(os.path.join(OUT, "impressum.html"), "w", encoding="utf-8").write(
    page_shell("Impressum | Patricia Luber",
               "Impressum und Anbieterkennzeichnung von Patricia Luber-Laporte.",
               "impressum", impressum_body, path="impressum.html", image="assets/images/hero.jpg")
)

# ---------- datenschutz.html ----------
datenschutz_body = f'''    <section class="section legal-page">
      <h1>Datenschutzerklärung</h1>

      <h2>1. Verantwortliche Stelle</h2>
      <p>
        {full_name}<br>
        {addr_street}<br>
        {addr_zip} {addr_city}<br>
        E-Mail: <a href="mailto:{email_addr}">{email_addr}</a>
      </p>

      <h2>2. Hosting</h2>
      <p>Diese Website wird über GitHub Pages gehostet (Anbieter: GitHub, Inc., 88 Colpitts Ave, San Francisco, CA 94107, USA, bzw. deren europäische Gesellschaft). Beim Aufruf der Seite erfasst GitHub Pages automatisch technische Zugriffsdaten (sogenannte Server-Logfiles), zum Beispiel IP-Adresse, Datum und Uhrzeit des Zugriffs, verwendeter Browser und aufgerufene Seite. Diese Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einem sicheren und funktionsfähigen Betrieb der Website). Weitere Informationen: <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub Privacy Statement</a>.</p>

      <h2>3. Keine Cookies, kein Tracking</h2>
      <p>Diese Website selbst setzt keine Cookies und verwendet keine Analyse- oder Trackingdienste (z. B. keine Web-Analyse, kein Social-Media-Plugin).</p>

      <h2>4. Schriftarten</h2>
      <p>Die verwendeten Schriftarten (Fraunces und Work Sans) werden lokal von dieser Website ausgeliefert. Es findet keine Verbindung zu externen Schriftart-Servern (z. B. Google Fonts) statt, sodass beim Betrachten der Seite keine Daten an Dritte zu diesem Zweck übertragen werden.</p>

      <h2>5. Kontaktformular</h2>
      <p>Das Kontaktformular auf der Seite &bdquo;Kontakt&ldquo; übermittelt die eingegebenen Daten nicht an einen Server dieser Website. Beim Absenden öffnet sich stattdessen das auf Ihrem Gerät eingerichtete E-Mail-Programm mit einer vorausgefüllten Nachricht an {email_addr}. Die eingegebenen Daten (Name, E-Mail-Adresse, Nachricht) werden erst durch das tatsächliche Versenden dieser E-Mail über Ihren eigenen E-Mail-Anbieter verarbeitet und übermittelt (Art. 6 Abs. 1 lit. b bzw. f DSGVO – Bearbeitung Ihrer Anfrage). Die so erhaltenen Nachrichten werden ausschließlich zur Bearbeitung Ihrer Anfrage genutzt und nicht an Dritte weitergegeben.</p>

      <h2>6. Ihre Rechte</h2>
      <p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung oder Einschränkung der Verarbeitung Ihrer personenbezogenen Daten, ein Widerspruchsrecht gegen die Verarbeitung sowie das Recht auf Datenübertragbarkeit (Art. 15 bis 20 DSGVO). Wenden Sie sich hierzu gerne an die oben genannte Kontaktadresse.</p>
      <p>Zudem steht Ihnen ein Beschwerderecht bei einer Datenschutz-Aufsichtsbehörde zu, zum Beispiel bei der Landesbeauftragten für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW).</p>

      <h2>7. Aktualität dieser Datenschutzerklärung</h2>
      <p>Diese Datenschutzerklärung kann bei Bedarf angepasst werden, etwa bei Änderungen an der Website oder den rechtlichen Vorgaben.</p>
    </section>
'''
open(os.path.join(OUT, "datenschutz.html"), "w", encoding="utf-8").write(
    page_shell("Datenschutzerklärung | Patricia Luber",
               "Datenschutzerklärung der Website von Patricia Luber-Laporte.",
               "datenschutz", datenschutz_body, path="datenschutz.html", image="assets/images/hero.jpg")
)

# ---------- 404.html ----------
notfound_body = '''    <section class="section notfound-page">
      <h1>Seite nicht gefunden</h1>
      <p>Diese Seite gibt es leider nicht (mehr) – vielleicht wurde sie verschoben oder der Link ist fehlerhaft.</p>
      <p>Hier geht es weiter:</p>
      <div class="btn-row">
        <a class="btn" href="index.html">Zur Startseite</a>
        <a class="btn btn-outline" href="oel-acryl.html">Öl &amp; Acryl</a>
        <a class="btn btn-outline" href="aquarell.html">Aquarell</a>
      </div>
    </section>
'''
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
    page_shell("Seite nicht gefunden | Patricia Luber",
               "Diese Seite existiert nicht. Zur Startseite von Patricia Luber – Malerei aus Köln.",
               "", notfound_body, path="404.html", image="assets/images/hero.jpg")
)

# ---------- individual product pages (werke/<slug>.html) ----------
def breadcrumb(a):
    non_home = [c for c in a["cats"] if c != "home"]
    primary = non_home[0] if non_home else None
    parts = ['<a href="../index.html">Start</a>']
    if primary and primary in cat_by_slug:
        cat = cat_by_slug[primary]
        if cat["parent"] == "oel-acryl":
            parts.append('<a href="../oel-acryl.html">Öl &amp; Acryl</a>')
        parts.append(f'<a href="../{cat["slug"]}.html">{esc(cat["title"])}</a>')
    parts.append(f'<span>{esc(a["name"])}</span>')
    return '<nav class="breadcrumb">' + ' <span class="sep">/</span> '.join(parts) + '</nav>'

def tag_list(a):
    non_home = [c for c in a["cats"] if c != "home"]
    tags = []
    for cs in non_home:
        cat = cat_by_slug.get(cs)
        if cat:
            tags.append(f'<a class="tag" href="../{cat["slug"]}.html">{esc(cat["title"])}</a>')
    return '<div class="tag-list">' + ''.join(tags) + '</div>' if tags else ''

def product_meta(a):
    lines = a.get("medium_size") or []
    return ''.join(f'<span class="meta-line">{esc(line)}</span>' for line in lines)

def product_price(a):
    price = a.get("price")
    if not price:
        return ''
    cls = "product-price sold" if price == "VERKAUFT" else "product-price"
    return f'<p class="{cls}">{esc(price)}</p>'

def product_gallery(a):
    files = a.get("gallery_files") or [img_filename(a["slug"])]
    main = files[0]
    main_html = f'''<div class="gallery-main">
            <img id="gallery-main-img" src="../assets/images/{main}" alt="{esc(a["name"])}">
          </div>'''
    if len(files) <= 1:
        return main_html
    thumbs = []
    for i, f in enumerate(files):
        active = " active" if i == 0 else ""
        thumb_alt = esc(f'{a["name"]} – Ansicht {i + 1}')
        thumbs.append(
            f'<button type="button" class="thumb{active}" data-src="../assets/images/{f}" '
            f'aria-label="Ansicht {i + 1} von {esc(a["name"])} anzeigen">'
            f'<img src="../assets/images/{thumb_filename(f)}" alt="{thumb_alt}" loading="lazy"></button>'
        )
    thumbs_html = f'''<div class="gallery-thumbs">
            {''.join(thumbs)}
          </div>'''
    return main_html + '\n          ' + thumbs_html

product_count = 0
for a in artworks:
    subject = f'Interesse an "{a["name"]}"'
    subject_qs = quote(subject, safe='')
    body = f'''    <section class="section product-page">
      {breadcrumb(a)}
      <div class="product-layout">
        <div class="product-image">
          {product_gallery(a)}
        </div>
        <div class="product-info">
          <h1>{esc(a["name"])}</h1>
          {tag_list(a)}
          <p class="product-meta">{product_meta(a)}</p>
          {product_price(a)}
          <a class="btn" href="../kontakt.html?subject={subject_qs}">Jetzt kontaktieren</a>
          <p class="back-link"><a href="javascript:history.back()">&larr; Zurück zur Übersicht</a></p>
        </div>
      </div>
    </section>
'''
    open(os.path.join(OUT, "werke", f"{a['slug']}.html"), "w", encoding="utf-8").write(
        page_shell(f'{a["name"]} | Patricia Luber',
                   f'{a["name"]} – Originalgemälde von {site["artist"]}.',
                   "", body, prefix="../",
                   path=f"werke/{a['slug']}.html", image=f"assets/images/{img_filename(a['slug'])}")
    )
    product_count += 1

# ---------- sitemap.xml & robots.txt ----------
sitemap_paths = ["index.html", "oel-acryl.html"]
sitemap_paths += [f"{c['slug']}.html" for c in all_gallery_cats]
sitemap_paths += ["ueber-mich.html", "kontakt.html", "impressum.html", "datenschutz.html"]
sitemap_paths += [f"werke/{a['slug']}.html" for a in artworks]
sitemap_paths += ["en/index.html", "en/oel-acryl.html"]
sitemap_paths += [f"en/{c['slug']}.html" for c in all_gallery_cats]
sitemap_paths += ["en/ueber-mich.html", "en/kontakt.html"]

site_url = site.get("url", "")
if site_url:
    urls_xml = "\n".join(
        f"  <url><loc>{esc(site_url + p)}</loc></url>" for p in sitemap_paths
    )
    sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>
'''
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap_xml)

    robots_txt = f'''User-agent: *
Allow: /

Sitemap: {site_url}sitemap.xml
'''
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(robots_txt)

print("HTML pages written:", len(os.listdir(OUT)), "+", product_count, "Werk-Seiten")
