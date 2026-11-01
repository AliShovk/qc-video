#!/usr/bin/env python3
"""Анимация спички на слое anim: рисуется, вспыхивает, горит и гаснет."""
import base64
import os
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/htmlvid')
sys.path.insert(0, '/opt/qantcore/minibot')

import render  # noqa: E402

W, H, FPS = 1080, 1920, 30
DUR = 5.6
WORK = '/root/qc-video/builds/match'
os.makedirs(WORK, exist_ok=True)

FONT = base64.b64encode(open('/opt/qantcore/htmlvid/fonts/Caveat.ttf', 'rb').read()).decode()
ROUGH = open('/opt/qantcore/sketch/lib/rough.js', encoding='utf-8').read()

HTML = r'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
@font-face{font-family:Caveat;src:url(data:font/ttf;base64,__FONT__) format('truetype')}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#F7F4EA}
#stage{position:relative;width:1080px;height:1920px;background:#F7F4EA}
#paper{position:absolute;inset:0;background:
  radial-gradient(60% 40% at 50% 40%, rgba(0,0,0,.035) 0%, rgba(0,0,0,0) 70%)}
svg{position:absolute;inset:0}
#label{position:absolute;left:0;right:0;bottom:210px;text-align:center;
  font-family:Caveat;font-size:62px;color:#2A2A2A;opacity:0}
</style></head><body>
<div id="stage"><div id="paper"></div>
<svg id="sv" viewBox="0 0 1080 1920"></svg>
<div id="label">спичка</div>
</div>
<script>__ROUGH__</script>
<script>
const svg=document.getElementById('sv');
const rs=rough.svg(svg);
const NS='http://www.w3.org/2000/svg';
const T0=0.0, T_STICK=0.95, T_HEAD=1.5, T_SPARK=1.85, T_FLAME=2.25, T_BURN_END=4.7, T_OUT=5.1;

function el(tag,attrs){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);return e;}

// --- статичная геометрия
const STICK_TOP=820, STICK_BOT=1560, STICK_W=17;
const g=el('g',{}); svg.appendChild(g);

function drawPath(node){ g.appendChild(node); return node; }

// древко
const stick=drawPath(rs.line(540, STICK_TOP, 540, STICK_BOT,
  {stroke:'#8B5A2B', strokeWidth:STICK_W, roughness:1.1, bowing:.6}));
// голова
const head=drawPath(rs.ellipse(540, STICK_TOP-18, 58, 78,
  {fill:'#B3412C', fillStyle:'solid', stroke:'#78281A', strokeWidth:3, roughness:1.0}));
// обрезка сгоревшей части: клип по Y
const clip=el('clipPath',{id:'burn'});
const clipRect=el('rect',{x:0,y:STICK_TOP,width:1080,height:1920-STICK_TOP});
clip.appendChild(clipRect); svg.appendChild(clip);
stick.setAttribute('clip-path','url(#burn)');

// пламя (две оболочки) и искры
const flameOuter=drawPath(rs.curve([
  [540,700],[505,760],[498,815],[520,860],[540,872],[560,860],[582,815],[575,760],[540,700]
], {stroke:'#E4572E', strokeWidth:7, roughness:1.4, fill:'#F2994A', fillStyle:'solid'}));
const flameInner=drawPath(rs.curve([
  [540,762],[524,795],[522,828],[540,845],[558,828],[556,795],[540,762]
], {stroke:'#F2C14E', strokeWidth:5, roughness:1.2, fill:'#FFE066', fillStyle:'solid'}));
flameOuter.style.transformOrigin='540px 800px';
flameInner.style.transformOrigin='540px 805px';

const flameG=el('g',{});
flameG.appendChild(flameOuter); flameG.appendChild(flameInner);
g.appendChild(flameG);

const spark=el('g',{});
for(let i=0;i<10;i++){
  const a=i/10*Math.PI*2, r1=34, r2=58+ (i%3)*10;
  spark.appendChild(el('line',{x1:540+Math.cos(a)*r1,y1:800+Math.sin(a)*r1,
    x2:540+Math.cos(a)*r2,y2:800+Math.sin(a)*r2,stroke:'#E4A11B','stroke-width':5,'stroke-linecap':'round'}));
}
g.appendChild(spark);

// угольки
const embers=[];
for(let i=0;i<9;i++){
  const c=el('circle',{cx:540,cy:800,r:3+i%3,fill:i%2?'#E4572E':'#F2C14E'});
  g.appendChild(c); embers.push({node:c, dx:(i-4)*9 + (i%3-1)*6, delay:(i*0.13)});
}

