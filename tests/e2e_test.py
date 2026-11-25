#!/usr/bin/env python3
"""End-to-end and functional checks for the Somewhere in Mountains site.

Run from the repository root:
    pip install playwright && python3 -m playwright install chromium
    python3 tests/e2e_test.py            # serves ./site on a free port and tests it
    python3 tests/e2e_test.py --site path/to/site

No real messages are sent: WhatsApp and email links are captured through the
window.smOpen hook in site.js and checked as URLs.
"""
import argparse, functools, glob, http.server, json, os, re, socketserver, sys, threading, traceback
from urllib.parse import urlparse, parse_qs, unquote
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--site", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site"))
ap.add_argument("--out", default=None, help="write results as JSON here")
args = ap.parse_args()
SITE = os.path.abspath(args.site)
WA_NUMBER = "9779843204871"
EMAIL = "jenishmaharjan26@gmail.com"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=SITE))
httpd.daemon_threads = True
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/"

RESULTS = []
def test(name):
    def deco(fn):
        def run(*a):
            try:
                note = fn(*a) or ""
                RESULTS.append((name, "PASS", note))
            except AssertionError as ex:
                RESULTS.append((name, "FAIL", str(ex)))
            except Exception as ex:
                RESULTS.append((name, "FAIL", f"{type(ex).__name__}: {ex}"))
        run.__name__ = fn.__name__
        return run
    return deco

CAPTURE = "window.__opened=[];window.smOpen=function(u,t){window.__opened.push(u)};"

def new_page(browser, w=1360, h=900, **kw):
    ctx = browser.new_context(viewport={"width": w, "height": h}, **kw)
    ctx.add_init_script(CAPTURE)
    pg = ctx.new_page()
    pg._errors = []
    pg.on("console", lambda m: pg._errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: pg._errors.append(str(e)))
    pg.on("requestfailed", lambda r: pg._errors.append("failed: " + r.url) if r.url.startswith(BASE) else None)
    return pg

def opened(pg):
    return pg.evaluate("window.__opened")

def wa_text(u):
    p = urlparse(u)
    assert p.netloc == "wa.me" and p.path == "/" + WA_NUMBER, f"wrong WhatsApp URL {u[:60]}"
    return parse_qs(p.query)["text"][0]

PAGES = sorted(os.path.basename(f) for f in glob.glob(os.path.join(SITE, "*.html")) if not f.endswith(("contact.html", "404.html")))

# ------------------------------------------------------------------ static checks
@test("Every page: loads, one h1, no console errors or failed requests")
def t_pages(b):
    pg = new_page(b)
    bad = []
    for f in PAGES + ["404.html"]:
        pg._errors.clear()
        pg.goto(BASE + f); pg.wait_for_load_state("load")
        h1 = pg.locator("h1").count()
        if h1 != 1: bad.append(f"{f}: {h1} h1")
        if pg._errors: bad.append(f"{f}: {pg._errors[:2]}")
    assert not bad, "; ".join(bad)
    return f"{len(PAGES) + 1} pages"

@test("SEO: unique titles and descriptions, canonical, Open Graph, valid JSON-LD")
def t_seo(b):
    pg = new_page(b); titles, descs, bad = {}, {}, []
    for f in PAGES:
        pg.goto(BASE + f)
        t = pg.title(); d = pg.get_attribute('meta[name="description"]', "content")
        c = pg.get_attribute('link[rel="canonical"]', "href"); og = pg.get_attribute('meta[property="og:image"]', "content")
        titles.setdefault(t, []).append(f); descs.setdefault(d, []).append(f)
        if not c or not c.startswith("https://"): bad.append(f"{f} canonical")
        if not og: bad.append(f"{f} og:image")
        for s in pg.locator('script[type="application/ld+json"]').all_text_contents():
            try: json.loads(s)
            except Exception: bad.append(f"{f} JSON-LD")
        if not 20 <= len(t) <= 110: bad.append(f"{f} title length {len(t)}")
    dup = [v for v in list(titles.values()) + list(descs.values()) if len(v) > 1]
    assert not dup and not bad, f"duplicates {dup} {bad}"
    return f"{len(PAGES)} pages, all unique"

@test("Sitemap lists only existing pages; robots.txt points to it")
def t_sitemap(b):
    sm = open(os.path.join(SITE, "sitemap.xml")).read()
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    missing = [l for l in locs if not os.path.exists(os.path.join(SITE, urlparse(l).path.lstrip("/") or "index.html"))]
    rb = open(os.path.join(SITE, "robots.txt")).read()
    assert not missing and "Sitemap:" in rb, f"missing {missing}"
    return f"{len(locs)} URLs"

