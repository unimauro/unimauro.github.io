#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador estático multilenguaje de unimauro.github.io.
Fuente de la verdad del sitio. NO editar los index.html generados a mano.

Uso:  python3 build.py
Genera:  /index.html (es), /<loc>/index.html, sitemap.xml
Textos:  i18n/<loc>.json   (es.json es la base; faltantes -> fallback a es)
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://unimauro.github.io"

LOCALES = ["es", "en", "de", "fr", "zh", "hi", "pt", "ru"]
HTML_LANG = {"es": "es", "en": "en", "de": "de", "fr": "fr",
             "zh": "zh-Hans", "hi": "hi", "pt": "pt", "ru": "ru"}
OG_LOCALE = {"es": "es_PE", "en": "en_US", "de": "de_DE", "fr": "fr_FR",
             "zh": "zh_CN", "hi": "hi_IN", "pt": "pt_BR", "ru": "ru_RU"}
LANG_NAME = {"es": "Español", "en": "English", "de": "Deutsch", "fr": "Français",
             "zh": "中文", "hi": "हिन्दी", "pt": "Português", "ru": "Русский"}
LANG_FLAG = {"es": "🇪🇸", "en": "🇬🇧", "de": "🇩🇪", "fr": "🇫🇷",
             "zh": "🇨🇳", "hi": "🇮🇳", "pt": "🇧🇷", "ru": "🇷🇺"}


def url_for(loc):
    return "/" if loc == "es" else "/%s/" % loc


# ----- Estructura (no depende del idioma) -----
SEC_ICON = {"ia": "fa-robot", "peru": "fa-landmark", "mundo": "fa-globe",
            "ninos": "fa-child", "docencia": "fa-chalkboard-user",
            "oss": "fa-code-branch", "stack": "fa-laptop-code",
            "libros": "fa-book-open", "blog": "fa-feather-pointed", "videos": "fa-video"}

# key: (url, fa-icon, [badges], [tags])
PROJECTS = {
    "ia": [
        ("agentflow", "https://unimauro.github.io/agentflow-ai/", "fa-robot", ["new"], ["React", "TanStack", "Tailwind"]),
        ("suyay", "https://unimauro.github.io/agente-uni-demo/", "fa-robot", ["new"], ["AI Agent", "LLM", "Vanilla JS"]),
        ("modelo", "https://unimauro.github.io/modelo-predictivo-uni/", "fa-chart-line", ["new"], ["Machine Learning", "Reveal.js", "Chart.js"]),
    ],
    "peru": [
        ("observatorio", "https://unimauro.github.io/observatorio-fonafe/", "fa-building-columns", ["new"], ["React", "ECharts", "Python", "OCDS"]),
        ("inti", "https://unimauro.github.io/proyecto-inti/", "fa-sun", ["new"], ["Vanilla JS", "Chart.js", "Leaflet"]),
        ("petroperu", "https://unimauro.github.io/petroperu-analytics/", "fa-oil-well", ["new"], ["React", "TypeScript", "ECharts", "Python"]),
        ("congreso", "https://unimauro.github.io/congreso-abierto-peru/", "fa-landmark", ["new"], ["Python", "Playwright", "Chart.js"]),
        ("riesgos", "https://unimauro.github.io/unimaurox-peru-riesgos/", "fa-triangle-exclamation", ["new"], ["Vanilla JS", "Leaflet", "Chart.js"]),
        ("finanzas", "https://unimauro.github.io/unimaurox-peru-finanzas-publicas/", "fa-landmark", ["live"], ["React", "D3", "Recharts"]),
        ("colegios", "https://unimauro.github.io/unimaurox-colegios/", "fa-school", ["new"], ["JavaScript"]),
        ("oaf", "https://unimauro.github.io/unimaurox-separaciones-denuncias/", "fa-balance-scale", ["new"], ["HTML"]),
        ("salarios", "https://unimauro.github.io/salariosperu/", "fa-chart-line", ["live"], ["Python", "Plotly"]),
        ("transparencia", "https://unimauro.github.io/salariosperu/transparencia.html", "fa-circle-info", ["new"], ["HTML"]),
    ],
    "mundo": [
        ("vuelos", "https://unimauro.github.io/unimaurox-vuelos-internacionales/", "fa-plane", ["new"], ["Vanilla JS", "Leaflet", "Chart.js", "OpenSky"]),
    ],
    "ninos": [
        ("libelula", "https://unimauro.github.io/libelula/", "fa-bug", ["new"], ["HTML/CSS/JS", "Supabase", "GitHub Pages"]),
        ("panchita", "https://unimauro.github.io/panchita/", "fa-cat", ["new"], ["HTML/CSS/JS", "PWA", "GitHub Pages"]),
    ],
    "docencia": [
        ("tesis", "https://github.com/unimauro/ThesisUNIFIISTemplate", "fa-graduation-cap", [], ["LaTeX", "UNI-FIIS", "2009"]),
        ("biotec", "https://github.com/unimauro/analisis-datos-biotecnologia-python", "fa-dna", [], ["Python", "Colab", "Bioinformatics"]),
        ("sisop", "https://github.com/unimauro/SistemasOperativos", "fa-microchip", [], ["Java", "UNI-FIIS", "Slides"]),
        ("mecatronica", "https://github.com/unimauro/Curso-PostGrado-Mecatronica-2021", "fa-robot", [], ["Python", "Postgrade"]),
    ],
    "oss": [
        ("quantum", "https://github.com/unimauro/QuantumResources", "fa-atom", ["star30"], ["Jupyter"]),
        ("lifecompass", "https://github.com/unimauro/life-compass", "fa-heart", ["new"], ["React"]),
        ("springer", "https://github.com/unimauro/Springer202004Books", "fa-book", ["star4"], ["Python"]),
    ],
    "blog": [
        ("blog", "https://unimauro.blogspot.com/", "fa-blog", [], ["Blog"]),
    ],
}
SECTION_ORDER = ["ia", "peru", "mundo", "ninos", "docencia", "oss", "blog"]

