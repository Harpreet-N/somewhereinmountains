"""Accessibility checks. Serve the site first:  cd site && python3 -m http.server 8765
Needs: npm install axe-core (in tests/a11y) and pip install playwright pillow."""
import os
SITE=os.environ.get('SITE_DIR',os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','site'))
BASE='http://localhost:8765/'
import io,glob,os,re
from playwright.sync_api import sync_playwright
from PIL import Image
axe=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'node_modules','axe-core','axe.min.js')).read()
def lum(c):
    def ch(v):
        v/=255; return v/12.92 if v<=.03928 else ((v+.055)/1.055)**2.4
    r,g,b=c[:3]; return .2126*ch(r)+.7152*ch(g)+.0722*ch(b)
def cr(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+.05)/(lb+.05)
pages=sorted(os.path.basename(f) for f in glob.glob(os.path.join(SITE,'*.html')))
inc={}
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1) axe 'incomplete' contrast (text over images/gradients) — list where it couldn't decide
    for w,h in [(1360,900),(390,844)]:
        for f in pages:
            pg=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce'); pg.goto(BASE+f); pg.wait_for_timeout(400)
            pg.add_script_tag(content=axe)
            r=pg.evaluate("axe.run(document,{runOnly:['color-contrast','color-contrast-enhanced']}).then(r=>r.incomplete.map(x=>[x.id,x.nodes.map(n=>n.target[0])]))")
            for rid,ns in r:
                for n in ns: inc.setdefault(n,set()).add(f+'@'+str(w))
            pg.close()
    print('axe could not decide (text over images/gradients):',len(inc))
    for k in sorted(inc)[:40]: print('  ',k,sorted(inc[k])[:2])
    # 2) pixel check of text over photos: heroes, nav on hero, home trek card
    worst=[]
    for w,h in [(1360,900),(390,844),(320,640)]:
        for f in pages:
            pg=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce'); pg.goto(BASE+f); pg.wait_for_timeout(500)
            for sel in ['.hero','.svc-main']:
                if not pg.query_selector(sel): continue
                pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start'}})") if sel!='.hero' else pg.evaluate("scrollTo(0,0)")
                pg.wait_for_timeout(250)
                boxes=pg.evaluate("""s=>{const root=document.querySelector(s);const els=[...root.querySelectorAll('h1,h3,p,a,span,li')].filter(e=>e.offsetParent&&(e.childElementCount===0||e.matches('h1,h3,p'))&&!e.closest('.btn-light')&&e.textContent.trim().length>0);
                  if(s=='.hero')els.push(...document.querySelectorAll('.nav .brand,.nav-links a'));
                  return els.map(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return [s+' '+e.textContent.trim().slice(0,28),r.x,r.y,r.width,r.height,cs.color,parseFloat(cs.fontSize),cs.fontWeight]}).filter(x=>x[3]>2&&x[4]>2&&x[2]<innerHeight&&x[2]>=0)}""",sel)
                pg.add_style_tag(content='.hero-copy,.nav-row,.bubble,.svc-main .in{visibility:hidden!important}'); pg.wait_for_timeout(150)
                img=Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
                for t,x,y,ww,hh,col,fs,fw in boxes:
                    m=re.findall(r'[\d.]+',col); fg=tuple(int(float(v)) for v in m[:3])
                    if len(m)>3 and float(m[3])<1: continue
                    px=list(img.crop((int(x),int(y),int(x+ww),int(y+hh))).getdata())[::5]
                    if not px: continue
                    cs=sorted(cr(fg,q) for q in px); c=cs[len(cs)//20]
                    need=3 if (fs>=24 or (fs>=18.66 and int(fw)>=700)) else 4.5
                    worst.append((round(c,2),need,f,w,t))
                pg.add_style_tag(content='.hero-copy,.nav-row,.bubble,.svc-main .in{visibility:visible!important}')
            pg.close()
    fails=[x for x in worst if x[0]<x[1]]
    print('\ntext-over-photo checks:',len(worst),'fails:',len(fails))
    for x in sorted(fails)[:20]: print('  ',x)
    print('lowest 8:',sorted(worst)[:8])
    b.close()
