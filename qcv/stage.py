"""HTML-сцена: тёмный неон, сцены по таймингам, прогресс-бар, луп."""
import json

from . import board as board_mod

W, H = 1080, 1920

PALETTES = {
    'teal': {'bg': '#040A0F', 'bg2': '#0A2230', 'a1': '#00E0B8', 'a2': '#FFB020', 'a3': '#2B6CFF'},
    'violet': {'bg': '#0A0614', 'bg2': '#1B0B33', 'a1': '#C6F432', 'a2': '#8B5CF6', 'a3': '#FF5DB1'},
    'amber': {'bg': '#0C0703', 'bg2': '#2A1405', 'a1': '#FFC24B', 'a2': '#FF6B3D', 'a3': '#7CE0C3'},
    'lime': {'bg': '#060A05', 'bg2': '#12240D', 'a1': '#B6FF3D', 'a2': '#00E0A8', 'a3': '#FF7A45'},
    'paper': {'bg': '#F7F4EA', 'bg2': '#EFE7D6', 'a1': '#2F6BFF', 'a2': '#FF7A3D', 'a3': '#1D1D1D'},
}

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:__W__px;height:__H__px;overflow:hidden;background:var(--bg);
  font-family:'DejaVu Sans',sans-serif;color:var(--ink)}
