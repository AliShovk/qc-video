"""CLI: qc-video make spec.json"""
import argparse
import json
import os
import sys

from . import assemble, audio, publish as publish_mod, qa, spec as spec_mod, stage, voice

WORK = '/root/qc-video/builds'


def cmd_make(args):
    sp = spec_mod.load(args.spec)
    work = os.path.join(WORK, sp.slug)
    os.makedirs(work, exist_ok=True)
    print(f'[1/7] спецификация: {sp.slug}, сцен {len(sp.scenes)}')

    lines = [s.say for s in sp.scenes]
    wav = os.path.join(work, 'voice.wav')
    cues = voice.narrate(lines, wav, speaker=sp.speaker, rate=sp.rate)
    srt = voice.write_srt(cues, lines, os.path.join(work, f'{sp.slug}.srt'))
    print(f'[2/7] озвучка: {cues[-1][1]:.1f} с речи')

    html = os.path.join(work, 'scene.html')
    _, total = stage.build(sp, cues, html)
    print(f'[3/7] сцена: {total:.1f} с, кадров {int(total * 30)}')

    frames_dir = os.path.join(work, 'frames')
    assemble.frames(html, frames_dir, total, port=args.port)
    print('[4/7] кадры отрендерены')

    video = assemble.encode(frames_dir, os.path.join(work, 'video.mp4'), total)
    bed = audio.build_bed(total, os.path.join(work, 'bed.wav'))
    mix = audio.mix(wav, bed, os.path.join(work, 'mix.wav'), total)
    mux = assemble.mux(video, mix, os.path.join(work, f'{sp.slug}_raw.mp4'), total)
    final = os.path.join(work, sp.out)
    audio.master(mix, os.path.join(work, 'master.m4a'), total)
    assemble.mux(video, os.path.join(work, 'master.m4a'), final, total)
    print(f'[5/7] сборка: {final}')

    report = qa.check(final, expect=total)
    print(f'[6/7] QA: {"ок" if report["ok"] else report["problems"]}')
    print(json.dumps(report, ensure_ascii=False))

    if args.no_publish:
        print('[7/7] публикация пропущена')
        return 0 if report['ok'] or args.force else 1

    urls = publish_mod.publish(final, srt, name=sp.out)
    print(f'[7/7] опубликовано: {urls["mp4"]}')
    if 'srt' in urls:
        print(f'      субтитры: {urls["srt"]}')
    return 0 if report['ok'] else 1


def main(argv=None):
    p = argparse.ArgumentParser(prog='qc-video')
    sub = p.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('make', help='собрать ролик по спецификации')
    m.add_argument('spec')
    m.add_argument('--no-publish', action='store_true')
    m.add_argument('--force', action='store_true', help='не падать на предупреждениях QA')
    m.add_argument('--port', type=int, default=9611)
    m.set_defaults(func=cmd_make)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