STACK = ["Python", "Go", "TypeScript", "Ruby", "Rust", "C++", "Java", "React",
         "Node.js", "Docker", "PostgreSQL", "MongoDB", "GenAI", "LLMs", "ML/AI", "DevOps", "Cloud"]

BOOKS = [
    ("fa-heart", "De Libertad, Esperanza y Amor", "https://leanpub.com/de_libertad_esperanza_y_amor"),
    ("fa-microchip", "Evaluación de la OLPC con Ingeniería de Usabilidad", "https://leanpub.com/evaluacion_de_la_olpc_con_ingeniera_de_usabilidad"),
]

VIDEOS = ["mHX1f-W-5as", "8Kf0i_j_yeo", "lcteoKvYcCY", "jBjjqzg6uJM"]

SAMEAS = [
    "https://github.com/unimauro",
    "https://www.linkedin.com/in/carloscardenasf/",
    "https://x.com/unimauro",
    "https://www.youtube.com/channel/UCUDcs3s8Src2jP3-xa-aV1w",
    "https://platzi.com/p/unimauro",
    "https://unimauro.blogspot.com/",
    "https://scholar.google.com/citations?hl=es&user=-bBexuUAAAAJ",
    "https://cardenas.pe/",
]

KEYWORDS = ("Carlos Cardenas, Carlos Mauro Cardenas, Carlos Cardenas Fernandez, unimauro, "
            "Carlos Cardenas Peru, ingeniero AI, GenAI engineer Peru, data scientist Peru, "
            "Lima developer, SalariosPeru, quantum computing Peru, AI agents Peru, "
            "docente UNI FIIS, profesor universitario Peru, tesis UNI FIIS, "
            "blog Carlos Cardenas, unimauro blogspot, Google Scholar Carlos Cardenas")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_strings():
    es = json.load(open(os.path.join(ROOT, "i18n", "es.json"), encoding="utf-8"))
    out = {}
    for loc in LOCALES:
        p = os.path.join(ROOT, "i18n", "%s.json" % loc)
        d = dict(es)
        if os.path.exists(p):
            d.update({k: v for k, v in json.load(open(p, encoding="utf-8")).items() if v})
        out[loc] = d
    return out


def creed_html(s):
    return re.sub(r"\*(.+?)\*", r'<span class="accent">\1</span>', esc(s))


def badge_html(tok, t):
    if tok == "new":
        return '<span class="project-badge new">✨ %s</span>' % esc(t["badge_new"])
    if tok == "live":
        return '<span class="project-badge new">✨ %s</span>' % esc(t["badge_live"])
    if tok == "star30":
        return '<span class="project-badge star">⭐ 30</span>'
    if tok == "star4":
        return '<span class="project-badge star">⭐ 4</span>'
    return ""


