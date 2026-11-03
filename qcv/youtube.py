"""Публикация на YouTube: OAuth один раз, дальше загрузка по refresh-token.

Ключи не коммитятся: клиент и токен лежат в /root/qc-video/ с правами 600.
"""
from __future__ import annotations

import json
import os
import time

import requests

CLIENT = '/root/qc-video/youtube-client.json'
TOKEN = '/root/qc-video/youtube-token.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube.readonly']
REDIRECT = 'http://127.0.0.1:8080/'
AUTH = 'https://accounts.google.com/o/oauth2/v2/auth'
TOK = 'https://oauth2.googleapis.com/token'
API = 'https://www.googleapis.com/youtube/v3'


def _client():
    if not os.path.exists(CLIENT):
        raise SystemExit(f'нет файла клиента {CLIENT}')
    return json.load(open(CLIENT))


def auth_url():
    c = _client()
    from urllib.parse import urlencode
    q = {
        'client_id': c['client_id'],
        'redirect_uri': REDIRECT,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true',
    }
    return f'{AUTH}?{urlencode(q)}'


def exchange(code: str):
    c = _client()
    r = requests.post(TOK, data={
        'client_id': c['client_id'], 'client_secret': c['client_secret'],
        'code': code, 'grant_type': 'authorization_code', 'redirect_uri': REDIRECT}, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f'обмен кода не удался: {r.status_code} {r.text[:300]}')
    data = r.json()
    data['obtained_at'] = int(time.time())
    os.makedirs(os.path.dirname(TOKEN), exist_ok=True)
    with open(TOKEN, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(TOKEN, 0o600)
    return data


def access_token():
    if not os.path.exists(TOKEN):
        raise SystemExit('нет токена: сначала qc-video yt-auth')
    t = json.load(open(TOKEN))
    if t.get('expires_in') and t.get('obtained_at') and \
            time.time() < t['obtained_at'] + int(t['expires_in']) - 60:
        return t['access_token']
    c = _client()
    r = requests.post(TOK, data={
        'client_id': c['client_id'], 'client_secret': c['client_secret'],
        'refresh_token': t['refresh_token'], 'grant_type': 'refresh_token'}, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f'refresh не удался: {r.status_code} {r.text[:300]}')
    d = r.json()
    t['access_token'] = d['access_token']
    t['expires_in'] = d['expires_in']
    t['obtained_at'] = int(time.time())
    with open(TOKEN, 'w', encoding='utf-8') as f:
        json.dump(t, f, ensure_ascii=False, indent=2)
    os.chmod(TOKEN, 0o600)
    return t['access_token']


def channel():
    tok = access_token()
    r = requests.get(f'{API}/channels', params={'part': 'snippet,statistics', 'mine': 'true'},
                     headers={'Authorization': f'Bearer {tok}'}, timeout=30)
    r.raise_for_status()
    items = r.json().get('items', [])
    return items[0] if items else {}


def upload(video, title, description='', tags=None, privacy='unlisted',
           category='28', cover=None, playlist=None):
    """Загружает ролик (resumable) и, если есть, ставит обложку."""
    tok = access_token()
    size = os.path.getsize(video)
    meta = {
        'snippet': {
            'title': title[:100],
            'description': description[:4900],
            'tags': (tags or [])[:15],
            'categoryId': category,
        },
        'status': {'privacyStatus': privacy, 'selfDeclaredMadeForKids': False},
    }
    init = requests.post(
        f'https://www.googleapis.com/upload/youtube/v3/videos',
        params={'uploadType': 'resumable', 'part': 'snippet,status'},
        headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(size), 'X-Upload-Content-Type': 'video/mp4'},
        data=json.dumps(meta, ensure_ascii=False).encode('utf-8'), timeout=60)
    if init.status_code not in (200, 201):
        raise SystemExit(f'инициализация загрузки: {init.status_code} {init.text[:300]}')
    url = init.headers['Location']

    with open(video, 'rb') as f:
        up = requests.put(url, data=f, headers={'Content-Type': 'video/mp4'}, timeout=1800)
    if up.status_code not in (200, 201):
        raise SystemExit(f'загрузка: {up.status_code} {up.text[:300]}')
    vid = up.json()['id']

    if cover and os.path.exists(cover):
        with open(cover, 'rb') as f:
            requests.post('https://www.googleapis.com/upload/youtube/v3/thumbnails/set',
                          params={'videoId': vid},
                          headers={'Authorization': f'Bearer {tok}',
                                   'Content-Type': 'image/png'},
                          data=f, timeout=120)

    if playlist:
        requests.post(f'{API}/playlistItems', params={'part': 'snippet'},
                      headers={'Authorization': f'Bearer {tok}',
                               'Content-Type': 'application/json'},
                      json={'snippet': {'playlistId': playlist,
                                        'resourceId': {'kind': 'youtube#video', 'videoId': vid}}},
                      timeout=60)
    return vid
