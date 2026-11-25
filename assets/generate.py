#!/usr/bin/env python3
"""Generate the SVG assets used in the profile README.

Run from the repository root:  python3 assets/generate.py

Content and palette mirror https://mik3sw.github.io (neutrals + one "signal"
accent). Every asset is written in a light and a dark variant; the README
picks one with <picture> and prefers-color-scheme.

Sources in assets/src: Open Peeps illustration (CC0), project logos and site
screenshots from the website repo, Simple Icons (CC0) in assets/src/icons.
"""
import base64
import io
import re
import textwrap
from pathlib import Path

OUT = Path(__file__).parent
SRC = OUT / "src"

# Hex conversions of the oklch tokens in the website's app/globals.css.
THEMES = {
    "light": {
        "bg": "#f9fafb", "surface": "#eef0f2", "line": "#dadce0", "fg": "#121417",
        "muted": "#585b61", "subtle": "#9a9da3", "signal": "#3d5fef", "signal_fg": "#f9fafb",
        "panel": "#dee8ff", "primary": "#121417", "primary_fg": "#f9fafb",
    },
    "dark": {
        "bg": "#0d0e11", "surface": "#17181b", "line": "#292b2f", "fg": "#eff0f2",
        "muted": "#a2a5aa", "subtle": "#5c5f65", "signal": "#7896ff", "signal_fg": "#080d1a",
        "panel": "#bccaec", "primary": "#eff0f2", "primary_fg": "#0d0e11",
    },
}

SANS = "'Schibsted Grotesk', Geist, Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
STYLE = f"<style>.s{{font-family:{SANS}}}.m{{font-family:{MONO}}}</style>"

