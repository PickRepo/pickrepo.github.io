#!/usr/bin/env python3
"""Generate the static PickRepo site for GitHub Pages from the prepared catalog."""
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
DATA = SITE / 'data'
CATALOG = json.loads((DATA / 'catalog.json').read_text())
GUIDES = json.loads((DATA / 'guides.json').read_text())['detailed']
MEDIA_FILE = DATA / 'repo-media.json'
MEDIA = json.loads(MEDIA_FILE.read_text(encoding='utf-8')).get('images', {}) if MEDIA_FILE.exists() else {}
REPOS = CATALOG['repos']
VIEWS = CATALOG['views']

# Organization Pages root URL.
BASE_URL = 'https://pickrepo.github.io'


CSS = ''':root{--orange:#ff6600;--orange-dark:#e65c00;--bg:#f6f6ef;--surface:#fff;--text:#000;--muted:#65655e;--border:#e5e5e5;--sidebar:#eef3f8;--border-side:#d5dfe8}
*{box-sizing:border-box}html{line-height:1.5}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:var(--text);background:var(--bg)}
a{color:inherit;text-decoration:none}a:hover{opacity:.85}button{font:inherit;cursor:pointer}
.site-header{position:sticky;top:0;z-index:40;background:var(--orange);color:#000;padding:16px 24px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.site-header .brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;white-space:nowrap}
.site-header .brand img{width:34px;height:34px;display:block}
.nav{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.nav a{font-weight:600;font-size:15px;color:#000;padding:6px 10px}
.atlas-layout{display:grid;grid-template-columns:230px minmax(0,1fr);gap:24px;max-width:min(1266px,calc(100% - 64px));margin:28px auto 40px;align-items:start}
.sidebar{position:sticky;top:24px;background:var(--sidebar);border:1px solid var(--border-side);border-radius:7px;overflow:hidden;max-height:calc(100dvh - 48px);overflow-y:auto}
.sidebar-heading{padding:18px 18px 14px;border-bottom:1px solid var(--border-side);background:#e7edf2}
.sidebar-eyebrow{display:block;font-size:10px;letter-spacing:1.4px;color:#475664;text-transform:uppercase;margin-bottom:6px}
.sidebar-heading h2{margin:0;font-size:17px;letter-spacing:-.4px}
.sidebar-links{padding:12px 16px 6px;display:grid;gap:4px}
.sidebar-links a{display:block;padding:8px 0;font-size:13px;color:var(--text);border-bottom:1px solid rgba(0,0,0,.06)}
.sidebar-links a.current{border-left:3px solid var(--orange);padding-left:13px}
main{min-width:0}
.page-heading{padding:0 0 24px;border-bottom:1px solid var(--border);margin-bottom:0}
.page-heading h1{font-size:28px;margin:0 0 6px;font-weight:700;letter-spacing:-.5px}
.page-heading p{margin:0;color:var(--muted);font-size:15px}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:18px 0 4px}
.controls label{font-size:13px;color:var(--muted)}
.controls .gh-select{padding:6px 10px;border:1px solid var(--border);background:#fff;border-radius:6px;font-size:13px;min-width:150px}
.repo-list{display:flex;flex-direction:column;gap:12px}
.row{display:flex;gap:14px;align-items:flex-start;padding:14px;border:1px solid var(--border);border-radius:7px;background:#fff}
.pos{font-size:13px;color:var(--muted);min-width:24px;text-align:right;white-space:nowrap;padding-top:2px}
.main{flex:1;min-width:0}
.main h2.title{margin:0 0 4px;font-size:18px;font-weight:700;line-height:1.35}
.main h2.title a{color:var(--text)}
.main h2.title strong{font-weight:800}
.desc{margin:0 0 8px;font-size:14px;color:var(--muted);line-height:1.45}
.meta{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px}
.meta span{display:flex;align-items:center;gap:4px}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.actions .btn{padding:6px 12px;border:1px solid var(--border);border-radius:6px;background:#fff;color:var(--text);font-size:13px;font-weight:600}
.actions .guide-btn{border-color:var(--orange-dark);color:var(--orange-dark)}
.right{min-width:110px;text-align:right}
.star{font-size:14px;font-weight:700;color:#000}
.star-icon{color:#f0bd24}
.empty{text-align:center;padding:40px 0;color:var(--muted)}
.sponsor{margin-top:18px;border:1px solid var(--border-side);border-radius:8px;background:#fff;padding:14px 16px;display:flex;gap:12px;align-items:flex-start}
.sponsor strong{display:block;font-size:13px;color:var(--text)}
.sponsor p{margin:2px 0 10px;font-size:12px;color:var(--muted);line-height:1.5}
.sponsor .btn{margin-left:auto;display:inline-flex;align-items:center;padding:6px 12px;border:1px solid var(--border);border-radius:6px;background:#fff;font-size:13px;font-weight:600;white-space:nowrap}
footer{border-top:1px solid var(--border);padding:30px 24px;font-size:12px;color:var(--muted);display:flex;gap:16px;flex-wrap:wrap;justify-content:center}
footer .brand{font-weight:700;color:var(--text)}
@media(max-width:900px){.atlas-layout{grid-template-columns:1fr;gap:16px;margin:16px auto}.sidebar{max-height:none}main{order:2}.sidebar{order:1}}
.view-language-row{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.view-switcher{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 8px}
.view-switcher button{border:1px solid var(--border-side);border-radius:7px;background:#fff;padding:8px 13px;font-size:13px;font-weight:700;color:var(--text)}
.locale-switch{display:flex;align-items:center;gap:4px;margin:14px 0 8px;padding:3px;border:1px solid var(--border-side);border-radius:8px;background:#eef3f8}
.locale-switch span{padding:0 5px;color:#56616d;font-size:11px;font-weight:700}
.locale-switch button{border:0;border-radius:5px;background:transparent;padding:5px 8px;font-size:11px;font-weight:800;color:#4b5563}
.locale-switch button.current{background:#fff;color:#000;box-shadow:0 1px 2px rgba(0,0,0,.12)}
.view-switcher button.current{border-color:var(--orange);background:#fff4e8;box-shadow:inset 0 0 0 1px var(--orange)}
.discovery-tools{margin:12px 0 16px;padding:14px;background:#eef3f8;border:1px solid var(--border-side);border-radius:8px}
.search-filter-grid{display:grid;grid-template-columns:minmax(200px,2fr) repeat(3,minmax(130px,1fr));gap:10px;align-items:end}
.form-field{display:grid;gap:5px;min-width:0}
.form-field label{font-size:12px;font-weight:700;color:#334155}
.form-input,.form-select{width:100%;min-height:38px;padding:7px 10px;border:1px solid #cbd5df;border-radius:6px;background:#fff;color:var(--text);font:inherit;font-size:13px}
.form-input:focus,.form-select:focus,.view-switcher button:focus-visible,.score-panel summary:focus-visible{outline:2px solid #1463a5;outline-offset:2px}
.result-count{margin:10px 0 0;color:#475569;font-size:12px;font-weight:700}
.score-panel{margin-top:12px;border-top:1px solid #d5dfe8;padding-top:10px}
.score-panel summary{cursor:pointer;font-size:13px;font-weight:700;color:#1f2937}
.score-panel-intro{margin:7px 0 10px;font-size:12px;color:#475569;line-height:1.5}
.weight-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 18px}
.weight-control{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;align-items:center}
.weight-control label{font-size:12px;font-weight:600;color:#263445}
.weight-control output{font-size:12px;font-weight:700;color:var(--orange-dark)}
.weight-control input{grid-column:1 / -1;width:100%;accent-color:var(--orange)}
.weight-note{font-size:11px;color:#56616d;margin:8px 0 0}
.reset-weights{margin-top:8px;border:1px solid #cbd5df;border-radius:6px;background:#fff;padding:6px 10px;font-size:12px;font-weight:700}
.repo-list{display:flex;flex-direction:column;gap:12px}
.project-card{padding:16px 18px;border:1px solid var(--border);border-radius:8px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.025)}
.project-card-top{display:grid;grid-template-columns:48px minmax(0,1fr) auto;gap:12px;align-items:start}
.project-card-content{display:grid;grid-template-columns:180px minmax(0,1fr);gap:16px;align-items:start;margin-top:10px}
.project-visual{width:180px;margin:0}
.project-visual>img,.project-visual-art{display:block;width:100%;height:112px;border:1px solid #e5e7eb;border-radius:8px;object-fit:cover;background:#f4f6f8}
.project-visual figcaption{margin-top:4px;text-align:center;color:#647080;font-size:10px;line-height:1.3}
.project-visual figcaption a{color:#8a3c00;font-weight:700}
.project-visual-art{position:relative;overflow:hidden;display:flex;flex-direction:column;justify-content:center;padding:10px;background:linear-gradient(135deg,hsl(var(--visual-hue) 75% 90%),#fff5e9)}
.art-orbit{position:absolute;width:96px;height:96px;border-radius:50%;right:-22px;top:-28px;background:hsl(var(--visual-hue) 70% 70% / .35)}
.art-window{position:relative;z-index:1;width:100%;height:65px;padding:6px 8px;border:1px solid rgba(30,41,59,.12);border-radius:7px;background:rgba(255,255,255,.9);box-shadow:0 3px 10px rgba(20,30,40,.08)}
.art-window-bar{display:flex;gap:3px;height:7px;border-bottom:1px solid #e6e8ec}
.art-window-bar i{width:4px;height:4px;border-radius:50%;background:hsl(var(--visual-hue) 65% 52%)}
.art-window-content{display:flex;align-items:center;gap:9px;padding-top:6px}
.art-glyph{display:grid;place-items:center;width:34px;height:34px;border-radius:8px;background:hsl(var(--visual-hue) 60% 52%);color:#fff;font-size:12px;font-weight:800}
.art-lines{display:grid;gap:4px;flex:1}.art-lines i{height:4px;border-radius:5px;background:#dfe4e9}.art-lines i:nth-child(2){width:78%}.art-lines i:nth-child(3){width:56%}
.art-caption{position:relative;z-index:1;display:flex;justify-content:space-between;gap:5px;margin-top:6px;color:#394250;font-size:9px;line-height:1.2}
.art-caption strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.art-caption span{flex-shrink:0}
.project-summary{min-width:0}
.source-description-label{display:block;color:#687386;font-size:10px;font-weight:700;letter-spacing:.03em;text-transform:uppercase}
.localized-explainer{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-bottom:13px}
.localized-explainer section{padding:9px 10px;border:1px solid #e6e8ec;border-radius:7px;background:#fbfbfa}
.localized-explainer h3{margin:0 0 4px;font-size:12px;color:#8a3c00}
.localized-explainer p{margin:0;font-size:12px;line-height:1.5;color:#444}
.rank-number{display:grid;place-items:center;width:48px;height:48px;padding:0;border-radius:6px;background:var(--orange);color:#000;font-size:26px;line-height:1;font-weight:900;box-shadow:0 2px 5px rgba(0,0,0,.16)}
.project-title{margin:0;font-size:18px;line-height:1.35;overflow-wrap:anywhere}
.project-title a{color:var(--text)}
.project-title strong{font-weight:800}
.project-score{min-width:116px;text-align:right;border:1px solid #f4d39a;border-radius:8px;background:#fff9ed;padding:6px 9px}
.project-score span{display:block;color:#76521c;font-size:10px;line-height:1.25}
.project-score strong{display:block;color:#111;font-size:22px;line-height:1.2}
.project-score small{font-size:11px;color:#5d5d5d;margin-left:2px}
.project-description{margin:10px 0 9px;color:#3f454c;font-size:14px;line-height:1.55;overflow-wrap:anywhere}
.topic-list{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 9px}
.topic-chip{display:inline-block;padding:3px 8px;border-radius:999px;background:#eef3f8;color:#405164;font-size:11px;line-height:1.4}
.project-meta{display:flex;gap:8px 15px;flex-wrap:wrap;align-items:center;color:#5e6670;font-size:12px}
.project-meta .star{color:#111;font-weight:800}.project-meta .star-icon{color:#f0bd24}
.project-details{margin-top:12px;border-top:1px solid #ececec;padding-top:8px}
.project-details summary{cursor:pointer;color:#8a3c00;font-size:12px;font-weight:700}
.details-body{padding-top:10px}
.detail-lead{margin:0 0 10px;color:#444;font-size:13px;line-height:1.5}
.detail-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0 14px}
.detail-facts>div{padding:8px 9px;border:1px solid #e7e9ed;border-radius:6px;background:#fafafa;min-width:0}
.detail-facts strong,.detail-facts span{display:block;overflow-wrap:anywhere}
.detail-facts strong{font-size:10px;color:#59616d;text-transform:uppercase;letter-spacing:.04em}
.detail-facts span{margin-top:3px;font-size:12px;color:#222}
.details-body h3{margin:12px 0 7px;font-size:13px}
.inline-guide-link{display:inline-block;margin:4px 0 0;color:var(--orange-dark);font-size:11px;font-weight:700}
.signal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 18px}
.signal-heading{display:flex;justify-content:space-between;gap:10px;font-size:11px;color:#444}
.signal-heading span:last-child{font-weight:700;white-space:nowrap}
.signal-track{height:6px;margin-top:3px;background:#e8edf2;border-radius:99px;overflow:hidden}
.signal-track span{display:block;height:100%;border-radius:99px;background:var(--orange)}
.method-note{margin:12px 0 7px;padding:9px 10px;border-left:3px solid #f0bd24;background:#fffaf0;color:#53504a;font-size:11px;line-height:1.5}
.detail-actions,.project-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.project-actions .btn,.detail-actions a{display:inline-flex;align-items:center;padding:6px 10px;border:1px solid var(--border);border-radius:6px;background:#fff;font-size:12px;font-weight:700}
.project-actions .guide-btn,.detail-actions .guide-btn{border-color:var(--orange-dark);color:var(--orange-dark)}
@media(max-width:760px){.search-filter-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.search-filter-grid .search-field{grid-column:1 / -1}.project-card-content{grid-template-columns:140px minmax(0,1fr);gap:11px}.project-visual{width:140px}.localized-explainer{grid-template-columns:1fr}}
@media(max-width:560px){.atlas-layout{max-width:calc(100% - 24px)}.discovery-tools{padding:11px}.search-filter-grid{grid-template-columns:1fr}.search-filter-grid .search-field{grid-column:auto}.weight-grid,.signal-grid{grid-template-columns:1fr}.project-card{padding:13px}.project-card-top{grid-template-columns:48px minmax(0,1fr);gap:8px}.project-score{grid-column:2;justify-self:start;text-align:left;min-width:100px}.project-score strong{display:inline-block;margin-right:4px}.project-score span{display:inline-block;margin-right:5px}.project-title{font-size:16px}.project-card-content{grid-template-columns:1fr}.project-visual{width:min(100%,280px)}.project-visual>img,.project-visual-art{height:142px}.detail-facts{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''

# Editorial dark, cream and gold theme inspired by the supplied Ramify case-study reference.
CSS += r"""
:root{
  --orange:#EECB96;--orange-dark:#B39264;--bg:#1A1517;--surface:#F7F3EA;
  --text:#F7F3EA;--muted:#AE9877;--border:#E5D8C3;--sidebar:#211B1C;
  --border-side:rgba(238,203,150,.22);--ink:#1A1517;--gold:#EECB96;
  --cream:#F7DEBB;--dark-panel:#211B1C;--dark-line:rgba(238,203,150,.18)
}
html{scroll-behavior:smooth;scroll-padding-top:86px}
body{background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
a{transition:color .18s ease,background-color .18s ease,transform .18s ease,opacity .18s ease}
.site-header{justify-content:space-between;padding:13px clamp(18px,5vw,76px);background:rgba(26,21,23,.96);color:var(--cream);border-bottom:1px solid var(--dark-line);box-shadow:0 10px 28px rgba(0,0,0,.16);backdrop-filter:blur(14px)}
.site-header .brand{font-size:17px;letter-spacing:.13em;text-transform:uppercase}
.site-header .brand img{width:31px;height:31px}
.nav{margin-left:auto;gap:13px}
.nav a{padding:9px 13px;color:#F4EBDD;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}
.nav a:hover{color:var(--gold)}
.nav a:last-child{border:1px solid rgba(238,203,150,.55);border-radius:2px;color:var(--cream)}
.nav a:last-child:hover{background:var(--gold);color:var(--ink);opacity:1}
.atlas-layout{max-width:1320px;margin:0 auto 58px;padding:28px 32px 0;grid-template-columns:215px minmax(0,1fr);gap:26px}
.sidebar{background:#201A1B;border-color:var(--dark-line);border-radius:3px;box-shadow:0 16px 36px rgba(0,0,0,.16)}
.sidebar-heading{background:#251F20;border-bottom-color:var(--dark-line)}
.sidebar-eyebrow{color:var(--gold)}
.sidebar-heading h2{color:#F7F3EA}
.sidebar-links a{color:#D3C6B2;border-bottom-color:rgba(238,203,150,.12)}
.sidebar-links a:hover,.sidebar-links a.current{color:var(--gold);border-left-color:var(--gold)}
.page-heading h1{color:#F8F3EA}
.page-heading p{color:#C6B9A4}
.home-page .atlas-layout{display:block;width:min(1240px,calc(100% - 64px));max-width:none;margin:0 auto 64px;padding:0}
.home-page .sidebar{display:none}
.home-page main{min-width:0}
.home-page .page-heading{position:relative;isolation:isolate;display:block;overflow:hidden;min-height:390px;margin:30px 0 24px;padding:52px clamp(26px,6vw,80px) 34px;border:1px solid rgba(238,203,150,.2);border-radius:3px;background:radial-gradient(circle at 84% 30%,rgba(201,160,96,.13),transparent 27%),linear-gradient(118deg,#211B1C 0%,#171314 58%,#211A17 100%);box-shadow:0 24px 54px rgba(0,0,0,.24)}
.home-page .page-heading::before{content:"";position:absolute;z-index:0;right:-70px;top:-230px;width:480px;height:480px;border-radius:50%;background:radial-gradient(circle,rgba(238,203,150,.17),rgba(179,146,100,.06) 42%,transparent 70%);filter:blur(4px);pointer-events:none}
.home-page .page-heading::after{content:"";position:absolute;z-index:0;right:7%;top:49%;width:clamp(220px,30vw,390px);aspect-ratio:1;transform:translateY(-50%);border:1px solid rgba(238,203,150,.13);border-radius:50%;box-shadow:0 0 0 28px rgba(238,203,150,.025),0 0 0 58px rgba(238,203,150,.018);pointer-events:none}
.hero-content,.hero-metrics{position:relative;z-index:1}
.hero-content{max-width:790px}
.hero-eyebrow{display:flex;align-items:center;gap:10px;margin-bottom:19px;color:var(--gold);font-size:10px;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.hero-dot{width:7px;height:7px;border-radius:50%;background:var(--gold);box-shadow:0 0 14px rgba(238,203,150,.8)}
.home-page .page-heading h1{max-width:760px;margin:0;font-size:clamp(46px,7.3vw,84px);font-weight:550;line-height:.98;letter-spacing:-.065em}
.home-page .page-heading p{max-width:670px;margin:18px 0 0;color:#C9BDA9;font-size:16px;line-height:1.65}
.hero-actions{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin-top:24px}
.hero-cta{display:inline-flex;align-items:center;min-height:43px;padding:0 17px;background:var(--gold);color:var(--ink);font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;border:1px solid var(--gold);border-radius:2px}
.hero-cta::after{content:"↘";margin-left:14px;font-size:16px}
.hero-cta:hover{background:#F7DEBB;color:var(--ink);transform:translateY(-2px);opacity:1}
.hero-note{color:#B6A486;font-size:10px;letter-spacing:.04em}
.hero-metrics{display:flex;gap:clamp(26px,5vw,70px);max-width:760px;margin-top:30px;padding-top:19px;border-top:1px solid rgba(238,203,150,.2)}
.hero-metric{display:grid;gap:1px;min-width:100px}
.hero-metric strong{color:#F7F3EA;font-size:28px;font-weight:500;line-height:1.1;letter-spacing:-.04em}
.hero-metric span{color:#B6A486;font-size:9px;font-weight:750;letter-spacing:.12em;text-transform:uppercase}
.home-page .view-language-row{margin:18px 0 12px}
.view-switcher{gap:7px;margin:0}
.view-switcher button{border:1px solid rgba(238,203,150,.22);border-radius:2px;background:#211B1C;color:#E8DDCB;padding:9px 13px;font-size:11px;letter-spacing:.025em}
.view-switcher button:hover{border-color:var(--gold);color:var(--gold)}
.view-switcher button.current{border-color:var(--gold);background:var(--gold);color:var(--ink);box-shadow:none}
.locale-switch{border:1px solid rgba(238,203,150,.22);border-radius:2px;background:#211B1C}
.locale-switch span{color:#B6A486}
.locale-switch button{color:#D5C8B5}
.locale-switch button.current{background:var(--gold);color:var(--ink);box-shadow:none}
.discovery-tools{margin:12px 0 17px;padding:17px 18px;background:#211B1C;border:1px solid rgba(238,203,150,.2);border-radius:3px;box-shadow:0 12px 30px rgba(0,0,0,.14)}
.form-field label{color:#D9CBB5;font-size:10px;letter-spacing:.09em;text-transform:uppercase}
.form-input,.form-select{min-height:40px;border-color:#544638;border-radius:2px;background:#171314;color:#F6F0E6}
.form-input::placeholder{color:#9E8D73}
.form-input:focus,.form-select:focus,.view-switcher button:focus-visible,.score-panel summary:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.form-select option{background:#211B1C;color:#F7F3EA}
.result-count{color:#C7B699}
.score-panel{border-top-color:rgba(238,203,150,.18)}
.score-panel summary{color:#F3E7D3}
.score-panel-intro,.weight-note{color:#B6A486}
.weight-control label{color:#E1D4C0}
.weight-control output{color:var(--gold)}
.weight-control input{accent-color:var(--gold)}
.reset-weights{border-color:#806D50;border-radius:2px;background:#2A2320;color:#F3E7D3}
.reset-weights:hover{background:var(--gold);color:var(--ink)}
.home-page .repo-list{gap:15px}
.project-card{padding:20px 22px;border:1px solid #E6D9C5;border-radius:3px;background:#F7F3EA;color:#1A1517;box-shadow:0 12px 30px rgba(0,0,0,.16);transition:transform .2s ease,box-shadow .2s ease}
.project-card:hover{transform:translateY(-2px);box-shadow:0 18px 38px rgba(0,0,0,.22)}
.project-card-top{grid-template-columns:48px minmax(0,1fr) auto;gap:16px;align-items:center}
.rank-number{background:#EECB96;color:#1A1517;border-radius:2px;box-shadow:0 4px 12px rgba(120,86,42,.17)}
.project-title{font-size:21px;letter-spacing:-.02em}
.project-title a{color:#1A1517}
.project-title a:hover{color:#765D38;opacity:1}
.project-score{border-color:#D8C49F;border-radius:2px;background:#F1E4CE;color:#3E3223}
.project-score span{color:#765D38}
.project-score strong{color:#1A1517}
.project-score small{color:#76664E}
.project-card-content{grid-template-columns:240px minmax(0,1fr);gap:23px;margin-top:15px}
.project-visual{width:240px}
.project-visual>img,.project-visual-art{height:150px;border:1px solid #E6DCCB;border-radius:2px;background:#EAE1D2}
.project-visual figcaption{color:#796D5B}
.project-visual figcaption a{color:#79603C}
.project-visual-art{background:linear-gradient(135deg,hsl(var(--visual-hue) 24% 90%),#F7E8D1)}
.art-window{background:rgba(255,255,255,.94)}
.project-summary{min-width:0}
.source-description-label{color:#857760}
.project-description{color:#3E3932}
.topic-chip{background:#EDE3D2;color:#655238}
.project-meta{color:#655B4D}
.project-meta .star{color:#1A1517}
.project-meta .star-icon{color:#B58A43}
.project-details{border-top-color:#E3D7C4}
.project-details summary{color:#735A35}
.project-details summary:hover{color:#1A1517}
.localized-explainer section{border-color:#E7DCCB;background:#FCF9F2}
.localized-explainer h3{color:#765D38}
.localized-explainer p,.detail-lead{color:#413B33}
.detail-facts>div{border-color:#E6DCCB;background:#FCF9F2}
.detail-facts strong{color:#7C705E}
.detail-facts span{color:#28231E}
.details-body h3{color:#312820}
.signal-heading{color:#4D4438}
.signal-track{background:#E7DDCF}
.signal-track span{background:#B39264}
.method-note{border-left-color:#B39264;background:#F2E7D5;color:#564B3B}
.project-actions .btn,.detail-actions a{border-color:#D5C8B2;border-radius:2px;background:#FCF9F2;color:#2A241E}
.project-actions .btn:hover,.detail-actions a:hover{border-color:#B39264;background:#EECB96;color:#1A1517;opacity:1}
.project-actions .guide-btn,.detail-actions .guide-btn{border-color:#B39264;color:#725934}
.sponsor{border-color:#D8C49F;border-radius:3px;background:#F7F3EA;color:#1A1517;box-shadow:0 12px 28px rgba(0,0,0,.12)}
.sponsor strong{color:#1A1517}
.sponsor p{color:#6E6250}
.sponsor .btn{border-color:#B39264;border-radius:2px;background:#EECB96;color:#1A1517}
.empty{color:#D7C7AE}
footer{background:#151112;border-top:1px solid rgba(238,203,150,.18);color:#AE9877}
footer .brand{color:#F7DEBB}
footer a:hover{color:var(--gold)}
.sponsor-slot{margin-top:0}
@media(max-width:900px){.home-page .atlas-layout{width:min(100% - 36px,760px);margin-bottom:44px}.atlas-layout{grid-template-columns:1fr}.sidebar{position:static;max-height:none}.home-page .sidebar{display:none}}
@media(max-width:760px){.home-page .page-heading{min-height:0;padding:40px 30px 27px}.home-page .page-heading::after{right:-10%;top:40%;opacity:.75}.hero-metrics{gap:24px}.hero-metric{min-width:0}.project-card-content{grid-template-columns:190px minmax(0,1fr);gap:16px}.project-visual{width:190px}.project-visual>img,.project-visual-art{height:130px}}
@media(max-width:560px){.site-header{padding:11px 16px;gap:10px}.site-header .brand{font-size:14px}.site-header .brand img{width:27px;height:27px}.nav{gap:3px}.nav a{padding:7px 8px;font-size:9px;letter-spacing:.08em}.home-page .atlas-layout{width:calc(100% - 28px)}.home-page .page-heading{margin:18px 0 17px;padding:31px 22px 24px}.home-page .page-heading h1{font-size:clamp(42px,13vw,61px)}.home-page .page-heading p{font-size:14px}.hero-eyebrow{font-size:9px;letter-spacing:.13em}.hero-actions{gap:12px;margin-top:19px}.hero-note{font-size:9px}.hero-metrics{gap:14px;margin-top:23px;padding-top:16px}.hero-metric strong{font-size:23px}.hero-metric span{font-size:8px;letter-spacing:.06em}.home-page .view-language-row{align-items:flex-start}.view-switcher{gap:5px}.view-switcher button{padding:8px 9px;font-size:10px}.locale-switch{margin:0}.discovery-tools{padding:13px}.search-filter-grid{grid-template-columns:1fr}.search-filter-grid .search-field{grid-column:auto}.project-card{padding:14px}.project-card-top{grid-template-columns:44px minmax(0,1fr);gap:10px}.rank-number{width:44px;height:44px;font-size:23px}.project-title{font-size:17px}.project-score{grid-column:2;justify-self:start;text-align:left;min-width:100px}.project-card-content{grid-template-columns:1fr;gap:9px;margin-top:10px}.project-visual{width:min(100%,360px)}.project-visual>img,.project-visual-art{height:170px}.project-description{font-size:13px}.project-meta{font-size:11px}.sponsor{padding:12px}.guide-head h1{font-size:21px}}
"""
# Keep the generated home-page stylesheet in sync with this build source.
(SITE / 'styles.css').write_text(CSS, encoding='utf-8')


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def star_markup(count):
    return f'<span class="star"><span class="star-icon" aria-hidden="true">★</span> {count:,}</span>'


def slug(name):
    return name.lower().replace('/', '-')


def page_path(path):
    return BASE_URL + path


def head_tags(title, description, css='/styles.css?v=4', canonical=None, og_type='website'):
    canon = canonical or page_path('/')
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)} · PickRepo</title>
<link rel="canonical" href="{canon}">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<meta property="og:site_name" content="PickRepo">
<meta property="og:title" content="{esc(title)} · PickRepo">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{page_path('/assets/icon.svg')}">
<link rel="stylesheet" href="{css}">
</head><body>'''


