"""Белый маркер-слой: rough.js, штрихи ложатся по ходу речи."""
import base64
import os

FONT_PATH = '/opt/qantcore/htmlvid/fonts/Caveat.ttf'
ROUGH_PATH = '/opt/qantcore/sketch/lib/rough.js'

_cache = {}


def assets():
    if 'font' not in _cache:
        _cache['font'] = base64.b64encode(open(FONT_PATH, 'rb').read()).decode()
    if 'rough' not in _cache:
        _cache['rough'] = open(ROUGH_PATH, encoding='utf-8').read()
    return _cache


BOARD_CSS = """
.board{background:#F7F4EA}
.board svg{position:absolute;inset:0}
.board .bcap{position:absolute;left:70px;right:70px;bottom:120px;text-align:center;
  font-family:Caveat,serif;font-size:44px;color:#3A3A3A;opacity:.9}
@font-face{font-family:Caveat;src:url(data:font/ttf;base64,__FONT__) format('truetype')}
"""


def markup(i, sc):
    """SVG-контейнер: содержимое рисуется в JS через rough.js."""
    items = sc.data.get('items', [])[:3]
    heading = sc.data.get('heading', '')
    import json
    return (f'<svg id="sv{i}" viewBox="0 0 1080 1920" data-items=\'{json.dumps(items, ensure_ascii=False)}\' '
            f'data-heading="{heading}"></svg>')


BOARD_JS = r"""
function boardSetup(i){
  const svg=document.getElementById('sv'+i);
  if(!svg || svg.dataset.done) return;
  const items=JSON.parse(svg.dataset.items||'[]');
  const heading=svg.dataset.heading||'';
  const rs=rough.svg(svg);
  const NS='http://www.w3.org/2000/svg';
  const groups=[];

  function group(){
    const g=document.createElementNS(NS,'g');
    svg.appendChild(g); return g;
  }
  function paths(g){
    return [].slice.call(g.querySelectorAll('path')).map(p=>{
      const len=p.getTotalLength?p.getTotalLength():600;
      p.style.strokeDasharray=len; p.style.strokeDashoffset=len;
      return {p,len};
    });
  }
  function textReveal(g, x, y, size, txt, color, weight){
    const clip=document.createElementNS(NS,'clipPath');
    clip.id='cl'+i+Math.random().toString(36).slice(2,7);
    const rect=document.createElementNS(NS,'rect');
    rect.setAttribute('x',x-20); rect.setAttribute('y',y-size*1.1);
    rect.setAttribute('height',size*1.6); rect.setAttribute('width',0);
    clip.appendChild(rect); svg.appendChild(clip);
    const t=document.createElementNS(NS,'text');
    t.setAttribute('x',x); t.setAttribute('y',y);
    t.setAttribute('font-family','Caveat'); t.setAttribute('font-size',size);
    t.setAttribute('fill',color); t.setAttribute('font-weight',weight||400);
    t.textContent=txt; t.setAttribute('clip-path','url(#'+clip.id+')');
    g.appendChild(t);
    return rect;
  }

  // заголовок
  const g0=group();
  const headRect=textReveal(g0, 80, 250, 96, heading, '#1D1D1D');
  const under=rs.line(84, 285, Math.min(1000, 84+heading.length*44), 282, {stroke:'#D93A3A', strokeWidth:7, roughness:1.2});
  g0.appendChild(under);
  groups.push({g:g0, paths:paths(g0), rect:headRect, start:0, dur:0.5});

  // блоки и стрелки
  const top=470, boxH=270, gap=130;
  items.forEach(function(it,k){
    const y=top+k*(boxH+gap);
    const gb=group();
    const box=rs.rectangle(72, y, 936, boxH, {stroke:'#1D1D1D', strokeWidth:4, roughness:1.6, bowing:1.4});
    gb.appendChild(box);
    const num=textReveal(gb, 104, y+78, 54, (k+1)+'.', '#D93A3A');
    const title=textReveal(gb, 160, y+96, 62, it.title||'', '#1D1D1D');
    const sub=textReveal(gb, 106, y+180, 44, it.text||'', '#2A2A2A');
    groups.push({g:gb, paths:paths(gb), rect:num, rects:[title,sub],
                 start:0.55+k*0.9, dur:0.55});

    if(k<items.length-1){
      const ga=group();
      const arrow=rs.line(540, y+boxH+18, 540, y+boxH+gap-18,
                          {stroke:'#0F8F7E', strokeWidth:6, roughness:1.1});
      ga.appendChild(arrow);
      ga.appendChild(rs.line(540, y+boxH+gap-18, 512, y+boxH+gap-52, {stroke:'#0F8F7E', strokeWidth:6}));
      ga.appendChild(rs.line(540, y+boxH+gap-18, 568, y+boxH+gap-52, {stroke:'#0F8F7E', strokeWidth:6}));
      groups.push({g:ga, paths:paths(ga), start:0.55+k*0.9+0.5, dur:0.28});
    }
  });
  svg._groups=groups; svg._total=Math.max.apply(null, groups.map(g=>g.start+g.dur));
  svg.dataset.done='1';
}

function boardFrame(i, lt, dur){
  const svg=document.getElementById('sv'+i);
  if(!svg) return;
  boardSetup(i);
  const groups=svg._groups||[];
  const scale=dur/Math.max(0.1, svg._total||1);
  groups.forEach(function(gr){
    const s=gr.start*scale, d=Math.max(0.12, gr.dur*scale);
    const p=clamp((lt-s)/d);
    (gr.paths||[]).forEach(function(o){
      o.p.style.strokeDashoffset=(o.len*(1-p)).toFixed(1);
      o.p.style.opacity=p>0?1:0;
    });
    if(gr.rect) gr.rect.setAttribute('width', (1000*p).toFixed(0));
    if(gr.rects) gr.rects.forEach(function(r){ r.setAttribute('width',(1000*p).toFixed(0)); });
  });
}
"""
