"""Обложка 1280×720 (YouTube): лого слева, цифра и робот справа."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys

sys.path.insert(0, '/opt/qc-video')
from qcv import cover as cover_mod, spec as spec_mod

CHROME = '/usr/local/bin/google-chrome'
W, H = 1280, 720


def html(spec, logo_path):
    title = spec.title.upper()
    if len(title) > 16 and ' ' in title:
        head, tail = title.split(' ', 1)
        title = f'{head}<br>{tail}'
    num, unit = cover_mod._pick_number(spec)
    tag = cover_mod._tagline(spec)
    size = 96 if len(spec.title) <= 12 else (74 if len(spec.title) <= 18 else 58)
    logo = ''
    left = 232 if logo_path else 58
    width = 600 if logo_path else 760
    if logo_path:
        mime = 'image/svg+xml' if logo_path.endswith('.svg') else 'image/png'
        b64 = base64.b64encode(open(logo_path, 'rb').read()).decode()
        logo = f'<div class="logo"><img src="data:{mime};base64,{b64}" alt=""></div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:#F7F4EA;font-family:'DejaVu Sans',sans-serif;overflow:hidden}}
.wrap{{position:relative;width:{W}px;height:{H}px;
 background-image:radial-gradient(rgba(0,0,0,.06) 1.6px,transparent 1.6px);background-size:40px 40px}}
.kick{{position:absolute;left:56px;top:70px;font-size:22px;letter-spacing:.28em;color:#2F6BFF;font-weight:700}}
.logo{{position:absolute;left:56px;top:130px;width:150px;height:150px;border-radius:36px;background:#fff;
 border:2px solid rgba(0,0,0,.07);display:flex;align-items:center;justify-content:center;
 box-shadow:0 10px 24px rgba(60,50,30,.12)}}
.logo img{{width:104px;height:104px;object-fit:contain}}
h1{{position:absolute;left:{left}px;top:140px;width:{width}px;font-size:{size}px;line-height:.98;letter-spacing:-.02em;font-weight:800}}
.desc{{position:absolute;left:58px;top:330px;width:660px;font-size:38px;font-weight:800;line-height:1.2;
 padding-left:22px;border-left:8px solid #FF7A3D}}
.num{{position:absolute;right:70px;top:250px;font-size:210px;font-weight:800;line-height:1;color:#FF7A3D;text-align:right}}
.unit{{position:absolute;right:74px;top:470px;width:520px;font-size:28px;color:#3A4452;text-align:right;line-height:1.25}}
.foot{{position:absolute;left:56px;bottom:52px;font-size:24px;color:#4A5568}}
.foot b{{display:block;font-size:40px;color:#1D1D1D;margin-bottom:2px}}
.badge{{position:absolute;right:70px;bottom:56px;padding:10px 20px;border:3px dashed #2F6BFF;border-radius:14px;
 font-size:22px;color:#2F6BFF;transform:rotate(-3deg)}}
</style></head><body><div class="wrap">
<div class="kick">{spec.kicker.upper()} · QANTCORE</div>
{logo}
<h1>{title}</h1>
<div class="desc">{tag}</div>
<div class="num">{num}</div>
<div class="unit">{unit}</div>
<div class="foot"><b>qantcore.space</b>полный разбор</div>
<div class="badge">видеоразбор</div>
</div></body></html>"""


def make(spec_json, out_png):
    sp = spec_mod.load(spec_json)
    logo = cover_mod.find_logo(sp)
    html_path = out_png.replace('.png', '.html')
    open(html_path, 'w', encoding='utf-8').write(html(sp, logo))
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    f'--window-size={W},{H}', f'--screenshot={out_png}', f'file://{html_path}'],
                   check=False, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_png


if __name__ == '__main__':
    n = 0
    for f in sorted(os.listdir('/opt/qc-video/specs')):
        if not f.endswith('.json'):
            continue
        slug = f[:-5]
        out = f'/var/www/qantcore/images/covers/{slug}-16x9.png'
        try:
            make(os.path.join('/opt/qc-video/specs', f), out)
            n += 1
        except Exception as e:
            print('fail', slug, e)
    print(n, 'широких обложек')