def shell(body_html, title, description, css='/styles.css?v=4', canonical=None, extra_script=''):
    return head_tags(title, description, css, canonical) + f'''
<header class="site-header"><div class="brand"><a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit"><img src="/assets/icon.svg" alt="PickRepo logosu">PickRepo</a></div>
<nav class="nav"><a id="navDiscover" href="/">Keşfet</a><a id="navGuides" href="/guides.html">Rehberler</a></nav></header>
<div class="atlas-layout"><aside class="sidebar" aria-label="Site navigasyonu"><div class="sidebar-heading"><span class="sidebar-eyebrow">PickRepo</span><h2 id="sidebarTitle">Keşfet</h2></div>
<nav class="sidebar-links"><a id="sidebarDiscover" href="/">↗ Projeleri keşfet</a><a id="sidebarGuides" href="/guides.html">▤ Kaynaklı rehberler</a></nav></aside>
<main>{body_html}</main></div>
<footer><div class="brand">PickRepo</div><span id="footerNote">GitHub ile bağlantılı olmayan bağımsız bir keşif aracı.</span><a id="footerSponsor" href="/sponsor.html">Sponsor olun</a><a id="footerPrivacy" href="/privacy.html">Gizlilik</a><a id="footerTerms" href="/terms.html">Kullanım koşulları</a></footer>
{extra_script}
</body></html>'''


