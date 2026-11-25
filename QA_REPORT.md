# QA report

Verification of the redesign, 24 November 2026. Every result below comes from a command
that was actually run. Nothing was deployed and no WhatsApp message or email was sent.

## Test environment

- Linux container, Python 3.13, Chromium (Playwright 1.x), Node 22.
- Site served locally from the built `site/` folder: Python `http.server` for functional
  tests, `serve@14` (gzip, like Vercel) for Lighthouse.
- Lighthouse 12.8.2, mobile form factor, simulated slow 4G (lab data, not field data).
- axe-core 4.10.2 via Playwright, rule sets wcag2a, wcag2aa, wcag21aa, wcag22aa, best-practice.

## Commands executed

```bash
python3 source/build.py                          # build: "built 17 pages", no errors
python3 tests/e2e_test.py --site site            # 20 passed, 0 failed
python3 a11y/audit2.py                           # axe on 18 pages × 2 widths: 0 violations
python3 a11y/full.py                             # text over photos, 3 widths: 212 checks, 0 below AA
lighthouse http://localhost:8766/<page> --form-factor=mobile   # 8 pages after, 3 pages before
```

There is no linter, type checker or unit test framework in this project (plain Python and
JavaScript, no package.json). JavaScript was syntax-checked with `node -e "new Function(...)"`;
`build.py` and `data.py` were parsed with Python 3.11 to confirm they run on older Pythons.

## End-to-end and functional tests (`tests/e2e_test.py`)

| Test | Result | Notes |
|---|---|---|
| Every page: loads, one h1, no console errors or failed requests | PASS | 18 pages |
| SEO: unique titles and descriptions, canonical, Open Graph, valid JSON-LD | PASS | 17 pages |
| Sitemap lists only existing pages; robots.txt points to it | PASS | 17 URLs |
| All internal links and images resolve | PASS | incl. every srcset entry |
| Navigation: same five items on every page, logo goes home, one active state | PASS | |
| Journey 1 – undecided beginner: finder → trek → quote → WhatsApp message | PASS | 8 days + first trek → ABC, Langtang, Pikey Peak |
| Journey 2 – experienced trekker: filters → challenging trek → quote preselected | PASS | Challenging + Annapurna → North Annapurna BC only |
| Journey 3 – trust-focused: guide → reviews → FAQ → email message | PASS | mailto subject and body checked |
| Journey 4 – mobile (390 px): menu → trek → sticky quote bar → inquiry | PASS | bar inside viewport, page has bottom padding for it |
| Journey 5 – flexible traveller: not sure + no dates → message | PASS | no "undefined"/"null" |
| Journey 6 – edge cases | PASS | `<script>`, unknown, empty and `../` trek params fall back to "not sure"; old `contact.html?trek=` forwards; empty name and bad email blocked with messages; Zoë & Jürgen `<b>“test”</b> #1 100%` survives encoding; no-result filters show the empty state; reset works; `#raft` deep link |
| Journey 7 – keyboard only | PASS | skip link → main, menu focus and Escape, select filters, accordion with Enter, form submit with Enter, 40 Tab stops all visible |
| Copy inquiry message | PASS | clipboard equals preview |
| Review form | PASS | errors shown, then WhatsApp link with the review |
| Photo viewer | PASS | arrow keys, Escape, focus returns to the photo |
| Every trip page uses the full template | PASS | 10 trip pages, 10 sections each, quote link preselects the right trek |
| Responsive: no horizontal overflow | PASS | 17 pages × 320, 375, 390, 430, 768, 1024, 1280, 1440, 1920 px |
| Sticky UI never hides the focused element (2.4.11) | PASS | 60 Tab stops on a trip page at 390 px |
| Reduced motion | PASS | no transforms on landscape/hero, no animations |
| Tracking hook without personal data | PASS | name and email never appear in events |

Defects found and fixed during QA: trip pages overflowed at 320–430 px (grid track without
`minmax(0,…)`), test server deadlock (single-threaded), `#raft` deep link ignored on same-page
hash change, FAQ page heading order, duplicate landmark name on tours, quote bar outside a
landmark. All re-tested.

## Accessibility

