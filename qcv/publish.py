"""Публикация на сайте."""
import os
import shutil

DEST = '/var/www/qantcore/video/reviews'
BASE = 'https://qantcore.space/video/reviews'


def publish(mp4, srt, name=None):
    os.makedirs(DEST, exist_ok=True)
    name = name or os.path.basename(mp4)
    shutil.copy(mp4, os.path.join(DEST, name))
    out = {'mp4': f'{BASE}/{name}'}
    if srt and os.path.exists(srt):
        srt_name = os.path.splitext(name)[0] + '.srt'
        shutil.copy(srt, os.path.join(DEST, srt_name))
        out['srt'] = f'{BASE}/{srt_name}'
    return out