def visual_markup(full_name, language, media=None):
    media = media or {}
    image_path = media.get('path', '')
    image_exists = image_path.startswith('/assets/repo-media/') and (SITE / image_path.lstrip('/')).is_file()
    if image_exists:
        alt = media.get('alt') or (full_name + ' project image')
        source = media.get('source', '')
        caption = 'Resmî depo görseli'
        source_link = f' · <a href="{esc(source)}" target="_blank" rel="noopener noreferrer">kaynağı ↗</a>' if source else ''
        return f'''<figure class="project-visual"><img src="{esc(image_path)}" alt="{esc(alt)}" loading="lazy" decoding="async"><figcaption>{caption}{source_link}</figcaption></figure>'''
    hue = sum((i + 1) * ord(ch) for i, ch in enumerate(full_name)) % 360
    short_name = full_name.rsplit('/', 1)[-1][:2].upper()
    return f'''<figure class="project-visual"><div class="project-visual-art" style="--visual-hue:{hue}" role="img" aria-label="{esc(full_name)} için temsili illüstrasyon">
      <div class="art-orbit" aria-hidden="true"></div><div class="art-window" aria-hidden="true"><div class="art-window-bar"><i></i><i></i><i></i></div>
      <div class="art-window-content"><span class="art-glyph">{esc(short_name)}</span><span class="art-lines"><i></i><i></i><i></i></span></div></div>
      <div class="art-caption"><strong>{esc(full_name.rsplit('/', 1)[-1])}</strong><span>{esc(language)}</span></div></div><figcaption>Temsili illüstrasyon</figcaption></figure>'''


