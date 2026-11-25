(function(){
'use strict';
document.documentElement.classList.add('js');
var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
function copyBtn(btn,ta,label){var ok=function(){btn.textContent='Copied';setTimeout(function(){btn.textContent=label},1800)};try{navigator.clipboard.writeText(ta.value).then(ok,function(){ta.select()})}catch(_){ta.select()}}
function monthLabel(v){if(!v)return '';var p=v.split('-');return MONTHS[(+p[1]||1)-1].slice(0,3)+' '+p[0]}

/* ---------- privacy-friendly event hook ----------
   No analytics provider is loaded. If one is added later (for example Plausible or
   Vercel Web Analytics), connect it here. Never pass names, emails or messages. */
function track(name,props){
  props=props||{};
  try{if(window.plausible)window.plausible(name,{props:props})}catch(_){}
  try{document.dispatchEvent(new CustomEvent('sm:track',{detail:{name:name,props:props}}))}catch(_){}
}
window.smTrack=track;
document.addEventListener('click',function(e){
  var a=e.target.closest('[data-track]'); if(!a) return;
  track(a.dataset.track,{trek:a.dataset.trek||'',page:location.pathname.split('/').pop()||'index.html'});
});

/* ---------- nav ---------- */
var nav=$('#nav'), menuBtn=$('#menuBtn'), noHero=document.body.classList.contains('no-hero');
function paintNav(){nav.classList.toggle('solid',noHero||window.scrollY>40||nav.classList.contains('open'))}
function setMenu(open,focusFirst){
  nav.classList.toggle('open',open);menuBtn.setAttribute('aria-expanded',String(open));menuBtn.textContent=open?'Close':'Menu';paintNav();
  if(open&&focusFirst){var f=$('#sheet a');if(f)f.focus()}
}
menuBtn.addEventListener('click',function(e){setMenu(!nav.classList.contains('open'),e.detail===0)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){setMenu(false);menuBtn.focus()}});
document.addEventListener('pointerdown',function(e){if(nav.classList.contains('open')&&!nav.contains(e.target))setMenu(false)});
$('#sheet').addEventListener('focusout',function(e){if(nav.classList.contains('open')&&e.relatedTarget&&!nav.contains(e.relatedTarget))setMenu(false)});
$$('#sheet a').forEach(function(a){a.addEventListener('click',function(){setMenu(false)})});

/* ---------- accordions (FAQ, trip questions) ---------- */
$$('[data-acc]').forEach(function(acc){
  acc.addEventListener('click',function(e){
    var b=e.target.closest('button[aria-controls]'); if(!b||!acc.contains(b)) return;
    var open=b.getAttribute('aria-expanded')==='true';
    b.setAttribute('aria-expanded',String(!open)); $('#'+b.getAttribute('aria-controls')).classList.toggle('open',!open);
    if(!open) track('faq_opened',{q:b.id});
  });
});

/* ---------- trek finder (home) ---------- */
var finder=$('#finder');
if(finder){
  var TREKS=JSON.parse($('#finderData').textContent), out=$('#finderOut');
  var BUCKET={'5':[0,5],'8':[6,8],'12':[9,12],'99':[13,99]};
  finder.addEventListener('submit',function(e){
    e.preventDefault();
    var f=new FormData(finder), days=f.get('days'), exp=f.get('exp'), want=f.get('want');
    var scored=TREKS.map(function(t){
      var s=0, why=[];
      if(days!=='any'){var b=BUCKET[days];
        if(t.days>=b[0]&&t.days<=b[1]){s+=4;why.push('fits '+(days==='99'?'13 days or more':days==='5'?'up to 5 days':days==='8'?'about a week':'9 to 12 days'))}
        else if(Math.abs(t.days-(b[0]+b[1])/2)<=3){s+=1}else{s-=3}}
      var ED={first:{easy:3,moderate:2,challenging:-4},some:{easy:1,moderate:3,challenging:1},lots:{easy:-1,moderate:1,challenging:3}}[exp];
      s+=ED[t.diff];
      if(exp==='first'&&t.diff!=='challenging')why.push('works as a first trek');
      if(exp==='lots'&&t.diff==='challenging')why.push('a real challenge for experienced trekkers');
      if(want!=='any'&&t.tags.indexOf(want)>-1){s+=3;why.push({iconic:'one of the famous views',quiet:'quieter trails',culture:'villages and culture along the way'}[want])}
      return {t:t,s:s,why:why};
    }).sort(function(a,b){return b.s-a.s});
    var top=scored.filter(function(x){return x.s>0}).slice(0,3);
    out.innerHTML='';
    var h=document.createElement('h3'); h.className='finder-h';
    if(!top.length){
      h.textContent='No trek fits all of that perfectly';
      var p=document.createElement('p'); p.textContent='That happens. Jenish can shorten, stretch or combine routes, so tell him what you have in mind.';
      out.appendChild(h);out.appendChild(p);
    }else{
      h.textContent=top.length===1?'One trek fits well':'These '+top.length+' treks fit well'; out.appendChild(h);
      var ul=document.createElement('ul'); ul.className='finder-list';
      top.forEach(function(x){
        var li=document.createElement('li'), a=document.createElement('a'); a.href=x.t.slug+'.html'; a.textContent=x.t.title; a.dataset.track='finder_result_clicked'; a.dataset.trek=x.t.id;
        var meta=document.createElement('span'); meta.className='meta'; meta.textContent=x.t.dur+' · '+x.t.level+' · up to '+x.t.peak;
        var why=document.createElement('p'); why.textContent=x.why.length?('Why: '+x.why.join(', ')+'.'):x.t['for']+'.';
        li.appendChild(a);li.appendChild(meta);li.appendChild(why);ul.appendChild(li);
      });
      out.appendChild(ul);
    }
    var ask=document.createElement('p'); ask.className='finder-ask';
    var al=document.createElement('a'); al.className='btn btn-secondary btn-sm'; al.href='plan-your-trip.html?trek='+(top[0]?top[0].t.id:'custom'); al.textContent=top[0]?'Ask Jenish about '+top[0].t.title:'Ask Jenish for advice';
    ask.appendChild(al); out.appendChild(ask);
    out.focus();
    track('trek_recommendation_completed',{days:days,exp:exp,want:want,top:top[0]?top[0].t.id:'none'});
  });
}

/* ---------- tours: filters ---------- */
var filters=$('#filters');
if(filters){
  var items=$$('#tourList>li'), total=items.length, count=$('#count'), empty=$('#empty');
  var get=function(k){var el=$('[data-filter="'+k+'"]',filters);return el.type==='checkbox'?(el.checked?'true':'all'):el.value};
  var apply=function(fromUser){
    var type=get('type'), days=get('days'), diff=get('diff'), area=get('area'), first=get('first'), n=0;
    var r=days==='all'?null:days.split('-').map(Number);
    items.forEach(function(li){
      var d=+li.dataset.days;
      var show=(type==='all'||li.dataset.type===type)&&(!r||(d>=r[0]&&d<=r[1]))&&(diff==='all'||li.dataset.diff===diff)&&(area==='all'||li.dataset.area===area)&&(first==='all'||li.dataset.first==='true');
      li.hidden=!show; if(show){n++;li.classList.add('in')}
    });
    count.textContent=n===total?'Showing all '+total+' trips':'Showing '+n+' of '+total+' trips';
    empty.hidden=n>0;
    if(fromUser) track('trek_filter_used',{type:type,days:days,diff:diff,area:area,first:first,results:n});
  };
  filters.addEventListener('change',function(){apply(true)});
  filters.addEventListener('submit',function(e){e.preventDefault()});
  filters.addEventListener('reset',function(){setTimeout(function(){apply(false)},0)});
  $('#emptyReset').addEventListener('click',function(){filters.reset();setTimeout(function(){apply(false);$('#ft-type').focus()},0)});
  var fromHash=function(){var h=(location.hash||'').slice(1); if(/^(trek|raft|safari)$/.test(h)){$('#ft-type').value=h;apply(false)}};
  window.addEventListener('hashchange',fromHash);
  apply(false); fromHash();
}

/* ---------- plan your trip: inquiry → WhatsApp / email / copy ---------- */
var plan=$('#plan');
if(plan){
  var NAMES=JSON.parse($('#trekNames').textContent), pv=$('#f-preview'), status=$('#planStatus'), trekSel=$('#f-trek');
  /* preselect from ?trek=<id> (or the old #trip-<id>); unknown values are ignored */
  var q=null; try{q=new URLSearchParams(location.search).get('trek')}catch(_){}
  if(!q){var hm=(location.hash||'').match(/^#trip-([a-z0-9-]+)$/);if(hm)q=hm[1]}
  if(q&&/^[a-z0-9-]{1,40}$/.test(q)&&(q==='custom'||Object.prototype.hasOwnProperty.call(NAMES,q))) trekSel.value=q;
  var started=false;
  function val(n){var el=plan.elements[n];if(!el)return '';if(el.length&&el[0]&&el[0].type==='radio'){var c=$('input[name="'+n+'"]:checked',plan);return c?c.value:''}if(el.type==='checkbox')return el.checked?'yes':'';return String(el.value||'').trim()}
  function message(){
    var name=val('name'), trek=val('trek'), when=val('when'), flex=val('flexible'), ppl=val('people'), exp=val('exp'), msg=val('message'), email=val('email');
    var lines=['Hi Jenish!','',"I'm interested in trekking in Nepal and would love your help planning my adventure.",''];
    lines.push('Name: '+(name||'(not given)'));
    lines.push('Preferred trek: '+(trek&&trek!=='custom'?NAMES[trek]:"I'm not sure yet, please help me choose"));
    lines.push('Travel dates: '+(when?monthLabel(when)+(flex?' (flexible)':''):(flex?'Flexible, not decided yet':'Not decided yet')));
    lines.push('Number of travellers: '+(ppl||'Not sure yet'));
    if(exp) lines.push('Previous trekking experience: '+exp);
    if(msg) lines.push('Additional wishes: '+msg);
    if(email) lines.push('Email for replies: '+email);
    lines.push('','Could you help me plan a suitable itinerary and give me an estimated price?','','Thank you!');
    return lines.join('\n');
  }
  function refresh(){pv.value=message()}
  plan.addEventListener('input',function(){refresh();if(!started){started=true;track('inquiry_form_started',{trek:trekSel.value})}});
  plan.addEventListener('change',refresh);
  refresh();
  function valid(){
    var ok=true, first=null;
    var nb=!val('name'); $('#f-name').setAttribute('aria-invalid',String(nb)); $('#e-name').hidden=!nb; if(nb){ok=false;first=first||$('#f-name')}
    var em=val('email'), eb=!!em&&!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em); $('#f-email').setAttribute('aria-invalid',String(eb)); $('#e-email').hidden=!eb; if(eb){ok=false;first=first||$('#f-email')}
    if(first) first.focus();
    return ok;
  }
  /* tests can replace window.smOpen to check the URL without opening anything */
  function openExt(u,newTab){if(window.smOpen)return window.smOpen(u,newTab);if(newTab)window.open(u,'_blank','noopener');else location.href=u}
  function say(html){status.innerHTML=html;status.hidden=false;status.focus()}
  function send(kind){
    if(!valid()) return;
    var body=message(), trekId=trekSel.value;
    if(kind==='wa'){
      var url='https://wa.me/'+plan.dataset.wa+'?text='+encodeURIComponent(body);
      openExt(url,true);
      say('<b>WhatsApp should open in a new tab with your message.</b> It isn\'t sent until you press send there. Nothing opened? <a href="'+url+'" target="_blank" rel="noopener">Open WhatsApp again</a>, or copy the message and send it to '+plan.dataset.waDisplay+'.');
      track('inquiry_whatsapp_clicked',{trek:trekId});
    }else if(kind==='email'){
      var subj='Trek inquiry: '+(trekId&&trekId!=='custom'?NAMES[trekId]:'help me choose a trek');
      var mail='mailto:'+plan.dataset.email+'?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(body);
      openExt(mail,false);
      say('<b>Your email app should open with the message ready.</b> It isn\'t sent until you press send there. If no email app opens, copy the message and send it to <a href="mailto:'+plan.dataset.email+'">'+plan.dataset.email+'</a>.');
      track('inquiry_email_clicked',{trek:trekId});
    }else{
      var done=function(){say('<b>Message copied.</b> Paste it into WhatsApp ('+plan.dataset.waDisplay+') or an email to '+plan.dataset.email+'.');track('inquiry_message_copied',{trek:trekId})};
      var fail=function(){pv.focus();pv.select();say('Copying isn\'t allowed in this browser. The message is selected in the preview above, so press Ctrl+C or ⌘+C.')};
      try{navigator.clipboard.writeText(body).then(done,fail)}catch(_){fail()}
    }
  }
  plan.addEventListener('submit',function(e){e.preventDefault();send('wa')});
  $$('[data-send]',plan).forEach(function(b){if(b.type!=='submit')b.addEventListener('click',function(){send(b.dataset.send)})});
}

/* ---------- review → WhatsApp ---------- */
var revForm=$('#revForm');
if(revForm){
  var revDone=$('#revDone'), HINTS=['','Not great','Okay','Good','Great','Unforgettable'];
  $('#rate').addEventListener('change',function(e){$('#rateHint').textContent=HINTS[+e.target.value];$('#e-rating').hidden=true});
  revForm.addEventListener('submit',function(e){
    e.preventDefault();
    var d={}; new FormData(revForm).forEach(function(v,k){d[k]=String(v).trim()});
    var bad=[];
    if(!d.stars){$('#e-rating').hidden=false;bad.push('#st1')}
    var nb=!d.name; $('#r-name').setAttribute('aria-invalid',String(nb)); $('#e-rname').hidden=!nb; if(nb)bad.push('#r-name');
    var tb=(d.text||'').length<3; $('#r-text').setAttribute('aria-invalid',String(tb)); $('#e-rtext').hidden=!tb; if(tb)bad.push('#r-text');
    if(bad.length){$(bad[0]).focus();return}
    var n=+d.stars, body='Review for Somewhere in Mountains\n\n'+'★'.repeat(n)+'☆'.repeat(5-n)+' ('+n+'/5)\nName: '+d.name+(d.country?'\nCountry: '+d.country:'')+(d.trip?'\nTrip: '+d.trip:'')+(d.when?'\nWhen: '+monthLabel(d.when):'')+
      '\n\n"'+d.text+'"\n\n'+(d.consent?'OK to publish with my first name and country.':'Please don’t publish this, it’s just for you.');
    $('#revDoneTitle').textContent='Thank you, '+d.name.split(' ')[0]+'.';
    var ro=$('#revOpen'); ro.dataset.base=ro.dataset.base||ro.getAttribute('href'); $('#revMsg').value=body; ro.href=ro.dataset.base+'?text='+encodeURIComponent(body);
    revForm.hidden=true; revDone.hidden=false; revDone.focus();
  });
  $('#revCopy').addEventListener('click',function(){copyBtn(this,$('#revMsg'),'Copy review')});
  $('#revReset').addEventListener('click',function(){revDone.hidden=true;revForm.hidden=false;$('#r-text').focus()});
}

/* ---------- swipe carousels ---------- */
function project(v,d){d=d||0.998;return (v/1000)*d/(1-d)}  /* momentum: where a flick would come to rest */
$$('[data-car]').forEach(function(car){
  var track=$('.car-track',car), slides=$$('.car-slide',car), imgs=slides.map(function(s){return $('.car-img',s)}), count=$('.car-count b',car), bar=$('.car-bar',car), btns=$$('.car-btn',car);
  var offs=[], raf=0, active=-1;
  function measure(){offs=slides.map(function(s){return s.offsetLeft+s.offsetWidth/2})}
  function update(){
    raf=0;
    var sl=track.scrollLeft, w=track.clientWidth, mid=sl+w/2, max=track.scrollWidth-w, best=0, bd=1e9;
    slides.forEach(function(s,i){
      var d=(offs[i]-mid)/(w*0.75), ad=Math.min(1,Math.abs(d));
      if(!reduced){imgs[i].style.setProperty('--px',(Math.max(-1,Math.min(1,d))*-4).toFixed(2)+'%');imgs[i].style.setProperty('--s',(1-ad*0.03).toFixed(4))}
      s.style.setProperty('--d',ad.toFixed(3));
      var start=Math.abs(s.offsetLeft-(sl+parseFloat(getComputedStyle(track).scrollPaddingLeft||0))); if(start<bd){bd=start;best=i}
    });
    if(sl>=max-2) best=slides.length-1;
    if(best!==active){active=best;count.textContent=String(best+1).padStart(2,'0')}
    bar.style.setProperty('--p',max>0?(sl/max).toFixed(4):1);
    btns[0].disabled=sl<=2; btns[1].disabled=sl>=max-2;
  }
  function queue(){if(!raf)raf=requestAnimationFrame(update)}
  function go(dir){
    var step=slides[0].offsetWidth+14, target=Math.max(0,Math.min(track.scrollWidth,track.scrollLeft+dir*Math.max(step,track.clientWidth*0.66)));
    track.scrollTo({left:target,behavior:reduced?'auto':'smooth'});
  }
  btns.forEach(function(b){b.addEventListener('click',function(){go(+b.dataset.dir)})});
  track.addEventListener('scroll',queue,{passive:true});
  window.addEventListener('resize',function(){measure();queue()});
  /* mouse drag with momentum (touch and trackpads already swipe natively) */
  var drag=null;
  track.addEventListener('pointerdown',function(e){
    if(e.pointerType!=='mouse'||e.button!==0) return;
    drag={x:e.clientX,sl:track.scrollLeft,moved:false,h:[[e.clientX,performance.now()]]};
  });
  window.addEventListener('pointermove',function(e){
    if(!drag) return; var dx=e.clientX-drag.x;
    if(!drag.moved&&Math.abs(dx)>6){drag.moved=true;track.classList.add('dragging')}
    if(drag.moved){track.scrollLeft=drag.sl-dx;drag.h.push([e.clientX,performance.now()]);if(drag.h.length>5)drag.h.shift()}
  });
  window.addEventListener('pointerup',function(){
    if(!drag) return; var d=drag; drag=null; if(!d.moved) return;
    var a=d.h[0], b=d.h[d.h.length-1], v=(b[1]-a[1])>0?(b[0]-a[0])/(b[1]-a[1])*1000:0; /* px/s */
    var pad=parseFloat(getComputedStyle(track).scrollPaddingLeft)||0, rest=track.scrollLeft-project(v);
    var best=0,bd=1e9; slides.forEach(function(s,i){var dd=Math.abs(s.offsetLeft-pad-rest);if(dd<bd){bd=dd;best=i}});
    track.classList.remove('dragging');
    track.scrollTo({left:slides[best].offsetLeft-pad,behavior:reduced?'auto':'smooth'});
  });
  track.addEventListener('click',function(e){if(track.classList.contains('dragging'))e.preventDefault()},true);
  /* tap → photo viewer */
  slides.forEach(function(s,i){$('.car-open',s).addEventListener('click',function(){openViewer(slides,i,this)})});
  measure(); update();
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(function(){measure();queue()});
  window.addEventListener('load',function(){measure();queue()});
});

/* ---------- full-screen photo viewer (swipe sideways, swipe down to close) ---------- */
var lb=null, lbTrack, lbCount, lbCap, lbPrev, lbNext, lbItems=[], lbIdx=0, lbOpener=null;
function buildViewer(){
  lb=document.createElement('dialog'); lb.className='lb'; lb.setAttribute('aria-label','Photo viewer');
  var chev=$('.car-btn[data-dir="1"]').innerHTML, chevL=$('.car-btn[data-dir="-1"]').innerHTML;
  lb.innerHTML='<div class="lb-track"></div><div class="lb-top"><span class="lb-count" aria-live="polite"></span><button class="lb-btn lb-close" type="button" aria-label="Close photo viewer"><svg class="ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg></button></div>'+
    '<button class="lb-btn lb-nav lb-prev" type="button" aria-label="Previous photo">'+chevL+'</button><button class="lb-btn lb-nav lb-next" type="button" aria-label="Next photo">'+chev+'</button><p class="lb-cap"></p>';
  document.body.appendChild(lb);
  lbTrack=$('.lb-track',lb); lbCount=$('.lb-count',lb); lbCap=$('.lb-cap',lb); lbPrev=$('.lb-prev',lb); lbNext=$('.lb-next',lb);
  $('.lb-close',lb).addEventListener('click',closeViewer);
  lbPrev.addEventListener('click',function(){lbGo(lbIdx-1)}); lbNext.addEventListener('click',function(){lbGo(lbIdx+1)});
  lb.addEventListener('cancel',function(e){e.preventDefault();closeViewer()});
  lb.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){e.preventDefault();lbGo(lbIdx+1)}else if(e.key==='ArrowLeft'){e.preventDefault();lbGo(lbIdx-1)}});
  var raf2=0; lbTrack.addEventListener('scroll',function(){if(!raf2)raf2=requestAnimationFrame(function(){raf2=0;var i=Math.round(lbTrack.scrollLeft/lbTrack.clientWidth);if(i!==lbIdx){lbIdx=i;lbMeta()}})},{passive:true});
  /* swipe down to dismiss: tracks the finger 1:1, then either springs back or flies away */
  var g=null;
  lbTrack.addEventListener('pointerdown',function(e){var im=e.target.closest('.lb-slide')&&$('img',e.target.closest('.lb-slide'));g={x:e.clientX,y:e.clientY,id:e.pointerId,im:im||$('img',lbTrack.children[lbIdx]),mode:null,h:[[e.clientY,performance.now()]]}});
  lbTrack.addEventListener('pointermove',function(e){
    if(!g||e.pointerId!==g.id) return; var dx=e.clientX-g.x, dy=e.clientY-g.y;
    if(!g.mode){ if(Math.abs(dy)>10&&Math.abs(dy)>Math.abs(dx)*1.2){g.mode='y';try{lbTrack.setPointerCapture(e.pointerId)}catch(_){}} else if(Math.abs(dx)>10){g.mode='x'} }
    if(g.mode!=='y') return;
    g.h.push([e.clientY,performance.now()]); if(g.h.length>5)g.h.shift();
    g.im.classList.remove('settle'); g.im.style.setProperty('--dy',dy+'px'); g.im.style.setProperty('--ds',(1-Math.min(.25,Math.abs(dy)/1600)).toFixed(4));
    lb.style.setProperty('--o',(1-Math.min(.85,Math.abs(dy)/420)).toFixed(3));
  });
  function end(){
    if(!g) return; var s=g; g=null; if(s.mode!=='y') return;
    var a=s.h[0], b=s.h[s.h.length-1], v=(b[1]-a[1])>0?(b[0]-a[0])/(b[1]-a[1]):0, dy=b[0]-s.y;
    if(Math.abs(dy)>110||Math.abs(v)>0.6){ s.im.classList.add('settle'); s.im.style.setProperty('--dy',(dy>0?1:-1)*window.innerHeight+'px'); closeViewer(); }
    else { s.im.classList.add('settle'); s.im.style.setProperty('--dy','0px'); s.im.style.setProperty('--ds','1'); lb.style.setProperty('--o','1'); }
  }
  lbTrack.addEventListener('pointerup',end); lbTrack.addEventListener('pointercancel',end);
}
function lbMeta(){lbCount.textContent=String(lbIdx+1).padStart(2,'0')+' / '+String(lbItems.length).padStart(2,'0');lbCap.innerHTML='';lbCap.appendChild(document.createTextNode(lbItems[lbIdx].cap));var h=document.createElement('span');h.className='lb-hint';h.textContent=matchMedia('(hover:none)').matches?'Swipe sideways · swipe down to close':'← → to browse · Esc to close';lbCap.appendChild(h);lbPrev.disabled=lbIdx===0;lbNext.disabled=lbIdx===lbItems.length-1}
function lbGo(i){if(i<0||i>=lbItems.length)return;lbTrack.scrollTo({left:i*lbTrack.clientWidth,behavior:reduced?'auto':'smooth'})}
function openViewer(slides,i,opener){
  if(!lb) buildViewer();
  lbOpener=opener; lbItems=slides.map(function(s){var b=$('.car-open',s);return {src:b.dataset.full,cap:b.dataset.cap}});
  lbTrack.innerHTML=lbItems.map(function(it){return '<div class="lb-slide"><img src="'+it.src+'" alt="'+it.cap.replace(/"/g,'&quot;')+'" draggable="false"></div>'}).join('');
  lb.style.setProperty('--o','1'); lb.classList.remove('closing');
  document.documentElement.style.overflow='hidden';
  lb.showModal(); lbIdx=i; lbTrack.scrollLeft=i*lbTrack.clientWidth; lbMeta(); $('.lb-close',lb).focus();
}
function closeViewer(){
  if(!lb||!lb.open||lb.classList.contains('closing')) return;
  var done=function(){lb.classList.remove('closing');lb.close();document.documentElement.style.overflow='';if(lbOpener)lbOpener.focus({preventScroll:true})};
  if(reduced){done();return}
  lb.classList.add('closing'); setTimeout(done,220);
}

/* ---------- nav state on scroll ---------- */
var navRaf=0;
window.addEventListener('scroll',function(){if(!navRaf)navRaf=requestAnimationFrame(function(){navRaf=0;paintNav()})},{passive:true});
paintNav();

/* ---------- WhatsApp bubble: only when no other WhatsApp action is on screen ---------- */
var bub=$('.bubble');
if(bub&&$('#qbar')){bub.remove();bub=null}
if(bub){
  var busy=$$('.hero,.page-head,.guide-head,.book-card,.cta-box,.card-wa,form,footer.site');
  if('IntersectionObserver' in window&&busy.length){
    var seen=new Set();
    var bio=new IntersectionObserver(function(es){es.forEach(function(en){en.isIntersecting?seen.add(en.target):seen.delete(en.target)});bub.classList.toggle('show',seen.size===0)});
    busy.forEach(function(el){bio.observe(el)});
  }else bub.classList.add('show');
}

/* ---------- scroll landscape: ridges rise at different speeds, clouds drift ---------- */
if(!reduced){
  var scenes=$$('.ridges').map(function(el){return {el:el,layers:$$('[data-depth]',el),clouds:$$('[data-drift]',el)}});
  var hero=$('.hero'), heroBg=hero&&$('.hero-bg',hero), mist=hero?$$('.hero-mist [data-drift]',hero):[];
  var land=0;
  var paintLand=function(){
    land=0; var vh=innerHeight, vw=innerWidth;
    scenes.forEach(function(s){
      var r=s.el.getBoundingClientRect();
      if(r.bottom<-80||r.top>vh+80) return;
      // p: 1 when the band enters at the bottom, 0 mid-screen, -1 as it leaves the top
      var p=((r.top+r.height/2)-vh/2)/(vh/2+r.height/2);
      s.layers.forEach(function(l){l.style.transform='translate3d(0,'+(p*parseFloat(l.dataset.depth)*r.height*.6).toFixed(1)+'px,0)'});
      s.clouds.forEach(function(c){c.style.transform='translate3d('+(p*parseFloat(c.dataset.drift)*vw*.12).toFixed(1)+'px,'+(p*r.height*.18).toFixed(1)+'px,0)'});
    });
    if(heroBg){
      var hr=hero.getBoundingClientRect();
      if(hr.bottom>0){
        var t=Math.min(1,Math.max(0,-hr.top/hr.height));
        heroBg.style.transform='translate3d(0,'+(t*hr.height*.28).toFixed(1)+'px,0) scale('+(1+t*.06).toFixed(4)+')';
        mist.forEach(function(c){c.style.transform='translate3d('+(t*parseFloat(c.dataset.drift)*vw*.18).toFixed(1)+'px,'+(-t*40).toFixed(1)+'px,0)'});
      }
    }
  };
  window.addEventListener('scroll',function(){if(!land)land=requestAnimationFrame(paintLand)},{passive:true});
  window.addEventListener('resize',function(){if(!land)land=requestAnimationFrame(paintLand)});
  paintLand();
}

/* ---------- reveal on scroll ---------- */
if('IntersectionObserver' in window&&!reduced){
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}})},{rootMargin:'0px 0px -6% 0px',threshold:.05});
  $$('[data-reveal]').forEach(function(el){io.observe(el)});
}else{$$('[data-reveal]').forEach(function(el){el.classList.add('in')})}
})();
