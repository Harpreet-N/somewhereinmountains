# -*- coding: utf-8 -*-
"""Builds the static website from data.py into ../site (or the folder in DIST).

    python3 build.py

Every page, card, filter, table and form option is generated from data.py,
so trip facts only ever need to be changed in one place.
"""
import json, os, re, shutil, html as H
from urllib.parse import quote, urlencode
from data import *

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "..", "site")
ICONS = os.path.join(ROOT, "icons")
WA = f"https://wa.me/{WA_NUMBER}"
e = lambda s: H.escape(str(s), quote=True)
TRIP = {t["id"]: t for t in TRIPS}
TREKS = [t for t in TRIPS if t["type"] == "trek"]
PLAN = "plan-your-trip.html"
WIDTHS = (480, 800, 1200, 1800)
_LCP = {}  # hero image of the page being built, for the preload hint


# ---------------------------------------------------------------- helpers
def icon(name, cls="ic"):
    svg = open(os.path.join(ICONS, name + ".svg")).read()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    svg = re.sub(r"<svg[^>]*>", lambda m: re.sub(r'\s(width|height|class|stroke-width)="[^"]*"', "", m.group(0)), svg, count=1)
    return svg.replace("<svg", f'<svg class="{cls}" aria-hidden="true" focusable="false"', 1)

TRI = '<svg class="tri" viewBox="0 0 10 9" aria-hidden="true"><path d="M5 0 10 9H0z"/></svg>'
MARK = '<svg class="mark" viewBox="0 0 16 14" aria-hidden="true"><path d="M8 0 16 14H0z"/></svg>'
EXT = '<span class="sr"> (opens in new tab)</span>'

def summit(t):
    """Signature detail: a surveyor's summit marker with the trip's highest point."""
    if t["pl"] != "Max altitude": return ""
    return f'<span class="summit">{TRI}<span><span class="sr">Highest point </span>{e(t["peak"])}</span></span>'

def size(name):
    from PIL import Image
    return Image.open(os.path.join(DIST, "img", name + ".jpg")).size

def variants(name):
    """WebP copies at a few widths (made once, then reused)."""
    from PIL import Image
    w0, h0 = size(name)
    out_dir = os.path.join(DIST, "img", "w"); os.makedirs(out_dir, exist_ok=True)
    ws = [w for w in WIDTHS if w < w0] + [w0]
    for w in ws:
        p = os.path.join(out_dir, f"{name}-{w}.webp")
        if not os.path.exists(p):
            im = Image.open(os.path.join(DIST, "img", name + ".jpg")).convert("RGB")
            if w != w0: im = im.resize((w, round(h0 * w / w0)), Image.LANCZOS)
            im.save(p, "WEBP", quality=72, method=6)
    return ws

def srcset(name):
    return ", ".join(f"img/w/{name}-{w}.webp {w}w" for w in variants(name))

def pic(name, alt, sizes="100vw", lazy=True, cls=""):
    """<picture> with WebP sizes and the original JPEG as fallback. Width/height stop layout shift."""
    w, h = size(name)
    a = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture{c}><source type="image/webp" srcset="{srcset(name)}" sizes="{sizes}">'
            f'<img src="img/{name}.jpg" width="{w}" height="{h}" alt="{e(alt)}"{a}></picture>')

def wa(text):
    return f"{WA}?text={quote(text)}"

def plan_link(trip_id=None):
    return PLAN + (f"?trek={trip_id}" if trip_id else "")

def stars(n, label=None):
    s = "".join(f'<span class="{"on" if i < n else "off"}">{icon("star", "ic-star")}</span>' for i in range(5))
    return f'<div class="stars" role="img" aria-label="{e(label or f"{n} out of 5 stars")}">{s}</div>'

def month(v):
    y, m = v.split("-"); return MONTHS[int(m) - 1][:3] + " " + y

def url(path):
    return DOMAIN.rstrip("/") + "/" + path

def ratio(name):
    w, h = size(name); return f"{w / h:.4f}"

def season_table(kinds, label):
    head = '<div role="row"><span role="columnheader">Activity</span>' + "".join(f'<span role="columnheader" aria-label="{m}">{m[0]}</span>' for m in MONTHS) + "</div>"
    rows = ""
    for k in kinds:
        name, lv = SEASONS[k]
        rows += f'<div role="row"><span role="rowheader">{name}</span>' + "".join(
            f'<span role="cell" class="lv{l}" aria-label="{MONTHS[i]}: {LV[l][1]}" title="{MONTHS[i]}: {LV[l][1]}"><i class="mk mk{l}" aria-hidden="true"></i></span>' for i, l in enumerate(lv)) + "</div>"
    legend = "".join(f'<li><span class="lv{n}" aria-hidden="true"><i class="mk mk{n}"></i></span>{lab}</li>' for n, lab in [(3, "Best"), (2, "Good"), (1, "Possible"), (0, "Off-season")])
    # plain-text summary of the same chart for anyone who can't read the grid
    def months_at(lv, lvl): return [MONTHS[i] for i, x in enumerate(lv) if x == lvl]
    summary = "".join(f'<li><b>{SEASONS[k][0]}:</b> best in {", ".join(m[:3] for m in months_at(SEASONS[k][1], 3))}; '
                      f'off-season in {", ".join(m[:3] for m in months_at(SEASONS[k][1], 0)) or "none"}</li>' for k in kinds)
    return (f'<div class="scroll-x" tabindex="0" role="region" aria-label="Season table, scrollable" data-reveal><div class="season" role="table" aria-label="{e(label)}">{head}{rows}</div></div>'
            f'<ul class="legend" aria-label="Legend">{legend}</ul>'
            f'<details class="season-text"><summary>Show as text</summary><ul>{summary}</ul></details>')

def carousel(items, label, cls=""):
    n = len(items)
    slides = "".join(
        f'<li class="car-slide" style="--ar:{ratio(a)}" aria-roledescription="slide" aria-label="{i + 1} of {n}">'
        f'<button class="car-open" type="button" data-full="img/{a}.jpg" data-cap="{e(c)}" aria-label="Open photo {i + 1} of {n}: {e(c)}">'
        f'<span class="car-img">{pic(a, "", "(min-width: 1024px) 40vw, 80vw")}</span><span class="car-zoom" aria-hidden="true">{icon("expand")}</span></button>'
        f'<p class="car-cap" aria-hidden="true">{e(c)}</p></li>' for i, (a, c) in enumerate(items))
    return f'''<div class="car {cls}" data-car data-reveal>
  <div class="car-track" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{e(label)}, swipe or use the arrow buttons"><ul class="car-list">{slides}</ul></div>
  <div class="wrap car-ui">
    <span class="car-count" aria-hidden="true"><b>01</b> / {n:02d}</span><span class="car-bar" aria-hidden="true"><i></i></span>
    <button class="car-btn" type="button" data-dir="-1" aria-label="Previous photos">{icon("chevron-left")}</button><button class="car-btn" type="button" data-dir="1" aria-label="Next photos">{icon("chevron-right")}</button>
  </div>
</div>'''


# ---------------------------------------------------------------- scroll landscape: layered Himalayan ridges
import random as _rnd

def _ridge(seed, peaks, base, amp, W=1600, H=320):
    """A jagged ridge line: a few big peaks, each with sharp sub-summits, filled to the bottom."""
    r = _rnd.Random(seed)
    xs = sorted(r.uniform(.06, .94) * W for _ in range(peaks))
    pts = []
    for x in range(0, W + 1, 16):
        h = 0.0
        for px in xs:
            d = abs(x - px) / (W / (peaks * 1.6))
            h = max(h, max(0.0, 1 - d) ** 1.35)
        h = h * amp + r.uniform(-.045, .045) * amp * (0.4 + h)
        pts.append((x, H - base - max(0.0, h)))
    d = "M0 " + str(H) + " " + " ".join(f"L{x} {y:.1f}" for x, y in pts) + f" L{W} {H} Z"
    return f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" focusable="false"><path d="{d}"/></svg>'

RIDGE_SETS = {
    "a": [(11, 5, 120, 190), (23, 6, 60, 150), (37, 4, 0, 120)],
    "b": [(41, 6, 110, 200), (53, 5, 55, 140), (67, 7, 0, 110)],
    "c": [(71, 4, 120, 180), (83, 6, 60, 145), (97, 5, 0, 115)],
}

def ridges(kind, top, bottom, set_="a"):
    """Three ridge layers and clouds that move at different speeds on scroll (decorative)."""
    l = RIDGE_SETS[set_]
    layers = [f'<div class="rg rg{i}" data-depth="{d}">{_ridge(*l[i])}</div>' for i, d in enumerate((.55, .3, 0))]
    clouds = '<span class="cl cl1" data-drift="-1"></span><span class="cl cl2" data-drift="1"></span><span class="cl cl3" data-drift="-.6"></span>'
    return (f'<div class="ridges ridges-{kind}" aria-hidden="true" style="--sky:{top};--land:{bottom}">'
            f'{layers[0]}{layers[1]}{clouds}{layers[2]}</div>')