# ---------- Repo card (shared) ----------
def repo_card(r, idx):
    owner, _, name = r['full_name'].partition('/')
    full_name = r['full_name'].lower()
    github_url = r.get('html_url') or ('https://github.com/' + r['full_name'])
    stars = r.get('stargazers_count') or 0
    forks = r.get('forks_count') or 0
    desc = r.get('description') or 'GitHub açıklaması eklenmemiş; ayrıntılar için kaynak depoyu inceleyin.'
    language = r.get('language') or 'Belirtilmemiş'
    license = r.get('license') or 'GitHub’da belirtilmemiş'
    if license == 'NOASSERTION':
        license = 'GitHub’da belirtilmemiş'
    topics = r.get('topics') or []
    topic_tags = ''.join(f'<span class="topic-chip">{esc(topic)}</span>' for topic in topics[:6])
    guide_link = ''
    guide_data = GUIDES.get(full_name)
    if guide_data:
        guide_link = f'<a class="btn guide-btn" href="/guide/{slug(full_name)}.html">Kaynaklı rehber ↗</a>'
    guide_tr = (guide_data or {}).get('tr', {})
    what_text = guide_tr.get('what') or 'Bu proje GitHub’da yayımlanan herkese açık bir repo kaydıdır. Proje sahibinin özgün açıklaması aşağıda yer alır.'
    use_text = guide_tr.get('use') or 'Kullanım amacı proje sahibinin GitHub açıklaması ve README’sinde belirtilir; PickRepo burada ayrıca doğrulama yapmamıştır.'
    install_text = guide_tr.get('effort') or 'Kurulum adımları proje sahibinin resmî README’sindedir. Bu sitede kurulum denenmemiştir.'
    visual_html = visual_markup(full_name, language, MEDIA.get(full_name))
    return f'''\n<article class="project-card" data-language="{esc(language)}">
  <div class="project-card-top"><span class="rank-number" aria-label="Sıra {idx + 1}">{idx + 1}</span>
    <div class="project-title-wrap"><h2 class="project-title"><a href="{esc(github_url)}" target="_blank" rel="noopener noreferrer">{esc(owner)} / <strong>{esc(name)}</strong></a></h2>
    </div>
    <div class="project-score"><span>PickRepo keşif puanı</span><strong class="score-value">—<small>/100</small></strong></div>
  </div>
  <div class="project-card-content">{visual_html}<div class="project-summary">
    <span class="source-description-label">GitHub açıklaması · özgün dil</span><p class="project-description">{esc(desc)}</p>
    {f'<div class="topic-list" aria-label="GitHub konuları">{topic_tags}</div>' if topic_tags else ''}
    <div class="project-meta">{star_markup(stars)}<span>{esc(language)}</span><span>Fork {forks:,}</span><span>Lisans: {esc(license)}</span></div>
  </div></div>
  <details class="project-details"><summary>Ayrıntılar · Nedir? Ne işe yarar? Nasıl kurulur?</summary>
    <div class="details-body"><div class="localized-explainer">
      <section><h3>Nedir?</h3><p>{esc(what_text)}</p></section>
      <section><h3>Ne işe yarar?</h3><p>{esc(use_text)}</p></section>
      <section><h3>Nasıl kurulur?</h3><p>{esc(install_text)}</p></section>
    </div>
      <div class="detail-facts"><div><strong>Oluşturulma</strong><span>{esc(r.get('created_at') or 'Belirtilmemiş')}</span></div><div><strong>Son değişiklik</strong><span>{esc(r.get('pushed_at') or 'Belirtilmemiş')}</span></div><div><strong>Toplam yıldız</strong><span>{stars:,}</span></div><div><strong>Fork</strong><span>{forks:,}</span></div><div><strong>Lisans</strong><span>{esc(license)}</span></div><div><strong>GitHub konuları</strong><span>{esc(', '.join(topics) if topics else 'Belirtilmemiş')}</span></div></div>
      <p class="method-note">Keşif puanı arama uyumu ve GitHub metaverilerine dayanır; kod çalıştırılmaz, güvenlik veya kalite doğrulanmaz. Tarihsel yıldız kayıtları tutulmadığı için yıldız kazanma hızı ölçülmez.</p>
      <div class="detail-actions"><a href="{esc(github_url)}#readme" target="_blank" rel="noopener noreferrer">README / kaynak ↗</a>{guide_link}</div>
    </div>
  </details>
  <div class="project-actions">{guide_link}<a class="btn" href="{esc(github_url)}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
</article>'''