def project_card(p, t):
    key, url, icon, badges, tags = p
    meta = "".join(badge_html(b, t) for b in badges)
    meta += "".join('<span class="project-badge">%s</span>' % esc(x) for x in tags)
    return ('''            <a href="%s" class="project" target="_blank" rel="noopener">
                <div class="project-title"><i class="fas %s"></i> %s</div>
                <div class="project-desc">%s</div>
                <div class="project-meta">%s</div>
            </a>
''' % (url, icon, esc(t["t_" + key]), esc(t["d_" + key]), meta))


def section_html(sid, t):
    cards = "".join(project_card(p, t) for p in PROJECTS[sid])
    sub = ""
    if t.get("sec_%s_s" % sid):
        sub = '        <p class="sec-sub">%s</p>\n' % esc(t["sec_%s_s" % sid])
    return ('''        <h2 id="%s"><i class="fas %s"></i> %s</h2>
%s        <div class="projects">
%s        </div>
''' % (sid, SEC_ICON[sid], esc(t["sec_%s_t" % sid]), sub, cards))


def lang_menu(cur):
    items = []
    for loc in LOCALES:
        aria = ' aria-current="true"' if loc == cur else ''
        items.append('<a href="%s" data-lang="%s" hreflang="%s"%s>%s %s</a>'
                     % (url_for(loc), loc, HTML_LANG[loc], aria, LANG_FLAG[loc], esc(LANG_NAME[loc])))
    return "\n                    ".join(items)


def hreflang_links(cur):
    out = []
    for loc in LOCALES:
        out.append('    <link rel="alternate" hreflang="%s" href="%s%s">'
                   % (HTML_LANG[loc], BASE, url_for(loc)))
    out.append('    <link rel="alternate" hreflang="x-default" href="%s/">' % BASE)
    return "\n".join(out)


def og_locale_alts(cur):
    return "\n".join('    <meta property="og:locale:alternate" content="%s">' % OG_LOCALE[l]
                     for l in LOCALES if l != cur)


def schema_json(loc, t):
    d = {
        "@context": "https://schema.org", "@type": "Person",
        "name": "Carlos Mauro Cárdenas Fernandez",
        "alternateName": ["Carlos Cardenas", "unimauro", "Carlos Mauro Cárdenas"],
        "url": BASE + url_for(loc),
        "image": "https://github.com/unimauro.png",
        "jobTitle": "Engineer · AI · Data",
        "description": t["meta_desc"],
        "slogan": "Creo en el amor de los seres humanos",
        "inLanguage": HTML_LANG[loc],
        "knowsAbout": ["GenAI", "AI Agents", "Machine Learning", "Quantum Computing",
                       "Data Science", "Blockchain", "DevOps", "Cloud Computing",
                       "Python", "TypeScript", "Rust", "Go", "Higher education", "Operating Systems"],
        "knowsLanguage": ["es", "en"],
        "alumniOf": {"@type": "CollegeOrUniversity",
                     "name": "Universidad Nacional de Ingeniería (UNI) — Facultad de Ingeniería Industrial y de Sistemas",
                     "sameAs": "https://www.uni.edu.pe/"},
        "address": {"@type": "PostalAddress", "addressLocality": "Lima", "addressCountry": "PE"},
        "sameAs": SAMEAS,
        "email": "mailto:carlos@cardenas.pe",
        "worksFor": {"@type": "Organization", "name": "Independent / Open Source"},
    }
    return json.dumps(d, ensure_ascii=False, indent=2)