@test("All internal links and images resolve")
def t_links(b):
    bad = []
    for f in glob.glob(os.path.join(SITE, "*.html")):
        s = open(f).read()
        for m in re.findall(r'(?:src|href|data-full)="([^"]+)"', s) + [x.split(" ")[0] for ss in re.findall(r'srcset="([^"]+)"', s) for x in ss.split(", ")]:
            if m.startswith(("http", "mailto:", "#", "data:", "tel:")): continue
            p = m.split("#")[0].split("?")[0]
            if p and not os.path.exists(os.path.join(SITE, p)): bad.append(f"{os.path.basename(f)} -> {p}")
    assert not bad, bad[:5]

@test("Navigation: same five items on every page, logo goes home, one active state")
def t_nav(b):
    pg = new_page(b); bad = []
    for f in PAGES:
        pg.goto(BASE + f)
        labels = pg.locator("nav.links > a").all_inner_texts()
        if [l.strip() for l in labels][:4] != ["Explore Treks", "Meet Your Guide", "Reviews", "FAQ"] or "Plan Your Trip" not in labels[-1]:
            bad.append(f"{f}: {labels}")
        if pg.get_attribute(".nav .brand", "href") != "index.html": bad.append(f"{f}: logo")
        if pg.locator("nav.links [aria-current=page]").count() > 1: bad.append(f"{f}: 2 active")
    assert not bad, bad[:3]

# ------------------------------------------------------------------ journeys
@test("Journey 1 – undecided beginner: finder → trek → quote → WhatsApp message")
def j1(b):
    pg = new_page(b)
    pg.goto(BASE + "index.html")
    pg.locator('#finder input[name=days][value="8"]').check(force=True)
    pg.locator('#finder input[name=exp][value=first]').check(force=True)
    pg.click("#finder button[type=submit]")
    res = pg.locator("#finderOut .finder-list a").all_inner_texts()
    assert res, "no recommendation shown"
    assert "Langtang Valley Trek" in res, f"expected Langtang for a first week-long trek, got {res}"
    pg.locator("#finderOut .finder-list a", has_text="Langtang Valley Trek").click()
    assert pg.url.endswith("langtang-valley-trek.html")
    pg.locator(".book-card a", has_text="Request a Personalised Quote").click()
    assert "plan-your-trip.html?trek=langtang" in pg.url
    assert pg.input_value("#f-trek") == "langtang", "trek not preselected"
    pg.fill("#f-name", "Anna")
    pg.click('button[data-send="wa"]')
    txt = wa_text(opened(pg)[-1])
    assert "Preferred trek: Langtang Valley Trek" in txt and "Name: Anna" in txt
    assert "undefined" not in txt and "null" not in txt
    assert "isn't sent until you press send" in pg.inner_text("#planStatus")
    return f"recommended: {', '.join(res)}"

@test("Journey 2 – experienced trekker: filters → challenging trek → quote preselected")
def j2(b):
    pg = new_page(b)
    pg.goto(BASE + "index.html"); pg.click("nav.links >> text=Explore Treks")
    pg.select_option("#ft-diff", "challenging"); pg.select_option("#ft-area", "annapurna")
    vis = pg.locator("#tourList > li:not([hidden]) h2").all_inner_texts()
    assert vis == ["North Annapurna Base Camp Trek"], vis
    assert pg.inner_text("#count") == "Showing 1 of 10 trips"
    pg.locator("#tourList > li:not([hidden]) h2 a").click()
    assert pg.locator("#itin-h").is_visible()
    pg.locator(".book-card a", has_text="Request a Personalised Quote").click()
    assert pg.input_value("#f-trek") == "nabc"

