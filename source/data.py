# -*- coding: utf-8 -*-
"""All website content lives here. Edit this file, then run build.py."""

SITE_NAME = "Somewhere in Mountains"
# Set this once the website has its own domain, e.g. "https://www.somewhereinmountains.com"
# It turns on canonical links, the sitemap and social-share preview links.
DOMAIN = "https://somewhereinmountains.vercel.app"

WA_NUMBER = "9779843204871"
WA_DISPLAY = "+977 984-3204871"
EMAIL = "jenishmaharjan26@gmail.com"
INSTAGRAM = "https://www.instagram.com/somewhereinmountains/"
INSTAGRAM_HANDLE = "@somewhereinmountains"

# Analytics: off. The site sets no cookies, so it shows no consent banner.
# To add analytics later, set one of these and update the privacy policy (legal_body.html):
#   ANALYTICS = "plausible:somewhereinmountains.com"   # Plausible, loaded only after consent
#   ANALYTICS = "vercel"                               # Vercel Web Analytics, loaded only after consent
# A consent banner then appears automatically and nothing loads until the visitor agrees.
ANALYTICS = ""

# ---------------------------------------------------------------------------
# REVIEWS — newest first. Only publish reviews the guest agreed to share.
# stars: 1–5 · when: "YYYY-MM"
# ---------------------------------------------------------------------------
REVIEWS = [
    {"name": "Harpreet", "country": "Austria", "trip": "langtang", "when": "2026-03", "stars": 5,
     "text": "I was in the Langtang Valley with Jenish in March and it was wonderful. He was a really good guide and took real care of us."},
]

TYPE = {"trek": "Trekking", "raft": "Rafting", "safari": "Rafting and safari"}
TYPE_ICON = {"trek": "mountain-snow", "raft": "waves", "safari": "paw-print"}

