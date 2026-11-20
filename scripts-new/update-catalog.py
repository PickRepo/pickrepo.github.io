#!/usr/bin/env python3
"""Refresh public GitHub metadata for the static site. Python standard library only."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'site' / 'data'
HEADERS = {'User-Agent': 'PickRepo-static-catalog', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
if os.environ.get('GITHUB_TOKEN'):
    HEADERS['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']

def get(path):
    req = urllib.request.Request('https://api.github.com/' + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)

def clean(repo):
    return {k: repo.get(k) for k in ('full_name', 'description', 'language', 'stargazers_count', 'forks_count', 'topics', 'created_at', 'pushed_at', 'archived')} | {'license': (repo.get('license') or {}).get('spdx_id')}

def main():
    now = dt.datetime.now(dt.timezone.utc)
    dates = {'trending': (now - dt.timedelta(days=7)).date().isoformat(), 'early': (now - dt.timedelta(days=30)).date().isoformat()}
    queries = {'trending': 'is:public fork:false archived:false created:>=' + dates['trending'], 'popular': 'is:public fork:false archived:false stars:>=1000', 'early': 'is:public fork:false archived:false created:>=' + dates['early'] + ' stars:10..1000'}
    repos, views, incomplete = {}, {}, []
    for name, query in queries.items():
        result = get('search/repositories?' + urllib.parse.urlencode({'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': 50}))
        if not isinstance(result.get('items'), list):
            raise RuntimeError('Incomplete GitHub response; keeping previous catalog.')
        if result.get('incomplete_results'):
            incomplete.append(name)
        views[name] = []
        for repo in result['items']:
            item = clean(repo)
            repos[item['full_name'].lower()] = item
            views[name].append(item['full_name'].lower())
    guides = json.loads((DATA / 'guides.json').read_text())['projects']
    views['guides'] = list(guides)
    for name in guides:
        if name not in repos:
            repos[name] = clean(get('repos/' + name))
    output = {'updatedAt': now.isoformat(), 'source': 'GitHub REST API', 'views': views, 'incompleteViews': incomplete, 'repos': repos}
    tmp = DATA / 'catalog.next.json'
    tmp.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')) + '\n')
    tmp.replace(DATA / 'catalog.json')
    print('PickRepo: updated', len(repos), 'public repositories.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Never emit request headers or credentials.
        print('Catalog refresh failed; existing snapshot is unchanged. ' + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