@test("Journey 3 – trust-focused: guide → reviews → FAQ → email message")
def j3(b):
    pg = new_page(b)
    pg.goto(BASE + "index.html"); pg.click("nav.links >> text=Meet Your Guide")
    assert pg.locator("h1").inner_text().startswith("Hi, I'm Jenish")
    pg.click("nav.links >> text=Reviews"); assert pg.locator(".rev-card").count() >= 1
    pg.click("nav.links >> text=FAQ")
    btn = pg.locator(".faq-item button").nth(2)
    assert btn.get_attribute("aria-expanded") == "false"; btn.click(); assert btn.get_attribute("aria-expanded") == "true"
    btn.click(); assert btn.get_attribute("aria-expanded") == "false"
    pg.click("nav.links >> text=Plan Your Trip")
    pg.fill("#f-name", "Sam"); pg.fill("#f-email", "sam@example.com")
    pg.click('button[data-send="email"]')
    u = opened(pg)[-1]; p = urlparse(u)
    assert u.startswith("mailto:" + EMAIL), u[:40]
    q = parse_qs(p.query)
    assert q["subject"][0] == "Trek inquiry: help me choose a trek", q["subject"]
    assert "Email for replies: sam@example.com" in q["body"][0]

@test("Journey 4 – mobile: menu → trek → sticky quote bar → inquiry")
def j4(b):
    pg = new_page(b, 390, 844, is_mobile=True, has_touch=True)
    pg.goto(BASE + "index.html")
    pg.click("#menuBtn"); assert pg.get_attribute("#menuBtn", "aria-expanded") == "true"
    pg.locator("#sheet a", has_text="Explore Treks").click()
    pg.locator("#tourList h2 a", has_text="Everest Base Camp Trek").click()
    pg.mouse.wheel(0, 2500); pg.wait_for_timeout(300)
    bar = pg.locator("#qbar")
    assert bar.is_visible(), "quote bar hidden"
    box = bar.bounding_box(); assert box["y"] + box["height"] <= 844 + 1
    pad = pg.evaluate("parseFloat(getComputedStyle(document.body).paddingBottom)")
    assert pad >= box["height"] - 1, "page has no room for the bar, content would be hidden"
    bar.locator("a", has_text="Request a Quote").click()
    assert pg.input_value("#f-trek") == "ebc"
    pg.fill("#f-name", "Lee"); pg.click('button[data-send="wa"]')
    assert "Everest Base Camp Trek" in wa_text(opened(pg)[-1])
    over = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    assert over <= 0, f"horizontal overflow {over}px"

@test("Journey 5 – flexible traveller: not sure + no dates → message")
def j5(b):
    pg = new_page(b); pg.goto(BASE + "plan-your-trip.html")
    assert pg.input_value("#f-trek") == "custom"
    pg.fill("#f-name", "Kai"); pg.check("#f-flex"); pg.click('button[data-send="wa"]')
    txt = wa_text(opened(pg)[-1])
    assert "I'm not sure yet, please help me choose" in txt and "Travel dates: Flexible, not decided yet" in txt and "Number of travellers: Not sure yet" in txt
    assert "undefined" not in txt and "null" not in txt

@test("Journey 6 – edge cases: bad parameters, empty and invalid fields, special characters, no filter results")
def j6(b):
    pg = new_page(b)
    for q in ["?trek=%3Cscript%3Ealert(1)%3C/script%3E", "?trek=nope", "?trek=", "?trek=../../etc"]:
        pg.goto(BASE + "plan-your-trip.html" + q); assert pg.input_value("#f-trek") == "custom", q
    pg.goto(BASE + "contact.html?trek=pikey"); pg.wait_for_url("**/plan-your-trip.html?trek=pikey")
    assert pg.input_value("#f-trek") == "pikey", "old contact URL lost the trek"
    pg.goto(BASE + "plan-your-trip.html"); pg.click('button[data-send="wa"]')
    assert pg.is_visible("#e-name") and pg.get_attribute("#f-name", "aria-invalid") == "true"
    assert pg.evaluate("document.activeElement.id") == "f-name" and opened(pg) == []
    pg.fill("#f-name", "Zoë & Jürgen <b>“test”</b> #1 100%"); pg.fill("#f-email", "not-an-email"); pg.click('button[data-send="email"]')
    assert pg.is_visible("#e-email") and opened(pg) == [], "invalid email accepted"
    pg.fill("#f-email", ""); pg.fill("#f-msg", "Line 1\nLine 2 & ? = #")
    pg.click('button[data-send="wa"]')
    txt = wa_text(opened(pg)[-1])
    assert "Name: Zoë & Jürgen <b>“test”</b> #1 100%" in txt and "Line 2 & ? = #" in txt, "special characters changed"
    pg.goto(BASE + "tours.html")
    pg.select_option("#ft-days", "0-5"); pg.select_option("#ft-diff", "challenging")
    assert pg.is_visible("#empty") and pg.inner_text("#count") == "Showing 0 of 10 trips"
    pg.click("#emptyReset"); pg.wait_for_timeout(50)
    assert pg.is_hidden("#empty") and pg.inner_text("#count") == "Showing all 10 trips"
    pg.goto(BASE + "tours.html#raft")
    assert pg.input_value("#ft-type") == "raft" and pg.inner_text("#count") == "Showing 2 of 10 trips"

