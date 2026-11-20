#!/usr/bin/env python3
"""Find one official repository image per repo and save a small local copy.

Prefer images embedded in the project's README. If that has none, inspect the
public repository tree for likely screenshots, demos, or project visuals. The
homepage downloads only local copies; visitors never request images from GitHub.
"""
import concurrent.futures
import hashlib
import html
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
DATA = SITE / 'data'
ASSETS = SITE / 'assets' / 'repo-media'
CATALOG_PATH = DATA / 'catalog.json'
MEDIA_PATH = DATA / 'repo-media.json'
USER_AGENT = 'PickRepo-static-media/1.0'
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
MAX_README_BYTES = 350_000
MAX_IMAGE_BYTES = 3 * 1024 * 1024
MAX_TOTAL_BYTES = 18 * 1024 * 1024
README_NAMES = ('README.md', 'README.MD', 'README.markdown', 'README.rst', 'README')
SCREEN_WORDS = ('screenshot', 'screen-shot', 'screen shot', 'screenshots', 'gui-', 'gui_', 'interface', 'dashboard', 'preview', 'demo', 'app-ui', 'app_ui', 'ui-shot', 'ui_shot', 'walkthrough', 'recording')
BAD_WORDS = ('badge', 'shield', 'logo', 'icon', 'avatar', 'favicon', 'social-preview', 'social_preview', 'thumb')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg')


def request_bytes(url, limit, accept='*/*'):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': accept})
    with urllib.request.urlopen(req, timeout=16) as response:
        length = response.headers.get('Content-Length')
        if length and int(length) > limit:
            return None, response.headers.get('Content-Type', ''), response.geturl()
        data = response.read(limit + 1)
        if len(data) > limit:
            return None, response.headers.get('Content-Type', ''), response.geturl()
        return data, response.headers.get('Content-Type', ''), response.geturl()


def markdown_images(text):
    found = []
    seen = set()

    def add(alt, src):
        src = html.unescape((src or '').strip().strip('<>'))
        if src and src not in seen:
            seen.add(src)
            found.append(((alt or '').strip(), src))

    # Inline Markdown images (including angle-bracket URLs).
    pattern = re.compile(r'!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)', re.I)
    for match in pattern.finditer(text):
        add(match.group(1), match.group(2) or match.group(3))

    # Reference-style Markdown images: ![alt][key] followed by [key]: URL.
    definitions = {}
    for match in re.finditer(r'(?m)^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))', text):
        definitions[match.group(1).strip().lower()] = match.group(2) or match.group(3)
    for match in re.finditer(r'!\[([^\]]*)\]\s*\[([^\]]*)\]', text):
        label = (match.group(2) or match.group(1)).strip().lower()
        if label in definitions:
            add(match.group(1), definitions[label])

    # HTML images and responsive-picture source tags embedded in a README.
    for match in re.finditer(r'<(?:img|source)\b[^>]*?>', text, re.I):
        tag = match.group(0)
        alt_match = re.search(r'\balt=["\']([^"\']*)["\']', tag, re.I)
        src_match = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.I)
        if not src_match:
            srcset = re.search(r'\bsrcset=["\']([^"\']+)["\']', tag, re.I)
            if srcset:
                src_match = re.match(r'\s*(\S+)', srcset.group(1))
        if src_match:
            add(alt_match.group(1) if alt_match else '', src_match.group(1))

    # reStructuredText README image directives.
    for match in re.finditer(r'(?m)^\s*\.\.\s+(?:image|figure)::\s+(\S+)', text, re.I):
        add('', match.group(1))
    return found