# ---------- Build index ----------
items = []
for name in VIEWS.get('trending', []):
    key = name.lower()
    r = REPOS.get(key) or {}
    if not r.get('html_url'):
        r['html_url'] = 'https://github.com/' + name
    items.append(r)

# Keep the static first paint aligned with the default trending sort.
items.sort(key=lambda repo: int(repo.get('stargazers_count') or 0), reverse=True)

index_cards = []
for i, repo in enumerate(items):
    index_cards.append(repo_card(repo, i))
    if i + 1 in (3, 6, 9):
        index_cards.append('<div class="sponsor sponsor-slot"><div><strong>Sponsor alanı</strong><p>Henüz aktif sponsor yok.</p></div><a class="btn" href="/sponsor.html">Sponsor ol ↗</a></div>')

view_buttons = ''.join(
    f'<button type="button" data-view="{view}" class="{"current" if view == "trending" else ""}" aria-pressed="{"true" if view == "trending" else "false"}">{label}</button>'
    for view, label in [('trending', 'Yükselenler'), ('popular', 'Popüler'), ('early', 'Erken keşif'), ('guides', 'Kaynaklı rehberler')]
)
weight_fields = '''
<div class="weight-control"><label id="weightLabelRelevance" for="weightRelevance">Arama ve konu uyumu</label><output id="weightOutRelevance">30%</output><input id="weightRelevance" type="range" min="0" max="100" value="30"></div>
<div class="weight-control"><label id="weightLabelActivity" for="weightActivity">Yakın tarihli güncelleme</label><output id="weightOutActivity">25%</output><input id="weightActivity" type="range" min="0" max="100" value="25"></div>
<div class="weight-control"><label id="weightLabelCommunity" for="weightCommunity">Yıldız ve fork topluluğu</label><output id="weightOutCommunity">20%</output><input id="weightCommunity" type="range" min="0" max="100" value="20"></div>
<div class="weight-control"><label id="weightLabelRecency" for="weightRecency">Projenin yeniliği</label><output id="weightOutRecency">15%</output><input id="weightRecency" type="range" min="0" max="100" value="15"></div>
<div class="weight-control"><label id="weightLabelContext" for="weightContext">Proje bilgilerinin doluluğu</label><output id="weightOutContext">10%</output><input id="weightContext" type="range" min="0" max="100" value="10"></div>'''
index_body = (
    '<section class="page-heading"><div class="hero-content"><div class="hero-eyebrow"><span class="hero-dot" aria-hidden="true"></span><span id="heroEyebrow">Açık kaynak dünyasına yeni bir bakış</span></div><h1 id="pageTitle">Yükselenler</h1><p id="pageDescription">Son 7 günde oluşturulan herkese açık depolar; toplam yıldız sayısına göre sıralanır. Haftalık yıldız artışı ölçülmez.</p><div class="hero-actions"><a class="hero-cta" id="heroBrowse" href="#repoList">Projeleri keşfet</a><span class="hero-note" id="heroNote">Her gün yenilenir · Ücretsiz · Hesap gerekmez</span></div></div><div class="hero-metrics"><div class="hero-metric"><strong>' + str(len(VIEWS)) + '</strong><span id="heroStatCollections">Keşif listesi</span></div><div class="hero-metric"><strong>' + f'{len(REPOS):,}' + '</strong><span id="heroStatRepositories">Açık repo</span></div><div class="hero-metric"><strong>' + str(len(GUIDES)) + '</strong><span id="heroStatGuides">Kaynaklı rehber</span></div></div></section>' +
    '<div class="view-language-row"><nav class="view-switcher" aria-label="Keşif listeleri">' + view_buttons + '</nav>'
    '<div class="locale-switch" role="group" aria-label="Arayüz dili"><span id="localeLabel">Dil</span><button id="localeTr" type="button" data-locale="tr" aria-pressed="true">TR</button><button id="localeEn" type="button" data-locale="en" aria-pressed="false">EN</button></div></div>'
    '<section class="discovery-tools" aria-label="Proje arama ve filtreleri">'
    '<div class="search-filter-grid">'
    '<div class="form-field search-field"><label id="searchLabel" for="searchInput">Proje ara</label><input class="form-input" type="search" id="searchInput" placeholder="Ad, açıklama veya GitHub konusu" autocomplete="off"></div>'
    '<div class="form-field"><label id="languageLabel" for="langSelect">Programlama dili</label><select class="form-select" id="langSelect"><option value="all">Tüm diller</option></select></div>'
    '<div class="form-field"><label id="topicLabel" for="topicSelect">GitHub konusu</label><select class="form-select" id="topicSelect"><option value="all">Tüm konular</option></select></div>'
    '<div class="form-field"><label id="sortLabel" for="sortSelect">Sıralama</label><select class="form-select" id="sortSelect"><option id="sortMatch" value="match">PickRepo keşif puanı</option><option id="sortStars" value="stars" selected>En çok yıldız</option><option id="sortUpdated" value="updated">Son güncellenen</option><option id="sortCreated" value="created">En yeni oluşturulan</option></select></div>'
    '</div><p class="result-count" id="resultCount" aria-live="polite">50 proje</p>'
    '<details class="score-panel"><summary id="scoreSummary">Keşif puanını kişiselleştir · nasıl hesaplanıyor?</summary>'
    '<p class="score-panel-intro" id="scoreIntro">Ağırlıkları değiştirince sıralama tarayıcınızda yenilenir. Yüzdeler otomatik olarak 100’e tamamlanır; tercih kaydedilmez.</p>'
    '<div class="weight-grid">' + weight_fields + '</div><p class="weight-note" id="weightTotal">Puan: arama uyumu, güncellik, yıldız/fork sayısı, proje yaşı ve bilgi doluluğu.</p>'
    '<button class="reset-weights" type="button" id="resetWeights">Varsayılan ağırlıkları geri yükle</button>'
    '<p class="method-note" id="scoreMethod">Bu puan bir keşif yardımcısıdır; kalite veya güvenlik garantisi değildir. PickRepo repo kodunu çalıştırmaz. Tarihsel yıldız kayıtları olmadığı için son hafta kazanılan yıldız sayısı ölçülmez. Lisans etiketi hukuki lisans değerlendirmesi değildir. Hesap, e-posta uyarısı veya sunucu gerekmez.</p>'
    '</details></section>'
    '<div class="repo-list" id="repoList">' + '\n'.join(index_cards) + '</div>'
    '<p class="empty" id="emptyState" hidden>Bu filtrelerde sonuç bulunamadı. Arama sözcüğünü veya filtreleri değiştirebilirsiniz.</p>'
)