@test("Journey 7 – keyboard only: skip link, menu, filters, accordion, form")
def j7(b):
    pg = new_page(b)
    pg.goto(BASE + "index.html"); pg.keyboard.press("Tab")
    assert pg.evaluate("document.activeElement.className") == "skip"
    pg.keyboard.press("Enter"); assert pg.evaluate("document.activeElement.id") == "main"
    pg.goto(BASE + "tours.html"); pg.focus("#ft-type"); pg.keyboard.press("ArrowDown")
    pg.goto(BASE + "faq.html"); pg.focus(".faq-item button >> nth=1"); pg.keyboard.press("Enter")
    assert pg.get_attribute(".faq-item button >> nth=1", "aria-expanded") == "true"
    pg.goto(BASE + "plan-your-trip.html"); pg.focus("#f-name"); pg.keyboard.type("Mo"); pg.keyboard.press("Enter")
    assert opened(pg), "Enter in the form did not prepare the message"
    pg.goto(BASE + "index.html")
    seen = set()
    for _ in range(40):
        pg.keyboard.press("Tab")
        info = pg.evaluate("(()=>{const e=document.activeElement;const r=e.getBoundingClientRect();const s=getComputedStyle(e);return [e.tagName+'.'+e.className, s.outlineStyle!=='none'||s.boxShadow!=='none', r.width>0&&r.height>0]})()")
        seen.add(info[0])
        assert info[2], f"focused element is invisible: {info[0]}"
    pg2 = new_page(b, 390, 844)
    pg2.goto(BASE + "index.html"); pg2.focus("#menuBtn"); pg2.keyboard.press("Enter")
    assert pg2.evaluate("document.activeElement.closest('#sheet')!==null"), "menu did not move focus"
    pg2.keyboard.press("Escape")
    assert pg2.get_attribute("#menuBtn", "aria-expanded") == "false" and pg2.evaluate("document.activeElement.id") == "menuBtn"
    return f"{len(seen)} distinct focus stops checked"

# ------------------------------------------------------------------ components
@test("Copy inquiry message puts the exact preview on the clipboard")
def t_copy(b):
    pg = new_page(b, permissions=["clipboard-read", "clipboard-write"])
    pg.goto(BASE + "plan-your-trip.html?trek=abc"); pg.fill("#f-name", "Rae")
    pg.click('button[data-send="copy"]'); pg.wait_for_timeout(100)
    assert pg.evaluate("navigator.clipboard.readText()") == pg.input_value("#f-preview")
    assert "Message copied" in pg.inner_text("#planStatus")

@test("Review form validates, then prepares a WhatsApp message")
def t_review(b):
    pg = new_page(b); pg.goto(BASE + "reviews.html")
    pg.click("#revForm button[type=submit]")
    assert pg.is_visible("#e-rating") and pg.is_visible("#e-rname") and pg.is_visible("#e-rtext")
    pg.check("#st5", force=True); pg.fill("#r-name", "Ana"); pg.fill("#r-text", "Great trek")
    pg.click("#revForm button[type=submit]")
    assert pg.is_visible("#revDone") and "Great trek" in wa_text(pg.get_attribute("#revOpen", "href"))

@test("Photo viewer opens, arrow keys browse, Escape closes and focus returns")
def t_viewer(b):
    pg = new_page(b); pg.goto(BASE + "langtang-valley-trek.html")
    btn = pg.locator(".car-open").first; btn.scroll_into_view_if_needed(); btn.click()
    assert pg.locator("dialog.lb[open]").count() == 1
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(400)
    assert pg.inner_text(".lb-count").startswith("02")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
    assert pg.locator("dialog.lb[open]").count() == 0 and pg.evaluate("document.activeElement.classList.contains('car-open')")

