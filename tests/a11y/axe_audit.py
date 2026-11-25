"""Accessibility checks. Serve the site first:  cd site && python3 -m http.server 8765
Needs: npm install axe-core (in tests/a11y) and pip install playwright pillow."""
import os
SITE=os.environ.get('SITE_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','site'))
BASE='http://localhost:8765/'
import glob,os
from playwright.sync_api import sync_playwright
axe=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'node_modules','axe-core','axe.min.js')).read()
pages=sorted(os.path.basename(f) for f in glob.glob(os.path.join(SITE,'*.html')))
res={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in [(1360,900),(390,844)]:
        for f in pages:
            pg=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce'); pg.goto(BASE+f); pg.wait_for_timeout(500)
            pg.add_script_tag(content=axe)
            r=pg.evaluate("axe.run(document,{runOnly:['wcag2a','wcag2aa','wcag21aa','wcag22aa','best-practice']})")
            for x in r['violations']:
                e=res.setdefault(x['id'],{'help':x['help'],'n':set()})
                for n in x['nodes'][:4]: e['n'].add((f+'@'+str(w),n['target'][0],(n.get('failureSummary') or '')[:140].replace('\n',' ')))
            if w==1360 and f=='index.html':
                print('h1 count / titles ok:',pg.evaluate("document.querySelectorAll('h1').length"))
            pg.close()
    b.close()
for k,v in res.items():
    print('\n##',k,v['help'])
    for n in sorted(v['n'])[:8]: print('  ',n)
print('rules failing:',len(res))
