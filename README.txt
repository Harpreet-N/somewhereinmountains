Somewhere in Mountains — final website
======================================
site/     The finished website (16 pages). Upload everything in this folder to a web host
          such as Netlify, Cloudflare Pages or GitHub Pages. index.html is the home page.
source/   To change text, trips, photos or reviews: edit source/data.py, then run
              cd source && python3 build.py      (needs Python 3 with Pillow)
          It rebuilds the pages straight into ../site.

Before going live
- Set DOMAIN in source/data.py once Jenish has a domain, then rebuild. That adds the
  canonical links, social-share previews, sitemap.xml and robots.txt for Google.
- Fill the yellow gaps on the Legal page (address, licence no., partner agency, PAN,
  deposit and cancellation rules) in source/legal_body.html.

Design: field-notebook direction made with unslop by Damir Sokolovsky (@heydamir), CC BY 4.0.
Fonts: Newsreader and Instrument Sans (SIL Open Font License). Icons: Lucide (ISC).
