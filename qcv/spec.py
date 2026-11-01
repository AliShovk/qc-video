"""Загрузка и валидация спецификации ролика."""
import json
from dataclasses import dataclass, field
from typing import Any

SCENE_TYPES = {'hook', 'stats', 'cards', 'board', 'steps', 'verdict', 'final'}
# Короткое имя слоя — anim. board и wb оставлены для совместимости.
ALIASES = {'anim': 'board', 'wb': 'board'}


@dataclass
class Scene:
    kind: str
    say: str
    cap: str = ''
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Spec:
    slug: str
    title: str
    scenes: list[Scene]
    kicker: str = 'обзор'
    template: str = 'review-30'
    speaker: str = 'eugene'
    rate: float = 0.94
    accent: str = 'teal'
    palette: str = 'teal'
    out_name: str = ''

    @property
    def out(self) -> str:
        return self.out_name or f'{self.slug}.mp4'


def load(path: str) -> Spec:
    raw = json.load(open(path, encoding='utf-8'))
    scenes = []
    for item in raw.get('scenes', []):
        kind = ALIASES.get(item.get('type'), item.get('type'))
        if kind not in SCENE_TYPES:
            raise ValueError(f'неизвестный тип сцены: {kind}')
        say = (item.get('say') or '').strip()
        if not say:
            raise ValueError(f'сцена {kind} без текста речи')
        data = {k: v for k, v in item.items() if k not in {'type', 'say', 'cap'}}
        scenes.append(Scene(kind=kind, say=say, cap=item.get('cap', ''), data=data))

    if not scenes:
        raise ValueError('в спецификации нет сцен')
    if scenes[-1].kind != 'final':
        raise ValueError('последняя сцена должна быть final')
    if scenes[0].kind != 'hook':
        raise ValueError('первая сцена должна быть hook')

    return Spec(
        slug=raw['slug'],
        title=raw.get('title', raw['slug']),
        kicker=raw.get('kicker', 'обзор'),
        template=raw.get('template', 'review-30'),
        speaker=raw.get('voice', {}).get('speaker', 'eugene'),
        rate=float(raw.get('voice', {}).get('rate', 0.94)),
        accent=raw.get('accent', 'teal'),
        palette=raw.get('palette', 'teal'),
        out_name=raw.get('out', ''),
        scenes=scenes,
    )