STYLE = """    <style>
        :root{
            --bg1:#1a2332; --bg2:#2c3e50;
            --text:#ffffff; --heading:#ecf0f1; --muted:#95a5a6; --soft:#b0bec5; --faint:#7f8c8d;
            --surface:rgba(255,255,255,0.05); --surface-h:rgba(255,255,255,0.09);
            --border:rgba(255,255,255,0.08); --border-h:rgba(255,255,255,0.18);
            --chip:rgba(255,255,255,0.06); --navbg:rgba(26,35,50,0.92);
            --btnbg:rgba(255,255,255,0.08); --btnborder:rgba(255,255,255,0.12); --btnbg-h:rgba(255,255,255,0.14);
            --badge-bg:rgba(52,152,219,0.18); --badge-tx:#5fb8ff;
            --badge-new-bg:rgba(46,204,113,0.18); --badge-new-tx:#2ecc71;
            --badge-star-bg:rgba(241,196,15,0.18); --badge-star-tx:#f1c40f;
            --accent:#3498db; --accent2:#9b59b6; --link:#5fb8ff;
            --avatar-border:rgba(255,255,255,0.15); --shadow:rgba(0,0,0,0.3); --skel:rgba(255,255,255,0.04);
        }
        [data-theme="light"]{
            --bg1:#eef2f7; --bg2:#dbe4f0;
            --text:#1f2d3d; --heading:#16222e; --muted:#5b6b7a; --soft:#43545f; --faint:#6b7a88;
            --surface:rgba(0,0,0,0.04); --surface-h:rgba(0,0,0,0.07);
            --border:rgba(0,0,0,0.10); --border-h:rgba(0,0,0,0.20);
            --chip:rgba(0,0,0,0.05); --navbg:rgba(255,255,255,0.92);
            --btnbg:rgba(0,0,0,0.05); --btnborder:rgba(0,0,0,0.12); --btnbg-h:rgba(0,0,0,0.09);
            --badge-bg:rgba(41,128,185,0.14); --badge-tx:#1f6fa8;
            --badge-new-bg:rgba(39,174,96,0.16); --badge-new-tx:#1e8e4f;
            --badge-star-bg:rgba(214,160,8,0.18); --badge-star-tx:#8a6b00;
            --accent:#2980b9; --accent2:#8e44ad; --link:#1f6fa8;
            --avatar-border:rgba(0,0,0,0.12); --shadow:rgba(0,0,0,0.15); --skel:rgba(0,0,0,0.04);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
            color: var(--text); min-height: 100vh; line-height: 1.6; padding: 2rem 1rem;
            transition: background 0.3s ease, color 0.3s ease;
        }
        .container { max-width: 880px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 3rem; padding-top: 2rem; }
        .avatar {
            width: 130px; height: 130px; border-radius: 50%; margin: 0 auto 1.2rem;
            box-shadow: 0 10px 30px var(--shadow); border: 4px solid var(--avatar-border);
            object-fit: cover; display: block; transition: transform 0.3s ease, border-color 0.3s ease;
        }
        .avatar:hover { transform: scale(1.04); border-color: rgba(52,152,219,0.6); }
        .gh-stats { margin: 1.2rem auto 0; max-width: 720px; display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
        .gh-stats img { width: 100%; border-radius: 10px; background: var(--skel); border: 1px solid var(--border); min-height: 80px; }
        .gh-stats img.broken { display: none; }
        @media (max-width: 600px) { .gh-stats { grid-template-columns: 1fr; max-width: 360px; } }
        h1 { font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0.4rem; color: var(--text); }
        .tagline { color: var(--muted); font-size: 1.05rem; margin-bottom: 0.6rem; font-weight: 400; }
        .creed { font-size: 1.08rem; font-weight: 600; color: var(--heading); margin: 0.2rem auto 1.4rem; max-width: 560px; line-height: 1.5; }
        .creed .accent, .accent { background: linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
        .location { display: inline-flex; align-items: center; gap: 0.4rem; background: var(--chip); padding: 0.4rem 0.9rem; border-radius: 20px; font-size: 0.82rem; color: var(--soft); margin-bottom: 1.5rem; }
        .socials { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; }
        .social-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.55rem 1rem; background: var(--btnbg); border: 1px solid var(--btnborder); border-radius: 8px; color: var(--text); text-decoration: none; font-size: 0.88rem; font-weight: 500; transition: all 0.2s ease; }
        .social-btn:hover { background: var(--btnbg-h); transform: translateY(-2px); box-shadow: 0 6px 18px var(--shadow); }
        .social-btn.linkedin:hover { border-color: #0077B5; }
        .social-btn.twitter:hover { border-color: #1da1f2; }
        .social-btn.github:hover { border-color: var(--text); }
        .social-btn.email:hover { border-color: #ea4335; }
        .social-btn.web:hover { border-color: #3498db; }
        .social-btn.youtube:hover { border-color: #ff0000; }
        .social-btn.platzi:hover { border-color: #98ca3f; }
        .social-btn.blog:hover { border-color: #ff8000; }
        .social-btn.scholar:hover { border-color: #4285f4; }

        .topnav { position: sticky; top: 0.6rem; z-index: 30; margin-bottom: 1.5rem; padding: 0.5rem; background: var(--navbg); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); border: 1px solid var(--border); border-radius: 14px; box-shadow: 0 8px 24px var(--shadow); display: flex; gap: 0.5rem; align-items: center; }
        .topnav .inner { display: flex; gap: 0.45rem; overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none; flex: 1; }
        .topnav .inner::-webkit-scrollbar { display: none; }
        .topnav a.navlink { flex-shrink: 0; white-space: nowrap; text-decoration: none; color: var(--soft); font-size: 0.85rem; font-weight: 600; padding: 0.45rem 0.85rem; border-radius: 20px; background: var(--surface); border: 1px solid transparent; transition: all 0.2s ease; }
        .topnav a.navlink:hover { background: var(--surface-h); color: var(--text); transform: translateY(-1px); }
        .topnav a.navlink.activo { background: linear-gradient(90deg,var(--accent),var(--accent2)); color: #fff; }
        .ctrl { display: flex; gap: 0.4rem; align-items: center; flex-shrink: 0; }
        .iconbtn { width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.1rem; line-height: 1; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; color: var(--text); cursor: pointer; transition: all 0.2s ease; }
        .iconbtn:hover { background: var(--surface-h); transform: translateY(-1px); }
        .langpick { position: relative; }
        .langpick summary { list-style: none; cursor: pointer; display: inline-flex; align-items: center; gap: 0.35rem; height: 38px; padding: 0 0.7rem; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; color: var(--text); font-size: 0.85rem; font-weight: 600; white-space: nowrap; }
        .langpick summary::-webkit-details-marker { display: none; }
        .langpick summary:hover { background: var(--surface-h); }
        .langpick summary i { color: var(--accent); }
        .langmenu { position: absolute; right: 0; top: 46px; min-width: 170px; display: flex; flex-direction: column; gap: 0.15rem; padding: 0.4rem; background: var(--navbg); -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 12px 30px var(--shadow); z-index: 50; }
        .langmenu a { text-decoration: none; color: var(--soft); font-size: 0.9rem; font-weight: 600; padding: 0.5rem 0.7rem; border-radius: 8px; transition: all 0.15s ease; }
        .langmenu a:hover { background: var(--surface-h); color: var(--text); }
        .langmenu a[aria-current="true"] { background: linear-gradient(90deg,var(--accent),var(--accent2)); color: #fff; }
        @media (max-width: 600px) { .langpick .lp-name { display: none; } }

        h2 { font-size: 1.3rem; font-weight: 700; margin: 2.5rem 0 1rem; display: flex; align-items: center; gap: 0.6rem; color: var(--heading); }
        h2 i { color: var(--accent); font-size: 1.1rem; }
        h2[id] { scroll-margin-top: 80px; }
        .sec-sub { color: var(--faint); font-size: 0.85rem; margin: -0.6rem 0 1rem; }
        .projects { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
        .project { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.3rem; text-decoration: none; color: inherit; transition: all 0.25s ease; display: flex; flex-direction: column; gap: 0.5rem; position: relative; overflow: hidden; }
        .project::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2)); opacity: 0; transition: opacity 0.25s ease; }
        .project:hover { background: var(--surface-h); border-color: var(--border-h); transform: translateY(-3px); box-shadow: 0 12px 28px var(--shadow); }
        .project:hover::before { opacity: 1; }
        .project-title { font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; color: var(--text); }
        .project-title i { color: var(--accent); font-size: 0.9rem; }
        .project-desc { font-size: 0.85rem; color: var(--soft); flex: 1; }
        .project-meta { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.3rem; }
        .project-badge { background: var(--badge-bg); color: var(--badge-tx); padding: 0.18rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }
        .project-badge.new { background: var(--badge-new-bg); color: var(--badge-new-tx); }
        .project-badge.star { background: var(--badge-star-bg); color: var(--badge-star-tx); }
        .books { display: grid; gap: 0.6rem; }
        .book { background: var(--surface); border-left: 3px solid var(--accent2); padding: 0.7rem 1rem; border-radius: 6px; text-decoration: none; color: inherit; transition: all 0.2s ease; font-size: 0.92rem; display: flex; align-items: center; gap: 0.6rem; }
        .book:hover { background: var(--surface-h); transform: translateX(3px); }
        .book i { color: var(--accent2); }
        .stack { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.8rem; }
        .stack span { background: var(--chip); padding: 0.3rem 0.7rem; border-radius: 6px; font-size: 0.78rem; color: var(--soft); }
        .video-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.9rem; margin: 0.5rem 0 1.3rem; }
        .video-grid .vid { position: relative; aspect-ratio: 16/9; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
        .video-grid .vid iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
        footer { text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--faint); font-size: 0.82rem; }
        footer a { color: var(--link); text-decoration: none; }
        footer a:hover { text-decoration: underline; }
        @media (max-width: 600px) { h1 { font-size: 1.8rem; } .avatar { width: 90px; height: 90px; } body { padding: 1rem 0.8rem; } .social-btn { padding: 0.5rem 0.8rem; font-size: 0.8rem; } }
    </style>"""


