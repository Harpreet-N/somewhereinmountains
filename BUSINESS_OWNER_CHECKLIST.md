# Checklist for Jenish

Information only Jenish (or Harpreet) can confirm. Nothing here has been made up on the
website: where a fact is missing, the site either leaves it out or shows a yellow
placeholder on the legal page.

**Required before launch** = needed before the site is promoted as a business.
**Recommended before promotion** = makes the site much more convincing.
**Optional** = nice to have later.

## Required before launch

| Item | Where it appears | What to send |
|---|---|---|
| Official business name | Legal notice, footer, schema | Is it "Somewhere in Mountains", "Somewhere in Mountains Nepal", or Jenish's own name? |
| Business address | Legal notice (placeholder) | Street, ward, city, postcode |
| Guide licence number | Legal notice (placeholder) | Number and issuing office (Department of Tourism) |
| Partner trekking agency | Legal notice, booking terms (placeholders) | Name, registration number, TAAN membership |
| Tax registration (PAN) | Legal notice (placeholder) | PAN, or confirm none |
| Deposit | Booking terms (placeholder) | Percentage and when it's paid |
| Balance and payment methods | Booking terms (placeholder) | When the rest is due; cash USD/NPR, card, bank transfer? |
| Cancellation and refund rules | Booking terms (placeholder) | Charges by days before departure |
| Complaint reply time | Booking terms (placeholder) | e.g. 14 days |
| Health-data deletion period | Privacy policy (placeholder) | e.g. 30 days after the trek |
| Hosting plan | Privacy policy, Vercel | Vercel's Hobby plan is for non-commercial use; move to Pro (or another host) for the business site |
| What's included vs optional | Home and guide "Why trek with me", trip pages | Confirm which extras come with every trek (film, trail log, oxygen checks, comfort pouch, gear check) and which cost extra (cooking sessions, food walk, massage, breathwork) |

## Recommended before promotion

| Item | Where it would appear | What to send |
|---|---|---|
| Prices | Trip pages, comparison table | Indicative price per person for 1, 2 and 4 people, or "from" prices, and what's included |
| Daily itineraries | Trip pages → Itinerary | Day-by-day: start/end place, walking hours, distance, altitude, overnight stop, rest days |
| Start and end points | Key facts | Missing for Manaslu, North Annapurna, Everest (end), Langtang (end), ABC (end), 2-day rafting (start), combo |
| Distances and overnight altitudes | Key facts, itinerary | Highest sleeping altitude per trek (e.g. Gorak Shep on EBC) |
| Accommodation details | Trip pages | Teahouse standard, private rooms possible? Chitwan lodge name |
| Qualifications and training | Guide page | Licence, first aid / wilderness first aid, altitude or rescue training, with dates |
| Years of experience | Guide page | Since when guiding; number of seasons |
| Languages | Guide page, schema | Which languages and how well |
| Safety procedures | Trip pages | Evacuation plan, what's carried (oximeter, first-aid kit), emergency contacts |
| Insurance requirements | FAQ, booking terms | Minimum cover amounts if any |
| More genuine reviews | Reviews page | Guests who agree to be published, with first name, country, trip, month |
| Photo permissions | Gallery, trip pages | Who took the wildlife photos (`SAA_…` files)? Permission for photos showing guests' faces |
| Custom domain | Everywhere (canonical, sitemap) | Buy a domain, add it in Vercel, then set `DOMAIN` in `source/data.py` and rebuild |
| Professional email | Contact, legal | e.g. hello@yourdomain.com instead of Gmail |
| Google Business Profile | Off-site | Lets reviews appear in Google Maps and search |

## Optional future improvements

| Item | Notes |
|---|---|
| Route maps and elevation profiles | Only from real GPS tracks (GPX files from past treks) |
| Analytics | Vercel Web Analytics or Plausible (cookieless); the site already sends privacy-safe events to `smTrack` |
| Guest photos with reviews | Only with written permission |
| More treks (Mardi Himal, Upper Mustang, Tsum Valley) | Mentioned as possible; add pages when confirmed |
| Trek-specific FAQs | e.g. Lukla flight delays, Manaslu group-size rule for restricted permits |
