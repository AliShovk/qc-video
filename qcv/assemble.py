"""Сборка кадров и финального MP4."""
import os
import subprocess
import sys

sys.path.insert(0, '/opt/qantcore/htmlvid')
sys.path.insert(0, '/opt/qantcore/minibot')

import render  # noqa: E402

W, H, FPS = 1080, 1920, 30


def frames(html, out_dir, dur, port=9611):
    subprocess.run(['rm', '-rf', out_dir])
    os.makedirs(out_dir, exist_ok=True)
    render.W, render.H = W, H
    render.render_frames_cdp(html, out_dir, dur, FPS, port=port)
    return out_dir


def encode(frames_dir, out, dur):
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{frames_dir}/%05d.jpg',
        '-vf', f'scale={W}:{H}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
        '-pix_fmt', 'yuv420p', '-t', f'{dur:.2f}', out], check=True)
    return out


def mux(video, audio, out, dur):
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', video, '-i', audio,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.2f}', out], check=True)
    return out


def with_cover(video, cover_png, out, dur=1.6):
    """Приклеивает обложку первым кадром — видео всегда открывается титульником."""
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error',
        '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.2f}', '-i', cover_png,
        '-i', video,
        '-filter_complex',
        f'[0:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p[v0];'
        f'[1:v]setsar=1,fps={FPS},format=yuv420p[v1];[v0][v1]concat=n=2:v=1:a=0[v]',
        '-map', '[v]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
        '-pix_fmt', 'yuv420p', out], check=True)
    return out


def delay_audio(audio, out, ms):
    """Сдвигает звук вправо, чтобы он совпал с видео после обложки."""
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', audio,
        '-af', f'adelay={ms}|{ms}', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    return out
