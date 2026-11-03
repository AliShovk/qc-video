"""Обложка ролика: HTML → PNG через headless Chrome.

Собирается из той же спеки, что и видео: название, кикер, главная цифра
(из хука или вердикта), подпись, адрес. Стиль — бумажный, с рисованным роботом.
"""
from __future__ import annotations

import json
import os
import subprocess

CHROME = '/usr/local/bin/google-chrome'
ROUGH = '/opt/qantcore/sketch/lib/rough.js'
W, H = 1080, 1920


def _pick_number(spec):
    """Главная цифра обложки: из хука, иначе из вердикта."""
    for sc in spec.scenes:
        d = getattr(sc, 'data', {}) or {}
        if sc.kind == 'hook' and d.get('num'):
            return str(d['num']).strip(), str(d.get('unit', '')).strip()
        if sc.kind == 'verdict' and d.get('score'):
            return str(d['score']).strip(), 'из 10 — вердикт'
    return '', ''


def _tagline(spec):
    for sc in spec.scenes:
        d = getattr(sc, 'data', {}) or {}
        if sc.kind in ('hook', 'type') and d.get('tag'):
            return str(d['tag']).strip()
        if sc.kind == 'final' and d.get('sub'):
            return str(d['sub']).strip()
    return ''


def _html(spec, path_png):
    title = spec.title.upper()
    if len(title) > 14 and ' ' in title:
        head, tail = title.split(' ', 1)
        title = f'{head}<br>{tail}'

    num, unit = _pick_number(spec)
    tag = _tagline(spec)
    kicker = (spec.kicker or 'обзор').upper()
    size = 118 if len(title) <= 12 else (96 if len(title) <= 18 else 76)
    rough = open(ROUGH, encoding='utf-8').read() if os.path.exists(ROUGH) else ''

    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#F7F4EA;color:#1D1D1D;
 font-family:'DejaVu Sans',sans-serif;overflow:hidden}}
.wrap{{position:relative;width:{W}px;height:{H}px;
 background-image:radial-gradient(rgba(0,0,0,.07) 1.7px,transparent 1.7px);background-size:44px 44px}}