- **axe-core:** 0 violations, 18 pages × 1360 px and 390 px.
- **Text over photos:** 212 measurements (5th-percentile pixel contrast): lowest 5.7:1, all ≥ AA.
- **Non-text contrast:** form borders 3.3:1, rating stars 3.1:1, option buttons 3.3:1.
- **Reflow / text size:** no sideways scrolling at 320 px, or at 640 px with 200% text.
- **Keyboard and focus:** verified by Journey 7 and the 2.4.11 test.
- **Not verified:** screen reader testing with VoiceOver/NVDA/TalkBack, real-device touch
  testing, Windows High Contrast. Automated tests don't prove full WCAG 2.2 AA compliance.

## Performance (Lighthouse mobile, lab data)

| Page | Before perf | After perf | LCP before → after | Weight before → after |
|---|---|---|---|---|
| index.html | 78 | 96 | 5.9 s → 2.7 s | 1,272 → 364 KiB |
| tours.html | 78 | 98 | 6.0 s → 2.3 s | 1,390 → 355 KiB |
| langtang-valley-trek.html | 77 | 99 | 6.7 s → 2.0 s | 1,766 → 171 KiB |
| everest-base-camp-trek.html | – | 99 | – → 1.8 s | – → 139 KiB |
| trishuli-rafting-chitwan-safari.html | – | 99 | – → 2.0 s | – → 184 KiB |
| guide.html | new | 99 | 2.1 s | 195 KiB |
| plan-your-trip.html | new | 100 | 1.7 s | 113 KiB |
| faq.html / reviews.html | new | 99 / 100 | 1.7 s | 113 / 112 KiB |

After: Accessibility 100, Best Practices 100, SEO 100 on all 8 pages. CLS 0 everywhere except
Langtang 0.037 (font swap). TBT ≤ 30 ms. JavaScript: one 27 KiB file (≈ 8 KiB gzipped).
**Remaining limitation:** home-page LCP is 2.7 s in the lab, just over the 2.5 s target. Field
data (real visitors) isn't available until the site has traffic; check Vercel Speed Insights
or PageSpeed Insights after launch.

## SEO verification

- Unique titles (17) and descriptions (17): PASS. Canonical on every page: PASS.
- robots.txt allows all and links the sitemap; sitemap has 17 URLs, all exist: PASS.
- JSON-LD parses on every page: PASS. Types: TravelAgency, Person, WebSite, ProfilePage,
  TouristTrip, BreadcrumbList, FAQPage, ItemList. **Not run:** Google Rich Results Test and
  validator.schema.org (they need a public URL; run them after deployment). Note that Google
  shows FAQ rich results only for government and health sites, so FAQPage helps AI answers
  more than search snippets.
- Redirect `contact.html → plan-your-trip.html` (308) is configured in `vercel.json`;
  **not verified on Vercel** (only the HTML fallback was tested locally).
- Indexability: no `noindex` except `404.html` and the `contact.html` fallback.

## Content verification

- No prices, discounts, availability, credentials, years of experience, languages,
  reviews or ratings were invented. One genuine review (Harpreet) is shown; the average
  rating appears only from 3 reviews.
- Durations, altitudes, seasons and difficulty come from `data.py` and are the same in cards,
  table, finder and trip pages (single source).
- Unsupported claims removed or softened: safety wording around oxygen checks, Khumbu guide
  rule exception, "every photo by Jenish".
- **Open:** 9 legal placeholders (release blocker), unverified photo credit for the wildlife
  photos, partner agency name.

## Screenshots

`docs/screenshots/` — before and after, 1440 px and 390 px, full page (cut at 9,000 px):
`after-index`, `after-tours`, `after-everest-base-camp-trek`, `after-guide`,
`after-plan-your-trip`, `after-faq`, `after-reviews`, and `before-index`, `before-tours`,
`before-everest-base-camp-trek`, `before-contact`.

## Requirement traceability matrix

Statuses: PASS (implemented and verified), PARTIAL, FAIL, BLOCKED (missing business info or
capability), N/A.