def render(loc, S):
    t = S[loc]
    nav = "\n                ".join(
        '<a class="navlink" href="#%s">%s</a>' % (sid, esc(t["nav_%s" % sid]))
        for sid in ["ia", "peru", "mundo", "ninos", "docencia", "oss", "stack", "libros", "blog", "videos"])
    sections = "".join(section_html(sid, t) for sid in SECTION_ORDER)
    stack = "".join("<span>%s</span>" % esc(x) for x in STACK)
    books = "".join('''            <a href="%s" class="book" target="_blank" rel="noopener"><i class="fas %s"></i> %s</a>
''' % (u, ic, esc(name)) for ic, name, u in BOOKS)
    videos = "".join('''            <div class="vid"><iframe src="https://www.youtube.com/embed/%s" title="Video — Carlos Mauro Cárdenas" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
''' % v for v in VIDEOS)

    # script de autodetección sólo en la raíz (es)
    autodetect = ""
    if loc == "es":
        autodetect = """    <script>
    (function(){
      try{
        var supported=['es','en','de','fr','zh','hi','pt','ru'];
        var choice=null; try{ choice=localStorage.getItem('lang'); }catch(e){}
        function pick(){
          if(choice && supported.indexOf(choice)>=0) return choice;
          var langs=(navigator.languages&&navigator.languages.length)?navigator.languages:[navigator.language||'es'];
          for(var i=0;i<langs.length;i++){
            var base=(langs[i]||'').toLowerCase().split('-')[0];
            if(base==='zh') return 'zh';
            if(supported.indexOf(base)>=0) return base;
          }
          return 'en';
        }
        var target=pick();
        if(target!=='es'){ location.replace('/'+target+'/'); }
      }catch(e){}
    })();
    </script>
"""

    return """<!DOCTYPE html>
<html lang="{htmllang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="icon" type="image/png" href="https://github.com/unimauro.png">
    <link rel="apple-touch-icon" href="https://github.com/unimauro.png">
    <meta name="description" content="{desc}">
    <meta name="author" content="Carlos Mauro Cárdenas Fernandez">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="{base}{url}">

    <!-- Tema (evita parpadeo) -->
    <script>
    (function(){{
      try{{
        var th=localStorage.getItem('theme');
        if(!th){{ th = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'; }}
        document.documentElement.setAttribute('data-theme', th);
      }}catch(e){{ document.documentElement.setAttribute('data-theme','dark'); }}
    }})();
    </script>
{autodetect}
    <!-- Idiomas alternativos (hreflang) -->
{hreflang}

    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="googlebot" content="index, follow">

    <meta property="og:title" content="{ogtitle}">
    <meta property="og:description" content="{ogdesc}">
    <meta property="og:url" content="{base}{url}">
    <meta property="og:type" content="profile">
    <meta property="og:image" content="https://github.com/unimauro.png">
    <meta property="og:image:alt" content="Carlos Mauro Cárdenas">
    <meta property="og:locale" content="{oglocale}">
{oglocalealt}
    <meta property="profile:first_name" content="Carlos Mauro">
    <meta property="profile:last_name" content="Cárdenas Fernandez">
    <meta property="profile:username" content="unimauro">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@unimauro">
    <meta name="twitter:creator" content="@unimauro">
    <meta name="twitter:title" content="{ogtitle}">
    <meta name="twitter:description" content="{ogdesc}">
    <meta name="twitter:image" content="https://github.com/unimauro.png">

    <script type="application/ld+json">
{schema}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <script async src="https://www.googletagmanager.com/gtag/js?id=G-170L71ZZK1"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-170L71ZZK1');
    </script>
{style}
</head>
<body>
    <div class="container">
        <header>
            <img src="https://github.com/unimauro.png" alt="Carlos Mauro Cárdenas" class="avatar" loading="eager" />
            <h1>Carlos Mauro Cárdenas</h1>
            <p class="tagline">{tagline}</p>
            <p class="creed">{creed}</p>
            <div class="location"><i class="fas fa-map-marker-alt"></i> {location}</div>
            <div class="socials">
                <a href="https://github.com/unimauro" class="social-btn github" target="_blank" rel="noopener"><i class="fab fa-github"></i> GitHub</a>
                <a href="https://www.linkedin.com/in/carloscardenasf/" class="social-btn linkedin" target="_blank" rel="noopener"><i class="fab fa-linkedin"></i> LinkedIn</a>
                <a href="https://x.com/unimauro" class="social-btn twitter" target="_blank" rel="noopener"><i class="fab fa-x-twitter"></i> Twitter / X</a>
                <a href="https://www.youtube.com/channel/UCUDcs3s8Src2jP3-xa-aV1w" class="social-btn youtube" target="_blank" rel="noopener"><i class="fab fa-youtube"></i> YouTube</a>
                <a href="mailto:carlos@cardenas.pe" class="social-btn email"><i class="fas fa-envelope"></i> {email}</a>
                <a href="https://platzi.com/p/unimauro" class="social-btn platzi" target="_blank" rel="noopener"><i class="fas fa-graduation-cap"></i> Platzi</a>
                <a href="https://unimauro.blogspot.com/" class="social-btn blog" target="_blank" rel="noopener"><i class="fas fa-feather-pointed"></i> Blog</a>
                <a href="https://scholar.google.com/citations?hl=es&user=-bBexuUAAAAJ" class="social-btn scholar" target="_blank" rel="noopener"><i class="fas fa-graduation-cap"></i> Scholar</a>
                <a href="https://cardenas.pe/" class="social-btn web" target="_blank" rel="noopener"><i class="fas fa-globe"></i> cardenas.pe</a>
            </div>
            <div class="gh-stats">
                <img src="https://github-readme-stats.vercel.app/api?username=unimauro&show_icons=true&include_all_commits=true&count_private=true&theme=tokyonight&hide_border=true&bg_color=00000080" alt="{ghstats}" loading="lazy" onerror="this.classList.add('broken')" />
                <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=unimauro&layout=compact&theme=tokyonight&hide_border=true&count_private=true&bg_color=00000080" alt="{ghlangs}" loading="lazy" onerror="this.classList.add('broken')" />
            </div>
        </header>

        <nav class="topnav" aria-label="{navaria}">
            <div class="inner">
                {nav}
            </div>
            <div class="ctrl">
                <button class="iconbtn theme-toggle" type="button" aria-label="{themelabel}" title="{themelabel}">☀️</button>
                <details class="langpick">
                    <summary aria-label="{langlabel}" title="{langlabel}"><i class="fas fa-globe"></i> {curflag} <span class="lp-name">{curname}</span></summary>
                    <div class="langmenu">
                    {langmenu}
                    </div>
                </details>
            </div>
        </nav>

{sections}
        <h2 id="stack"><i class="fas fa-laptop-code"></i> {stack_t}</h2>
        <div class="stack">{stack}</div>

        <h2 id="libros"><i class="fas fa-book-open"></i> {libros_t}</h2>
        <div class="books">
{books}        </div>

        <h2 id="videos"><i class="fas fa-video"></i> {videos_t}</h2>
        <div class="video-grid">
{videos}        </div>
        <div class="socials">
            <a href="https://www.youtube.com/channel/UCUDcs3s8Src2jP3-xa-aV1w" class="social-btn youtube" target="_blank" rel="noopener"><i class="fab fa-youtube"></i> {ytchannel}</a>
            <a href="https://www.linkedin.com/in/carloscardenasf/" class="social-btn linkedin" target="_blank" rel="noopener"><i class="fab fa-linkedin"></i> LinkedIn</a>
            <a href="https://x.com/unimauro" class="social-btn twitter" target="_blank" rel="noopener"><i class="fab fa-x-twitter"></i> Twitter / X</a>
            <a href="https://platzi.com/p/unimauro" class="social-btn platzi" target="_blank" rel="noopener"><i class="fas fa-graduation-cap"></i> Platzi</a>
            <a href="https://unimauro.blogspot.com/" class="social-btn blog" target="_blank" rel="noopener"><i class="fas fa-feather-pointed"></i> Blog</a>
            <a href="https://scholar.google.com/citations?hl=es&user=-bBexuUAAAAJ" class="social-btn scholar" target="_blank" rel="noopener"><i class="fas fa-graduation-cap"></i> Scholar</a>
        </div>

        <footer><p>{footer} <a href="https://github.com/unimauro/unimauro.github.io">GitHub</a></p></footer>
    </div>
    <script>
      var tb=document.querySelector('.theme-toggle');
      function themeIcon(){{var th=document.documentElement.getAttribute('data-theme'); if(tb){{tb.textContent= th==='light'?'🌙':'☀️'; tb.setAttribute('aria-pressed', th==='light');}}}}
      themeIcon();
      if(tb) tb.addEventListener('click',function(){{var cur=document.documentElement.getAttribute('data-theme'); var nx=cur==='light'?'dark':'light'; document.documentElement.setAttribute('data-theme',nx); try{{localStorage.setItem('theme',nx);}}catch(e){{}} themeIcon();}});
      document.querySelectorAll('.langmenu a').forEach(function(a){{a.addEventListener('click',function(){{try{{localStorage.setItem('lang', a.getAttribute('data-lang'));}}catch(e){{}}}});}});
      var lp=document.querySelector('.langpick');
      document.addEventListener('click',function(e){{ if(lp && lp.open && !lp.contains(e.target)) lp.open=false; }});
      var navLinks = Array.from(document.querySelectorAll('.topnav a.navlink'));
      var secs = navLinks.map(function(a){{return document.getElementById(a.getAttribute('href').slice(1));}}).filter(Boolean);
      var io = new IntersectionObserver(function(es){{ es.forEach(function(e){{ if(e.isIntersecting){{ var id=e.target.id; navLinks.forEach(function(a){{a.classList.toggle('activo', a.getAttribute('href')==='#'+id);}}); }} }}); }},{{rootMargin:'-40% 0px -55% 0px'}});
      secs.forEach(function(s){{io.observe(s);}});
    </script>
</body>
</html>
""".format(
        htmllang=HTML_LANG[loc], title=esc(t["meta_title"]), desc=esc(t["meta_desc"]),
        keywords=KEYWORDS, base=BASE, url=url_for(loc), autodetect=autodetect,
        hreflang=hreflang_links(loc), ogtitle=esc(t["og_title"]), ogdesc=esc(t["og_desc"]),
        oglocale=OG_LOCALE[loc], oglocalealt=og_locale_alts(loc), schema=schema_json(loc, t),
        style=STYLE, tagline=esc(t["tagline"]), creed=creed_html(t["creed"]),
        location=esc(t["location"]), email=esc(t["ui_email"]), ghstats=esc(t["gh_stats_alt"]),
        ghlangs=esc(t["gh_langs_alt"]), navaria=esc(t["ui_lang"]), nav=nav,
        themelabel=esc(t["ui_theme_toggle"]), langlabel=esc(t["ui_lang"]),
        curflag=LANG_FLAG[loc], curname=esc(LANG_NAME[loc]), langmenu=lang_menu(loc),
        sections=sections, stack_t=esc(t["sec_stack_t"]), stack=stack,
        libros_t=esc(t["sec_libros_t"]), books=books, videos_t=esc(t["sec_videos_t"]),
        videos=videos, ytchannel=esc(t["ui_yt_channel"]),
        footer=esc(t["footer_built"]),
    )