.kick{{position:absolute;left:80px;top:150px;font-size:26px;letter-spacing:.3em;color:#2F6BFF;font-weight:700}}
h1{{position:absolute;left:80px;top:250px;width:920px;font-size:{size}px;line-height:.98;
 letter-spacing:-.02em;font-weight:800}}
.mark{{position:absolute;left:84px;top:508px;width:190px;height:12px}}
.num{{position:absolute;left:78px;top:560px;font-size:180px;font-weight:800;line-height:1;color:#FF7A3D}}
.unit{{position:absolute;left:84px;top:790px;width:820px;font-size:40px;color:#3A4452;line-height:1.3}}
.tag{{position:absolute;left:80px;top:900px;width:900px;padding:22px 26px;border:3px dashed #2F6BFF;
 border-radius:22px;font-size:34px;color:#2F6BFF;line-height:1.3}}
.foot{{position:absolute;left:80px;bottom:130px;width:620px;font-size:34px;color:#4A5568}}
.foot b{{display:block;font-size:56px;color:#1D1D1D;margin-bottom:8px}}
.badge{{position:absolute;right:80px;bottom:120px;padding:16px 26px;border:3px dashed #2F6BFF;border-radius:18px;
 font-size:30px;color:#2F6BFF;transform:rotate(-4deg)}}
#bot{{position:absolute;right:30px;bottom:300px;width:320px;height:364px}}
</style></head><body><div class="wrap">
<div class="kick">{kicker} · QANTCORE</div>
<h1>{title}</h1>
<svg class="mark" viewBox="0 0 190 12"><path d="M4 8 C 40 2, 80 11, 118 5 S 168 9, 186 4"
 stroke="#FF7A3D" stroke-width="7" fill="none" stroke-linecap="round"/></svg>
<div class="num">{num}</div>
<div class="unit">{unit}</div>
<div class="tag">{tag}</div>
<svg id="bot" viewBox="0 0 300 340"></svg>
<div class="foot"><b>qantcore.space</b>полный разбор</div>
<div class="badge">видеоразбор</div>
</div>
<script>{rough}</script>
<script>
(function(){{
  if(typeof rough==='undefined') return;
  const svg=document.getElementById('bot'), rc=rough.svg(svg), B='#2F6BFF', NS='http://www.w3.org/2000/svg';
  const o={{stroke:B,strokeWidth:3.4,roughness:1.6,bowing:1.3}};
  const F={{fill:'rgba(47,107,255,.12)',fillStyle:'hachure',hachureGap:8}};
  const body=document.createElementNS(NS,'g');
  body.appendChild(rc.line(114,240,108,278,o)); body.appendChild(rc.line(186,240,192,278,o));
  body.appendChild(rc.ellipse(102,284,34,13,Object.assign({{}},o,{{fill:'#fff',fillStyle:'solid'}})));
  body.appendChild(rc.ellipse(198,284,34,13,Object.assign({{}},o,{{fill:'#fff',fillStyle:'solid'}})));
  body.appendChild(rc.rectangle(80,150,140,90,Object.assign({{}},o,F,{{hachureAngle:-38}})));
  body.appendChild(rc.line(110,182,190,182,{{stroke:'#FF7A3D',strokeWidth:5,roughness:1.2}}));
  body.appendChild(rc.line(110,205,165,205,{{stroke:'rgba(29,29,29,.35)',strokeWidth:4,roughness:1.2}}));
  svg.appendChild(body);
  const head=document.createElementNS(NS,'g');
  head.appendChild(rc.rectangle(38,40,224,110,Object.assign({{}},o,F,{{hachureGap:7,hachureAngle:-41}})));
  head.appendChild(rc.rectangle(60,62,180,66,{{stroke:'#16233D',strokeWidth:3,roughness:1.2,fill:'#16233D',fillStyle:'solid'}}));
  [[96,95],[150,95]].forEach(function(p){{var c=document.createElementNS(NS,'circle');
    c.setAttribute('cx',p[0]);c.setAttribute('cy',p[1]);c.setAttribute('r',11);c.setAttribute('fill','#8FD0FF');head.appendChild(c);}});
  head.appendChild(rc.curve([[124,110],[136,120],[150,110]],{{stroke:'#8FD0FF',strokeWidth:5,roughness:1.1}}));
  head.appendChild(rc.line(150,40,150,18,o));
  head.appendChild(rc.circle(150,14,16,{{stroke:B,strokeWidth:3,fill:B,fillStyle:'solid'}}));
  svg.appendChild(head);
  svg.appendChild(rc.line(62,168,34,214,o)); svg.appendChild(rc.circle(30,220,14,Object.assign({{}},o,{{fill:'#fff',fillStyle:'solid'}})));
  svg.appendChild(rc.line(238,168,266,206,o)); svg.appendChild(rc.circle(270,212,14,Object.assign({{}},o,{{fill:'#fff',fillStyle:'solid'}})));
}})();
</script>
</body></html>"""


def make(spec, out_png):
    """Рисует обложку из спеки. Возвращает путь к PNG.

    Если в спеке указан готовый файл (`cover`), используется он.
    """
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    custom = (getattr(spec, 'cover', '') or '').strip()
    if custom and os.path.exists(custom):
        import shutil
        shutil.copy(custom, out_png)
        return out_png
    html_path = out_png.replace('.png', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(_html(spec, out_png))
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    f'--window-size={W},{H}', f'--screenshot={out_png}', f'file://{html_path}'],
                   check=False, timeout=120,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(out_png) or os.path.getsize(out_png) < 5000:
        raise RuntimeError('обложка не отрисовалась')
    return out_png
