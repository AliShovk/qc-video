"""Публикация на сайте."""
import os
import shutil

DEST = '/var/www/qantcore/video/reviews'
COVERS = '/var/www/qantcore/images/covers'
BASE = 'https://qantcore.space/video/reviews'
CBASE = 'https://qantcore.space/images/covers'


def publish(mp4, srt, name=None, cover=None):
    os.makedirs(DEST, exist_ok=True)
    name = name or os.path.basename(mp4)
    shutil.copy(mp4, os.path.join(DEST, name))
    out = {'mp4': f'{BASE}/{name}'}
    if srt and os.path.exists(srt):
        srt_name = os.path.splitext(name)[0] + '.srt'
        shutil.copy(srt, os.path.join(DEST, srt_name))
        out['srt'] = f'{BASE}/{srt_name}'
    if cover and os.path.exists(cover):
        os.makedirs(COVERS, exist_ok=True)
        cov_name = os.path.splitext(name)[0] + '.png'
        shutil.copy(cover, os.path.join(COVERS, cov_name))
        out['cover'] = f'{CBASE}/{cov_name}'
    return out