def write_sitemap():
    home_alts = "\n".join(
        '        <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (HTML_LANG[l], BASE, url_for(l))
        for l in LOCALES) + '\n        <xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>' % BASE
    urls = []
    for loc in LOCALES:
        urls.append('''    <url>
        <loc>%s%s</loc>
%s
        <lastmod>2026-06-07</lastmod>
        <changefreq>weekly</changefreq>
        <priority>%s</priority>
    </url>''' % (BASE, url_for(loc), home_alts, "1.0" if loc == "es" else "0.9"))
    # páginas de proyectos (no traducidas)
    project_pages = [
        "/salariosperu/", "/proyecto-inti/", "/petroperu-analytics/", "/congreso-abierto-peru/",
        "/unimaurox-peru-riesgos/", "/unimaurox-peru-finanzas-publicas/", "/unimaurox-colegios/",
        "/unimaurox-separaciones-denuncias/", "/unimaurox-vuelos-internacionales/",
        "/agentflow-ai/", "/agente-uni-demo/", "/modelo-predictivo-uni/", "/libelula/", "/panchita/",
    ]
    for p in project_pages:
        urls.append('''    <url>
        <loc>%s%s</loc>
        <lastmod>2026-06-07</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>''' % (BASE, p))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)


def main():
    S = load_strings()
    for loc in LOCALES:
        html = render(loc, S)
        if loc == "es":
            out = os.path.join(ROOT, "index.html")
        else:
            d = os.path.join(ROOT, loc)
            os.makedirs(d, exist_ok=True)
            out = os.path.join(d, "index.html")
        open(out, "w", encoding="utf-8").write(html)
        print("wrote", out)
    write_sitemap()
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