def quote_url(url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=-._~%")
    query = urllib.parse.quote(parts.query, safe="=&%:@!$'()*+,;/?-._~")
    fragment = urllib.parse.quote(parts.fragment, safe="=&%:@!$'()*+,;/?-._~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


def eligible_host(url):
    host = (urllib.parse.urlparse(url).hostname or '').lower()
    return host == 'raw.githubusercontent.com' or host == 'github.com' or host.endswith('.githubusercontent.com')


def candidate_score(alt, url):
    parsed = urllib.parse.urlparse(url)
    text = (alt + ' ' + urllib.parse.unquote(parsed.path)).lower().replace('-', ' ').replace('_', ' ')
    if any(word.replace('-', ' ').replace('_', ' ') in text for word in BAD_WORDS):
        return 0
    host = (parsed.hostname or '').lower()
    if 'shields.io' in host or 'badge' in host:
        return 0
    if not eligible_host(url):
        return 0
    # Any sizeable non-badge image embedded in the official README is an eligible
    # project visual; explicit UI/screenshot terms rank it ahead of generic images.
    score = 1
    for word in SCREEN_WORDS:
        if word.replace('-', ' ').replace('_', ' ') in text:
            score += 3 if word in ('screenshot', 'screen-shot', 'screen shot', 'screenshots', 'interface', 'dashboard', 'preview') else 2
    return score


def readme_candidate(full_name):
    base = f'https://raw.githubusercontent.com/{full_name}/HEAD/'
    for filename in README_NAMES:
        url = urllib.parse.urljoin(base, filename)
        try:
            body, _, final_url = request_bytes(url, MAX_README_BYTES, 'text/plain,*/*')
            if body is None:
                continue
            text = body.decode('utf-8', 'replace')
            candidates = []
            for order, (alt, src) in enumerate(markdown_images(text)):
                absolute = quote_url(urllib.parse.urljoin(final_url, src))
                score = candidate_score(alt, absolute)
                if score:
                    candidates.append((score, -order, alt or 'Repository UI screenshot', absolute, final_url))
            if candidates:
                candidates.sort(reverse=True)
                score, _, alt, image_url, _readme_url = candidates[0]
                return full_name, alt, image_url, f'https://github.com/{full_name}#readme', score
            # A README with no image is enough; don't keep probing other names.
            return full_name, None, None, final_url, 0
        except Exception:
            continue
    return full_name, None, None, f'https://github.com/{full_name}#readme', 0


def github_api_json(url):
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = 'Bearer ' + GITHUB_TOKEN
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def repository_tree_candidate(full_name):
    """Find a likely visual in the repo tree when the README has no image."""
    encoded_name = urllib.parse.quote(full_name, safe='/')
    url = f'https://api.github.com/repos/{encoded_name}/git/trees/HEAD?recursive=1'
    tree = github_api_json(url)
    entries = tree.get('tree', []) if isinstance(tree, dict) else []
    directory_hints = {'doc', 'docs', 'image', 'images', 'media', 'screenshot', 'screenshots', 'screen', 'screens', 'asset', 'assets', 'public', 'site', 'demo', 'demos'}
    candidates = []
    for order, entry in enumerate(entries):
        path = str(entry.get('path') or '')
        if entry.get('type') != 'blob' or Path(path).suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        size = entry.get('size')
        if size is not None and (size < 12_000 or size > MAX_IMAGE_BYTES):
            continue
        parts = path.lower().split('/')
        hinted_name = any(word.replace('-', ' ').replace('_', ' ') in path.lower().replace('-', ' ').replace('_', ' ') for word in SCREEN_WORDS)
        in_visual_dir = bool(set(parts[:-1]) & directory_hints)
        if not (hinted_name or in_visual_dir):
            continue
        quoted_path = urllib.parse.quote(path, safe='/-._~')
        image_url = f'https://raw.githubusercontent.com/{full_name}/HEAD/{quoted_path}'
        score = candidate_score('', image_url)
        if not score:
            continue
        score += 4 if hinted_name else 2
        source_url = f'https://github.com/{full_name}/blob/HEAD/{quoted_path}'
        alt = re.sub(r'[-_]+', ' ', Path(path).stem).strip() or 'Repository image'
        candidates.append((score, -order, alt, image_url, source_url))
    if not candidates:
        return full_name, None, None, f'https://github.com/{full_name}', 0
    candidates.sort(reverse=True)
    score, _, alt, image_url, source_url = candidates[0]
    return full_name, alt, image_url, source_url, score


def repository_candidate(full_name):
    readme = readme_candidate(full_name)
    if readme[2]:
        return readme
    try:
        return repository_tree_candidate(full_name)
    except Exception:
        return full_name, None, None, f'https://github.com/{full_name}', 0


def image_type(data, content_type, final_url):
    content_type = (content_type or '').split(';', 1)[0].strip().lower()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return '.webp'
    if data.startswith((b'GIF87a', b'GIF89a')):
        return '.gif'
    if re.search(rb'<svg(?:\s|>)', data[:4096].lstrip(b'\xef\xbb\xbf \t\r\n'), re.I):
        return '.svg'
    suffix = Path(urllib.parse.urlparse(final_url).path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return '.jpg' if suffix == '.jpeg' else suffix
    guessed = mimetypes.guess_extension(content_type) if content_type else None
    return guessed if guessed in IMAGE_EXTENSIONS else None


def filename_for(full_name, suffix):
    label = re.sub(r'[^a-z0-9]+', '-', full_name.lower()).strip('-')[:60] or 'repo'
    digest = hashlib.sha256(full_name.lower().encode()).hexdigest()[:8]
    return f'{label}-{digest}{suffix}'


def main():
    catalog = json.loads(CATALOG_PATH.read_text(encoding='utf-8'))
    all_names = sorted({name.lower() for group in catalog.get('views', {}).values() for name in group})
    requested = {name.lower() for name in sys.argv[1:]}
    names = [name for name in all_names if not requested or name in requested]
    if requested:
        unknown = requested - set(all_names)
        if unknown:
            raise SystemExit('Unknown repositories: ' + ', '.join(sorted(unknown)))
    print(f'Checking official repository images for {len(names)} repositories…')
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(repository_candidate, name) for name in names]
        for future in concurrent.futures.as_completed(futures):
            try:
                record = future.result()
                if record[2]:
                    found.append(record)
            except Exception as exc:
                print('Image lookup skipped:', type(exc).__name__, file=sys.stderr)

    # Preserve previously cached images if a scheduled run cannot reach a repository.
    try:
        previous = json.loads(MEDIA_PATH.read_text(encoding='utf-8')).get('images', {})
    except (OSError, ValueError, AttributeError):
        previous = {}
    active_names = set(all_names)
    ASSETS.mkdir(parents=True, exist_ok=True)
    media = {
        name: item for name, item in previous.items()
        if name in active_names
        and isinstance(item, dict)
        and str(item.get('path', '')).startswith('/assets/repo-media/')
        and (SITE / str(item.get('path', '')).lstrip('/')).is_file()
    }
    # Download in a deterministic order and respect a total size ceiling.
    found.sort(key=lambda row: (-row[4], row[0]))
    total_bytes = sum((SITE / item['path'].lstrip('/')).stat().st_size for item in media.values())
    for full_name, alt, image_url, source_url, score in found:
        old = media.get(full_name.lower())
        if old and old.get('imageSource') == image_url:
            continue
        if total_bytes >= MAX_TOTAL_BYTES:
            continue
        try:
            data, content_type, final_url = request_bytes(image_url, MAX_IMAGE_BYTES, 'image/png,image/jpeg,image/webp,image/gif,image/svg+xml,*/*')
            if not data:
                continue
            suffix = image_type(data, content_type, final_url)
            if not suffix:
                continue
            # Skip files that look like a tiny logo/badge, not a screenshot.
            if len(data) < 12_000:
                continue
            if total_bytes + len(data) > MAX_TOTAL_BYTES:
                continue
            filename = filename_for(full_name, suffix)
            (ASSETS / filename).write_bytes(data)
            media[full_name.lower()] = {
                'path': '/assets/repo-media/' + filename,
                'alt': alt,
                'source': source_url,
                'imageSource': final_url
            }
            total_bytes += len(data)
            print(f'OK {full_name}: {len(data):,} bytes')
        except Exception as exc:
            print(f'Skipped {full_name}: {type(exc).__name__}', file=sys.stderr)

    MEDIA_PATH.write_text(json.dumps({'images': media}, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    used_files = {Path(item['path']).name for item in media.values()}
    for old_file in ASSETS.iterdir():
        if old_file.is_file() and old_file.name not in used_files:
            old_file.unlink()
    print(f'Saved {len(media)} official repository images ({total_bytes:,} bytes) to {ASSETS.relative_to(ROOT)}.')
    print('All other cards use the local decorative illustration fallback.')


if __name__ == '__main__':
    main()
