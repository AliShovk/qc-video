"""Проверки качества: длительность, звук, кадры, обрезка."""
import os
import re
import subprocess


def _probe(path, entries):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entries,
                          '-of', 'default=nw=1', path],
                         capture_output=True, text=True).stdout
    return dict(l.split('=', 1) for l in out.strip().splitlines() if '=' in l)


def check(path, expect=None, tol=0.12):
    info = _probe(path, 'format=duration:stream=width,height,codec_name')
    dur = float(info.get('duration', 0))
    res = {'path': path, 'duration': round(dur, 2),
           'width': info.get('width'), 'height': info.get('height')}
    problems = []

    if expect and abs(dur - expect) > max(2.0, expect * tol):
        problems.append(f'длительность {dur:.1f} с против ожидаемых {expect:.1f}')

    if str(info.get('width')) != '1080' or str(info.get('height')) != '1920':
        problems.append(f'разрешение {info.get("width")}x{info.get("height")}')

    vd = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-f', 'null', '-'],
                        capture_output=True, text=True).stderr
    mean = re.search(r'mean_volume: (-?[\d.]+) dB', vd)
    peak = re.search(r'max_volume: (-?[\d.]+) dB', vd)
    if mean and peak:
        res['mean_db'] = float(mean.group(1))
        res['peak_db'] = float(peak.group(1))
        if res['peak_db'] > -0.2:
            problems.append(f'пик {res["peak_db"]} dB — клиппинг')
        if not (-22 <= res['mean_db'] <= -11):
            problems.append(f'средняя громкость {res["mean_db"]} dB вне коридора')
    else:
        problems.append('нет звуковой дорожки')

    res['problems'] = problems
    res['ok'] = not problems
    return res


def grab(path, times, out_dir='/tmp/qcv-frames'):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for t in times:
        p = f'{out_dir}/f{str(t).replace(".", "_")}.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', path,
                        '-frames:v', '1', p], check=True)
        paths.append(p)
    return paths