| # | Requirement | Implementation location | Verification | Status | Notes |
|---|---|---|---|---|---|
| 3 | Analyse repository, stack, pages, IA, inquiry, content, issues | WEBSITE_AUDIT.md | Manual review + baseline Lighthouse/axe | PASS | |
| 4 | Visitor understands offer, place, guide, why, how to find, contact, what happens next in 5–10 s | index.html hero, trust strip, steps | Screenshot review | PARTIAL | Content present above and near the fold; no user test done |
| 5 | Visual direction: authentic photos, editorial type, restrained radius/shadow | site.css | Screenshot review | PASS | Blue palette kept by owner's choice instead of earthy |
| 5 | No AI imagery | site/img | Inspection | PASS | Only owner-supplied photos |
| 6 | Design system: tokens, buttons, forms, cards, accordions, states | site.css `:root`, components | Screenshot review, axe | PASS | |
| 7 | Nav: Explore Treks, Meet Your Guide, Reviews, FAQ, Plan Your Trip; logo → home | build.py `NAV`, `page()` | e2e "Navigation" | PASS | |
| 7 | WhatsApp secondary in nav | `page()` | Inspection | PASS | Hidden < 1100 px to keep the bar uncluttered; in mobile menu |
| 7 | Accessible mobile menu, focus management, active states | site.js nav | Journey 4, 7 | PASS | |
| 7 | Breadcrumbs on trek pages | `crumbs()` | e2e trip template | PASS | Also on tours, guide, FAQ, reviews, plan |
| 8.01 | Hero: eyebrow, headline, description, Plan My Trek, Explore Trekking Routes, microcopy | `build_home` | Screenshot, Journey 1 | PASS | Headline kept specific per owner's choice |
| 8.02 | Trust indicators, verified only | `TRUST` in data.py | Content review | PASS | "Licensed guide" omitted: not verified |
| 8.03 | 3–4 featured treks with photo, desc, duration, difficulty, altitude, traveller type, Explore Trek, View All | `FEATURED`, `trip_card` | Screenshot | PASS | Price shown as "personalised quote" |
| 8.04 | Find your perfect trek (days, experience, interests) + direct inquiry, not a safety check | `finder_html`, site.js | Journey 1 | PASS | Region preference not asked (covered by tours filters) |
| 8.05 | Meet your guide section + CTA to profile | home `#guide` | Journey 3 | PASS | |
| 8.06 | How it works, 4 steps + CTA | `STEPS` | Screenshot | PASS | |
| 8.07 | Why trek with me, included vs optional | `why_html`, `BEYOND` status | Screenshot | PARTIAL | Included/optional split is our reading of the old site; needs Jenish's confirmation |
| 8.08 | Traveller stories, consistent card, Read Traveller Stories, form moved | `review_card`, reviews.html | Review test | PASS | Guest photos: none with permission |
| 8.09 | More adventures, bookable alone or added | home `#more` | Screenshot | PASS | Based on statements already on the site |
| 8.10 | Best time with visual calendar and text alternative | `season_table` (+ "Show as text") | axe, screenshot | PASS | |
| 8.11 | FAQ with the 14 brief questions | data.py `FAQS` (18) | e2e accordion | PASS | Answers limited to verified/general info |
| 8.12 | Final CTA, inquiry ≠ booking | `final_cta` | Screenshot | PASS | |
| 8.13 | Footer with all listed parts | `footer()` | e2e links | PASS | |
| 9 | Tours: heading, count, filters, empty state, reset, comparison, inquiry CTA | `build_tours`, site.js | Journeys 2, 6 | PASS | Experience filter implemented as "Good for a first trek" |
| 10 | One template for every trip, 21 sections | `build_trip` | e2e trip template | PARTIAL | Route map, elevation profile and day-by-day itinerary omitted (no reliable data) |
| 10 | Key facts incl. start/end | `TRIP_FACTS` | Screenshot | PARTIAL | Start/end only where confirmed; walking time missing |
| 10 | Pricing explanation / "Request a personalised quote" | `#price-h` | Screenshot | PASS | No prices exist |
| 10 | Sticky inquiry: desktop panel, mobile bar with safe area | `.book-card`, `.qbar` | Journey 4, 2.4.11 test | PASS | |
| 10 | Trek preselected in form | `?trek=` | Journeys 1, 2, 4 | PASS | |
| 11 | Guide profile page with listed content | guide.html | Journey 3, screenshot | PARTIAL | Qualifications, languages, safety training, years: BLOCKED (not provided) |
| 12 | Form fields, minimal required, optional marked | plan-your-trip.html | Journeys 5, 6 | PASS | Budget folded into the free-text hint |
| 12 | WhatsApp / Email / Copy with structured message, encoding, validation | site.js plan | Journeys 1, 3, 6, copy test | PASS | |
| 12 | Inquiry ≠ booking notice; no fake success; fallback | status text, notice | Journey 1 | PASS | |
| 13 | CTA hierarchy and labels | build.py | e2e + inspection | PASS | |
| 14 | Copy review, no unsupported claims | data.py, build.py | Content review | PASS | |
| 15 | Legal: hosting corrected, no invented terms | legal_body.html | Inspection | PASS | |
| 15 | Missing legal facts filled | legal_body.html | – | BLOCKED | 9 placeholders; release blocker |
| 15 | Mountain safety content, no guarantees | trip `#prep-h`, FAQ | Content review | PASS | |
| 15 | Permit rules checked against sources | FAQ | Web sources (Kathmandu Post, NTB reports) | PASS | Recheck before each season |
| 16 | Responsive at 9 widths, no overflow, sticky behaviour | site.css | e2e responsive, Journey 4 | PASS | No real-device test |
| 17 | WCAG 2.2 AA checklist | all | axe, e2e, contrast scripts | PARTIAL | Automated + keyboard verified; screen reader not tested |
| 18 | WebP, srcset, sizes, lazy, hero priority, fonts, caching | `pic()`, vercel.json | Lighthouse | PASS | |
| 18 | LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms | – | Lighthouse lab | PARTIAL | LCP 1.7–2.7 s (home 2.7); CLS ≤ 0.037; INP needs field data (TBT ≤ 30 ms) |
| 18 | Lighthouse ≥ 90/95/95/95 | – | Lighthouse | PASS | 96–100 / 100 / 100 / 100 on 8 pages |
| 19 | Titles, descriptions, canonical, robots, sitemap, OG, favicon, alt, internal links | `page()` | e2e SEO | PASS | |
| 19 | Redirects for changed URLs | vercel.json | Local fallback test | PARTIAL | Vercel redirect not tested until deployed |
| 19 | Custom domain readiness | `DOMAIN` in data.py | – | PASS | One-line change |
| 19 | Structured data, only visible facts | JSON-LD | JSON parse test | PARTIAL | Google Rich Results Test not run (needs public URL) |
| 20 | Privacy-safe event hook, no PII | `smTrack` | e2e tracking test | PASS | No provider enabled; consent N/A until one is |
| 21 | Single source of truth, no hardcoded contact details in JS | data.py, build.py | grep | PASS | |
| 21 | Vercel compatibility | vercel.json | – | PARTIAL | Root Directory stays `./`; verify the first deploy |
| 22A | Build | build.py | Run | PASS | |
| 22A | Lint / type check / unit tests | – | – | N/A | None exist in this stack |
| 22B–C | Functional tests and 7 journeys | tests/e2e_test.py | Run | PASS | 20/20 |
| 22D | Desktop and mobile screenshots inspected | docs/screenshots | Visual review | PASS | Fixed: footer email wrapping, FAQ spacing |
| 22E | Accessibility verification | a11y scripts | Run | PARTIAL | See 17 |
| 22F | Performance measured | Lighthouse | Run | PASS | Lab only |
| 22G | SEO verification | e2e | Run | PASS | |
| 22H | Content verification | review | Manual | PASS | Open items in checklist |
| 24 | Deliverable documents | repo root | – | PASS | 5 documents |

**Completion summary:** 59 rows — 46 PASS (78%), 11 PARTIAL, 1 BLOCKED, 1 N/A, 0 FAIL. Not 100%:
the partial and blocked rows depend on business facts from Jenish, a public deployment, or
manual testing with assistive technology and real devices.

## Remaining defects and risks

1. **Legal placeholders (release blocker):** address, licence, partner agency, PAN, deposit,
   payment, cancellation, complaint reply time, health-data retention.
2. Vercel Hobby plan is for non-commercial use; a business site needs Pro.
3. Home-page LCP 2.7 s (lab) on slow 4G.
4. Wildlife photo credit unverified.
5. Included/optional service split needs Jenish's confirmation.
6. No screen-reader or real-device testing yet.
