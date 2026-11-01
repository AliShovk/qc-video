"""Озвучка через Silero + тайминги + SRT.

Голосовой профиль зафиксирован: Silero v4_ru, спикер eugene, темп 0.94.
Это тот голос, которым собраны ролики Manus, LTX и Cherry Studio.
"""
import sys

sys.path.insert(0, '/opt/qantcore/minibot')

from minibot.voice import Narrator  # noqa: E402

# Единый профиль озвучки проекта. Меняется только осознанно: темп и паузы
# подобраны под вертикальные ролики 20–40 секунд.
VOICE_PROFILE = {
    'backend': 'silero',
    'speaker': 'eugene',
    'rate': 0.94,
    'lead': 0.3,
    'gap': 0.16,
}


def narrate(lines, out_wav, speaker=None, rate=None, lead=None, gap=None):
    speaker = speaker or VOICE_PROFILE['speaker']
    rate = VOICE_PROFILE['rate'] if rate is None else rate
    lead = VOICE_PROFILE['lead'] if lead is None else lead
    gap = VOICE_PROFILE['gap'] if gap is None else gap

    n = Narrator(speaker=speaker, lead=lead, gap=gap, length_scale=rate)
    cues = [n.add(t) for t in lines]
    n.write(out_wav)
    n.cleanup()
    return cues


def _ts(x: float) -> str:
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


def write_srt(cues, texts, path):
    rows = []
    for i, ((a, b), txt) in enumerate(zip(cues, texts), 1):
        rows.append(f'{i}\n{_ts(a)} --> {_ts(b)}\n{txt}\n')
    open(path, 'w', encoding='utf-8').write('\n'.join(rows))
    return path
