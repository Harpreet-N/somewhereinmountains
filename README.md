# Somewhere in Mountains

Website for Jenish Maharjan, a local trekking guide from Kathmandu: private Himalayan treks,
Trishuli rafting and Chitwan safaris. Static HTML, CSS and JavaScript, built from one Python
content file. Hosted on Vercel.

```
source/     build.py (builds the site), data.py (all content), site.css, site.js,
            legal_body.html, fonts/, icons/
site/       the built website (this is what Vercel serves)
tests/      e2e_test.py (Playwright end-to-end tests)
docs/       screenshots
vercel.json tells Vercel to serve site/, redirects and cache headers
*.md        audit, implementation report, QA report, owner checklist
```

## Install

You need Python 3.9 or newer.

```bash
pip3 install pillow                  # for the build (image sizes and WebP versions)
pip3 install playwright              # only for the tests
python3 -m playwright install chromium
```

## Develop and build

1. Edit `source/data.py` (content), `source/site.css` (styles) or `source/site.js` (behaviour).
2. Build:

   ```bash
   cd source && python3 build.py      # prints "built 17 pages"
   ```

3. Preview:

   ```bash
   cd site && python3 -m http.server 8000      # open http://localhost:8000
   ```

The first build creates WebP versions of new photos in `site/img/w/`; later builds reuse them.

## Test

```bash
python3 tests/e2e_test.py            # from the repository root
```

It serves `site/` on a free port and runs 20 checks, including 7 customer journeys.
WhatsApp and email links are captured and checked as URLs — nothing is sent.

## Deploy

Vercel builds nothing; it serves the committed `site/` folder (see `vercel.json`).

```bash
cd source && python3 build.py && cd ..
python3 tests/e2e_test.py
git add -A && git commit -m "Describe the change" && git push
```

Vercel redeploys automatically after the push. In the Vercel project, leave **Root Directory**
as `./` and **Framework Preset** as Other; `vercel.json` does the rest.

> Vercel's free Hobby plan is for non-commercial use. A business site needs Vercel Pro
> (or another host such as Cloudflare Pages or Netlify — check their terms).

## Update trekking information

Everything about trips is in `source/data.py`:

- `TRIPS` — title, short name, duration, level, highest point (`peak`), season, photo, alt
  text, description, highlights and gallery for each trip. The `slug` is the page address;
  don't change it for existing trips (it would break links and search rankings).
- `TRIP_FACTS` — numbers and labels used by filters, the finder and the comparison table:
  `days`, `diff` (easy / moderate / challenging), `area`, `first` (good for a first trek),
  `for` (who it suits), `start`, `end`, `stay`, `tags` (iconic, quiet, culture). Leave
  `start` / `end` empty (`""`) if not confirmed — empty fields are simply not shown.
- `FEATURED` — the four treks on the home page.
- `SEASONS` — the season chart (0 off-season, 1 possible, 2 good, 3 best).

New photos: put a JPEG in `site/img/` (about 1,300–2,000 px wide) and refer to it by name
without `.jpg`.

## Update contact details

At the top of `source/data.py`: `WA_NUMBER` (digits only, with country code), `WA_DISPLAY`,
`EMAIL`, `INSTAGRAM`, `INSTAGRAM_HANDLE`. They're used everywhere, including the inquiry
form and structured data. When a custom domain is ready, set `DOMAIN` (e.g.
`"https://www.somewhereinmountains.com"`) and rebuild — canonicals, the sitemap and social
previews update.

## Add reviews

Reviews come in on WhatsApp from the form on `reviews.html`. Only publish them if the guest
ticked "Jenish may publish this review". Add them at the top of `REVIEWS` in `data.py`:

```python
{"name": "Anna", "country": "Germany", "trip": "abc", "when": "2026-10", "stars": 5,
 "text": "Exactly as the guest wrote it."},
```

`trip` is the trip `id` (e.g. `abc`, `langtang`, `ebc`). The average rating appears once
there are three reviews.

## Update pricing

There are no prices on the site yet — every trip says "Request a personalised quote". To add
an indicative price, add a field such as `"price": "From US$ 650 per person (2 people)"` to
the trip in `TRIP_FACTS`, then show it in `trip_card()` and the trip page's price section in
`build.py`. Only publish prices Jenish has confirmed, and say per person or per group.

## The inquiry form

`plan-your-trip.html` builds a message in the visitor's browser and opens WhatsApp
(`wa.me/<WA_NUMBER>`) or their email app (`mailto:`), or copies the text. Nothing is stored
or sent by the website. A trip page links to `plan-your-trip.html?trek=<id>` to preselect the
trip; unknown values fall back to "I'm not sure yet". The old `contact.html` redirects here.

The form logic is in `source/site.js` (section "plan your trip"). Messages are plain text and
URL-encoded, so special characters are safe.

## Analytics

No analytics is installed. `site.js` sends privacy-safe events (trip IDs, filter values,
never names or messages) to `window.smTrack`, and forwards them to Plausible automatically if
its script is added. Add a provider only after updating the privacy policy.