guide_summaries = {
    name.lower(): {
        lang: {
            'what': content.get('what', ''),
            'use': content.get('use', ''),
            'install': content.get('effort', '')
        }
        for lang, content in (('tr', GUIDE.get('tr', {})), ('en', GUIDE.get('en', {})))
    }
    for name, GUIDE in GUIDES.items()
}
catalog_payload = {
    'views': VIEWS,
    'repos': REPOS,
    'guideSlugs': {name.lower(): slug(name) for name in GUIDES},
    'guideSummaries': guide_summaries,
    'media': MEDIA
}
safe_catalog_json = json.dumps(catalog_payload, ensure_ascii=False, separators=(',', ':'))
safe_catalog_json = safe_catalog_json.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
cat_script = '<script type="application/json" id="catalogData">' + safe_catalog_json + '</script>'
discovery_source = ROOT / 'scripts' / 'discovery.js'
(SITE / 'discovery.js').write_text(discovery_source.read_text(encoding='utf-8'), encoding='utf-8')
index_html = shell(
    index_body,
    'Keşfet',
    'GitHub projelerini arayın, filtreleyin ve GitHub verilerine dayalı keşif puanını kendi tercihlerinize göre ayarlayın.',
    canonical=page_path('/'),
    extra_script=cat_script + '<script src="/discovery.js?v=4" defer></script>')
index_html = index_html.replace('<body>', '<body class="home-page">', 1)
(SITE / 'index.html').write_text(index_html, encoding='utf-8')