# ---------------------------------------------------------------- page shell
NAV = [("tours.html", "Explore Treks", "tours"), ("guide.html", "Meet Your Guide", "guide"),
       ("reviews.html", "Reviews", "reviews"), ("faq.html", "FAQ", "faq")]

def page(fname, title, desc, body, active="", jsonld=None, hero=True, og_img="og-image", qbar=""):
    canon = url("" if fname == "index.html" else fname)
    pre = ""
    if _LCP.get("img"):
        pre = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(_LCP["img"])}" imagesizes="100vw" fetchpriority="high">'
    seo = [f'<title>{e(title)}</title>', f'<meta name="description" content="{e(desc)}">',
           '<meta name="robots" content="index,follow,max-image-preview:large">',
           f'<link rel="canonical" href="{canon}">',
           f'<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}">',
           f'<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">',
           f'<meta property="og:url" content="{canon}"><meta property="og:image" content="{url("img/" + og_img + ".jpg")}">',
           '<meta property="og:locale" content="en_GB"><meta name="twitter:card" content="summary_large_image">',
           '<meta name="theme-color" content="#f3f6f9">',
           '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Cpath d=%22M16 4 30 28H2z%22 fill=%22%232b5c88%22/%3E%3C/svg%3E">']
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    def nl(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a class="l" href="{href}"{cur}>{label}</a>'
    links = "".join(nl(*n) for n in NAV)
    plan_cur = ' aria-current="page"' if active == "plan" else ""
    _LCP.clear()
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{chr(10).join(seo)}
<link rel="preload" href="fonts/instrument-sans-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="site.css">
{ld}
</head>
<body class="{'has-hero' if hero else 'no-hero'}{' has-qbar' if qbar else ''}">
<a class="skip" href="#main">Skip to content</a>
<header class="nav" id="nav">
  <div class="wrap nav-row">
    <a class="brand" href="index.html">{MARK}{SITE_NAME}<span class="sr"> home</span></a>
    <nav class="links" aria-label="Main">{links}
      <a class="l l-wa" href="{wa("Namaste Jenish! I have a question.")}" target="_blank" rel="noopener" data-track="nav_whatsapp_clicked">{icon("message-circle")}WhatsApp{EXT}</a>
      <a class="btn btn-primary" href="{PLAN}"{plan_cur} data-track="nav_plan_clicked">Plan Your Trip</a>
    </nav>
    <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="sheet">Menu</button>
  </div>
  <nav class="sheet" id="sheet" aria-label="Main, mobile">{links}
    <a class="btn btn-primary" href="{PLAN}" data-track="nav_plan_clicked">Plan Your Trip</a>
    <a class="btn btn-secondary" href="{wa("Namaste Jenish! I have a question.")}" target="_blank" rel="noopener">{icon("message-circle")}Message on WhatsApp{EXT}</a>
  </nav>
</header>
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
{qbar}
<script src="site.js" defer></script>
</body>
</html>
'''

def footer():
    treks = "".join(f'<a href="{t["slug"]}.html">{e(t["short"])}</a>' for t in TREKS)
    return ridges("night", "var(--bg)", "var(--n-bg)", "c") + f'''<footer class="site">
  <div class="wrap foot">
    <div class="foot-brand">
      <a class="brand" href="index.html">{MARK}{SITE_NAME}</a>
      <p>Private Himalayan treks, Trishuli rafting and Chitwan safaris with Jenish Maharjan, a local trekking guide from Kathmandu.</p>
      <a class="btn btn-light btn-sm" href="{PLAN}">Plan Your Trip</a>
    </div>
    <nav aria-label="Treks"><span class="k">Treks</span>{treks}<a href="tours.html">All treks and tours</a></nav>
    <nav aria-label="More"><span class="k">More</span><a href="guide.html">Meet Your Guide</a><a href="trishuli-river-rafting-day-trip.html">Trishuli rafting</a><a href="trishuli-rafting-chitwan-safari.html">Chitwan safari</a><a href="reviews.html">Reviews</a><a href="faq.html">FAQ</a></nav>
    <nav aria-label="Legal"><span class="k">Legal</span><a href="legal.html#imprint">Legal notice</a><a href="legal.html#privacy">Privacy policy</a><a href="legal.html#terms">Booking terms</a></nav>
    <address><span class="k">Contact</span>
      <a href="{WA}" target="_blank" rel="noopener">{icon("message-circle")}<span>WhatsApp <span class="nw">{WA_DISPLAY}</span></span>{EXT}</a>
      <a href="mailto:{EMAIL}">{icon("mail")}<span class="brk">{EMAIL}</span></a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">{icon("instagram")}{INSTAGRAM_HANDLE}<span class="sr"> on Instagram (opens in new tab)</span></a>
      <span class="addr">{icon("map-pin")}Thamel, Kathmandu and Lakeside, Pokhara</span></address>
  </div>
  <div class="wrap legal"><span>© 2026 {SITE_NAME}</span><span>An inquiry is not a booking. No payment is taken on this website.</span></div>
  <a class="bubble" href="{wa("Namaste Jenish! I'd like to ask about a trip.")}" target="_blank" rel="noopener" aria-label="Chat with Jenish on WhatsApp (opens in new tab)">{icon("message-circle")}<span>Chat on WhatsApp</span></a>
</footer>'''

def photo_hero(img_name, alt, h1, sub="", top="", cta="", cls="hero-sub"):
    _LCP["img"] = img_name
    return f'''<section class="hero {cls}" aria-labelledby="h1">
  <div class="hero-bg">{pic(img_name, alt, "100vw", lazy=False)}</div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="hero-mist" aria-hidden="true"><span class="cl cl1" data-drift="-1"></span><span class="cl cl2" data-drift="1.2"></span></div>
  {ridges("hero", "transparent", "var(--bg)", "b")}
  <div class="wrap hero-copy">
    {top}
    <h1 id="h1" style="--i:1">{h1}</h1>
    {sub}{cta}
  </div>
</section>'''

def plain_head(h1, sub, top="", extra=""):
    return f'''<section class="page-head" aria-labelledby="h1"><div class="wrap">{top}<h1 class="h1" id="h1">{h1}</h1>{f'<p class="sub">{sub}</p>' if sub else ""}{extra}</div></section>'''

def head(title, lede, hid, extra="", num=""):
    n = f'<p class="sec-num" aria-hidden="true">{num}</p>' if num else ""
    return f'<div class="head" data-reveal>{n}<h2 class="h2" id="{hid}">{title}</h2>{f"<p class=lede>{lede}</p>" if lede else ""}{extra}</div>'

def crumbs(items):
    """items: [(href or None, label)] — the last one is the current page."""
    parts = []
    for i, (href, label) in enumerate(items):
        if href: parts.append(f'<a href="{href}">{e(label)}</a>')
        else: parts.append(f'<span aria-current="page">{e(label)}</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb" style="--i:0">{icon("chevron-right").join(parts)}</nav>'

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": label, **({"item": url(href if href != "index.html" else "")} if href else {})}
        for i, (href, label) in enumerate(items)]}

def alt_fact(t):
    return ("Highest point", summit(t)) if t["pl"] == "Max altitude" else (t["pl"], e(t["peak"]))

def diff_badge(t):
    """Difficulty as text plus a bar count, so it never relies on colour alone."""
    n = {"easy": 1, "moderate": 2, "challenging": 3}[t["diff"]]
    bars = "".join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(3))
    label = t["level"] if t["type"] == "trek" else DIFF[t["diff"]]
    return f'<span class="diff diff-{t["diff"]}"><span class="bars" aria-hidden="true">{bars}</span>{e(label)}</span>'

def trip_card(t, i=0, heading="h3"):
    k, v = alt_fact(t)
    return f'''<li class="tc" data-type="{t["type"]}" data-days="{t["days"]}" data-diff="{t["diff"]}" data-area="{t["area"]}" data-first="{str(t["first"]).lower()}" data-reveal style="--i:{i % 3}">
  <article class="tcard" aria-labelledby="t-{t["id"]}">
    <a class="tcard-media" href="{t["slug"]}.html" tabindex="-1" aria-hidden="true" data-track="trek_card_clicked" data-trek="{t["id"]}">{pic(t["img"], "", "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw")}</a>
    <div class="tcard-body">
      <p class="kind">{icon(TYPE_ICON[t["type"]])}{TYPE[t["type"]]} · {e(AREAS[t["area"]])}</p>
      <{heading} id="t-{t["id"]}"><a href="{t["slug"]}.html" data-track="trek_card_clicked" data-trek="{t["id"]}">{e(t["title"])}</a></{heading}>
      <p class="d">{e(t["desc"])}</p>
      <dl class="tfacts">
        <div><dt>Duration</dt><dd>{t["duration"]}</dd></div>
        <div><dt>Difficulty</dt><dd>{diff_badge(t)}</dd></div>
        <div><dt>{k}</dt><dd>{v}</dd></div>
        <div class="wide"><dt>Good for</dt><dd>{e(t["for"])}</dd></div>
      </dl>
      <div class="tcard-foot"><span class="price">Price: personalised quote</span><a class="link-arrow" href="{t["slug"]}.html" aria-hidden="true" tabindex="-1">Explore Trek{icon("arrow-right")}</a></div>
    </div>
  </article>
</li>'''

def faq_list(items, prefix="f", first_open=True, level=3):
    PLUS = icon("plus", "ic plus") + icon("minus", "ic minus")
    out = []
    for i, it in enumerate(items):
        q, a = it[0], it[1]
        o = first_open and i == 0
        out.append(f'<div class="faq-item"><h{level}><button type="button" id="{prefix}b{i}" aria-expanded="{str(o).lower()}" aria-controls="{prefix}p{i}"><span>{e(q)}</span><span class="ico">{PLUS}</span></button></h{level}>'
                   f'<div class="faq-panel{" open" if o else ""}" id="{prefix}p{i}" role="region" aria-labelledby="{prefix}b{i}"><div><p>{e(a)}</p></div></div></div>')
    return f'<div class="faq-list" data-acc>{"".join(out)}</div>'

def final_cta(h="Your next adventure starts with a conversation",
              p="Not sure which trek is right for you? Tell me about your dream trip and we'll plan your Himalayan adventure together.",
              trip=None, primary="Plan My Adventure"):
    msg = f"Namaste Jenish! I'm interested in the {trip['title']}." if trip else "Namaste Jenish! I'd like to plan a trip."
    return f'''<section class="cta" aria-labelledby="cta-h">
  <div class="cta-box" data-reveal>
    <div><h2 id="cta-h">{h}</h2><p>{p}</p><p class="cta-note">{icon("info")}An inquiry is not a booking. No payment is needed to ask.</p></div>
    <div class="acts"><a class="btn btn-light" href="{plan_link(trip["id"] if trip else None)}" data-track="cta_plan_clicked">{primary}</a><a class="btn btn-secondary" href="{wa(msg)}" target="_blank" rel="noopener" data-track="cta_whatsapp_clicked">{icon("message-circle")}Chat on WhatsApp{EXT}</a></div>
  </div>
</section>'''

def review_card(r):
    t = TRIP.get(r["trip"]); trip = f'<a href="{t["slug"]}.html">{e(t["short"])}</a>' if t else e(r["trip"])
    return (f'<article class="rev-card" data-reveal>{stars(r["stars"], "Rated %d out of 5 by the traveller" % r["stars"])}<blockquote><p>{e(r["text"])}</p></blockquote>'
            f'<footer><b>{e(r["name"])}</b>, {e(r["country"])}<br>{trip}, {month(r["when"])}</footer></article>')

def review_cards(items=None):
    items = REVIEWS if items is None else items
    if not items:
        return '<p class="rev-empty">No published reviews yet. Trekked with Jenish? <a href="reviews.html#write">Write the first one</a>.</p>'
    avg = sum(r["stars"] for r in items) / len(items)
    out = f'<div class="rev-summary"><b>{avg:.1f}</b><div>{stars(round(avg))}<span>{len(items)} reviews</span></div></div>' if len(items) >= 3 else ''
    return out + "".join(review_card(r) for r in items)


# ---------------------------------------------------------------- JSON-LD (only facts shown on the site)
PERSON = {"@type": "Person", "@id": url("guide.html") + "#jenish", "name": GUIDE["name"], "jobTitle": "Trekking guide",
          "homeLocation": {"@type": "Place", "name": "Kathmandu, Nepal"}, "sameAs": [INSTAGRAM], "url": url("guide.html"),
          "image": url("img/" + GUIDE["img"] + ".jpg")}
BUSINESS = {"@context": "https://schema.org", "@type": "TravelAgency", "@id": url("") + "#business", "name": SITE_NAME,
            "description": "Private trekking, Trishuli River rafting and Chitwan safari trips in Nepal with Jenish Maharjan, a local trekking guide from Kathmandu.",
            "url": url(""), "image": url("img/og-image.jpg"), "telephone": "+" + WA_NUMBER, "email": EMAIL, "sameAs": [INSTAGRAM],
            "areaServed": {"@type": "Country", "name": "Nepal"},
            "address": {"@type": "PostalAddress", "addressLocality": "Kathmandu", "addressCountry": "NP"},
            "founder": {"@id": PERSON["@id"]},
            "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "TouristTrip", "name": t["title"], "url": url(t["slug"] + ".html")}} for t in TRIPS]}
WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": url("") + "#website", "name": SITE_NAME, "url": url(""), "publisher": {"@id": BUSINESS["@id"]}, "inLanguage": "en"}

def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": it[0], "acceptedAnswer": {"@type": "Answer", "text": it[1]}} for it in items]}


# ---------------------------------------------------------------- HOME
def finder_html():
    def group(name, legend, opts):
        o = "".join(f'<label class="opt"><input type="radio" name="{name}" value="{v}"{" checked" if i == 0 else ""}><span>{l}</span></label>' for i, (v, l) in enumerate(opts))
        return f'<fieldset class="opts"><legend>{legend}</legend><div class="opt-row">{o}</div></fieldset>'
    return f'''<form class="finder" id="finder" aria-describedby="finder-note">
  {group("days", "How many days do you have for walking?", [("any", "Not sure yet"), ("5", "Up to 5"), ("8", "About a week"), ("12", "9 to 12"), ("99", "13 or more")])}
  {group("exp", "Have you trekked before?", [("first", "It's my first Himalayan trek"), ("some", "A few multi-day hikes"), ("lots", "Yes, including high altitude")])}
  {group("want", "What matters most?", [("any", "I'm not sure yet"), ("iconic", "An iconic mountain view"), ("quiet", "Quieter, less crowded trails"), ("culture", "Villages and culture")])}
  <div class="finder-acts"><button class="btn btn-primary" type="submit">Show my treks</button><p class="hint" id="finder-note">A starting point based on days, experience and interests. It isn't a fitness or medical check.</p></div>
</form>
<div class="finder-out" id="finderOut" tabindex="-1" aria-live="polite"></div>
<noscript><p><a href="tours.html">Compare all treks</a> or <a href="{PLAN}">ask Jenish to help you choose</a>.</p></noscript>'''

def why_html(groups, cls=""):
    out = ""
    for i, g in enumerate(groups):
        items = "".join(f'<li><b>{a}</b><span class="tag {"tag-inc" if s == "inc" else "tag-ask"}">{"Included with every trek" if s == "inc" else "Optional, ask when planning"}</span><p>{b}</p></li>' for a, b, s in g["items"])
        out += (f'<article class="serv-card" data-reveal style="--i:{i % 2}"><div class="photo">{pic(g["img"], g["alt"], "(min-width: 1024px) 50vw, 100vw")}</div>'
                f'<div class="serv-body"><h3>{icon(g["icon"])}{g["title"]}</h3><ul class="serv-items">{items}</ul></div></article>')
    return f'<div class="serv {cls}">{out}</div>'

def build_home():
    hero = photo_hero("hero-home", "Manaslu glowing gold at sunrise on the Manaslu Circuit, Nepal",
        "Himalayan treks with a local guide from Kathmandu",
        '<p class="sub" style="--i:2">Explore the Himalayas with Jenish, your personal trekking guide. Private treks to Annapurna, Langtang, Everest and Manaslu, planned around your pace, your days and what you want to see.</p>',
        '<p class="byline" style="--i:0">Private treks · Local guide · Nepal</p>',
        f'<div class="hero-cta" style="--i:3"><a class="btn btn-light" href="{PLAN}" data-track="hero_plan_trip_clicked">Plan My Trek</a><a class="btn btn-glass" href="tours.html" data-track="explore_treks_clicked">Explore Trekking Routes</a></div>'
        '<p class="hero-micro" style="--i:4">Personalised itineraries. No obligation to book.</p>',
        "hero-home")
    trust = "".join(f'<li data-reveal style="--i:{i}">{icon(ic)}<span><b>{a}</b><small>{b}</small></span></li>' for i, (ic, a, b) in enumerate(TRUST))
    featured = "".join(trip_card(TRIP[i], n) for n, i in enumerate(FEATURED))
    steps = "".join(f'<li data-reveal style="--i:{i}"><span class="step-n" aria-hidden="true">{i + 1:02d}</span><h3>{a}</h3><p>{b}</p></li>' for i, (a, b) in enumerate(STEPS))
    more = [t for t in TRIPS if t["type"] != "trek"]
    more_cards = "".join(f'''<a class="more-card" href="{t["slug"]}.html" data-reveal style="--i:{i}">{pic(t["img"], "", "(min-width: 1024px) 33vw, 100vw")}<span class="more-body"><span class="kind">{icon(TYPE_ICON[t["type"]])}{t["duration"]}</span><b>{e(t["title"])}</b><span>{e(t["desc"])}</span></span></a>''' for i, t in enumerate(more))
    home_faq = [f for f in FAQS if f[2]]
    finder_data = json.dumps([{"id": t["id"], "title": t["title"], "slug": t["slug"], "days": t["days"], "diff": t["diff"], "tags": t["tags"],
                               "for": t["for"], "dur": t["duration"], "level": t["level"], "peak": t["peak"]} for t in TREKS], ensure_ascii=False)
    body = hero + f'''
<section class="trust" aria-label="Why travel with Jenish"><ul class="wrap trust-list">{trust}</ul></section>

<section class="wrap sec" id="treks" aria-labelledby="treks-h">
  {head("Popular trekking adventures", "Four routes that show the range: a short first trek, a week in the valleys, a classic and a big one for experienced trekkers.", "treks-h", f'<a class="link-arrow" href="tours.html" data-track="explore_treks_clicked">View All Treks{icon("arrow-right")}</a>')}
  <ul class="tgrid tgrid-4">{featured}</ul>
</section>

<section class="tint" id="finder-sec" aria-labelledby="finder-h">
  <div class="wrap sec finder-wrap">
    <div class="finder-intro" data-reveal>
      <h2 class="h2" id="finder-h">Find your perfect trek</h2>
      <p class="lede">Not sure where to start? Answer three questions and see which of Jenish's treks fit.</p>
      <p class="finder-alt">Prefer to talk it through? <a href="{plan_link("custom")}" data-track="finder_ask_clicked">Ask Jenish to help you choose</a></p>
    </div>
    <div data-reveal>{finder_html()}</div>
  </div>
  <script type="application/json" id="finderData">{finder_data}</script>
</section>

<section class="wrap sec about" id="guide" aria-labelledby="about-h">
  <div class="photo" data-reveal>{pic(GUIDE["img"], GUIDE["alt"], "(min-width: 860px) 40vw, 100vw")}</div>
  <div class="about-txt">
    <h2 class="h2" id="about-h" data-reveal>Meet the person behind your adventure</h2>
    <p data-reveal style="--i:1">I'm Jenish Maharjan, a freelance trekking guide based in Kathmandu. For as long as I can remember, my life has been tied to the mountains.</p>
    <p class="quote" data-reveal style="--i:2">Trekking isn't just about reaching the highest pass or ticking a destination off a map. It's about the rhythm of the trail and the stories shared along the way.</p>
    <p data-reveal style="--i:3">I plan every trip myself, walk it with you, and help you meet the families and communities who call these mountains home.</p>
    <p data-reveal style="--i:4"><a class="btn btn-secondary" href="guide.html" data-track="guide_profile_clicked">Get to Know Your Guide</a></p>
  </div>
</section>

<section class="wrap sec-sm" id="how" aria-labelledby="how-h">
  {head("How it works", "From first message to the first morning on the trail, in four steps.", "how-h")}
  <ol class="steps">{steps}</ol>
  <p class="steps-cta" data-reveal><a class="btn btn-primary" href="{PLAN}" data-track="how_plan_clicked">Plan My Trek</a><span>Sending an inquiry is free and doesn't commit you to anything.</span></p>
</section>

{ridges("dusk", "var(--bg)", "var(--n-bg)", "a")}
<section class="dark" id="why" aria-labelledby="why-h">
  <div class="wrap sec">
    {head("Why trek with me", "Your adventure at your pace, with care on the trail and the people of Nepal at its heart. Here's what I bring along, and what you can add.", "why-h")}
    {why_html(BEYOND)}
  </div>
</section>

{ridges("snow", "var(--n-bg)", "var(--bg)", "b")}
<section class="wrap sec" id="reviews" aria-labelledby="rev-h">
  {head("Traveller stories", "Real words from people who have trekked with Jenish, shared with their permission.", "rev-h", f'<a class="link-arrow" href="reviews.html">Read Traveller Stories{icon("arrow-right")}</a>')}
  <div class="rev-list rev-row">{review_cards()}</div>
</section>

<section class="tint" id="more" aria-labelledby="more-h">
  <div class="wrap sec">
    {head("More adventures", "Book them on their own, or add a day on the river or in the jungle to the end of your trek.", "more-h")}
    <div class="more">{more_cards}</div>
  </div>
</section>

<section class="wrap sec" id="seasons" aria-labelledby="seasons-h">
  {head("Best time to visit Nepal", "Autumn, October to November, usually brings the clearest views. Spring, March to May, is warmer, with rhododendrons in bloom. June to August is monsoon: rain, leeches and high rivers. Conditions differ by region and altitude, and no month is right for every trek, so we choose dates together.", "seasons-h")}
  {season_table(["trek", "raft", "safari"], "Best months for trekking, Trishuli rafting and Chitwan safari in Nepal")}
</section>

<section id="faq" class="rule" aria-labelledby="faq-h">
  <div class="wrap sec faq">
    <div class="faq-intro" data-reveal><h2 class="h2" id="faq-h">Questions travellers ask</h2><p class="lede"><a href="faq.html">See all {len(FAQS)} questions</a> or <a href="{wa("Namaste Jenish! I have a question.")}" target="_blank" rel="noopener">ask Jenish on WhatsApp{EXT}</a></p></div>
    <div data-reveal>{faq_list(home_faq, "h")}</div>
  </div>
</section>
{final_cta()}'''
    return page("index.html", "Local Trekking Guide in Nepal: Private Himalayan Treks with Jenish | Somewhere in Mountains",
                "Private, personalised Himalayan treks with Jenish Maharjan, a local trekking guide from Kathmandu: Annapurna, Langtang, Everest, Manaslu and Poon Hill, plus Trishuli rafting and Chitwan safaris.",
                body, "home", [BUSINESS, WEBSITE, {"@context": "https://schema.org", **PERSON}])


# ---------------------------------------------------------------- TOURS (overview, filters, comparison)
def build_tours():
    def sel(id_, label, opts):
        o = "".join(f'<option value="{v}">{l}</option>' for v, l in opts)
        return f'<div class="field"><label for="{id_}">{label}</label><select id="{id_}" data-filter="{id_[3:]}">{o}</select></div>'
    filters = (sel("ft-type", "Activity", [("all", "All activities"), ("trek", "Trekking"), ("raft", "Rafting"), ("safari", "Rafting and safari")]) +
               sel("ft-days", "Duration", [("all", "Any length"), ("0-5", "Up to 5 days"), ("6-8", "6 to 8 days"), ("9-12", "9 to 12 days"), ("13-99", "13 days or more")]) +
               sel("ft-diff", "Difficulty", [("all", "Any difficulty")] + list(DIFF.items())) +
               sel("ft-area", "Region", [("all", "All regions")] + list(AREAS.items())))
    cards = "".join(trip_card(t, i, "h2") for i, t in enumerate(TRIPS))
    rows = "".join(f'<tr><th scope="row"><a href="{t["slug"]}.html">{e(t["title"])}</a></th><td>{t["duration"]}</td><td>{diff_badge(t)}</td>'
                   f'<td>{e(t["peak"]) if t["pl"] == "Max altitude" else "–"}</td><td>{e(t["for"])}</td><td>On request</td></tr>' for t in TRIPS)
    body = photo_hero("hero-tours", "Machhapuchhre (Fishtail) rising above the clouds, Annapurna Sanctuary, Nepal", "Treks and tours in Nepal",
                      f'<p class="sub" style="--i:2">{len(TREKS)} private treks, two Trishuli rafting trips and a rafting and Chitwan safari combination. Every trip can be shortened, stretched or combined.</p>',
                      crumbs([("index.html", "Home"), (None, "Explore Treks")])) + f'''
<section class="filters" aria-labelledby="filter-h">
  <div class="wrap">
    <h2 class="sr" id="filter-h">Filter trips</h2>
    <form class="filter-row" id="filters" role="search" aria-label="Filter trips">
      {filters}
      <label class="check check-inline"><input type="checkbox" id="ft-first" data-filter="first" value="true"><span>Good for a first trek</span></label>
      <button class="btn btn-secondary btn-sm" type="reset" id="ftReset">{icon("refresh-ccw")}Reset filters</button>
    </form>
  </div>
</section>
<section class="wrap tours" aria-labelledby="list-h"><h2 class="sr" id="list-h">Trips</h2>
  <p class="count" id="count" role="status">Showing all {len(TRIPS)} trips</p>
  <ul class="tgrid" id="tourList">{cards}</ul>
  <div class="empty" id="empty" hidden>
    <h2 class="h3">No trips match all of those filters</h2>
    <p>Try fewer filters, or tell Jenish what you're looking for. Many trips can be shortened or combined.</p>
    <p class="acts"><button class="btn btn-secondary" type="button" id="emptyReset">Reset filters</button><a class="btn btn-primary" href="{plan_link("custom")}">Ask Jenish to help</a></p>
  </div>
</section>
<section class="wrap sec-sm" aria-labelledby="cmp-h">
  <h2 class="h3" id="cmp-h" data-reveal>Compare all trips</h2>
  <p class="lede cmp-note">Prices depend on your group size, season and route, so every trip is quoted personally.</p>
  <div class="scroll-x cmp-wrap" tabindex="0" role="region" aria-label="Comparison table, scrollable">
    <table class="cmp"><caption class="sr">Duration, difficulty, highest point, who it suits and price for every trip</caption>
      <thead><tr><th scope="col">Trip</th><th scope="col">Duration</th><th scope="col">Difficulty</th><th scope="col">Highest point</th><th scope="col">Good for</th><th scope="col">Price</th></tr></thead>
      <tbody>{rows}</tbody></table>
  </div>
</section>
{final_cta("Can't decide? Ask me", "Tell me your dates, fitness and what you'd love to see. I'll suggest one or two routes and explain why. Mardi Himal, Upper Mustang or a family week can be arranged too.", None, "Help Me Choose")}'''
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "Treks and tours in Nepal with Jenish Maharjan",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t["title"], "url": url(t["slug"] + ".html")} for i, t in enumerate(TRIPS)]},
          crumbs_ld([("index.html", "Home"), (None, "Explore Treks")])]
    return page("tours.html", "Nepal Treks and Tours with a Local Guide: Compare Routes | Somewhere in Mountains",
                "Compare private treks in Nepal with a local guide: Annapurna Base Camp, Manaslu Circuit, Langtang Valley, Everest Base Camp, Pikey Peak, Poon Hill, plus Trishuli rafting and Chitwan safari.",
                body, "tours", ld)


# ---------------------------------------------------------------- TRIP PAGES (one template for every trip)
PERMIT = {"annapurna": "An Annapurna Conservation Area (ACAP) permit", "manaslu": "A Manaslu restricted-area permit, plus conservation area permits",
          "langtang": "A Langtang National Park permit", "everest": "A Sagarmatha National Park and local area permit", "chitwan": ""}

def build_trip(t):
    msg = f"Namaste Jenish! I have a question about the {t['title']}."
    cr = [("index.html", "Home"), ("tours.html", "Explore Treks"), (None, t["short"])]
    ctas = (f'<div class="hero-cta" style="--i:3"><a class="btn btn-light" href="{plan_link(t["id"])}" data-track="trek_quote_clicked" data-trek="{t["id"]}">Request a Personalised Quote</a>'
            f'<a class="btn btn-glass" href="{wa(msg)}" target="_blank" rel="noopener" data-track="trek_question_clicked" data-trek="{t["id"]}">{icon("message-circle")}Ask Jenish a Question{EXT}</a></div>')
    top = photo_hero(t["img"], t["alt"], e(t["title"]), f'<p class="sub" style="--i:2">{e(t["desc"])}</p>', crumbs(cr), ctas)
    k, v = alt_fact(t)
    facts = [("Duration", t["duration"]), ("Difficulty", diff_badge(t)), (k, v), ("Group", "Private, your group only"), ("Best season", t["season"])]
    if t["start"]: facts.append(("Starts", e(t["start"])))
    if t["end"]: facts.append(("Ends", e(t["end"])))
    facts_html = '<dl class="facts">' + "".join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in facts) + "</dl>"
    hl = "".join(f'<li>{icon("check")}{e(h)}</li>' for h in t["hl"])
    is_trek = t["type"] == "trek"
    # itinerary: only the confirmed outline; the day-by-day plan comes with the quote
    if t["id"] == "combo":
        itin = f'<ol class="itin">{"".join(f"<li>{e(h)}</li>" for h in t["hl"])}</ol>'
    else:
        itin = ""
    itin_note = (f'<p>Jenish sends a day-by-day itinerary with your quote, with walking times, overnight stops and {"acclimatisation days" if is_trek else "timings"} '
                 f'planned around your pace. A typical {t["duration"].replace("days", "day").replace(" day", "-day")} trip is the starting point; it can be shortened, stretched or combined.</p>')
    incl = [f'{icon("check")}Jenish as your guide for the whole trip']
    if is_trek:
        if PERMIT[t["area"]]: incl.append(f'{icon("check")}{PERMIT[t["area"]]} and TIMS card, arranged through a registered agency')
        incl += [f'{icon("check")}{a}' for g in BEYOND for a, b, s in g["items"] if s == "inc"]
    incl += [f'{icon("check")}{e(h)}' for h in t["hl"] if re.search(r"included|arranged|meals|tents", h, re.I)]
    incl_html = "".join(f"<li>{x}</li>" for x in dict.fromkeys(incl))
    excl_html = (f'<li>{icon("x")}International flights and your Nepal visa</li><li>{icon("x")}Travel insurance (required)</li>'
                 f'<li>{icon("circle-help")}Everything else, such as meals, transport and porters, is listed in your written quote</li>')
    revs = [r for r in REVIEWS if r["trip"] == t["id"]]
    rev_html = (f'<section class="wrap sec-sm" aria-labelledby="tr-h"><h2 class="h3" id="tr-h" data-reveal>What travellers say</h2><div class="rev-list rev-row">{review_cards(revs)}</div></section>' if revs else "")
    tfaq = []
    if is_trek:
        tfaq.append((f"Can the {t['short']} be my first trek?", ("Yes, if you're active and walk regularly. " if t["first"] else "It's better as a second or third trek. ") + DIFF_TEXT[t["diff"]]))
        if PERMIT[t["area"]]: tfaq.append(("Which permits do I need?", f"{PERMIT[t['area']]}, plus a TIMS card. I arrange them through my partner agency before the trek."))
        tfaq.append(("Do I need travel insurance?", "Yes. It must cover trekking up to the highest altitude of this trip and helicopter evacuation."))
    else:
        tfaq.append(("Do I need experience?", "No. First-timers are welcome. Every trip starts with a safety briefing and paddle training, and licensed local operators run the river and safari activities."))
        tfaq.append(("Do I need travel insurance?", "Yes. It must cover white-water rafting and medical treatment."))
    related = [r for r in TRIPS if r["id"] != t["id"] and (r["type"] == t["type"] or (t["type"] != "trek" and r["type"] != "trek"))][:3]
    if len(related) < 3: related += [r for r in TRIPS if r["id"] != t["id"] and r not in related][:3 - len(related)]
    safety = ("<p>Height is gained slowly, with acclimatisation days where the route needs them. Jenish checks how you feel every morning and evening and adjusts the pace. "
              "If symptoms of altitude sickness appear, such as headache, nausea or unusual tiredness, we rest or go down. No plan removes the risk completely, so travel insurance with evacuation cover is required.</p>"
              if is_trek else
              "<p>Licensed local operators run the rafting and safari activities, with helmets and life jackets on the river. Their safety rules apply, and the river is only run when water levels allow.</p>")
    toc = [("ov", "Overview"), ("itin-h", "Itinerary"), ("fit-h", "Difficulty"), ("ss-h", "Season"), ("stay-h", "Stay and meals"), ("inc-h", "What's included"), ("prep-h", "Preparation and safety"), ("price-h", "Price"), ("tf-h", "Questions")]
    toc_html = '<nav class="toc" aria-label="On this page">' + "".join(f'<a href="#{a}">{b}</a>' for a, b in toc) + "</nav>"
    gal = (f'<section class="sec-sm" aria-labelledby="tg-h"><div class="wrap car-head" data-reveal><h2 class="h3" id="tg-h">Photos from the trail</h2>'
           f'<p class="car-hint">{icon("camera")}{len(t["gallery"])} photos, swipe or tap to enlarge</p></div>{carousel(t["gallery"], "Photos from the " + t["title"])}</section>') if t["gallery"] else ""
    book = f'''<aside class="book-card" aria-labelledby="bk-h">
      <h2 id="bk-h">Plan the {e(t["short"])}</h2>
      <p>A private trip with Jenish. Tell him your dates and group size and you get a day-by-day plan and a price.</p>
      <a class="btn btn-primary" href="{plan_link(t["id"])}" data-track="trek_quote_clicked" data-trek="{t["id"]}">Request a Personalised Quote</a>
      <a class="btn btn-secondary" href="{wa(msg)}" target="_blank" rel="noopener" data-track="trek_question_clicked" data-trek="{t["id"]}">{icon("message-circle")}Ask Jenish a Question{EXT}</a>
      <p class="small">An inquiry is not a booking. No payment is needed to ask.</p>
    </aside>'''
    body = top + f'''
<div class="wrap trip-layout">
  <div class="trip-main">
    {toc_html}
    <section aria-labelledby="ov" class="tsec">
      <h2 class="h3" id="ov">Trip overview</h2>
      {facts_html}
      <p class="tlead">{e(t["desc"])}</p>
      <h3 class="sub-h">Highlights</h3>
      <ul class="hl-list">{hl}</ul>
    </section>
    <section aria-labelledby="itin-h" class="tsec">
      <h2 class="h3" id="itin-h">Itinerary</h2>
      {itin}{itin_note}
    </section>
    <section aria-labelledby="fit-h" class="tsec">
      <h2 class="h3" id="fit-h">Difficulty and fitness</h2>
      <p>{diff_badge(t)}</p>
      <p>{DIFF_TEXT[t["diff"]]}</p>
      <p><b>Good for:</b> {e(t["for"])}.</p>
    </section>
    <section aria-labelledby="ss-h" class="tsec">
      <h2 class="h3" id="ss-h">Best season</h2>
      <p>Best: {t["season"]}. Weather in the mountains changes fast and every season has trade-offs, so we choose dates together.</p>
      {season_table([t["type"]], "Best months for " + t["title"])}
    </section>
    <section aria-labelledby="stay-h" class="tsec">
      <h2 class="h3" id="stay-h">Accommodation and meals</h2>
      <p>{e(t["stay"])}. {"Meals are cooked fresh in the teahouses: dal bhat, noodles, soups and plenty of tea." if t["stay"].startswith("Teahouses") else "Your quote lists exactly where you sleep and which meals are included."}</p>
    </section>
    <section aria-labelledby="inc-h" class="tsec">
      <h2 class="h3" id="inc-h">Included and not included</h2>
      <div class="incl2"><div><h3 class="sub-h">Included</h3><ul class="ilist">{incl_html}</ul></div>
      <div><h3 class="sub-h">Not included</h3><ul class="ilist">{excl_html}</ul></div></div>
    </section>
    <section aria-labelledby="prep-h" class="tsec">
      <h2 class="h3" id="prep-h">Preparation and safety</h2>
      <p>{"We meet the day before in Thamel or Lakeside to check your gear and rent anything missing at local prices." if is_trek else "Bring clothes that can get wet, sun cream and a change for the evening. Helmets, life jackets and paddle jackets are provided."}</p>
      {safety}
    </section>
    <section aria-labelledby="price-h" class="tsec">
      <h2 class="h3" id="price-h">Price</h2>
      <p><b>Request a personalised quote.</b> Every trip is priced for your group. The price depends on group size, number of days, season, permits and transport{", including the Lukla flights" if t["id"] == "ebc" else ""}. Your written quote lists what is and isn't included, and the <a href="legal.html#terms">booking terms</a> explain deposits and cancellations.</p>
      <p><a class="btn btn-primary" href="{plan_link(t["id"])}" data-track="trek_quote_clicked" data-trek="{t["id"]}">Request a Personalised Quote</a></p>
    </section>
    <section aria-labelledby="tf-h" class="tsec">
      <h2 class="h3" id="tf-h">Questions about this trip</h2>
      {faq_list(tfaq, "t", False)}
      <p><a href="faq.html">More questions and answers</a></p>
    </section>
  </div>
  {book}
</div>
{gal}
{rev_html}
<section class="wrap sec-sm" aria-labelledby="rel-h" style="padding-bottom:var(--sec)"><h2 class="h3" id="rel-h" data-reveal style="margin-bottom:24px">You might also like</h2><ul class="tgrid tgrid-3">{"".join(trip_card(r, i) for i, r in enumerate(related))}</ul></section>
{final_cta(f"Ready for the {t['short']}?", "Send your dates and group size, and Jenish replies with a day-by-day plan and a price for your group.", t, "Request a Personalised Quote")}'''
    qbar = f'''<aside class="qbar" id="qbar" aria-label="Quick actions for this trip"><a class="btn btn-primary" href="{plan_link(t["id"])}" data-track="trek_quote_clicked" data-trek="{t["id"]}">Request a Quote</a><a class="btn btn-secondary" href="{wa(msg)}" target="_blank" rel="noopener" aria-label="Ask Jenish a question on WhatsApp (opens in new tab)">{icon("message-circle")}Ask</a></aside>'''
    trip_ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": t["title"], "description": t["meta"], "url": url(t["slug"] + ".html"),
               "image": url("img/" + t["img"] + ".jpg"), "touristType": e(t["for"]),
               "provider": {"@type": "TravelAgency", "@id": BUSINESS["@id"], "name": SITE_NAME},
               "itinerary": {"@type": "Place", "name": AREAS[t["area"]] + ", Nepal"}}
    return page(t["slug"] + ".html", f'{t["title"]}: Private Trip with a Local Guide, {t["duration"]} | {SITE_NAME}', t["meta"], body, "tours",
                [trip_ld, crumbs_ld(cr), faq_ld(tfaq)], og_img=t["img"], qbar=qbar)


# ---------------------------------------------------------------- GUIDE
def build_guide():
    cr = [("index.html", "Home"), (None, "Meet Your Guide")]
    sus = [("Fair treatment for porters and crew", "Porters carry a fair load and get proper gear, beds and meals. Everyone on the team is paid properly, not left to depend on tips."),
           ("Local teahouses and family lodges", "We sleep and eat where the money stays in the village. No big chains, no middlemen."),
           ("Wildlife without exploitation", "In Chitwan we use jeeps, canoes and our own feet. No elephant rides, ever.")]
    sus_html = "".join(f'<li data-reveal style="--i:{i}"><h3>{a}</h3><p>{b}</p></li>' for i, (a, b) in enumerate(sus))
    picks = [("First time in Nepal", "poonhill", "Four days, big views, gentle on the legs."), ("One week, no flights", "langtang", "Straight from Kathmandu into Tamang villages and glaciers."),
             ("Away from the crowds", "manaslu", "A wild circuit around the eighth-highest mountain on Earth.")]
    picks_html = "".join(f'<li><span class="k">{a}</span><a href="{TRIP[i]["slug"]}.html">{e(TRIP[i]["title"])}</a><p>{b}</p></li>' for a, i, b in picks)
    body = f'''<section class="guide-head" aria-labelledby="h1">
  <div class="wrap guide-grid">
    <div class="guide-txt">
      {crumbs(cr)}
      <h1 class="h1" id="h1">Hi, I'm Jenish. Your local guide to Nepal</h1>
      <p class="sub">The Himalayas are more than a destination to me. They're home. I help travellers experience Nepal beyond the usual routes, from quiet mountain villages and stone teahouses to the big Himalayan views.</p>
      <p class="sub">Whether it's your first trek or your next big adventure, we'll plan a journey that matches your pace, your interests and your experience.</p>
      <div class="hero-cta"><a class="btn btn-primary" href="{PLAN}" data-track="guide_plan_clicked">Plan Your Trip with Jenish</a><a class="btn btn-secondary" href="{wa("Namaste Jenish! I'd like to ask you something before I decide.")}" target="_blank" rel="noopener">{icon("message-circle")}Ask Me Anything{EXT}</a></div>
      <ul class="about-meta"><li>{icon("map-pin")}Based in Kathmandu</li><li>{icon("users-round")}Meet-ups in Thamel and Lakeside</li><li><a href="{INSTAGRAM}" target="_blank" rel="noopener">{icon("instagram")}{INSTAGRAM_HANDLE}<span class="sr"> on Instagram (opens in new tab)</span></a></li></ul>
    </div>
    <div class="photo guide-photo">{pic(GUIDE["img"], GUIDE["alt"], "(min-width: 860px) 40vw, 100vw", lazy=False)}</div>
  </div>
</section>

<section class="wrap sec-sm story" aria-labelledby="story-h">
  <h2 class="h2" id="story-h" data-reveal>My story</h2>
  <div class="story-txt" data-reveal>
    <p>For as long as I can remember, my life has been deeply intertwined with the rugged peaks and quiet majesty of the mountains.</p>
    <p class="quote">Trekking isn't just about reaching the highest pass or ticking a destination off a map. It's about the rhythm of the trail and the stories shared along the way.</p>
    <p>As a freelance trekking guide in Nepal, I spend my days on these trails, completely immersed in the wild spirit of the Himalayas. My greatest passion is bridging worlds: helping travellers connect with untouched nature while building genuine, respectful exchanges with the communities who call these mountains home.</p>
    <p>Whether we're sharing a cup of butter tea in a remote stone teahouse or watching the sunrise paint the peaks gold, my goal is to make your journey feel less like a tour and more like a meaningful adventure.</p>
  </div>
</section>

<section class="wrap sec-sm" aria-labelledby="ph-h">
  <h2 class="h2" id="ph-h" data-reveal>How I guide</h2>
  <ul class="approach" data-reveal>
    <li>{icon("footprints")}<h3>Your pace, not a schedule</h3><p>Every trip is private. We walk at the speed that lets you enjoy it, with rest days where you need them.</p></li>
    <li>{icon("heart-pulse")}<h3>Care at altitude</h3><p>Morning and evening check-ins on how you feel, a slow ascent and the readiness to turn around when it's the right call.</p></li>
    <li>{icon("hand-heart")}<h3>Real encounters</h3><p>Teahouse kitchens, monasteries and conversations I translate, rather than facts recited from a book.</p></li>
    <li>{icon("camera")}<h3>Memories you can keep</h3><p>Photos, an edited highlight film and a trail log, so you can stay present on the trail.</p></li>
  </ul>
</section>

<section class="wrap sec-sm" aria-labelledby="pick-h">
  <h2 class="h2" id="pick-h" data-reveal>My recommendations</h2>
  <ul class="picks" data-reveal>{picks_html}</ul>
</section>

{ridges("dusk", "var(--bg)", "var(--n-bg)", "a")}
<section class="dark" aria-labelledby="why-h">
  <div class="wrap sec">
    {head("What I bring along", "Some of this comes with every trek. The rest you can add when we plan.", "why-h")}
    {why_html(BEYOND)}
  </div>
</section>
{ridges("snow", "var(--n-bg)", "var(--bg)", "b")}

<section class="wrap sec-sm" aria-labelledby="sus-h">
  <div class="sus">
    <div class="head" data-reveal style="margin:0"><h2 class="h2" id="sus-h">Leave the trail better than we found it</h2><p class="lede">Tourism feeds whole villages in Nepal. How we travel decides who benefits.</p></div>
    <ul class="sus-list">{sus_html}</ul>
  </div>
</section>

<section id="gallery" aria-labelledby="gallery-h">
  <div class="wrap sec-sm head-row" data-reveal>
    <div class="head" style="margin:0"><h2 class="h2" id="gallery-h">From the trail</h2><p class="lede">Photos from treks Jenish has guided.</p></div>
    <a class="btn btn-secondary btn-sm" href="{INSTAGRAM}" target="_blank" rel="noopener">{icon("instagram")}More on Instagram{EXT}</a>
  </div>
  {carousel([(g[0], g[1]) for g in GALLERY], "Photos from Jenish's treks", "car-home")}
</section>

<section class="wrap sec" aria-labelledby="gr-h">
  {head("What travellers say", "", "gr-h", f'<a class="link-arrow" href="reviews.html">All traveller stories{icon("arrow-right")}</a>')}
  <div class="rev-list rev-row">{review_cards()}</div>
</section>
{final_cta("Let's talk about your trip", "Ask me anything, from which trek suits you to what to pack. There's no obligation to book.", None, "Plan Your Trip")}'''
    ld = [{"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": PERSON, "url": url("guide.html")}, crumbs_ld(cr)]
    return page("guide.html", "Meet Jenish Maharjan, Your Local Trekking Guide in Nepal | Somewhere in Mountains",
                "Jenish Maharjan is a freelance trekking guide from Kathmandu. Read his story, how he guides private treks in Nepal, his route recommendations and traveller reviews.",
                body, "guide", ld, hero=False, og_img=GUIDE["img"])


# ---------------------------------------------------------------- REVIEWS
def build_reviews():
    cr = [("index.html", "Home"), (None, "Reviews")]
    rate = "".join(f'<input type="radio" name="stars" id="st{n}" value="{n}"><label for="st{n}" title="{n} star{"s" if n > 1 else ""}"><span class="sr">{n} star{"s" if n > 1 else ""}</span>{icon("star")}</label>' for n in range(1, 6))
    trip_opts = '<option value="">Choose your trip</option>' + "".join(f'<option>{e(t["title"])}</option>' for t in TRIPS) + "<option>Custom trip</option>"
    body = plain_head("Traveller stories", "Reviews from people who have trekked with Jenish. Each one is published with the traveller's permission, exactly as they wrote it.", crumbs(cr)) + f'''
<section class="wrap sec-sm rev" aria-labelledby="rl-h">
  <div><h2 class="h3" id="rl-h">Published reviews</h2><div class="rev-list">{review_cards()}</div></div>
  <div class="form-card" id="write">
    <form id="revForm" novalidate aria-labelledby="revf-h">
      <h2 id="revf-h" class="form-title">Write a review</h2>
      <p class="hint">Fields marked * are required.</p>
      <fieldset><legend>Your rating *</legend>
        <div class="rate" id="rate">{rate}</div>
        <p class="rate-hint" id="rateHint" aria-live="polite"></p><span class="err" id="e-rating" hidden>Please choose a rating.</span></fieldset>
      <div class="grid2">
        <div class="field"><label for="r-name">Your name *</label><input id="r-name" name="name" autocomplete="name" required aria-describedby="e-rname"><span class="err" id="e-rname" hidden>Please enter your name.</span></div>
        <div class="field"><label for="r-country">Country (optional)</label><input id="r-country" name="country" autocomplete="country-name"></div>
      </div>
      <div class="grid2">
        <div class="field"><label for="r-trip">Trip (optional)</label><select id="r-trip" name="trip">{trip_opts}</select></div>
        <div class="field"><label for="r-when">When did you go (optional)</label><input id="r-when" name="when" type="month"></div>
      </div>
      <div class="field"><label for="r-text">Your review *</label><textarea id="r-text" name="text" rows="5" required aria-describedby="h-rtext e-rtext"></textarea><span class="hint" id="h-rtext">The trail, the teahouses, the people, the pace</span><span class="err" id="e-rtext" hidden>Please write a few words about your trip.</span></div>
      <label class="check"><input type="checkbox" name="consent" id="r-consent"><span>Jenish may publish this review with my first name and country</span></label>
      <p class="hint">Nothing is sent until you press send in WhatsApp. See the <a href="legal.html#privacy">privacy policy</a></p>
      <div><button class="btn btn-primary" type="submit">{icon("message-circle")}Prepare review for WhatsApp</button></div>
    </form>
    <div class="rev-done" id="revDone" tabindex="-1" role="status" hidden>
      <h2 class="form-title" id="revDoneTitle"></h2>
      <p>Your review isn't sent yet. Open WhatsApp and press send, or copy the text and email it to {EMAIL}.</p>
      <label class="sr" for="revMsg">Your review message</label><textarea id="revMsg" rows="7" readonly></textarea>
      <div class="acts"><a class="btn btn-primary btn-sm" id="revOpen" href="{WA}" target="_blank" rel="noopener">{icon("message-circle")}Open WhatsApp{EXT}</a><button class="btn btn-secondary btn-sm" id="revCopy" type="button">Copy review</button><button class="btn btn-secondary btn-sm" id="revReset" type="button">Edit</button></div>
    </div>
  </div>
</section>
{final_cta()}'''
    return page("reviews.html", "Traveller Reviews of Treks with Jenish Maharjan | Somewhere in Mountains",
                "Read reviews from travellers who trekked in Nepal with local guide Jenish Maharjan, and share your own trip experience.",
                body, "reviews", [crumbs_ld(cr)], hero=False)


# ---------------------------------------------------------------- FAQ
def build_faq():
    cr = [("index.html", "Home"), (None, "FAQ")]
    body = plain_head("Questions and answers", "Straight answers about planning, booking, permits, altitude and what to bring. Can't find yours? Just ask.", crumbs(cr),
                      f'<p class="acts"><a class="btn btn-secondary btn-sm" href="{wa("Namaste Jenish! I have a question.")}" target="_blank" rel="noopener">{icon("message-circle")}Ask on WhatsApp{EXT}</a><a class="btn btn-secondary btn-sm" href="mailto:{EMAIL}?subject={quote("Question about trekking in Nepal")}">{icon("mail")}Email Jenish</a></p>') + f'''
<section class="wrap sec-sm faq-page" aria-label="All questions">
  {faq_list(FAQS, "q", True, 2)}
</section>
{final_cta()}'''
    return page("faq.html", "Nepal Trekking FAQ: Permits, Altitude, Costs and Booking | Somewhere in Mountains",
                "Answers about trekking in Nepal with a local guide: experience needed, costs, permits and TIMS, altitude sickness, insurance, gear, accommodation and how booking works.",
                body, "faq", [faq_ld(FAQS), crumbs_ld(cr)], hero=False)


# ---------------------------------------------------------------- PLAN YOUR TRIP (inquiry)
def build_plan():
    cr = [("index.html", "Home"), (None, "Plan Your Trip")]
    opts = ('<option value="custom">I\'m not sure yet – help me choose</option>' +
            '<optgroup label="Treks">' + "".join(f'<option value="{t["id"]}">{e(t["title"])} ({t["duration"]})</option>' for t in TREKS) + "</optgroup>" +
            '<optgroup label="Rafting and safari">' + "".join(f'<option value="{t["id"]}">{e(t["title"])} ({t["duration"]})</option>' for t in TRIPS if t["type"] != "trek") + "</optgroup>")
    people = '<option value="">Select</option>' + "".join(f'<option value="{n}">{n}</option>' for n in range(1, 10)) + '<option value="10+">10 or more</option>'
    body = plain_head("Plan your trip", "Tell Jenish a little about the trip you have in mind. Only your name is required, so it's fine if you haven't decided on dates or a route yet.", crumbs(cr)) + f'''
<section class="wrap plan" aria-label="Trip inquiry">
  <div class="form-card">
    <form id="plan" novalidate aria-labelledby="form-h" data-wa="{WA_NUMBER}" data-wa-display="{WA_DISPLAY}" data-email="{EMAIL}">
      <h2 id="form-h" class="form-title">Your trip</h2>
      <p class="notice" id="notice">{icon("info")}<span>This is an inquiry, not a confirmed booking. No payment is required.</span></p>
      <p class="hint">Fields marked * are required. Everything else is optional.</p>
      <div class="field"><label for="f-name">Your name *</label><input id="f-name" name="name" required autocomplete="name" maxlength="80" aria-describedby="e-name"><span class="err" id="e-name" hidden>Please enter your name so Jenish knows who he's talking to.</span></div>
      <div class="field"><label for="f-trek">Preferred trek</label><select id="f-trek" name="trek">{opts}</select></div>
      <div class="grid2">
        <div class="field"><label for="f-when">When would you like to go?</label><input id="f-when" name="when" type="month" aria-describedby="h-when"><span class="hint" id="h-when">Month and year, if you know it</span></div>
        <div class="field"><label for="f-people">Number of travellers</label><select id="f-people" name="people">{people}</select></div>
      </div>
      <label class="check"><input type="checkbox" name="flexible" id="f-flex" value="yes"><span>My dates are flexible or not decided yet</span></label>
      <fieldset class="opts"><legend>Previous trekking experience</legend><div class="opt-row">
        <label class="opt"><input type="radio" name="exp" value="" checked><span>Prefer not to say</span></label>
        <label class="opt"><input type="radio" name="exp" value="This would be my first multi-day trek"><span>First multi-day trek</span></label>
        <label class="opt"><input type="radio" name="exp" value="I've done a few multi-day hikes"><span>A few multi-day hikes</span></label>
        <label class="opt"><input type="radio" name="exp" value="I've trekked at high altitude before"><span>Trekked at high altitude</span></label>
      </div></fieldset>
      <div class="field"><label for="f-msg">Anything else? (optional)</label><textarea id="f-msg" name="message" rows="4" maxlength="1500" aria-describedby="h-msg"></textarea><span class="hint" id="h-msg">Fitness, wishes, budget, or adding rafting, a safari or a food walk in Patan</span></div>
      <div class="field"><label for="f-email">Your email (optional)</label><input id="f-email" name="email" type="email" autocomplete="email" maxlength="120" aria-describedby="h-email e-email"><span class="hint" id="h-email">Only if you'd like Jenish to reply by email</span><span class="err" id="e-email" hidden>That email address doesn't look complete. Check it, or leave it empty.</span></div>
      <div class="preview"><label for="f-preview">Your message preview</label><textarea id="f-preview" rows="9" readonly aria-describedby="h-preview"></textarea><span class="hint" id="h-preview">This is exactly what will be sent. You can still change it in WhatsApp or your email app.</span></div>
      <div class="send-acts">
        <button class="btn btn-primary" type="submit" data-send="wa">{icon("message-circle")}Continue on WhatsApp</button>
        <button class="btn btn-secondary" type="button" data-send="email">{icon("mail")}Send via Email</button>
        <button class="btn btn-secondary" type="button" data-send="copy">{icon("copy")}Copy Inquiry Message</button>
      </div>
      <div class="status" id="planStatus" role="status" tabindex="-1" hidden></div>
      <p class="hint">Nothing is sent from this website. WhatsApp or your email app opens with the message, and you press send there. See the <a href="legal.html#privacy">privacy policy</a>.</p>
    </form>
  </div>
  <aside class="side" aria-label="Other ways to reach Jenish">
    <div class="card"><span class="k">{icon("list-checks")}What happens next</span>
      <ol class="next"><li>You send the message from WhatsApp or email.</li><li>Jenish replies, usually within a few hours (Nepal time), with questions or a suggested route.</li><li>You get a day-by-day plan and a price for your group.</li><li>You decide. Nothing is booked until you confirm.</li></ol></div>
    <a class="card card-wa" href="{wa("Namaste Jenish! I'd like to plan a trip.")}" target="_blank" rel="noopener"><span class="k">{icon("message-circle")}WhatsApp</span><span class="big">Chat directly</span><span class="s nw">{WA_DISPLAY}</span>{EXT}</a>
    <a class="card" href="mailto:{EMAIL}?subject={quote("Trekking in Nepal")}"><span class="k">{icon("mail")}Email</span><span class="v brk">{EMAIL}</span><span class="s">For longer questions or documents</span></a>
    <address class="card"><span class="k">{icon("map-pin")}Meet in person</span><span class="v">Thamel, Kathmandu and Lakeside, Pokhara</span><span class="s">We meet the day before departure to check gear and get you ready.</span></address>
  </aside>
</section>
<script type="application/json" id="trekNames">{json.dumps({t["id"]: t["title"] for t in TRIPS}, ensure_ascii=False)}</script>'''
    return page(PLAN, "Plan Your Trek in Nepal: Free Inquiry with Jenish | Somewhere in Mountains",
                "Plan a private trek, Trishuli rafting or Chitwan safari with local guide Jenish Maharjan. Send a free, no-obligation inquiry on WhatsApp or email.",
                body, "plan", [BUSINESS, crumbs_ld(cr)], hero=False)

def build_contact_redirect():
    """contact.html moved to plan-your-trip.html. Vercel redirects it (vercel.json); this page is the fallback elsewhere."""
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Plan your trip | {SITE_NAME}</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{url(PLAN)}"><meta http-equiv="refresh" content="0; url={PLAN}"></head>
<body><p>This page has moved to <a href="{PLAN}">Plan your trip</a>.</p><script>location.replace('{PLAN}'+location.search+location.hash)</script></body></html>'''


# ---------------------------------------------------------------- LEGAL
def build_legal():
    src = open(os.path.join(ROOT, "legal_body.html")).read().replace("{{WA}}", WA).replace("{{WA_DISPLAY}}", WA_DISPLAY).replace("{{EMAIL}}", EMAIL)
    return page("legal.html", "Legal Notice, Privacy Policy and Booking Terms | Somewhere in Mountains",
                "Legal notice, privacy policy and booking terms for private treks and tours with Jenish Maharjan in Nepal.", src, "", None, hero=False)

def build_404():
    body = plain_head("This trail doesn't exist", "The page may have moved. Try one of these instead.", "",
                      f'<p class="acts"><a class="btn btn-primary" href="tours.html">Explore Treks</a><a class="btn btn-secondary" href="index.html">Home</a><a class="btn btn-secondary" href="{PLAN}">Plan Your Trip</a></p>')
    s = page("404.html", f"Page not found | {SITE_NAME}", "This page doesn't exist.", body, "", None, hero=False)
    return s.replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')


# ---------------------------------------------------------------- write
VERCEL = {
    "redirects": [{"source": "/contact.html", "destination": "/plan-your-trip.html", "permanent": True},
                  {"source": "/contact", "destination": "/plan-your-trip.html", "permanent": True}],
    "headers": [
        {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        {"source": "/img/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=2592000"}]},
        {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                         {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                                         {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}]},
    ],
}