# img: file in img/ (None = no own photo yet → icon panel)
TRIPS = [
    {"id": "abc", "slug": "annapurna-base-camp-trek", "type": "trek", "title": "Annapurna Base Camp Trek", "short": "Annapurna Base Camp",
     "region": "Annapurna", "duration": "8 days", "level": "Moderate", "pl": "Max altitude", "peak": "4,130 m", "season": "Oct–Nov, Mar–May",
     "img": "tour-abc", "alt": "Annapurna I towering over Annapurna Base Camp in deep snow",
     "meta": "Private 8-day Annapurna Base Camp trek from Pokhara with Jenish, a local guide from Kathmandu. Gurung villages, hot springs and sunrise below Annapurna I. Book on WhatsApp.",
     "desc": "From Pokhara through Gurung villages, rhododendron forest and the Modi Khola gorge into a ring of 7,000 m and 8,000 m peaks. The most rewarding trek for its length.",
     "hl": ["Sunrise at Annapurna Base Camp below Annapurna I (8,091 m)", "Natural hot springs at Jhinu Danda", "ACAP permit and teahouse stays arranged"],
     "gallery": [("trip-abc-1", "Teahouse terrace with views of Annapurna South and Machhapuchhre"), ("trip-abc-2", "The Namaste Annapurna Base Camp sign below Annapurna I"),
                 ("trip-abc-3", "Prayer flags strung above the Modi Khola valley"), ("trip-abc-4", "A flower-filled teahouse terrace on the trail"),
                 ("trip-abc-5", "A sheer rock face below Annapurna South, wrapped in cloud"), ("trip-abc-6", "Teahouses half-buried in snow at Annapurna Base Camp"), ("trip-abc-7", "An Annapurna cap and the Nepali flag at base camp"), ("trip-abc-8", "A trekker reaching the Annapurna Base Camp sign")]},
    {"id": "manaslu", "slug": "manaslu-circuit-trek", "type": "trek", "title": "Manaslu Circuit Trek", "short": "Manaslu Circuit",
     "region": "Manaslu", "duration": "14 days", "level": "Challenging", "pl": "Max altitude", "peak": "5,106 m (Larkya La)", "season": "Sep–Nov, Mar–May",
     "img": "tour-manaslu", "alt": "Trekkers sitting on a rock below the massive snow face of the Manaslu range",
     "meta": "Private Manaslu Circuit trek with a local guide: 14 days around the world's eighth-highest mountain, Tibetan-Buddhist villages and the Larkya La pass. Plan it on WhatsApp.",
     "desc": "A wild, quieter alternative to the Annapurna Circuit around the world's eighth-highest mountain — from green Gurung farmland up through Tibetan-Buddhist villages to the high Larkya La pass.",
     "hl": ["Crossing the Larkya La pass with views of Manaslu (8,163 m)", "Monasteries and mani walls in Samagaun and Lho", "Restricted-area permit arranged for you"],
     "gallery": [("trip-manaslu-1", "The Manaslu range rising above the forest"), ("trip-manaslu-2", "A glacier river through pine forest below snow peaks"),
                 ("trip-manaslu-3", "Golden autumn slopes below a rocky summit"), ("trip-manaslu-4", "Blue gentian flowers beside the trail"),
                 ("trip-manaslu-5", "Manaslu glowing orange at first light"), ("trip-manaslu-6", "Manaslu's snow face against a dark blue sky"), ("trip-manaslu-7", "Manaslu rising out of a sea of cloud"), ("trip-manaslu-8", "A river valley below snow peaks on the Manaslu Circuit"), ("trip-manaslu-9", "A trekker walking through sunlit forest"), ("trip-manaslu-10", "A rocky snow peak above dense forest"), ("trip-manaslu-11", "A trekker standing on a rock above the clouds"), ("trip-manaslu-12", "Mani walls and a stupa in a high Manaslu village")]},
    {"id": "nabc", "slug": "north-annapurna-base-camp-trek", "type": "trek", "title": "North Annapurna Base Camp Trek", "short": "North Annapurna Base Camp",
     "region": "Annapurna North", "duration": "11 days", "level": "Challenging", "pl": "Max altitude", "peak": "≈ 4,190 m", "season": "Oct–Nov, Apr–May",
     "img": "tour-nabc", "alt": "Glacial lake below the north face of Annapurna",
     "meta": "North Annapurna Base Camp trek — a remote camping expedition up the Miristi Khola gorge to the north face of Annapurna I, with a local guide. Ask on WhatsApp.",
     "desc": "One of the most remote treks in Nepal: a camping expedition up the Miristi Khola gorge to the north side of Annapurna I, the route of the first ascent in 1950. Very few people make it here.",
     "hl": ["Tented camping beyond the last villages — true wilderness", "Hidden waterfalls and wild gorges along the Miristi Khola", "Glacier views below the north face of Annapurna I (8,091 m)"],
     "gallery": [("trip-nabc-1", "Trekkers with heavy packs climbing toward a snow peak"), ("trip-nabc-2", "A trekker resting on a boulder beside a glacial lake"),
                 ("trip-nabc-3", "Icefalls below the north side of Annapurna"), ("trip-nabc-4", "Tents pitched at a forest camp"),
                 ("trip-nabc-5", "The crew resting on a dry hillside below snow peaks"), ("trip-nabc-6", "A stone hut with the Nepali flag below Annapurna"), ("trip-nabc-7", "The ice walls below Annapurna's north side"), ("trip-nabc-8", "A snow peak above the Miristi Khola valley")]},
    {"id": "langtang", "slug": "langtang-valley-trek", "type": "trek", "title": "Langtang Valley Trek", "short": "Langtang Valley",
     "region": "Langtang", "duration": "7 days", "level": "Moderate", "pl": "Max altitude", "peak": "3,870 m (4,773 m optional)", "season": "Oct–Dec, Mar–May",
     "img": "tour-langtang", "alt": "Kyanjin Gompa village beneath snow peaks in the Langtang Valley",
     "meta": "Langtang Valley trek with a local guide — 7 days from Kathmandu, no flight needed. Tamang villages, yak pastures and Kyanjin Gompa. Book your private trek on WhatsApp.",
     "desc": "The closest big-mountain trek to Kathmandu — no flight needed. Tamang villages, yak pastures and glaciers above Kyanjin Gompa.",
     "hl": ["Optional climb of Kyanjin Ri for a 360° glacier view", "Local cheese factory and Tamang heritage", "Starts with a scenic drive from Kathmandu"],
     "gallery": [("trip-langtang-1", "Langtang Lirung and jagged peaks above the valley"), ("trip-langtang-2", "A yellow teahouse in Kyanjin Gompa below snow peaks"),
                 ("trip-langtang-3", "Stone cairns with prayer flags above the valley"), ("trip-langtang-4", "A trekker sitting quietly above the Langtang valley"),
                 ("trip-langtang-5", "A green summit under a deep blue sky in the Langtang Valley"), ("trip-langtang-6", "A trekker looking up at the slopes above Kyanjin Gompa"), ("trip-langtang-7", "A cloud catching on a snow peak above Langtang")]},
    {"id": "ebc", "slug": "everest-base-camp-trek", "type": "trek", "title": "Everest Base Camp Trek", "short": "Everest Base Camp",
     "region": "Khumbu", "duration": "13 days", "level": "Challenging", "pl": "Max altitude", "peak": "5,644 m (Kala Patthar)", "season": "Oct–Nov, Mar–May",
     "img": "tour-ebc", "alt": "Lhotse and Nuptse above the Khumbu valley at dusk",
     "meta": "Private Everest Base Camp trek with a local guide: Lukla, Namche Bazaar, Tengboche and Kala Patthar sunrise, with daily altitude checks. Plan your EBC trek on WhatsApp.",
     "desc": "The classic: fly to Lukla, walk through Namche Bazaar and Tengboche Monastery to the foot of the world. Two acclimatisation days built in.",
     "hl": ["Everest Base Camp (5,364 m) and Kala Patthar sunrise", "Sherpa culture in Namche, Khumjung and Tengboche", "Permits and Lukla flights arranged"],
     "gallery": [("trip-ebc-1", "A yak grazing beside the trail in the Khumbu"), ("trip-ebc-2", "Teahouses below snow peaks at dusk in the Khumbu"),
                 ("trip-ebc-3", "Tents of Everest Base Camp on the Khumbu Glacier"), ("trip-ebc-4", "Wind-blown clouds over the peaks near Everest"),
                 ("trip-ebc-5", "A line of trekkers on the trail through the Khumbu"), ("trip-ebc-6", "Clouds rolling over the Khumbu Glacier")]},
    {"id": "pikey", "slug": "pikey-peak-trek", "type": "trek", "title": "Pikey Peak Trek", "short": "Pikey Peak",
     "region": "Lower Solukhumbu", "duration": "6 days", "level": "Moderate", "pl": "Max altitude", "peak": "4,065 m", "season": "Oct–Dec, Mar–May",
     "img": "tour-pikey", "alt": "Trekkers walking a grassy ridge toward a long Himalayan panorama at Pikey Peak",
     "meta": "Pikey Peak trek with a local guide — a short, quiet 6-day trek in Sherpa country with a Himalayan panorama including Everest, reached by road from Kathmandu.",
     "desc": "A short, uncrowded trek through Sherpa country with one of the widest Himalayan panoramas in Nepal — Everest included — without the Lukla flight.",
     "hl": ["Sunrise from Pikey Peak over Everest and the Khumbu range", "Sherpa villages, monasteries and cheese farms", "Reached by road from Kathmandu"],
     "gallery": [("trip-pikey-1", "The Himalayan panorama from the Pikey Peak ridge"), ("trip-pikey-2", "A trekker sitting on a wide grassy ridge facing the mountains"),
                 ("trip-pikey-3", "Trekkers resting on a stone ledge facing the snow range")]},
    {"id": "poonhill", "slug": "ghorepani-poon-hill-trek", "type": "trek", "title": "Ghorepani Poon Hill Trek", "short": "Poon Hill",
     "region": "Annapurna", "duration": "4 days", "level": "Easy–moderate", "pl": "Max altitude", "peak": "3,210 m", "season": "Oct–Apr",
     "img": "tour-poonhill", "alt": "Trekker on a bench looking at Annapurna South and Machhapuchhre",
     "meta": "Ghorepani Poon Hill trek with a local guide — a 4-day loop from Pokhara with the famous Dhaulagiri and Annapurna sunrise. Great for families and first-timers.",
     "desc": "Short on time? This loop from Pokhara gives the famous Dhaulagiri–Annapurna sunrise panorama in four days. Great for families and first-timers.",
     "hl": ["Sunrise over Dhaulagiri and Annapurna South", "Magar villages of Ghorepani and Ghandruk", "Easy to pair with Trishuli rafting"],
     "gallery": [("trip-poonhill-1", "A stone staircase through terraced fields to a hillside village"), ("trip-poonhill-2", "A stormy sunset sky over the hills near Ghorepani"),
                 ("trip-poonhill-3", "A teahouse meadow above a green valley"), ("trip-poonhill-4", "A trekker pointing at Annapurna South at sunrise"),
                 ("trip-poonhill-5", "A trekker on a mossy stone staircase through the forest"), ("trip-poonhill-6", "Climbing the stone steps towards Ghorepani"), ("trip-poonhill-7", "Tree-stump seats at a forest rest stop"), ("trip-poonhill-8", "Jenish at the Poon Hill viewpoint sign, 3,210 m")]},
    {"id": "trishuli-day", "slug": "trishuli-river-rafting-day-trip", "type": "raft", "title": "Trishuli River Rafting — Day Trip", "short": "Trishuli rafting day trip",
     "region": "Trishuli", "duration": "1 day", "level": "Grade III–IV", "pl": "On the water", "peak": "~3 hours, 20+ km", "season": "Oct–May",
     "img": "tour-raft-day", "alt": "A raft on the Trishuli River in a steep green valley",
     "meta": "Trishuli River white-water rafting day trip from Kathmandu (Grade III–IV), with pick-up in Thamel and lunch on a river beach. First-timers welcome. Book on WhatsApp.",
     "desc": "Nepal's favourite white-water day out. Pick-up in Kathmandu, a full safety briefing, then a fun run of rapids before lunch on a sandy beach.",
     "hl": ["Pick-up from Thamel, back by evening — or drop-off on to Pokhara", "Helmet, life jacket and paddle jacket included", "First-timers welcome"], "gallery": [('raft-3', 'A raft on the Trishuli in a steep green valley'), ('raft-2', 'Two rafts paddling the Trishuli below green hills'), ('raft-1', 'A rafting group on the rocky Trishuli bank beside their raft')]},
    {"id": "trishuli-2", "slug": "trishuli-rafting-beach-camp", "type": "raft", "title": "Trishuli 2-Day Rafting & Beach Camp", "short": "Trishuli 2-day rafting",
     "region": "Trishuli", "duration": "2 days", "level": "Grade III–IV", "pl": "On the water", "peak": "~6 hours, 40+ km", "season": "Oct–May",
     "img": "tour-raft-2", "alt": "Two rafts paddling the Trishuli River below green hills",
     "meta": "Two days of Trishuli River rafting with a night at a riverside beach camp — campfire, dal bhat and Grade III–IV rapids, a few hours from Kathmandu.",
     "desc": "Two days of rapids with a night on a white-sand beach: campfire, dal bhat cooked by the crew, and stars over the gorge.",
     "hl": ["Riverside tents, sleeping mats and all meals", "Swimming in calm stretches", "Ends near the Chitwan road — easy add-on"], "gallery": [('raft-2', 'Two rafts paddling the Trishuli below green hills'), ('raft-1', 'A rafting group on the rocky Trishuli bank beside their raft'), ('raft-3', 'A raft on the Trishuli in a steep green valley')]},
    {"id": "combo", "slug": "trishuli-rafting-chitwan-safari", "type": "safari", "title": "Trishuli Rafting and Chitwan Safari", "short": "Rafting and Chitwan safari",
     "region": "Trishuli → Chitwan", "duration": "4 days", "level": "Easy", "pl": "Wildlife", "peak": "Rhino, gharial, 500+ birds", "season": "Oct–Apr",
     "img": "tour-combo", "alt": "A herd of spotted deer in the forest of Chitwan National Park",
     "meta": "4-day Trishuli rafting and Chitwan National Park safari: river rapids, jeep safari, canoeing on the Rapti and a Tharu village walk. Plan it on WhatsApp.",
     "desc": "Raft the Trishuli downstream, then drive into Chitwan National Park — a UNESCO World Heritage Site and home to the one-horned rhino and Bengal tiger.",
     "hl": ["Day 1–2: Trishuli rafting and beach camp", "Day 3: jeep safari and dugout canoe on the Rapti River", "Day 4: Tharu village walk and birdwatching, then return"], "gallery": [('raft-3', 'A raft on the Trishuli in a steep green valley'), ('raft-1', 'A rafting group on the rocky Trishuli bank beside their raft'), ('safari-rhino', 'A one-horned rhino in the tall grass of Chitwan'), ('safari-deer', 'A herd of spotted deer in the Chitwan forest'), ('safari-canoes', 'Dugout canoes on the bank of the Rapti River'), ('safari-boatman', 'A boatman with dugout canoes on the Rapti River'), ('safari-jeep-track', 'A safari jeep on a jungle track in Chitwan'), ('safari-jeep-stream', 'A safari jeep at a stream in the Chitwan forest'), ('safari-deer-forest', 'Spotted deer half hidden in the jungle undergrowth')]},
]