# ---------- Guide pages ----------
def guide_body(name, lang):
    g = GUIDES[name]
    t = g[lang]
    sources = g.get('sources', []) or []
    gh_url = 'https://github.com/' + name
    title = t.get('what') or name
    guide_label = 'Kaynaklı rehber' if lang == 'tr' else 'Source-based guide'
    what_heading = 'Nedir?' if lang == 'tr' else 'What is it?'
    use_heading = 'Ne işe yarar?' if lang == 'tr' else 'What is it useful for?'
    how_heading = 'Nasıl kullanılır?' if lang == 'tr' else 'How do you use it?'
    effort_heading = 'Kurulum gereksinimleri' if lang == 'tr' else 'Installation requirements'
    install_heading = 'Nasıl kurulur?' if lang == 'tr' else 'How to install'
    limits_heading = 'Sınırlar ve riskler' if lang == 'tr' else 'Limitations and risks'
    sources_heading = 'Kaynaklar' if lang == 'tr' else 'Sources'
    prereq_heading = 'Başlamadan önce' if lang == 'tr' else 'Before you start'
    success_heading = 'Başarı işareti' if lang == 'tr' else 'Success check'
    help_heading = 'Takılırsan' if lang == 'tr' else 'If something goes wrong'
    install_note = 'Aşağıdaki adımlar kaynaklardan derlenmiştir; bu sitede kurulup denenmemiştir.' if lang == 'tr' else 'The steps below are based on the sources; installation was not tested on this site.'
    header = f'''<div class="guide-head"><div class="guide-brand"><span class="guide-eyebrow">{guide_label}</span><h1>{esc(title)}</h1></div>
<a class="gh-btn" href="{gh_url}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>'''
    first_use = t.get('firstUse') or t.get('example') or t.get('use', '')
    body = f'''<section class="guide-section"><h2>{what_heading}</h2><p>{esc(t.get("what", ""))}</p></section>
<section class="guide-section"><h2>{use_heading}</h2><p>{esc(t.get("use", ""))}</p></section>
<section class="guide-section"><h2>{how_heading}</h2><p>{esc(first_use)}</p></section>
<section class="guide-section"><h2>{effort_heading}</h2><p>{esc(t.get("effort", ""))}</p></section>
<section class="guide-section"><h2>{limits_heading}</h2><p>{esc(t.get("limits", ""))}</p></section>'''
    for path_data in g.get('paths', []):
        instructions = path_data.get(lang) or {}
        if not instructions:
            continue
        os_name = path_data.get('os', '')
        prereqs = ''.join(f'<li>{esc(item)}</li>' for item in instructions.get('prerequisites', []))
        commands = path_data.get('commands', {}) or {}
        step_items = []
        for index, step in enumerate(instructions.get('steps', [])):
            command = commands.get(str(index))
            command_html = f'<pre><code>{esc(command)}</code></pre>' if command else ''
            step_items.append(f'<li>{esc(step)}{command_html}</li>')
        success = instructions.get('success', '')
        help_items = ''.join(f'<li>{esc(item)}</li>' for item in instructions.get('help', []))
        body += f'''<section class="guide-section"><h2>{install_heading}: {esc(os_name)}</h2>
<p class="small">{install_note}</p>
<h3>{prereq_heading}</h3><ul>{prereqs}</ul>
<ol>{''.join(step_items)}</ol>
{f'<p><strong>{success_heading}:</strong> {esc(success)}</p>' if success else ''}
{f'<h3>{help_heading}</h3><ul>{help_items}</ul>' if help_items else ''}</section>'''
    if sources:
        li = 1 if lang == 'tr' else 2
        src = ''.join(f'<li><a href="{esc(s[0])}" target="_blank" rel="noopener noreferrer">{esc(s[li] if len(s) > li else s[0])}</a></li>' for s in sources if len(s) > 0)
        body += f'<section class="guide-section"><h2>{sources_heading}</h2><ul>{src}</ul></section>'
    editor_note = 'Bu rehber aşağıdaki kaynaklara dayanır; kurulum bu sitede denenmemiştir.' if lang == 'tr' else 'This guide is based on the sources below; installation was not tested on this site.'
    body += f'<p class="small">{editor_note}</p>'
    question_what = 'Nedir?' if lang == 'tr' else 'What is it?'
    question_use = 'Nasıl kullanılır?' if lang == 'tr' else 'How do you use it?'
    question_install = 'Nasıl kurulur?' if lang == 'tr' else 'How to install'
    question_limits = 'Sınırlar ve riskler' if lang == 'tr' else 'Limitations and risks'
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": question_what, "acceptedAnswer": {"@type": "Answer", "text": t.get("what", "")}},
            {"@type": "Question", "name": question_use, "acceptedAnswer": {"@type": "Answer", "text": first_use}},
            {"@type": "Question", "name": question_install, "acceptedAnswer": {"@type": "Answer", "text": t.get("effort", "")}},
            {"@type": "Question", "name": question_limits, "acceptedAnswer": {"@type": "Answer", "text": t.get("limits", "")}},
        ],
    }
    body += f'<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>'
    return header + f'<div class="guide-body">{body}</div>', title


GUIDE_CSS = CSS + '''

.guide-head{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:14px}
.guide-eyebrow{display:block;font-size:11px;letter-spacing:1.4px;color:#475664;text-transform:uppercase;margin-bottom:6px}
.guide-head h1{margin:0;font-size:22px;font-weight:700}
.guide-body{display:grid;gap:16px}
.guide-section{border:1px solid var(--border);border-radius:7px;padding:14px 16px;background:#fff}
.guide-section h2{margin:0 0 8px;font-size:16px;font-weight:700;color:var(--orange-dark)}
.guide-section h3{margin:12px 0 6px;font-size:14px;color:#222}
.guide-section p{margin:0 0 8px;color:#222;font-size:14px;line-height:1.6}
.guide-section ul,.guide-section ol{margin:0 0 8px;padding-left:22px;color:#222}
.guide-section li{margin-bottom:8px;font-size:14px;line-height:1.55}
.guide-section pre{overflow-x:auto;background:#f6f6ef;border:1px solid var(--border);border-radius:5px;padding:8px 10px;margin:8px 0;color:#111;font-size:13px}
.small{display:block;font-size:12px;color:var(--muted);margin-top:10px}
#langTrBtn,#langEnBtn{background:transparent;border:1px solid var(--border);border-radius:6px;padding:4px 10px;font-size:12px;cursor:pointer;color:var(--text)}
.current-lang{border-color:var(--orange-dark);color:var(--orange-dark);font-weight:700}
.lang-wrap{margin-top:16px}'''
GUIDE_CSS += r"""
.guide-head{position:relative;overflow:hidden;padding:28px 30px;background:radial-gradient(circle at 90% 20%,rgba(201,160,96,.12),transparent 34%),linear-gradient(120deg,#211B1C,#171314);border:1px solid rgba(238,203,150,.2);border-radius:3px;min-height:150px}
.guide-eyebrow{color:#EECB96;letter-spacing:.17em}
.guide-head h1{color:#F7F3EA;font-size:clamp(24px,4vw,38px);letter-spacing:-.04em}
.guide-head .gh-btn{display:inline-flex;align-items:center;padding:10px 15px;border:1px solid #B39264;border-radius:2px;background:#EECB96;color:#1A1517;font-size:11px;font-weight:800;letter-spacing:.07em;text-transform:uppercase}
.guide-body{gap:13px}
.guide-section{border:1px solid #E5D8C3;border-radius:3px;padding:19px 22px;background:#F7F3EA;color:#1A1517;box-shadow:0 12px 28px rgba(0,0,0,.14)}
.guide-section h2{color:#765D38}
.guide-section h3{color:#312820}
.guide-section p,.guide-section ul,.guide-section ol,.guide-section li{color:#413B33}
.guide-section a{color:#765D38;text-decoration:underline;text-underline-offset:3px}
.guide-section pre{background:#211B1C;border-color:#5D4C37;color:#F7F3EA;border-radius:2px}
.guide-section pre code{color:#F7F3EA}
.guide-section .small{color:#7C705E}
#langTrBtn,#langEnBtn{border-color:#806D50;border-radius:2px;background:#211B1C;color:#F7DEBB}
.current-lang{border-color:#EECB96!important;background:#EECB96!important;color:#1A1517!important}
.lang-wrap{border-top:1px solid rgba(238,203,150,.16);padding-top:15px}
@media(max-width:560px){.guide-head{padding:22px 19px}.guide-section{padding:15px 16px}}
"""
(SITE / 'styles').mkdir(exist_ok=True)
(SITE / 'styles' / 'guide.css').write_text(GUIDE_CSS, encoding='utf-8')


def guide_page(name):
    g = GUIDES[name]
    parts = {}
    titles = {}
    descriptions = {}
    for lang in ('tr', 'en'):
        body_html, title = guide_body(name, lang)
        parts[lang] = body_html
        titles[lang] = title
        descriptions[lang] = t.get('what', '') if (t := g[lang]) else ''
    body = f'''<article>
{parts['tr']}
<div class="lang-wrap" id="langEn" hidden>{parts['en']}</div>
<p class="small" style="margin-top:18px"><strong>Dil / Language:</strong> <button id="langTrBtn" class="current-lang">Türkçe</button> <button id="langEnBtn">English</button></p>
</article>'''
    sidebar_links = ''.join(f'<a href="/guide/{slug(n)}.html"{" class=current" if n == name else ""}>{esc(GUIDES[n]["tr"].get("what") or n)}</a>' for n in GUIDES)
    page = shell(
        body,
        titles['tr'],
        descriptions.get('tr', titles['tr']),
        css='/styles/guide.css?v=3',
        canonical=page_path(f'/guide/{slug(name)}.html'),
        extra_script='''<script>
document.getElementById("langEnBtn").onclick=function(){document.getElementById("langTrBtn").classList.remove("current-lang");this.classList.add("current-lang");document.querySelector("article > .guide-body").hidden=true;document.getElementById("langEn").hidden=false;return false;};
document.getElementById("langTrBtn").onclick=function(){document.getElementById("langEnBtn").classList.remove("current-lang");this.classList.add("current-lang");document.getElementById("langEn").hidden=true;document.querySelector("article > .guide-body").hidden=false;return false;};\n</script>''')
    page = page.replace('<h2>Keşfet</h2>', '<h2>Rehberler</h2>')
    page = page.replace('<nav class="sidebar-links"><a href="/">↗ Projeleri keşfet</a><a href="/guides.html">▤ Kaynaklı rehberler</a></nav>',
                        f'<nav class="sidebar-links">{sidebar_links}</nav>')
    return page


