"""HTML-сцена: тёмный неон, сцены по таймингам, прогресс-бар, луп."""
import json

from . import board as board_mod

W, H = 1080, 1920

PALETTES = {
    'teal': {'bg': 'var(--bg)', 'bg2': 'var(--bg2)', 'a1': 'var(--a1)', 'a2': 'var(--a2)', 'a3': 'var(--a3)'},
    'violet': {'bg': '#0A0614', 'bg2': '#1B0B33', 'a1': '#C6F432', 'a2': '#8B5CF6', 'a3': '#FF5DB1'},
    'amber': {'bg': '#0C0703', 'bg2': '#2A1405', 'a1': '#FFC24B', 'a2': '#FF6B3D', 'a3': '#7CE0C3'},
}

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:__W__px;height:__H__px;overflow:hidden;background:var(--bg);
  font-family:'DejaVu Sans',sans-serif;color:#E8FBFF}
#stage{position:relative;width:__W__px;height:__H__px;overflow:hidden;
  background:radial-gradient(80% 55% at 50% 20%,var(--bg2) 0%,#061018 55%,#03070B 100%)}
.scene{position:absolute;inset:0;opacity:0}
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
.ghost{position:absolute;left:0;right:0;top:1300px;text-align:center;font-size:170px;font-weight:800;letter-spacing:.02em;white-space:nowrap;color:rgba(0,224,184,.10)}
.ghostline{position:absolute;left:340px;right:340px;top:1260px;height:2px;background:rgba(0,224,184,.18)}
.rail{position:absolute;left:206px;top:560px;width:4px;height:0;background:var(--a1);opacity:.35}
.stepc{position:absolute;left:148px;width:120px;height:120px;border-radius:50%;border:4px solid var(--a1);
  display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:800;color:var(--a1);
  background:rgba(4,10,15,.65)}
.stept{position:absolute;left:312px;right:70px;font-size:46px;font-weight:700;line-height:1.15}
.stepd{position:absolute;left:314px;right:70px;font-size:30px;color:#8FD9E8;line-height:1.25}
.fnote{position:absolute;left:0;right:0;top:1120px;text-align:center;font-size:32px;color:#7FB3C4}
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

window.setTime=function(t){
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
  const act=CAPS.find(k=>t>=k[0]&&t<=k[1]);
  if(act&&!looping){
    cap.textContent=act[2];
    cap.style.opacity=clamp((t-act[0])/0.2).toFixed(2);
    const cur=SCENES.find(s=>t>=s.start&&t<s.end);
    const onBoard=!!(cur&&cur.kind==='board');
    cap.style.color=onBoard?'#1D1D1D':'#E8FBFF';
    cap.style.textShadow=onBoard?'none':'0 3px 20px rgba(0,0,0,.9)';
  }
  else cap.style.opacity='0';
};
setTime(0);
window.applyFrame=window.setTime;
"""


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def build(spec, cues, path):
    total = cues[-1][1] + 2.4
    scenes_js, caps, markup = [], [], []
    for i, (sc, (a, b)) in enumerate(zip(spec.scenes, cues)):
        end = cues[i + 1][0] if i + 1 < len(cues) else total
        scenes_js.append({'start': round(a, 3), 'end': round(end, 3), 'kind': sc.kind})
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
            m = m.replace('<div class="hnum"', f'<div class="brand">{_esc(spec.title.upper())}</div><div class="hnum"', 1)
            gsz = 210 if len(spec.title) <= 6 else (150 if len(spec.title) <= 10 else 112)
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
            m += f'<div class="ghost">{_esc(spec.title.upper())}</div>'
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
            m = ''.join(parts) + f'<div class="ghostline"></div><div class="ghost" style="font-size:120px">{_esc(spec.title.upper())}</div>'
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
    root_css = (f":root{{--bg:{pal['bg']};--bg2:{pal['bg2']};--a1:{pal['a1']};"
                f"--a2:{pal['a2']};--a3:{pal['a3']}}}")
    board_css = board_mod.BOARD_CSS.replace('__FONT__', board_mod.assets()['font'])
    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{root_css}{CSS.replace('__W__', str(W)).replace('__H__', str(H))}{board_css}</style></head>
<body><div id="stage">
<div class="glow" id="g1"></div><div class="glow" id="g2"></div><div class="glow" id="g3"></div>
<div id="prog">{seg_html}</div>
{''.join(markup)}
<div id="cap"></div>
</div>
<script>{board_mod.assets()['rough']}\n{board_mod.BOARD_JS}\n{JS.replace('__SCENES__', json.dumps(scenes_js)).replace('__CAPS__', json.dumps(caps, ensure_ascii=False)).replace('__TOTAL__', f'{total:.3f}').replace('__DUR__', f'{total:.3f}')}</script>
</body></html>'''

    open(path, 'w', encoding='utf-8').write(html)
    return path, total