def main():
    os.makedirs(DIST, exist_ok=True)
    pages = {"index.html": build_home(), "tours.html": build_tours(), "guide.html": build_guide(), "reviews.html": build_reviews(),
             "faq.html": build_faq(), PLAN: build_plan(), "legal.html": build_legal()}
    for t in TRIPS: pages[t["slug"] + ".html"] = build_trip(t)
    for name, s in pages.items(): open(os.path.join(DIST, name), "w").write(s)
    open(os.path.join(DIST, "contact.html"), "w").write(build_contact_redirect())
    open(os.path.join(DIST, "404.html"), "w").write(build_404())
    css = open(os.path.join(ROOT, "site.css")).read().replace("/*FONTS*/", open(os.path.join(ROOT, "fonts.css")).read())
    open(os.path.join(DIST, "site.css"), "w").write(css)
    open(os.path.join(DIST, "site.js"), "w").write(open(os.path.join(ROOT, "site.js")).read())
    os.makedirs(os.path.join(DIST, "fonts"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "fonts")): shutil.copy(os.path.join(ROOT, "fonts", f), os.path.join(DIST, "fonts", f))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f'  <url><loc>{url("" if n == "index.html" else n)}</loc></url>\n' for n in pages) + "</urlset>\n"
    open(os.path.join(DIST, "sitemap.xml"), "w").write(sm)
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {url('sitemap.xml')}\n")
    open(os.path.join(ROOT, "..", "vercel.json"), "w").write(json.dumps({"outputDirectory": os.path.basename(os.path.normpath(DIST)), "buildCommand": "", "framework": None, "cleanUrls": False, **VERCEL}, indent=2) + "\n")
    print("built", len(pages), "pages")

if __name__ == "__main__":
    main()