// длины для штрихов
[[stick],[head],[flameOuter],[flameInner]].forEach(function(arr){
  arr.forEach(function(node){
    node.querySelectorAll('path').forEach(function(p){
      const L=p.getTotalLength?p.getTotalLength():500;
      p.style.strokeDasharray=L; p.style.strokeDashoffset=L; p._len=L;
    });
  });
});
function progressPaths(node, pct){
  node.querySelectorAll('path').forEach(function(p){
    p.style.strokeDashoffset=(p._len*(1-pct)).toFixed(1);
  });
}

const label=document.getElementById('label');

window.setTime=function(t){
  // 1. древко
  progressPaths(stick, Math.min(1,(t-T0)/T_STICK));
  // 2. голова
  progressPaths(head, Math.min(1,(t-T_STICK)/0.5));
  // 3. искра
  const sp=(t-T_SPARK)/0.5;
  spark.style.opacity = sp>0 && sp<1 ? Math.min(1, 2.2*(1-sp)).toFixed(2) : 0;
  spark.style.transformOrigin='540px 800px';
  spark.style.transform='scale('+(0.6+sp*0.9).toFixed(2)+')';
  // 4. пламя
  const fl=Math.max(0,Math.min(1,(t-T_FLAME)/0.45));
  const burn=Math.max(0,Math.min(1,(t-T_FLAME)/(T_BURN_END-T_FLAME)));
  const flick=1+0.06*Math.sin(t*17)+0.04*Math.sin(t*29+1.1);
  const dying=Math.max(0,Math.min(1,(t-T_BURN_END)/(T_OUT-T_BURN_END)));
  const flameAmp=fl*(1-dying);
  const burnPxForFlame=burn*(STICK_BOT-STICK_TOP-60);
  flameOuter.style.opacity=flameAmp;
  flameInner.style.opacity=flameAmp;
  const fs=(0.55+0.55*fl)*flick*(1-0.55*dying);
  flameG.style.transform='translateY('+(burnPxForFlame).toFixed(1)+'px)';
  flameOuter.style.transform='scale('+fs.toFixed(3)+')';
  flameInner.style.transform='scale('+(fs*0.92).toFixed(3)+')';
  progressPaths(flameOuter, fl);
  progressPaths(flameInner, fl);

  // 5. горение: клип сверху, голова едет вниз
  const burnPx=burn*(STICK_BOT-STICK_TOP-60);
  clipRect.setAttribute('y', (STICK_TOP+burnPx).toFixed(1));
  head.style.transform='translateY('+(burnPx).toFixed(1)+'px)';
  head.style.opacity = t<T_HEAD+0.5 ? 1 : (1-0.15*dying);
  head.querySelectorAll('path').forEach(function(pp){
    if(pp.getAttribute('fill') && pp.getAttribute('fill')!=='none'){
      pp.setAttribute('fill', dying>0.45 ? '#4A3A32' : '#B3412C');
    }
  });

  // 6. угольки
  embers.forEach(function(e,i){
    const since=t-(T_FLAME+0.4+e.delay);
    const life=1.6;
    if(since<0||since>life){ e.node.setAttribute('opacity',0); return; }
    const p=since/life;
    e.node.setAttribute('opacity',(1-p).toFixed(2));
    e.node.setAttribute('cx',(540+e.dx*(0.4+p)).toFixed(1));
    e.node.setAttribute('cy',(800+burnPx-since*70+p*p*40).toFixed(1));
  });

  // 7. подпись
  label.style.opacity=Math.max(0,Math.min(1,(t-0.4)/0.5))*(1-Math.max(0,Math.min(1,(t-T_BURN_END)/0.4)));
};
setTime(0);
window.applyFrame=window.setTime;
</script></body></html>'''

html = HTML.replace('__FONT__', FONT).replace('__ROUGH__', ROUGH)
path = f'{WORK}/match.html'
open(path, 'w', encoding='utf-8').write(html)

render.W, render.H = W, H
frames = f'{WORK}/frames'
subprocess.run(['rm', '-rf', frames])
render.render_frames_cdp(path, frames, DUR, FPS, port=9621)

out = f'{WORK}/match.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{frames}/%05d.jpg',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
                '-t', str(DUR), out], check=True)
print('ГОТОВО', out)