# Lucide icons (ISC), 24x24, stroke based.
LUCIDE = {
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "arrow": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "pointer": '<path d="M14 4.1 12 6"/><path d="m5.1 8-2.9-.8"/><path d="m6 12-1.9 2"/><path d="M7.2 2.2 8 5.1"/><path d="M9.037 9.69a.498.498 0 0 1 .653-.653l11 4.5a.5.5 0 0 1-.074.949l-4.349 1.041a1 1 0 0 0-.74.739l-1.04 4.35a.5.5 0 0 1-.95.074z"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/>',
    "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "cap": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def lucide(name, x, y, size, color, width=2):
    body = LUCIDE[name].replace("currentColor", color)
    return (f'<g transform="translate({x} {y}) scale({size / 24})" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{body}</g>')


def simple(name, x, y, size, color):
    d = re.search(r'<path d="([^"]+)"', (SRC / "icons" / f"{name}.svg").read_text()).group(1)
    return f'<path transform="translate({x} {y}) scale({size / 24})" fill="{color}" d="{d}"/>'


def inline_svg(path, x, y, w, h, align="xMidYMid meet"):
    """Nest an external SVG file so the result stays a single self-contained image."""
    text = re.sub(r"<\?xml[^>]*\?>", "", path.read_text())
    m = re.search(r"<svg([^>]*)>(.*)</svg>", text, re.S)
    attrs, inner = m.group(1), m.group(2)
    vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
    extra = ""
    for a in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"):
        v = re.search(rf'\s{a}="([^"]+)"', attrs)
        if v:
            extra += f' {a}="{v.group(1)}"'
    # Prefix ids/classes so nested documents can't collide.
    p = path.stem.replace("-", "")
    inner = re.sub(r'\b(cls-\d+)', rf"{p}-\1", inner)
    inner = re.sub(r'id="([^"]+)"', rf'id="{p}-\1"', inner)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="{align}"{extra}>{inner}</svg>')


def image_data(path, width):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=72, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{STYLE}{body}</svg>\n')


def card(x, y, w, h, t, fill=None, rx=12):
    return (f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{rx}" '
            f'fill="{fill or t["surface"]}" stroke="{t["line"]}"/>')


def lines(text, x, y, width_chars, size, color, lh, cls="s"):
    out = []
    for i, ln in enumerate(textwrap.wrap(text, width_chars)):
        out.append(f'<text x="{x}" y="{y + i * lh}" class="{cls}" font-size="{size}" fill="{color}">{esc(ln)}</text>')
    return "".join(out), len(textwrap.wrap(text, width_chars))


def tags_row(tags, x, y, t):
    return (f'<text x="{x}" y="{y}" class="m" font-size="11.5" fill="{t["muted"]}" xml:space="preserve">'
            + esc("   ".join(tags)) + "</text>")


# --------------------------------------------------------------------------- hero
ROLES = ["AI pipelines.", "desktop apps.", "web platforms."]


def header(t):
    w, h = 840, 340
    dur = 7.5
    words = []
    for i, role in enumerate(ROLES):
        words.append(
            f'<text x="40" y="296" class="s" font-size="17" xml:space="preserve" opacity="0">'
            f'<tspan fill-opacity="0">real products. I build </tspan><tspan fill="{t["signal"]}" font-weight="600">{role}</tspan>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.04;.3;.333;1" '
            f'dur="{dur}s" begin="{i * dur / 3}s" repeatCount="indefinite"/></text>'
        )
    body = f"""
<style>
  .rise{{animation:rise .9s cubic-bezier(.16,1,.3,1) both}}
  .d1{{animation-delay:.08s}}.d2{{animation-delay:.16s}}.d3{{animation-delay:.24s}}.d4{{animation-delay:.32s}}
  @keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
  .peep{{animation:float 6s ease-in-out infinite}}
  @keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
</style>
<defs>
  <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{t['line']}" stroke-opacity=".55"/></pattern>
  <radialGradient id="fade" cx="15%" cy="0%" r="85%"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="mask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
  <clipPath id="card"><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16"/></clipPath>
  <clipPath id="panel"><rect x="520" y="40" width="280" height="260" rx="14"/></clipPath>
</defs>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="{t['bg']}" stroke="{t['line']}"/>
<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="url(#grid)" mask="url(#mask)"/></g>

<g class="rise">
  <rect x="40.5" y="40.5" width="206" height="27" rx="13.5" fill="{t['surface']}" stroke="{t['line']}"/>
  <circle cx="57" cy="54" r="3.5" fill="{t['signal']}"/>
  <circle cx="57" cy="54" r="3.5" fill="none" stroke="{t['signal']}">
    <animate attributeName="r" values="3.5;9" dur="2.2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".9;0" dur="2.2s" repeatCount="indefinite"/>
  </circle>
  {lucide("pin", 70, 47, 13, t['muted'])}
  <text x="88" y="58.5" class="s" font-size="12.5" font-weight="500" fill="{t['fg']}">Milan · Full-stack &amp; AI</text>
</g>
<text x="40" y="112" class="s rise d1" font-size="19" fill="{t['muted']}">Hi, I'm Mike.</text>
<g class="rise d2">
  <text x="37" y="170" class="s" font-size="56" font-weight="600" letter-spacing="-2.4" fill="{t['fg']}">AI Software</text>
  <text x="37" y="228" class="s" font-size="56" font-weight="600" letter-spacing="-2.4" fill="{t['signal']}">Engineer.</text>
</g>
<g class="rise d3">
  <text x="40" y="272" class="s" font-size="17" fill="{t['muted']}">Full-stack developer in Milan, wiring AI into</text>
  <text x="40" y="296" class="s" font-size="17" fill="{t['muted']}">real products. I build</text>
  {''.join(words)}
</g>

<g class="rise d4">
  <rect x="520" y="40" width="280" height="260" rx="14" fill="{t['panel']}"/>
  <g clip-path="url(#panel)">
    <g class="peep">{inline_svg(SRC / 'peep-hero.svg', 548, 58, 224, 296, 'xMidYMin meet')}</g>
  </g>
  <rect x="520.5" y="40.5" width="279" height="259" rx="13.5" fill="none" stroke="{t['line']}"/>
</g>
"""
    return svg(w, h, body, "Hi, I'm Mike. AI Software Engineer. Full-stack developer in Milan, wiring AI into real products.")


# --------------------------------------------------------------------------- buttons
def button(t, label, icon, primary=False):
    w, h = int(len(label) * 7.7) + 64, 40
    fill, fg = (t["primary"], t["primary_fg"]) if primary else (t["bg"], t["fg"])
    stroke = t["primary"] if primary else t["line"]
    ic = lucide(icon, 18, 12, 16, fg) if icon in LUCIDE else simple(icon, 18, 12, 16, fg)
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{h / 2 - .5}" fill="{fill}" stroke="{stroke}"/>'
            + ic + f'<text x="42" y="25" class="s" font-size="14" font-weight="500" fill="{fg}">{esc(label)}</text>')
    return svg(w, h, body, label)


def section(t, label, index):
    w, h = 840, 28
    lw = len(label) * 11.6 + 52
    body = (f'<text x="0" y="20" class="m" font-size="12" fill="{t["signal"]}">{index:02d}</text>'
            f'<text x="30" y="20" class="s" font-size="19" font-weight="600" letter-spacing="-.4" fill="{t["fg"]}">{esc(label)}</text>'
            f'<path d="M{lw} 14.5H{w}" stroke="{t["line"]}"/>')
    return svg(w, h, body, label)