for name in GUIDES:
    (SITE / 'guide').mkdir(exist_ok=True)
    (SITE / 'guide' / f'{slug(name)}.html').write_text(guide_page(name), encoding='utf-8')

# ---------- Guides listing ----------
guide_links = ''.join(f'<a href="/guide/{slug(n)}.html">{esc(GUIDES[n]["tr"].get("what") or n)}</a>' for n in GUIDES)
guide_rows = ''
for n in GUIDES:
    g = GUIDES[n]
    t = g.get('tr', {})
    repo = REPOS.get(n.lower()) or {}
    stars = repo.get('stargazers_count') or 0
    guide_rows += f'''<article class="row"><span class="pos">·</span><div class="main"><h2 class="title" style="font-size:16px"><a href="/guide/{slug(n)}.html">{esc(t.get("what") or n)}</a></h2><p class="desc">{esc(t.get("use",""))}</p></div><div class="right">{star_markup(stars)}</div></article>'''
guides_html = shell(
    '<section class="page-heading"><h1>Kaynaklı rehberler</h1><p>Nedir? · Nasıl kurulur? · Nasıl kullanılır?</p></section>'
    f'<div class="repo-list">{guide_rows}</div>',
    'Kaynaklı rehberler',
    'PickRepo kaynaklı rehberleri: Nedir? · Nasıl kurulur? · Nasıl kullanılır?',
    canonical=page_path('/guides.html'))
guides_html = guides_html.replace('<nav class="sidebar-links"><a href="/">↗ Projeleri keşfet</a><a href="/guides.html">▤ Kaynaklı rehberler</a></nav>',
                                  f'<nav class="sidebar-links">{guide_links}</nav>')
(SITE / 'guides.html').write_text(guides_html, encoding='utf-8')


def static_page(filename, title, description, main_html):
    page = shell(main_html, title, description, canonical=page_path(f'/{filename}'))
    (SITE / filename).write_text(page, encoding='utf-8')


static_page('sponsor.html', 'Sponsor olun',
    'PickRepo sponsor bilgileri. Şu anda ödeme veya sponsor bağlantısı etkin değil.',
    '<section class="page-heading"><h1>Sponsor olun</h1><p>PickRepo’yu destekleme bilgileri burada paylaşılacaktır.</p></section>'
    '<div class="sponsor"><div><strong>Henüz sponsor bağlantısı yok.</strong><p>Şu anda etkin bir ödeme veya sponsorluk bağlantısı bulunmuyor; bu sayfadan ödeme alınmaz.</p></div><a class="btn" href="/">Ana sayfa ↗</a></div>')

static_page('privacy.html', 'Gizlilik',
    'PickRepo gizlilik politikası: kullanıcıdan hesap, e-posta veya kişisel veri toplanmaz.',
    '<section class="page-heading"><h1>Gizlilik</h1><p>PickRepo, GitHub’dan herkese açık depo bilgilerini okur ve statik sayfalarda gösterir.</p>'
    '<p>Kullanıcıdan hesap, e-posta veya kişisel veri toplanmaz. Çerez kullanılmaz. Arama metni ve puan ağırlıkları yalnızca açık tarayıcı sekmesinde kullanılır; sunucuya gönderilmez ve kalıcı olarak kaydedilmez. Bağlantılar dış sitelere (GitHub ve proje resmî belgeleri) yönlendirir; bu sitelerin kendi gizlilik politikaları uygulanır.</p></section>')

static_page('terms.html', 'Kullanım koşulları',
    'PickRepo kullanım koşulları: içerik “şekli haliyle” sağlanır, GitHub ile bağlantılı değildir.',
    '<section class="page-heading"><h1>Kullanım koşulları</h1><p>PickRepo bağımsız bir keşif aracıdır ve GitHub ile bağlantılı değildir.</p>'
    '<p>İçerik “şekli haliyle” sağlanır; rehberlerdeki kurulumlar bu sitede denenmemiştir ve resmî belgeler kaynak bağlantılarıyla verilmiştir. Siteyi kendi riskinizle kullanın.</p></section>')

static_page('404.html', 'Sayfa bulunamadı',
    'İstediğiniz sayfa bulunamadı. PickRepo ana sayfasına veya rehberler bölümüne dönün.',
    '<section class="page-heading"><h1>Sayfa bulunamadı</h1><p>İstediğiniz sayfa mevcut değil. Ana sayfaya veya rehberler bölümüne dönün.</p>'
    '<p><a href="/">Ana sayfaya dön ↗</a></p></section>')

# ---------- sitemap.xml ----------
urls = [page_path('/')]
for n in GUIDES:
    urls.append(page_path(f'/guide/{slug(n)}.html'))
urls += [page_path('/guides.html'), page_path('/sponsor.html'), page_path('/privacy.html'), page_path('/terms.html')]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{esc(u)}</loc></url>\n' for u in urls) + '</urlset>\n'
(SITE / 'sitemap.xml').write_text(sitemap, encoding='utf-8')

# ---------- robots.txt ----------
robots = f'''# PickRepo robots.txt
User-agent: *
Allow: /

Sitemap: {page_path("/sitemap.xml")}
'''
(SITE / 'robots.txt').write_text(robots, encoding='utf-8')

# ---------- llms.txt ----------
llms = f'''# PickRepo — llms.txt

PickRepo, GitHub’dan herkese açık depo bilgilerini okur ve statik sayfalarda gösteren bağımsız bir keşif aracıdır.

## Sayfalar
- / — Yükselenler, Popüler, Erken keşif ve kaynaklı rehber listeleri; proje arama, dil/konu filtreleri ve sıralama seçenekleri
- /guides.html — Kaynaklı rehberler listesi
{chr(10).join('- /guide/' + slug(n) + '.html — ' + (GUIDES[n]['tr'].get('what') or n) + ' rehberi (Türkçe/İngilizce)' for n in GUIDES)}
- /privacy.html — Gizlilik politikası
- /terms.html — Kullanım koşulları
- /sponsor.html — Sponsor bilgileri

## Keşif puanı
Puan, ziyaretçinin seçtiği ağırlıklara göre tarayıcıda hesaplanan bir sıralama yardımcısıdır. Arama uyumu, güncelleme tarihi, toplam yıldız/fork, proje yaşı ve GitHub proje bilgileri kullanılır. Kod çalıştırılmaz, güvenlik veya kod kalitesi değerlendirilmez. Tarihsel yıldız anlık görüntüleri tutulmadığı için yıldız kazanma hızı ölçülmez.

## Hakkında
Filtreler ve puan tercihleri tarayıcıda çalışır; hesaba, çereze veya sunucuya gönderilmez/kaydedilmez. PickRepo, GitHub ile bağlantılı değildir. Tüm içerik “şekli haliyle” sağlanır.
'''
(SITE / 'llms.txt').write_text(llms, encoding='utf-8')

print('site built:', len(items), 'repos', len(GUIDES), 'guides')