SERVICES = [
    {"f": "trek", "img": "svc-trek", "title": "Himalayan treks", "alt": "Trekker on the Manaslu Circuit trail below snow peaks",
     "desc": "Annapurna, Manaslu, Langtang, Everest, Pikey Peak — teahouse and camping treks with permits, porters and acclimatisation sorted.", "meta": "4–14 days"},
    {"f": "raft", "img": "raft-2", "title": "Trishuli River rafting",
     "desc": "Nepal's classic white-water run, Grade III–IV, a few hours from Kathmandu. Day trips or an overnight riverside beach camp.", "meta": "1–2 days"},
    {"f": "safari", "img": "safari-rhino", "title": "Rafting and jungle safari",
     "desc": "Raft the Trishuli downstream toward Chitwan National Park, then jeep safari, canoe the Rapti and walk with a Tharu naturalist.", "meta": "4 days"},
]

# items: (title, text, status) — status "inc" = included with every trek, "ask" = optional, confirm when planning
BEYOND = [
    {"img": "serv-story", "icon": "camera", "alt": "Jenish facing a snow peak among prayer flags", "title": "Visual storytelling & trail keepsakes", "items": [
        ("Cinematic trail stories", "Instead of rushed phone snapshots, I capture smooth, stabilized video reels and natural, high-resolution portraits of you against sweeping Himalayan backdrops — delivering an edited highlight film at the end of our journey so you can stay present in the moment.", "inc"),
        ("Your personal Himalayan trail log", "Receive a custom digital memory book after your trek, mapping out our exact daily elevation gains, GPS routes, peak names you stood before, and candid moments from the trail.", "inc")]},
    {"img": "serv-wellness", "icon": "heart-pulse", "alt": "Trekkers resting on a rock ledge facing a snowy Himalayan range at Pikey Peak", "title": "Mountain wellness & high-altitude care", "items": [
        ("Daily altitude & vitals check-ins", "Trek with peace of mind through structured morning and evening wellness checks using a pulse oximeter and blood pressure monitor, tracking your oxygen levels (SpO₂) and resting heart rate so we notice early signs of altitude sickness and adjust the pace.", "inc"),
        ("The trail comfort pouch", "Small comforts make a big difference at 4,000 meters. I carry a dedicated trail kit stocked with warm ginger-lemon-honey packets, local masala tea, electrolytes, and blister care for our rest stops.", "inc"),
        ("Sunrise mobility & acclimatization breathwork", "Start your mornings with 10-minute gentle trail stretches and end your days with guided breathing exercises on the teahouse deck to help you settle into the thin mountain air.", "ask")]},
    {"img": "serv-culture", "icon": "hand-heart", "alt": "A local woman preparing tea at a teahouse hearth, black and white", "title": "Soulful cultural & village immersion", "items": [
        ("Teahouse kitchen & hearth sessions", "Step behind the counter with our local Didis (sisters) and Amas (mothers) to learn the art of folding momos by hand, frying crispy Gurung bread, or cooking traditional wood-fired dal bhat.", "ask"),
        ("Living heritage & unscripted conversations", "Sit quietly inside centuries-old monasteries during morning puja chants, share salted butter tea with yak herders, and meet local artisans — with me translating real human stories rather than reciting textbook facts.", "ask"),
        ("Whispering woods & skyline lore", "Discover the hidden ecology of the Himalayas as we spot Nepal's iridescent national bird (the danphe), identify high-altitude medicinal herbs used by local healers, and trace the names of every jagged peak on the horizon.", "ask")]},
    {"img": "serv-concierge", "icon": "compass", "alt": "Trekkers walking into a Sherpa village on the Everest trail", "title": "Local insider concierge — before & after the trail", "items": [
        ("Street-smart gear & logistics prep", "Meet a day before departure in Thamel or Lakeside to inspect and rent genuine down gear at local prices, set up your Nepali SIM/eSIM, and exchange currency safely without tourist markups.", "inc"),
        ("Hidden courtyard food walks & recovery", "Celebrate your return from the mountains with a guided culinary walk through the secret alleys, bahals (courtyards), and street-food stalls of historic Patan or Kathmandu — or unwind with a trusted Ayurvedic recovery massage.", "ask")]},
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
LV = [("–", "Off-season"), ("○", "Possible"), ("◐", "Good"), ("●", "Best")]
SEASONS = {"trek": ("Himalayan trekking", [1, 2, 3, 3, 2, 0, 0, 0, 2, 3, 3, 2]),
           "raft": ("Trishuli rafting", [1, 2, 3, 3, 3, 1, 0, 0, 1, 3, 3, 2]),
           "safari": ("Chitwan safari", [3, 3, 3, 2, 1, 0, 0, 0, 1, 2, 3, 3])}

GALLERY = [("gal-2", "Manaslu turning gold at first light", 1), ("gal-1", "Prayer flags on the trail to Annapurna Base Camp", 0),
           ("gal-3", "Stupa and prayer flags in the Langtang Valley", 0), ("gal-6", "A stone path climbing into the clouds near Ghorepani", 1),
           ("gal-4", "Blue gentians on the Everest Base Camp trail", 0), ("gal-7", "Teahouses below the peaks on the Manaslu Circuit", 0),
           ("gal-5", "A hidden waterfall on the North Annapurna Base Camp route", 1), ("gal-8", "Porters on the moraine near Everest Base Camp", 0),
           ("gal-9", "Sunrise over the Annapurnas from a teahouse window", 0), ("gal-11", "Jenish beside a mirror-still lake below the peaks", 0),
           ("gal-13", "A lone trekker on a ridge as clouds rise from the valley", 0), ("gal-12", "Jenish at sunrise facing Annapurna South and Machhapuchhre", 0),
           ("gal-10", "Jenish with a lantern at dusk below a glowing peak", 0)]

# FAQ — (question, answer, show on home page?). The FAQ page shows all of them.
# Keep answers factual. Booking terms (deposit, cancellation) live on legal.html.
FAQS = [
    ("Do I need previous trekking experience?", "No. Poon Hill, Langtang Valley, Pikey Peak and Annapurna Base Camp are good first treks if you're active and walk regularly. Everest Base Camp, Manaslu and North Annapurna Base Camp suit people with some multi-day hiking behind them. Tell me what you've done and I'll suggest a route that fits.", True),
    ("Can I travel alone?", "Yes. Many guests come on their own. You still trek with a guide, which Nepal's rules require on most routes, so you're never really alone on the trail.", False),
    ("Can the itinerary be personalised?", "Always. Every trip is private, so we can add rest days, shorten or stretch the route, or combine a trek with Trishuli rafting or a Chitwan safari.", True),
    ("What if I don't know which trek to choose?", "That's normal. Use the trek finder on the home page, or just message me your dates, fitness and what you'd love to see. I'll suggest one or two routes and explain why.", True),
    ("How much does a trek cost?", "Every trip is priced for your group. The price depends on the route, number of days, group size, season, permits and transport such as the Lukla flight. Send your plans and you get a written quote listing what's included.", True),
    ("How do I confirm a booking?", "When the itinerary and price suit you, you confirm in writing and pay the deposit described in the booking terms. Sending an inquiry is free and doesn't commit you to anything.", False),
    ("What equipment do I need?", "Good broken-in walking boots, layers for cold mornings, a warm jacket, a rain shell, a sleeping bag for higher teahouses, a headlamp and a water bottle. We meet the day before in Thamel or Lakeside to check your gear and rent anything missing at local prices.", False),
    ("Do I need a guide to trek in Nepal?", "On most routes, yes. Since April 2023, foreign trekkers in Nepal's national parks and conservation areas need a licensed guide, and the TIMS card is issued through a government-registered trekking agency. The Everest (Khumbu) region applies its own local rules. Rules change, so I check the current ones when we plan your trip.", False),
    ("What about trekking permits?", "It depends on the region. Annapurna treks need an ACAP permit, Langtang a national park permit, the Everest region a Sagarmatha National Park and local area permit, and Manaslu is a restricted area with a special permit. I arrange them for you through my partner agency.", False),
    ("What type of accommodation is available?", "On most treks we stay in teahouses and family lodges: simple rooms, shared bathrooms higher up, and meals cooked on the spot. North Annapurna Base Camp is a camping trek, and the 2-day Trishuli trip includes a night in riverside tents.", False),
    ("How is altitude sickness handled?", "Itineraries go up slowly and include acclimatisation days. I check how you feel every morning and evening, and if symptoms appear we slow down, rest or go down. Nothing can rule out altitude sickness completely, so please read up on the signs, and tell me about any health conditions before the trip.", True),
    ("Do I need travel insurance?", "Yes, it's required. Your policy must cover trekking up to your highest altitude, helicopter rescue and evacuation, medical treatment and, if you raft, white-water rafting.", False),
    ("What happens if my travel dates change?", "Tell me as early as you can and we'll look for new dates. What can be moved or refunded depends on permits and flights already booked. The booking terms explain the details.", False),
    ("How do I get to Nepal?", "International flights land at Tribhuvan International Airport in Kathmandu. Most treks start from Kathmandu or Pokhara, a short flight or a day's drive away.", False),
    ("Can I talk to Jenish before deciding?", "Of course. Message me on WhatsApp or email with any question, big or small. Asking is free and you're not booking anything.", True),
    ("When is the best time for trekking and rafting in Nepal?", "October to November and March to May. Autumn has the clearest mountain views and spring is warmer, with rhododendrons in bloom. The Trishuli is rafted from October to May. June to August is monsoon, when rivers run high and most trails are wet.", False),
    ("How far is the Trishuli River from Kathmandu?", "About 80 km west along the Prithvi Highway, a 2.5 to 3 hour drive. It's on the way to both Pokhara and Chitwan National Park, so it fits neatly between a trek and a safari.", False),
    ("Do I need rafting experience?", "No. The Trishuli is Grade III to IV, exciting but forgiving, and first-timers are welcome. Every trip starts with a safety briefing and paddle training.", False),
]


# ---------------------------------------------------------------------------
# EXTRA TRIP FACTS — used by cards, filters, the comparison table, the trek
# finder and the trip pages. Only fill in what Jenish has confirmed.
#   days:  number for filters        diff: easy | moderate | challenging
#   area:  region filter key         first: good for a first trek?
#   for:   who it suits (plain words)
#   start / end: leave "" if not confirmed
#   stay:  where you sleep           tags: for the trek finder (iconic, quiet, culture)
# ---------------------------------------------------------------------------
TRIP_FACTS = {
    "abc":      dict(days=8,  diff="moderate",    area="annapurna", first=True,  tags=["iconic"],
                     **{"for": "Fit first-timers who want big peaks up close"}, start="Pokhara", end="",
                     stay="Teahouses and family lodges along the trail"),
    "manaslu":  dict(days=14, diff="challenging", area="manaslu",   first=False, tags=["quiet", "culture"],
                     **{"for": "Experienced trekkers who want a quieter, remote circuit"}, start="", end="",
                     stay="Teahouses and family lodges along the trail"),
    "nabc":     dict(days=11, diff="challenging", area="annapurna", first=False, tags=["quiet"],
                     **{"for": "Experienced trekkers happy to camp beyond the last villages"}, start="", end="",
                     stay="Tented camping beyond the last villages"),
    "langtang": dict(days=7,  diff="moderate",    area="langtang",  first=True,  tags=["quiet", "culture"],
                     **{"for": "A first Himalayan trek within a week, no flight needed"}, start="Kathmandu, by road", end="",
                     stay="Teahouses and family lodges along the trail"),
    "ebc":      dict(days=13, diff="challenging", area="everest",   first=False, tags=["iconic", "culture"],
                     **{"for": "Fit trekkers ready for high altitude"}, start="Lukla, by flight", end="",
                     stay="Teahouses and family lodges along the trail"),
    "pikey":    dict(days=6,  diff="moderate",    area="everest",   first=True,  tags=["quiet", "culture"],
                     **{"for": "A short, uncrowded trek with an Everest view"}, start="Kathmandu, by road", end="",
                     stay="Teahouses and family lodges along the trail"),
    "poonhill": dict(days=4,  diff="easy",        area="annapurna", first=True,  tags=["iconic", "culture"],
                     **{"for": "Families and first-timers short on time"}, start="Pokhara", end="Pokhara (loop)",
                     stay="Teahouses and family lodges along the trail"),
    "trishuli-day": dict(days=1, diff="easy",     area="chitwan",   first=True,  tags=[],
                     **{"for": "First-timers wanting a day on the river"}, start="Thamel, Kathmandu (pick-up)", end="Kathmandu, or on to Pokhara",
                     stay="Back in Kathmandu by evening"),
    "trishuli-2": dict(days=2,  diff="easy",      area="chitwan",   first=True,  tags=[],
                     **{"for": "Anyone who wants a night by the river"}, start="", end="Near the Chitwan road",
                     stay="Riverside tents, sleeping mats and all meals"),
    "combo":    dict(days=4,  diff="easy",        area="chitwan",   first=True,  tags=[],
                     **{"for": "Ending a trek with river and jungle"}, start="", end="",
                     stay="Riverside beach camp, then a stay near Chitwan National Park"),
}
for _t in TRIPS: _t.update(TRIP_FACTS[_t["id"]])

DIFF = {"easy": "Easy", "moderate": "Moderate", "challenging": "Challenging"}
AREAS = {"annapurna": "Annapurna", "manaslu": "Manaslu", "langtang": "Langtang", "everest": "Everest region", "chitwan": "Trishuli and Chitwan"}
FEATURED = ["poonhill", "langtang", "abc", "manaslu"]   # home page: short, moderate, classic, challenging

# What it takes, by difficulty. Shown on trip pages.
DIFF_TEXT = {
    "easy": "Short days on good paths. If you are active and can walk a few hours with breaks, you'll be fine.",
    "moderate": "Five to six hours of walking on most days, with steep stone stairs. Regular walks or hikes at home are good preparation.",
    "challenging": "Long days at high altitude, often far from roads. Altitude and remoteness make it hard, not technical climbing. Some multi-day hiking experience helps.",
}

TRUST = [
    ("map-pin", "Local guide from Kathmandu", "You plan and walk with Jenish himself"),
    ("users-round", "Private trips", "Just you and your group, at your pace"),
    ("route", "Planned together", "Route, days and pace shaped around you"),
    ("file-check", "Permits arranged", "Through a government-registered agency"),
]

STEPS = [
    ("Tell me about your dream trip", "Share your interests, rough dates and experience. It's completely fine if you haven't picked a trek yet."),
    ("Get your personal plan", "I suggest a route that suits you and send a day-by-day itinerary with a price for your group."),
    ("Confirm your adventure", "We agree on the itinerary, dates and booking terms together. Nothing is booked until you say yes."),
    ("See you in Nepal", "We meet the day before in Thamel or Lakeside to check gear and get you ready, then head for the mountains."),
]

GUIDE = {
    "name": "Jenish Maharjan",
    "based": "Kathmandu",
    "img": "guide",
    "alt": "Jenish Maharjan, trekking guide, with his pack on a Himalayan trail",
}