# --------------------------------------------------------------------------- how I work
PRINCIPLES = [
    ("Full-stack, end to end",
     "Clean architecture, databases, REST APIs, frontends and Docker. I take software from the first diagram all the way to production.",
     ["Clean Architecture", "REST APIs", "Docker"]),
    ("Built to optimize",
     "Working software is the starting point. Then come careful refactors, performance work and pipelines that scale.",
     ["Performance", "Refactoring", "CI/CD"]),
    ("AI, put to work",
     "RAG systems, data extraction and processing pipelines that turn messy, unstructured data into something useful.",
     ["RAG", "Data Extraction", "LLMs"]),
    ("Specialized models",
     "When off-the-shelf models fall short, I fine-tune specialized LLMs on curated datasets for domain-specific precision.",
     ["Fine-tuning", "Datasets", "Hugging Face"]),
]


def principles(t):
    cw, ch, gap = 410, 184, 20
    parts = []
    for i, (title, body, tags) in enumerate(PRINCIPLES):
        x, y = (i % 2) * (cw + gap), (i // 2) * (ch + gap)
        txt, _ = lines(body, x + 24, y + 92, 54, 13.5, t["muted"], 20)
        parts.append(
            card(x, y, cw, ch, t)
            + f'<circle cx="{x + 31}" cy="{y + 32}" r="7" fill="none" stroke="{t["signal"]}" stroke-width="2"/>'
            + f'<circle cx="{x + 31}" cy="{y + 32}" r="3" fill="{t["signal"]}"/>'
            + f'<text x="{x + cw - 24}" y="{y + 37}" class="m" font-size="12" fill="{t["subtle"]}" text-anchor="end">0{i + 1}</text>'
            + f'<text x="{x + 24}" y="{y + 64}" class="s" font-size="17" font-weight="600" letter-spacing="-.3" fill="{t["fg"]}">{esc(title)}</text>'
            + txt + tags_row(tags, x + 24, y + ch - 22, t)
        )
    return svg(840, 2 * ch + gap, "".join(parts), "How I work")


# --------------------------------------------------------------------------- projects
PROJECTS = [
    ("alembic", "Alembic", "Visit site",
     "An enterprise platform for RAG, document sharing and management, powered by MCP tooling and local AI. Privacy-first and local-first.",
     ["RAG", "MCP", "Local AI", "Privacy-first"]),
    ("gymtonic", "GymTonic", "Coming to Google Play",
     "An Android gym diary: write your routines and run them set by set, with a rest timer that keeps going with the screen off.",
     ["Kotlin", "Jetpack Compose", "Offline-first"]),
    ("oneclick", "OneClick", "View code",
     "A native macOS menubar utility that puts quick system actions one click away. My most starred project.",
     ["Swift", "SwiftUI", "macOS"]),
    ("npr", "NPR Painting", "View code",
     "A non-photorealistic rendering filter that turns photos into oil-painting-style artwork.",
     ["OpenCV", "Python"]),
    ("skin", "Skin Detection", "View code",
     "Human skin detection and segmentation from images and video, using classic computer-vision techniques.",
     ["OpenCV", "Image Processing", "Python"]),
    ("localai", "LocalAI Chatbot", "View code",
     "A Telegram chatbot wired to a local LLM through Ollama. Private, self-hosted conversational AI.",
     ["Ollama", "Telegram", "Python"]),
]


def project(t, key, title, action, desc, tags):
    w, h = 410, 214
    logo = {
        "alembic": lambda: inline_svg(SRC / "alembic.svg", 33, 33, 26, 26),
        "gymtonic": lambda: f'<rect x="24" y="24" width="44" height="44" rx="10" fill="#121417"/>'
                            + inline_svg(SRC / "gymtonic.svg", 34, 34, 24, 24),
        "oneclick": lambda: lucide("pointer", 35, 35, 22, t["fg"]),
        "npr": lambda: lucide("palette", 35, 35, 22, t["fg"]),
        "skin": lambda: lucide("scan", 35, 35, 22, t["fg"]),
        "localai": lambda: simple("ollama", 35, 35, 22, t["fg"]),
    }[key]()
    box = f'<rect x="24.5" y="24.5" width="43" height="43" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    link = action != "Coming to Google Play"
    act = (f'<text x="{w - (44 if link else 24)}" y="51" class="s" font-size="13" fill="{t["muted"]}" text-anchor="end">{action}</text>'
           + (lucide("arrow", w - 40, 39, 15, t["muted"]) if link else ""))
    txt, _ = lines(desc, 24, 102, 56, 13.5, t["muted"], 20)
    body = (card(0, 0, w, h, t) + box + logo
            + f'<text x="84" y="51" class="s" font-size="18" font-weight="600" letter-spacing="-.3" fill="{t["fg"]}">{esc(title)}</text>'
            + act + txt + tags_row(tags, 24, h - 24, t))
    return svg(w, h, body, f"{title}: {desc}")


# --------------------------------------------------------------------------- websites
SITES = [
    ("redixlabs", "ReDiX Labs", "redixlabs.ai"),
    ("tastomatto", "Tasto Matto", "tastomatto.cc"),
    ("trioclelia", "Trio Clelia", "trioclelia.com"),
]
_shots = {}


def site(t, key, name, domain):
    w, iw = 400, 376
    ih = round(iw * 900 / 1440)
    h = 12 + 30 + ih + 84
    if key not in _shots:
        _shots[key] = image_data(SRC / f"{key}.webp", 752)
    body = (card(0, 0, w, h, t, rx=14)
            + f'<rect x="12.5" y="12.5" width="{iw - 1}" height="{ih + 29}" rx="9" fill="{t["bg"]}" stroke="{t["line"]}"/>'
            + "".join(f'<circle cx="{28 + i * 13}" cy="27" r="3.5" fill="{t["line"]}"/>' for i in range(3))
            + f'<rect x="{w / 2 - 70}" y="19" width="140" height="16" rx="8" fill="{t["surface"]}"/>'
            + f'<text x="{w / 2}" y="31" class="m" font-size="10" fill="{t["muted"]}" text-anchor="middle">{domain}</text>'
            + f'<clipPath id="c"><rect x="13" y="42" width="{iw - 2}" height="{ih - 1}" rx="0"/></clipPath>'
            + f'<image href="{_shots[key]}" x="13" y="42" width="{iw - 2}" height="{ih}" clip-path="url(#c)" preserveAspectRatio="xMidYMin slice"/>'
            + f'<text x="16" y="{h - 40}" class="s" font-size="22" font-weight="600" letter-spacing="-.3" fill="{t["fg"]}">{esc(name)}</text>'
            + f'<text x="16" y="{h - 16}" class="m" font-size="15" fill="{t["muted"]}">{domain}</text>'
            + lucide("arrow", w - 40, h - 52, 22, t["muted"]))
    return svg(w, h, body, f"{name} ({domain})")


# --------------------------------------------------------------------------- stack
STACK = [
    ("Languages", "Python and TypeScript every day, Swift and C# when the platform needs it.",
     [("python", "Python"), ("typescript", "TypeScript"), ("swift", "Swift"), ("sharp", "C#")]),
    ("AI and data", "Training, fine-tuning and vision work, plus local models.",
     [("pytorch", "PyTorch"), ("huggingface", "Hugging Face"), ("opencv", "OpenCV"), ("ollama", "Ollama")]),
    ("Web and shipping", "Interfaces for the products, containers to run them.",
     [("react", "React"), ("nextdotjs", "Next.js"), ("tailwindcss", "Tailwind CSS"), ("docker", "Docker")]),
]


def stack(t):
    w, rh = 840, 118
    h = rh * len(STACK)
    parts = [card(0, 0, w, h, t)]
    for r, (title, note, items) in enumerate(STACK):
        y = r * rh
        if r:
            parts.append(f'<path d="M1 {y + .5}H{w - 1}" stroke="{t["line"]}"/>')
        parts.append(f'<text x="24" y="{y + 36}" class="s" font-size="16" font-weight="600" letter-spacing="-.2" fill="{t["fg"]}">{title}</text>'
                     f'<text x="24" y="{y + 58}" class="s" font-size="13.5" fill="{t["muted"]}">{esc(note)}</text>')
        x = 24
        for icon, label in items:
            bw = int(len(label) * 7.3) + 46
            parts.append(f'<rect x="{x + .5}" y="{y + 74.5}" width="{bw - 1}" height="27" rx="13.5" fill="{t["bg"]}" stroke="{t["line"]}"/>'
                         + simple(icon, x + 11, y + 81, 14, t["fg"])
                         + f'<text x="{x + 32}" y="{y + 92.5}" class="s" font-size="12.5" font-weight="500" fill="{t["fg"]}">{esc(label)}</text>')
            x += bw + 8
    return svg(w, h, "".join(parts), "Stack: " + ", ".join(l for g in STACK for _, l in g[2]))


def main():
    for old in OUT.glob("*.svg"):
        old.unlink()
    sections = ["How I work", "Projects", "Websites", "Stack"]
    for name, t in THEMES.items():
        files = {
            "header": header(t),
            "btn-website": button(t, "mik3sw.github.io", "globe", primary=True),
            "btn-linkedin": button(t, "LinkedIn", "linkedin"),
            "btn-huggingface": button(t, "Hugging Face", "huggingface"),
            "btn-cv": button(t, "View CV", "file"),
            "principles": principles(t),
            "stack": stack(t),
        }
        for i, label in enumerate(sections, 1):
            files[f"section-{i}"] = section(t, label, i)
        for p in PROJECTS:
            files[f"project-{p[0]}"] = project(t, *p)
        for s in SITES:
            files[f"site-{s[0]}"] = site(t, *s)
        for key, content in files.items():
            (OUT / f"{key}-{name}.svg").write_text(content, encoding="utf-8")
    print("assets generated in", OUT)


if __name__ == "__main__":
    main()
