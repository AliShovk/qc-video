"""Музыкальная подложка и микс."""
import subprocess


def build_bed(dur, path, level=0.16):
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i',
        f"aevalsrc=0.10*sin(2*PI*49*t)*(0.55+0.45*sin(2*PI*0.2*t))"
        f"+0.05*sin(2*PI*98*t)*exp(-7*mod(t\\,0.5))"
        f"+0.032*sin(2*PI*196*t)*exp(-10*mod(t\\,0.25)):s=44100:d={dur:.2f}",
        '-af', 'lowpass=f=2400', path], check=True)
    return path


def mix(voice, bed, out, dur, bed_level=0.16):
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', voice, '-i', bed,
        '-filter_complex',
        f'[0:a]volume=1.0[v];[1:a]volume={bed_level}[m];'
        '[v][m]amix=inputs=2:duration=longest:dropout_transition=0,apad,alimiter=limit=0.95[a]',
        '-map', '[a]', '-t', f'{dur:.2f}', out], check=True)
    return out


def master(mix_path, out, dur, target_lufs=-15.0, peak=-1.3, fade=0.9):
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', mix_path,
        '-af', f'loudnorm=I={target_lufs}:TP={peak}:LRA=10,afade=t=out:st={max(0, dur - fade):.2f}:d={fade}',
        '-c:a', 'aac', '-b:a', '192k', out], check=True)
    return out