#stage{position:relative;width:__W__px;height:__H__px;overflow:hidden;
  background:radial-gradient(80% 55% at 50% 20%,var(--bg2) 0%,#061018 55%,#03070B 100%)}
.scene{position:absolute;inset:0;opacity:0}
#bggrid,#bgdots{position:absolute;inset:0;pointer-events:none}
#bggrid{background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:90px 90px;opacity:0}
#bgdots{background-image:radial-gradient(rgba(255,255,255,.14) 1.6px,transparent 1.6px);background-size:44px 44px;opacity:0}
.glow{position:absolute;border-radius:50%;filter:blur(80px);opacity:.45}
#g1{width:620px;height:620px;left:-170px;top:170px;background:var(--a1)}
#g2{width:540px;height:540px;right:-170px;top:760px;background:var(--a2)}
#g3{width:500px;height:500px;left:220px;bottom:-150px;background:var(--a3)}
.brand{position:absolute;left:70px;top:196px;font-size:72px;font-weight:800;letter-spacing:.03em;color:#E8FBFF}
.brand.sm{top:200px;font-size:46px;color:#BFE6EF;font-weight:700}
.kicker{position:absolute;left:70px;top:150px;font-size:24px;letter-spacing:.32em;
  color:var(--a1);text-transform:uppercase}
#prog{position:absolute;left:40px;right:40px;top:44px;height:8px;display:flex;gap:10px;z-index:9}
.seg{flex:1;background:rgba(255,255,255,.14);border-radius:6px;overflow:hidden}
.segfill{height:100%;width:0;background:linear-gradient(90deg,var(--a1),var(--a2))}
.hnum{position:absolute;left:0;right:0;top:560px;text-align:center;font-size:290px;
  font-weight:800;line-height:1;color:var(--a2);text-shadow:0 0 110px rgba(255,176,32,.5)}
.hunit{position:absolute;left:0;right:0;top:910px;text-align:center;font-size:48px;color:#E8FBFF}
.htag{position:absolute;left:50%;margin-left:-300px;top:1035px;width:600px;text-align:center;
  padding:18px 0;border:3px solid #FF4B5C;border-radius:16px;color:#FF4B5C;font-size:31px;font-weight:700;white-space:nowrap}
.statv{position:absolute;left:80px;font-weight:800;font-size:150px;line-height:1;color:#E8FBFF}
.statl{position:absolute;left:84px;font-size:32px;color:#7FB3C4}
.card{position:absolute;left:70px;width:940px;padding:34px 34px;border-radius:22px;
  border:1px solid rgba(0,224,184,.45);background:rgba(6,26,34,.82)}
.card .t{font-size:48px;font-weight:700;color:#E8FBFF}
.card .d{font-size:32px;color:#8FD9E8;margin-top:8px;line-height:1.3}
#cap{position:absolute;left:60px;right:60px;bottom:130px;text-align:center;font-size:38px;
  line-height:1.25;text-shadow:0 3px 20px rgba(0,0,0,.9)}
.vscore{position:absolute;left:0;right:0;top:520px;text-align:center;font-size:300px;
  font-weight:800;line-height:1;color:var(--a1);text-shadow:0 0 120px rgba(0,224,184,.45)}
.vnote{position:absolute;left:80px;right:80px;top:930px;text-align:center;font-size:40px;color:#8FD9E8}
.fhead{position:absolute;left:0;right:0;top:560px;text-align:center;font-size:66px;font-weight:800;
  color:#FF4B5C;text-shadow:0 0 70px rgba(255,75,92,.45)}
.fsub{position:absolute;left:70px;right:70px;top:700px;text-align:center;font-size:36px;
  color:#8FD9E8;line-height:1.35}
.faddr{position:absolute;left:0;right:0;top:960px;text-align:center;font-size:116px;font-weight:800;
  color:#FFFFFF;letter-spacing:-.02em;text-shadow:0 0 70px rgba(0,224,184,.75),0 0 160px rgba(43,108,255,.4)}
.ghost{position:absolute;left:0;right:0;top:1300px;text-align:center;font-size:120px;font-weight:800;letter-spacing:.02em;white-space:nowrap;color:rgba(0,224,184,.10)}
.ghostline{position:absolute;left:340px;right:340px;top:1260px;height:2px;background:rgba(0,224,184,.18)}
.rail{position:absolute;left:206px;top:560px;width:4px;height:0;background:var(--a1);opacity:.35}
.stepc{position:absolute;left:148px;width:120px;height:120px;border-radius:50%;border:4px solid var(--a1);
  display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:800;color:var(--a1);
  background:rgba(4,10,15,.65)}
.stept{position:absolute;left:312px;right:70px;font-size:46px;font-weight:700;line-height:1.15}
.stepd{position:absolute;left:314px;right:70px;font-size:30px;color:#8FD9E8;line-height:1.25}
.typo{position:absolute;left:64px;right:64px;top:520px;text-align:left}
.typo .ln{display:block;font-weight:800;line-height:.98;letter-spacing:-.02em;font-size:150px;color:#E8FBFF;margin-bottom:6px}
.typo .ln.acc{color:var(--a2)}
.typo .sub{font-size:34px;color:#8FD9E8;margin-top:34px;line-height:1.35}
.splitL{position:absolute;left:64px;top:560px;width:452px}
.splitL .k{font-size:22px;letter-spacing:.22em;color:var(--a1);text-transform:uppercase}
.splitL .v{font-size:118px;font-weight:800;line-height:1;margin-top:16px;color:#E8FBFF}
.splitL .t{font-size:34px;font-weight:700;margin-top:18px;color:#E8FBFF;line-height:1.2}
.splitR{position:absolute;right:48px;top:596px;width:452px}
.splitR .it{font-size:27px;line-height:1.35;color:#BFE6EF;padding:14px 0 14px 26px;border-left:3px solid var(--a1);margin-bottom:14px}
.filmstrip{position:absolute;left:40px;right:40px;top:430px}
.filmstrip .fr{position:relative;height:360px;border-radius:16px;border:2px solid rgba(255,255,255,.15);
  margin-bottom:26px;padding:26px 30px;background:rgba(255,255,255,.04);display:flex;flex-direction:column;justify-content:flex-end}
.filmstrip .fr .n{position:absolute;top:18px;left:26px;font-size:20px;letter-spacing:.2em;color:var(--a1)}
.filmstrip .fr .h{font-size:54px;font-weight:800;line-height:1.05}
.filmstrip .fr .d{font-size:28px;color:#8FD9E8;margin-top:10px}
.codebox{position:absolute;left:56px;right:56px;top:700px;border-radius:18px;background:#0B1017;
  border:1px solid rgba(148,163,184,.22);box-shadow:0 30px 80px rgba(0,0,0,.5);overflow:hidden}
.codebar{height:56px;display:flex;align-items:center;gap:10px;padding:0 20px;background:rgba(255,255,255,.03);
  border-bottom:1px solid rgba(148,163,184,.14)}
.codebar .d{width:12px;height:12px;border-radius:50%}
.codebar .lbl{margin-left:10px;font-size:22px;color:#7C8AA0;letter-spacing:.08em}
.codebody{padding:28px 30px 34px;font-family:'DejaVu Sans Mono',monospace;font-size:36px;line-height:1.6;color:#D7E3F4}
.codebody .pr{color:#6EE7B7}
.codebody .cm{color:#6B7A90}
#s0cursor,.cursor{display:inline-block;width:16px;height:38px;background:#B6FF3D;vertical-align:-6px;margin-left:4px}
.dgnode{position:absolute;left:50%;width:760px;margin-left:-380px;padding:26px 30px;border-radius:18px;
  border:2px solid rgba(255,255,255,.18);background:rgba(10,16,26,.85)}
.dgnode .t{font-size:44px;font-weight:800}
.dgnode .s{font-size:26px;color:#8FD9E8;margin-top:10px}
.dgarr{position:absolute;left:50%;width:4px;background:var(--a1);margin-left:-2px}
.dgarr::after{content:'';position:absolute;bottom:-11px;left:-6px;border-left:6px solid transparent;border-right:6px solid transparent;border-top:11px solid var(--a1)}
.mascot{position:absolute;left:40px;bottom:205px;width:262px;opacity:0;z-index:5;transform-origin:50% 100%;transition:transform .35s ease}
.mascot svg{width:100%;height:auto;display:block;overflow:visible}
.mascot g{transition:transform .35s ease}
.fnote{position:absolute;left:0;right:0;top:1120px;text-align:center;font-size:32px;color:#7FB3C4}
"""


PAPER_CSS = r"""
body.paper #stage{background:#F7F4EA}
body.paper .glow{display:none}
body.paper #bggrid{background-image:linear-gradient(rgba(0,0,0,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(0,0,0,.055) 1px,transparent 1px)}
body.paper #bgdots{background-image:radial-gradient(rgba(0,0,0,.16) 1.7px,transparent 1.7px)}
body.paper .brand{color:#1D1D1D}
body.paper .brand.sm{color:#5A6472}
body.paper .hunit,body.paper .statv,body.paper .card .t,body.paper .typo .ln,
body.paper .splitL .v,body.paper .splitL .t,body.paper .filmstrip .fr .h,
body.paper .vnote,body.paper .fsub,body.paper .stept,body.paper .dgnode .t{color:#1D1D1D}
body.paper .statl,body.paper .card .d,body.paper .stepd,body.paper .splitR .it,
body.paper .typo .sub,body.paper .filmstrip .fr .d,body.paper .dgnode .s,
body.paper .fnote{color:#4A5568}
body.paper .hnum{color:var(--a2);text-shadow:none}
body.paper .vscore{color:var(--a1);text-shadow:none}
body.paper .htag{border-color:transparent;color:#D93A3A}
body.paper .fhead{color:#1D1D1D;text-shadow:none}
body.paper .faddr{color:var(--a1);text-shadow:none}
body.paper #cap{color:#1D1D1D;font-weight:600;text-shadow:none}
body.paper .seg{background:rgba(0,0,0,.10)}
body.paper .ghost{color:rgba(20,20,20,.07)}
body.paper .ghostline{background:rgba(20,20,20,.12)}
body.paper .card{background:rgba(255,255,255,.8);border-color:transparent;box-shadow:0 10px 30px rgba(60,50,30,.08)}
body.paper .filmstrip .fr{background:rgba(255,255,255,.8);border-color:rgba(0,0,0,.16)}
body.paper .dgnode{background:rgba(255,255,255,.85);border-color:transparent}
body.paper .stepc{background:#fff}
body.paper .typo .ln.acc{color:var(--a1)}
body.paper .splitL{top:700px}
body.paper .splitR{top:742px}
body.paper .typo{top:640px}
"""

MARKUP = {
    'hook': '<div class="kicker">{kicker}</div>'
            '<div class="hnum" id="s{i}n">{num}</div>'
            '<div class="hunit" id="s{i}u">{unit}</div>'
            '<div class="htag" id="s{i}t">{tag}</div>',
    'verdict': '<div class="kicker">{kicker}</div>'
               '<div class="vscore" id="s{i}n">{score}</div>'
               '<div class="vnote" id="s{i}u">{note}</div>',
    'final': '<div class="fhead">{head}</div><div class="fsub">{sub}</div>'
             '<div class="faddr" id="s{i}a">{addr}</div><div class="fnote">{note}</div>',
}

JS = r"""
const SCENES=__SCENES__, CAPS=__CAPS__, DUR=__DUR__, TOTAL=__TOTAL__;
const clamp=x=>x<0?0:x>1?1:x;
const ease=x=>{x=clamp(x);return x*x*(3-2*x);};
const cap=document.getElementById('cap');
const segs=[].slice.call(document.querySelectorAll('.segfill'));
const LOOP=0.5;

function numText(v,isFloat){return isFloat? String(parseFloat(v.toFixed(2))).replace('.',',') : String(Math.round(v));}

function drawMascot(){
  const svg=document.getElementById('msvg'); if(!svg||typeof rough==='undefined') return;
  const NS='http://www.w3.org/2000/svg';
  const rc=rough.svg(svg), B='#2F6BFF', F='rgba(47,107,255,.12)';
  const o={stroke:B,strokeWidth:3.2,roughness:1.5,bowing:1.1};
  const g=id=>{const e=document.createElementNS(NS,'g');e.id=id;svg.appendChild(e);return e;};

  const gBody=g('mbody');
  gBody.appendChild(rc.line(84,206,80,236,o));
  gBody.appendChild(rc.line(136,206,140,236,o));
  gBody.appendChild(rc.ellipse(76,242,30,12,{...o,fill:'#fff',fillStyle:'solid'}));
  gBody.appendChild(rc.ellipse(144,242,30,12,{...o,fill:'#fff',fillStyle:'solid'}));
  gBody.appendChild(rc.rectangle(58,140,104,66,{...o,fill:F,fillStyle:'hachure',hachureGap:8,hachureAngle:-38}));
  gBody.appendChild(rc.line(82,164,138,164,{stroke:'#FF7A3D',strokeWidth:4,roughness:1.2}));
  gBody.appendChild(rc.line(82,182,120,182,{stroke:'rgba(29,29,29,.35)',strokeWidth:3,roughness:1.2}));

  const armL=g('armL');
  armL.appendChild(rc.line(56,148,34,196,o));
  armL.appendChild(rc.circle(32,200,12,{...o,fill:'#fff',fillStyle:'solid'}));
  const armR=g('armR');
  armR.appendChild(rc.line(164,148,186,196,o));
  armR.appendChild(rc.circle(188,200,12,{...o,fill:'#fff',fillStyle:'solid'}));

  const gHead=g('mhead');
  gHead.appendChild(rc.rectangle(30,36,160,88,{...o,fill:F,fillStyle:'hachure',hachureGap:7,hachureAngle:-41}));
  gHead.appendChild(rc.rectangle(48,54,124,52,{stroke:'#16233D',strokeWidth:3,roughness:1.2,fill:'#16233D',fillStyle:'solid'}));
  const eyes=document.createElementNS(NS,'g'); eyes.id='eyes';
  [[72,78],[116,78]].forEach(([cx,cy])=>{
    const e=document.createElementNS(NS,'circle');
    e.setAttribute('cx',cx);e.setAttribute('cy',cy);e.setAttribute('r',9);
    e.setAttribute('fill','#8FD0FF');eyes.appendChild(e);
  });
  gHead.appendChild(eyes);
  gHead.appendChild(rc.curve([[92,94],[104,102],[118,94]],{stroke:'#8FD0FF',strokeWidth:4,roughness:1.1}));
  gHead.appendChild(rc.line(110,36,110,14,o));
  gHead.appendChild(rc.circle(110,10,14,{stroke:B,strokeWidth:3,fill:B,fillStyle:'solid'}));

  armL.style.transformOrigin='56px 148px';
  armR.style.transformOrigin='164px 148px';
  gHead.style.transformOrigin='110px 230px';
}

function inkSvgFor(el){
  const sc=el.closest('.scene'); if(!sc) return null;
  let svg=sc.querySelector('svg.inksvg');
  if(!svg){
    svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('class','inksvg'); svg.setAttribute('viewBox','0 0 1080 1920');
    svg.style.cssText='position:absolute;inset:0;width:1080px;height:1920px;pointer-events:none';
    sc.appendChild(svg);
  }
  return svg;
}
function inkFor(el,opt){
  const sc=el.closest('.scene'), svg=inkSvgFor(el); if(!sc||!svg) return;
  const rc=rough.svg(svg), sr=sc.getBoundingClientRect(), r=el.getBoundingClientRect();
  svg.appendChild(rc.rectangle(r.left-sr.left-6,r.top-sr.top-6,r.width+12,r.height+12,opt));
}
function inkLine(el,opt,pad){
  const sc=el.closest('.scene'), svg=inkSvgFor(el); if(!sc||!svg) return;
  const rc=rough.svg(svg), sr=sc.getBoundingClientRect(), r=el.getBoundingClientRect();
  svg.appendChild(rc.line(r.left-sr.left+pad,r.bottom-sr.top+4,r.right-sr.left-pad,r.bottom-sr.top+8,opt));
}
function drawInk(){
  if(!document.body.classList.contains('paper')||typeof rough==='undefined') return;
  document.querySelectorAll('.dgnode').forEach((el,k)=>{
    inkFor(el,{stroke:'#2F6BFF',strokeWidth:3,roughness:1.7,bowing:1.4,
      fill:'rgba(47,107,255,.05)',fillStyle:'hachure',hachureGap:10,fillWeight:1,seed:11+k});});
  document.querySelectorAll('.card').forEach((el,k)=>{
    inkFor(el,{stroke:'#2F6BFF',strokeWidth:2.6,roughness:1.6,seed:31+k});});
  document.querySelectorAll('.htag').forEach(el=>{
    inkFor(el,{stroke:'#D93A3A',strokeWidth:3.4,roughness:2.1,bowing:2,seed:77});});
  document.querySelectorAll('.hnum').forEach((el,k)=>{
    const sc=el.closest('.scene'), svg=inkSvgFor(el); if(!sc||!svg) return;
    const rc2=rough.svg(svg), sr=sc.getBoundingClientRect(), r=el.getBoundingClientRect();
    const cx=(r.left+r.right)/2-sr.left, y=r.bottom-sr.top+2;
    svg.appendChild(rc2.line(cx-235,y,cx+235,y+4,{stroke:'#FF7A3D',strokeWidth:7,roughness:2.2,seed:91+k}));});
  document.querySelectorAll('.faddr').forEach((el,k)=>{
    inkLine(el,{stroke:'#2F6BFF',strokeWidth:9,roughness:2.2,seed:131+k},40);});
}

function setPose(p){
  const L=document.getElementById('armL'), R=document.getElementById('armR'),
        H=document.getElementById('mhead'), B=document.getElementById('mbody'),
        M=document.getElementById('mascot');
  if(!L||!R) return;
  const P={
    idle:  {l:0,   r:0,   head:0,  lift:0,  sc:1},
    point: {l:6,   r:-62, head:-3, lift:-6, sc:1},
    think: {l:-74, r:8,   head:6,  lift:0,  sc:1},
    cheer: {l:-146,r:146, head:0,  lift:-14,sc:1.06},
    shrug: {l:-34, r:34,  head:-5, lift:0,  sc:1}
  }[p]||{l:0,r:0,head:0,lift:0,sc:1};
  if(p==='cheer'){
    L.style.transform='scaleY(-1) rotate(-9deg)'; R.style.transform='scaleY(-1) rotate(9deg)';
  } else {
    L.style.transform='rotate('+P.l+'deg)'; R.style.transform='rotate('+P.r+'deg)';
  }
  L.style.transformOrigin='56px 148px';
  R.style.transformOrigin='164px 148px';
  if(H){H.style.transform='rotate('+P.head+'deg)';H.style.transformOrigin='110px 230px';}
  if(M){M.dataset.lift=P.lift;M.dataset.sc=P.sc;}
}
function fitGhosts(){
  document.querySelectorAll('.ghost').forEach(g=>{
    if(!g.dataset.wrapped){
      g.innerHTML='<span style="display:inline-block;white-space:nowrap">'+g.innerHTML+'</span>';
      g.dataset.wrapped='1';
    }
    const sp=g.firstElementChild;
    const w=sp?sp.getBoundingClientRect().width:0;
    if(w>1010){g.style.transformOrigin='center';g.style.transform='scale('+(1010/w).toFixed(3)+')';}
  });
}
window.setTime=function(t){
  if(!window.__gf){fitGhosts();drawInk();window.__gf=1;}
  const m=document.getElementById('mascot');
  if(m){
    if(!m.dataset.drawn){drawMascot();m.dataset.drawn='1';}
    m.style.opacity=1;
    const bob=Math.sin(t*2.2)*4;
    const lift=parseFloat(m.dataset.lift||0), sc=parseFloat(m.dataset.sc||1);
    m.style.transform='translateY('+(bob+lift).toFixed(1)+'px) scale('+sc+')';
    const blink=(t%3.4)>3.18?0.12:1;
    const eyes=document.getElementById('eyes');
    if(eyes) eyes.style.transform='scaleY('+blink+')';
    const arm=document.getElementById('armR');
    if(arm){
      const w=Math.sin(t*3.1)*14;
      arm.style.transformOrigin='164px 140px';
      arm.style.transform='rotate('+w.toFixed(1)+'deg)';
    }
  }
  const g1=document.getElementById('g1'), g2=document.getElementById('g2'), g3=document.getElementById('g3');
  if(g1){ g1.style.transform='translate('+(40*Math.sin(t*0.45)).toFixed(1)+'px,'+(60*Math.cos(t*0.37)).toFixed(1)+'px)'; }
  if(g2){ g2.style.transform='translate('+(-50*Math.sin(t*0.32+1)).toFixed(1)+'px,'+(40*Math.sin(t*0.5)).toFixed(1)+'px)'; }
  if(g3){ g3.style.transform='translate('+(30*Math.cos(t*0.41+2)).toFixed(1)+'px,'+(-45*Math.sin(t*0.28)).toFixed(1)+'px)'; }
  const looping = t >= TOTAL - LOOP;
  SCENES.forEach(function(s,i){
    const el=document.getElementById('sc'+i);
    el.style.opacity = (!looping && t>=s.start && t<s.end) ? 1 : 0;
  });
  // прогресс
  const bounds=SCENES.map(s=>s.start).concat([TOTAL]);
  for(let i=0;i<segs.length;i++){
    const p=looping?0:clamp((t-bounds[i])/(bounds[i+1]-bounds[i]));
    segs[i].style.width=(p*100).toFixed(1)+'%';
  }
  SCENES.forEach(function(s,i){
    const lt=t-s.start, on=(t>=s.start&&t<s.end);
    if(!on) return;
    if(s.kind==='hook'){
      const n=document.getElementById('s'+i+'n');
      const p=ease(lt/0.45);
      n.style.transform='scale('+(1.32-0.32*p)+')'; n.style.opacity=p;
      document.getElementById('s'+i+'u').style.opacity=ease((lt-0.3)/0.4);
      const tag=document.getElementById('s'+i+'t');
      tag.style.opacity=ease((lt-0.6)/0.35);
      tag.style.transform='scale('+(1+0.03*Math.sin(lt*9))+')';
    } else if(s.kind==='stats'){
      s.items.forEach(function(it,k){
        const p=ease((lt-0.05-k*0.32)/0.45);
        const el=document.getElementById('s'+i+'v'+k);
        const target=it.num, isF=it.float;
        el.textContent=numText(target*p,isF);
        el.style.opacity=p.toFixed(2);
        document.getElementById('s'+i+'l'+k).style.opacity=p.toFixed(2);
      });
    } else if(s.kind==='cards'){
      s.items.forEach(function(it,k){
        const p=ease((lt-0.05-k*0.35)/0.45);
        const el=document.getElementById('s'+i+'c'+k);
        el.style.opacity=p;
        el.style.transform='translateY('+((1-p)*26).toFixed(1)+'px)';
      });
    } else if(s.kind==='verdict'){
      const p=ease(lt/0.5);
      const el=document.getElementById('s'+i+'n');
      el.textContent=(s.score*p).toFixed(1).replace('.',',');
      el.style.opacity=p;
      document.getElementById('s'+i+'u').style.opacity=ease((lt-0.35)/0.45);
    } else if(s.kind==='code'){
      const code=s.code||[];
      const total=code.join('').length||1;
      const shown=Math.floor(total*clamp((lt-0.15)/Math.max(0.8,(s.end-s.start-0.9))));
      let left=shown;
      for(let k=0;k<code.length;k++){
        const line=code[k];
        const n=Math.max(0,Math.min(line.length,left));
        left-=line.length;
        const el=document.getElementById('s'+i+'cl'+k);
        const txt=line.slice(0,n);
        el.innerHTML=(k===0?'<span class="pr">$ </span>':'')+
          (txt.startsWith('#')?'<span class="cm">'+txt+'</span>':txt)+
          (left<=0 && n===line.length && k===code.length-1?'<span class="cursor"></span>':'');
        el.style.opacity=n>0?1:0.25;
      }
    } else if(s.kind==='diagram'){
      (function(){
        const n=s.nodes||0;
        for(let k=0;k<n;k++){
          const p=ease((lt-0.1-k*0.42)/0.4);
          const el=document.getElementById('s'+i+'n'+k);
          el.style.opacity=p;
          el.style.transform='translateY('+((1-p)*24).toFixed(1)+'px) scale('+(0.96+0.04*p).toFixed(3)+')';
          const ar=document.getElementById('s'+i+'a'+k);
          if(ar){ ar.style.height=(Math.max(0,Math.min(1,(lt-0.35-k*0.42)/0.3))*150).toFixed(0)+'px'; }
        }
      })();
    } else if(s.kind==='type'){
      for(let k=0;k<(s.lines||0);k++){
        const p=ease((lt-0.05-k*0.22)/0.4);
        const el=document.getElementById('s'+i+'l'+k);
        el.style.opacity=p;
        el.style.transform='translateX('+((1-p)*-40).toFixed(1)+'px)';
        el.style.clipPath='inset(0 '+(100-p*100).toFixed(1)+'% 0 0)';
      }
      const sb=document.getElementById('s'+i+'sub');
      if(sb){ sb.style.opacity=ease((lt-0.7)/0.5); sb.style.transform='translateY('+((1-ease((lt-0.7)/0.5))*18).toFixed(1)+'px)'; }
    } else if(s.kind==='split'){
      const pv=ease(lt/0.5);
      const v=document.getElementById('s'+i+'v');
      v.style.opacity=pv; v.style.transform='translateY('+((1-pv)*26).toFixed(1)+'px)';
      document.getElementById('s'+i+'t').style.opacity=ease((lt-0.2)/0.45);
      (s.items||[]).forEach(function(it,k){
        const p=ease((lt-0.25-k*0.3)/0.45);
        const el=document.getElementById('s'+i+'i'+k);
        el.style.opacity=p; el.style.transform='translateX('+((1-p)*26).toFixed(1)+'px)';
      });
    } else if(s.kind==='film'){
      for(let k=0;k<(s.frames||0);k++){
        const p=ease((lt-0.1-k*0.32)/0.45);
        const el=document.getElementById('s'+i+'f'+k);
        el.style.opacity=p;
        const dir=(k%2===0)?-1:1;
        el.style.transform='translateX('+((1-p)*60*dir).toFixed(1)+'px) scale('+(0.96+0.04*p).toFixed(3)+')';
      }
    } else if(s.kind==='steps'){
      const rail=document.getElementById('s'+i+'rail');
      if(rail) rail.style.height=(Math.min(1, lt/1.2)*((s.items.length-1)*330+60)).toFixed(0)+'px';
      s.items.forEach(function(it,k){
        const p=ease((lt-0.1-k*0.45)/0.45);
        const c=document.getElementById('s'+i+'c'+k);
        c.style.opacity=p;
        c.style.transform='scale('+(0.65+0.35*p).toFixed(3)+')';
        document.getElementById('s'+i+'t'+k).style.opacity=p;
        document.getElementById('s'+i+'d'+k).style.opacity=p;
      });
    } else if(s.kind==='board'){
      boardFrame(i, lt, s.end-s.start);
    } else if(s.kind==='final'){
      document.querySelectorAll('#sc'+i+' .fhead').forEach(e=>e.style.opacity=ease((lt-0.02)/0.4));
      document.querySelectorAll('#sc'+i+' .fsub').forEach(e=>e.style.opacity=ease((lt-0.2)/0.4));
      const a=document.getElementById('s'+i+'a');
      const p=ease((lt-0.45)/0.5);
      a.style.opacity=p; a.style.transform='scale('+(0.92+0.08*p)+')';
      document.querySelectorAll('#sc'+i+' .fnote').forEach(e=>e.style.opacity=ease((lt-0.7)/0.4));
    }
  });
  const curScene=SCENES.find(s=>t>=s.start&&t<s.end);
  if(curScene&&curScene.pose) setPose(curScene.pose);
  const act=CAPS.find(k=>t>=k[0]&&t<=k[1]);
  if(act&&!looping){
    cap.textContent=act[2];
    cap.style.opacity=clamp((t-act[0])/0.2).toFixed(2);
    const cur=SCENES.find(s=>t>=s.start&&t<s.end);
    const onBoard=!!(cur&&cur.kind==='board');
    const isPaper=document.body.classList.contains('paper');
    cap.style.color=(onBoard||isPaper)?'#1D1D1D':'#E8FBFF';
    cap.style.textShadow=(onBoard||isPaper)?'none':'0 3px 20px rgba(0,0,0,.9)';
  }
  else cap.style.opacity='0';
};
setTime(0);
if(document.fonts&&document.fonts.ready){document.fonts.ready.then(function(){fitGhosts();});}
window.applyFrame=window.setTime;
"""


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def build(spec, cues, path):
    total = cues[-1][1] + 2.4
    scenes_js, caps, markup = [], [], []
    for i, (sc, (a, b)) in enumerate(zip(spec.scenes, cues)):
        end = cues[i + 1][0] if i + 1 < len(cues) else total
        scenes_js.append({'start': round(a, 3), 'end': round(end, 3), 'kind': sc.kind,
                          'pose': sc.data.get('pose', 'idle')})
        cap = sc.cap or (sc.say if len(sc.say) <= 70 else sc.say[:67].rsplit(' ', 1)[0] + '…')
        if sc.kind == 'final' and cap.strip().lower() == str(sc.data.get('address', '')).lower():
            cap = ''
        if cap:
            caps.append([round(a, 3), round(end - 0.05, 3), cap])

        if sc.kind == 'hook':
            m = MARKUP['hook'].format(kicker=_esc(spec.kicker), i=i,
                                      num=_esc(sc.data.get('num', '')),
                                      unit=_esc(sc.data.get('unit', '')),
                                      tag=_esc(sc.data.get('tag', '')))
            _t = spec.title.upper()
            _bs = 72 if len(_t) <= 12 else (58 if len(_t) <= 17 else 46)
            m = m.replace('<div class="hnum"',
                f'<div class="brand" style="font-size:{_bs}px;line-height:1.08;right:70px">{_esc(_t)}</div><div class="hnum"', 1)
            gsz = max(46, min(180, int(980 / (0.70 * max(4, len(spec.title.upper()))))))
            m += (f'<div class="ghostline"></div>'
                  f'<div class="ghost" style="font-size:{gsz}px">{_esc(spec.title.upper())}</div>')
        elif sc.kind == 'verdict':
            raw_score = str(sc.data.get('score', '0')).replace(',', '.')
            try:
                scenes_js[-1]['score'] = float(raw_score)
            except ValueError:
                scenes_js[-1]['score'] = 0.0
            m = MARKUP['verdict'].format(kicker=_esc(spec.kicker), i=i,
                                         score=_esc(sc.data.get('score', '')),
                                         note=_esc(sc.data.get('note', '')))
            m = m.replace('<div class="vscore"', f'<div class="brand sm">{_esc(spec.title.upper())}</div><div class="vscore"', 1)
            gsz2 = max(46, min(180, int(980 / (0.70 * max(4, len(spec.title.upper()))))))
            m += f'<div class="ghost" style="font-size:{gsz2}px">{_esc(spec.title.upper())}</div>'
        elif sc.kind == 'steps':
            items = sc.data.get('items', [])[:4]
            parsed = [{'title': it.get('title', ''), 'text': it.get('text', '')} for it in items]
            scenes_js[-1]['items'] = parsed
            top = sc.data.get('top', 560)
            step = sc.data.get('gap', 330)
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker),
                     f'<div class="rail" id="s{i}rail"></div>']
            for k, it in enumerate(items):
                y = top + k * step
                parts.append(f'<div class="stepc" id="s{i}c{k}" style="top:{y}px;left:148px">{k + 1}</div>'
                             f'<div class="stept" id="s{i}t{k}" style="top:{y + 8}px">{_esc(it.get("title", ""))}</div>'
                             f'<div class="stepd" id="s{i}d{k}" style="top:{y + 66}px">{_esc(it.get("text", ""))}</div>')
            m = ''.join(parts)
        elif sc.kind == 'type':
            lines = sc.data.get('lines', [])
            acc = int(sc.data.get('accent', -1))
            parts = [f'<div class="kicker">{_esc(spec.kicker)}</div>', '<div class="typo">']
            for k, ln in enumerate(lines[:3]):
                cls = 'ln acc' if k == acc else 'ln'
                L = len(ln)
                fs = 150 if L <= 8 else (128 if L <= 10 else (108 if L <= 12 else 92))
                parts.append(f'<span class="{cls}" id="s{i}l{k}" style="font-size:{fs}px">{_esc(ln)}</span>')
            if sc.data.get('sub'):
                parts.append(f'<div class="sub" id="s{i}sub">{_esc(sc.data["sub"])}</div>')
            parts.append('</div>')
            scenes_js[-1]['lines'] = len(lines[:3])
            m = ''.join(parts)
        elif sc.kind == 'split':
            items = sc.data.get('items', [])[:4]
            scenes_js[-1]['items'] = [{'text': x} for x in items]
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker),
                     f'<div class="splitL"><div class="k">{_esc(sc.data.get("label",""))}</div>'
                     f'<div class="v" id="s{i}v">{_esc(sc.data.get("value",""))}</div>'
                     f'<div class="t" id="s{i}t">{_esc(sc.data.get("title",""))}</div></div>',
                     f'<div class="splitR" id="s{i}r">']
            for k, it in enumerate(items):
                parts.append(f'<div class="it" id="s{i}i{k}">{_esc(it)}</div>')
            parts.append('</div>')
            m = ''.join(parts)
        elif sc.kind == 'film':
            frames = sc.data.get('frames', [])[:3]
            scenes_js[-1]['frames'] = len(frames)
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker), '<div class="filmstrip">']
            for k, fr in enumerate(frames):
                parts.append(f'<div class="fr" id="s{i}f{k}"><div class="n">{k+1:02d}</div>'
                             f'<div class="h">{_esc(fr.get("h",""))}</div>'
                             f'<div class="d">{_esc(fr.get("d",""))}</div></div>')
            parts.append('</div>')
            m = ''.join(parts)
        elif sc.kind == 'code':
            lines = sc.data.get('lines', [])[:6]
            scenes_js[-1]['code'] = lines
            body = ''.join(f'<div class="ln" id="s{i}cl{k}"></div>' for k, _ in enumerate(lines))
            m = (f'<div class="kicker">{_esc(spec.kicker)}</div>'
                 f'<div class="codebox"><div class="codebar">'
                 f'<span class="d" style="background:#FF5F57"></span><span class="d" style="background:#FEBC2E"></span>'
                 f'<span class="d" style="background:#28C840"></span>'
                 f'<span class="lbl">{_esc(sc.data.get("label", "terminal"))}</span></div>'
                 f'<div class="codebody" id="s{i}cb">{body}</div></div>')
        elif sc.kind == 'diagram':
            nodes = sc.data.get('nodes', [])[:4]
            scenes_js[-1]['nodes'] = len(nodes)
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker)]
            top = sc.data.get('top', 470)
            step = sc.data.get('gap', 330)
            for k, nd in enumerate(nodes):
                y = top + k * step
                parts.append(f'<div class="dgnode" id="s{i}n{k}" style="top:{y}px">'
                             f'<div class="t">{_esc(nd.get("t",""))}</div>'
                             f'<div class="s">{_esc(nd.get("s",""))}</div></div>')
                if k < len(nodes) - 1:
                    parts.append(f'<div class="dgarr" id="s{i}a{k}" style="top:{y+150}px;height:0"></div>')
            m = ''.join(parts)
        elif sc.kind == 'board':
            m = board_mod.markup(i, sc)
        elif sc.kind == 'final':
            m = MARKUP['final'].format(head=_esc(sc.data.get('headline', '')),
                                       sub=_esc(sc.data.get('sub', '')),
                                       addr=_esc(sc.data.get('address', 'qantcore.space')),
                                       note=_esc(sc.data.get('note', '')),
                                       i=i)
        elif sc.kind == 'stats':
            items = sc.data.get('items', [])[:4]
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker),
                     '<div class="brand sm">%s</div>' % _esc(spec.title.upper())]
            parsed = []
            for k, it in enumerate(items):
                raw = str(it.get('value', '0')).replace(',', '.')
                is_f = '.' in raw
                val = float(raw) if is_f else float(int(float(raw)))
                parsed.append({'num': round(val, 3), 'float': is_f})
                top = 300 + k * 300
                parts.append(f'<div class="statv" id="s{i}v{k}" style="top:{top}px">0</div>'
                             f'<div class="statl" id="s{i}l{k}" style="top:{top + 170}px">{_esc(it.get("label", ""))}</div>')
            scenes_js[-1]['items'] = parsed
            m = ''.join(parts) + f'<div class="ghostline"></div><div class="ghost" style="font-size:{104 if len(spec.title) > 9 else 130}px">{_esc(spec.title.upper())}</div>'
        elif sc.kind == 'cards':
            items = sc.data.get('items', [])[:3]
            parsed = [{'title': it.get('title', ''), 'text': it.get('text', '')} for it in items]
            scenes_js[-1]['items'] = parsed
            parts = ['<div class="kicker">%s</div>' % _esc(spec.kicker),
                     '<div class="brand sm">%s</div>' % _esc(spec.title.upper())]
            for k, it in enumerate(items):
                top = 360 + k * 360
                parts.append(f'<div class="card" id="s{i}c{k}" style="top:{top}px">'
                             f'<div class="t">{_esc(it.get("title", ""))}</div>'
                             f'<div class="d">{_esc(it.get("text", ""))}</div></div>')
            m = ''.join(parts)
        else:
            m = ''

        markup.append(f'<div class="scene {sc.kind}" id="sc{i}" data-kind="{sc.kind}">{m}</div>')

    seg_html = ''.join('<div class="seg"><div class="segfill"></div></div>' for _ in spec.scenes)
    pal = PALETTES.get(getattr(spec, 'palette', 'teal'), PALETTES['teal'])
    bgstyle = getattr(spec, 'bgstyle', 'mesh')
    root_css = (f":root{{--bg:{pal['bg']};--bg2:{pal['bg2']};--a1:{pal['a1']};"
                f"--a2:{pal['a2']};--a3:{pal['a3']}}}")
    board_css = board_mod.BOARD_CSS.replace('__FONT__', board_mod.assets()['font'])
    paper = getattr(spec, 'palette', '') == 'paper'
    extra_css = PAPER_CSS if paper else ''
    body_cls = ' class="paper"' if paper else ''
    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{root_css}{CSS.replace('__W__', str(W)).replace('__H__', str(H))}{board_css}{extra_css}</style></head>
<body{body_cls}><div id="stage">
<div id="bggrid" style="opacity:{1 if bgstyle == 'grid' else 0}"></div><div id="bgdots" style="opacity:{1 if bgstyle == 'dots' else 0}"></div>
<div class="glow" id="g1"></div><div class="glow" id="g2"></div><div class="glow" id="g3"></div>
<div id="prog">{seg_html}</div>
{''.join(markup)}
<svg id="ink" width="1080" height="1920" style="position:absolute;inset:0;pointer-events:none;z-index:6"></svg>
<div class="mascot" id="mascot"><svg id="msvg" viewBox="0 0 220 270"></svg></div>
<div id="cap"></div>
</div>
<script>{board_mod.assets()['rough']}\n{board_mod.BOARD_JS}\n{JS.replace('__SCENES__', json.dumps(scenes_js)).replace('__CAPS__', json.dumps(caps, ensure_ascii=False)).replace('__TOTAL__', f'{total:.3f}').replace('__DUR__', f'{total:.3f}')}</script>
</body></html>'''

    if not getattr(spec, 'mascot', False):
        i = html.find('<div class="mascot" id="mascot">')
        j = html.find('<div id="cap">')
        if i > 0 and j > i:
            html = html[:i] + html[j:]
    open(path, 'w', encoding='utf-8').write(html)
    return path, total