@test("Every trip page uses the full template and links its quote to the right trek")
def t_trips(b):
    pg = new_page(b); bad = []
    trips = [f for f in PAGES if f.endswith("-trek.html") or f.startswith("trishuli")]
    for f in trips:
        pg.goto(BASE + f)
        for sec in ["#ov", "#itin-h", "#fit-h", "#ss-h", "#stay-h", "#inc-h", "#prep-h", "#price-h", "#tf-h", "#rel-h"]:
            if pg.locator(sec).count() != 1: bad.append(f"{f} {sec}")
        if pg.locator(".crumbs").count() != 1: bad.append(f"{f} breadcrumbs")
        href = pg.get_attribute(".book-card .btn-primary", "href")
        tid = href.split("trek=")[-1]
        pg.goto(BASE + href)
        if pg.input_value("#f-trek") != tid: bad.append(f"{f} preselect {tid}")
    assert not bad, bad[:5]
    return f"{len(trips)} trip pages"

@test("Responsive: no horizontal overflow at 9 widths on every page")
def t_widths(b):
    bad = []
    for w in [320, 375, 390, 430, 768, 1024, 1280, 1440, 1920]:
        pg = new_page(b, w, 900)
        for f in PAGES:
            pg.goto(BASE + f)
            o = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
            if o > 0: bad.append(f"{f}@{w}: {o}px")
        pg.context.close()
    assert not bad, bad[:6]
    return f"{len(PAGES)} pages × 9 widths"

@test("Sticky UI never hides the focused element (WCAG 2.4.11)")
def t_focus_obscured(b):
    pg = new_page(b, 390, 844); pg.goto(BASE + "manaslu-circuit-trek.html"); bad = []
    for _ in range(60):
        pg.keyboard.press("Tab")
        r = pg.evaluate("""(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const r=e.getBoundingClientRect();
          const bar=document.querySelector('#qbar');const nav=document.querySelector('#nav');
          if(bar&&bar.contains(e)||nav.contains(e)||e.classList.contains('skip'))return null;
          const b=bar?bar.getBoundingClientRect().top:innerHeight;const n=nav.getBoundingClientRect().bottom;
          return (r.top>=b||r.bottom<=n)?e.tagName+'.'+e.className+':'+e.textContent.trim().slice(0,30):null})()""")
        if r: bad.append(r)
    assert not bad, f"hidden behind sticky bars: {bad[:3]}"

@test("Reduced motion: no transforms on the landscape and no animations")
def t_reduced(b):
    pg = new_page(b, reduced_motion="reduce"); pg.goto(BASE + "index.html"); pg.mouse.wheel(0, 3000); pg.wait_for_timeout(300)
    tr = pg.evaluate("[...document.querySelectorAll('.rg,.hero-bg')].map(e=>getComputedStyle(e).transform).filter(t=>t!=='none')")
    an = pg.evaluate("getComputedStyle(document.querySelector('.hero-copy h1')).animationName")
    assert not tr and an == "none", f"{tr[:2]} {an}"


@test("Tracking hook fires events without personal data")
def t_track(b):
    pg = new_page(b)
    pg.add_init_script("window.__ev=[];document.addEventListener('sm:track',e=>window.__ev.push(e.detail))")
    pg.goto(BASE + "index.html"); pg.click('#finder button[type=submit]')
    pg.goto(BASE + "plan-your-trip.html?trek=ebc"); pg.fill("#f-name", "Secret Person"); pg.fill("#f-email", "secret@example.com")
    pg.click('button[data-send="wa"]')
    ev = pg.evaluate("window.__ev"); names = [e["name"] for e in ev]
    assert "inquiry_form_started" in names and "inquiry_whatsapp_clicked" in names, names
    blob = json.dumps(ev)
    assert "Secret" not in blob and "secret@" not in blob, "personal data in events"
    return ", ".join(sorted(set(names)))


if __name__ == "__main__":
    tests = [t_pages, t_seo, t_sitemap, t_links, t_nav, j1, j2, j3, j4, j5, j6, j7, t_copy, t_review, t_viewer, t_trips, t_widths, t_focus_obscured, t_reduced, t_track]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for t in tests: t(browser)
        browser.close()
    httpd.shutdown()
    w = max(len(n) for n, _, _ in RESULTS)
    for n, s, note in RESULTS: print(f"{s:4}  {n.ljust(w)}  {note}")
    fails = sum(1 for _, s, _ in RESULTS if s != "PASS")
    print(f"\n{len(RESULTS) - fails} passed, {fails} failed")
    if args.out: json.dump([dict(test=n, status=s, note=note) for n, s, note in RESULTS], open(args.out, "w"), indent=2, ensure_ascii=False)
    sys.exit(1 if fails else 0)
