#!/usr/bin/env python3
"""Generate the shadcn-style SVG assets used in the profile README.

Run from the repository root:  python3 assets/generate.py
Every asset is written in a light and a dark variant (zinc palette).
"""
from pathlib import Path

OUT = Path(__file__).parent

THEMES = {
    "dark": {
        "bg": "#09090b",
        "card": "#09090b",
        "muted_bg": "#18181b",
        "border": "#27272a",
        "fg": "#fafafa",
        "muted": "#a1a1aa",
        "subtle": "#52525b",
        "grid": "#18181b",
        "primary": "#fafafa",
        "primary_fg": "#09090b",
        "accent": "#22c55e",
        "code_kw": "#c084fc",
        "code_str": "#86efac",
        "code_key": "#93c5fd",
    },
    "light": {
        "bg": "#ffffff",
        "card": "#ffffff",
        "muted_bg": "#f4f4f5",
        "border": "#e4e4e7",
        "fg": "#09090b",
        "muted": "#71717a",
        "subtle": "#a1a1aa",
        "grid": "#f4f4f5",
        "primary": "#18181b",
        "primary_fg": "#fafafa",
        "accent": "#16a34a",
        "code_kw": "#9333ea",
        "code_str": "#15803d",
        "code_key": "#2563eb",
    },
}

SANS = "Geist, Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Lucide icons (ISC license), 24x24 viewBox, stroke based.
ICONS = {
    "bot": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "gamepad": '<line x1="6" x2="10" y1="11" y2="11"/><line x1="8" x2="8" y1="9" y2="13"/><line x1="15" x2="15.01" y1="12" y2="12"/><line x1="18" x2="18.01" y1="10" y2="10"/><path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 17.32 5z"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "send": '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/>',
    "arrow": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
    "coffee": '<path d="M10 2v2"/><path d="M14 2v2"/><path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1"/><path d="M6 2v2"/>',
    "github": '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
}


def icon(name, x, y, size, color, width=2):
    s = size / 24
    return (
        f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'
    )


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n'
    )


# --------------------------------------------------------------------------- header
def header(t):
    w, h = 840, 300
    code = [
        [("kw", "const"), ("fg", " michele = {")],
        [("key", "  role"), ("fg", ": "), ("str", '"Software Engineer"'), ("fg", ",")],
        [("key", "  based"), ("fg", ": "), ("str", '"Italy"'), ("fg", ",")],
        [("key", "  work"), ("fg", ": ["), ("str", '"C#"'), ("fg", ", "), ("str", '"Java"'), ("fg", "],")],
        [("key", "  focus"), ("fg", ": "), ("str", '"AI projects"'), ("fg", ",")],
        [("key", "  loves"), ("fg", ": ["), ("str", '"gaming"'), ("fg", ", "), ("str", '"travel"'), ("fg", "],")],
        [("fg", "}")],
    ]
    color = {"kw": t["code_kw"], "key": t["code_key"], "str": t["code_str"], "fg": t["fg"]}
    lines = []
    for i, parts in enumerate(code):
        y = 112 + i * 21
        spans = "".join(f'<tspan fill="{color[k]}">{v}</tspan>' for k, v in parts)
        lines.append(f'<text x="510" y="{y}" class="mono" xml:space="preserve">{spans}</text>')
        lines.append(f'<text x="490" y="{y}" class="mono" fill="{t["subtle"]}" text-anchor="end">{i + 1}</text>')

    body = f"""
<style>
  .sans {{ font-family: {SANS}; }}
  .mono {{ font-family: {MONO}; font-size: 12.5px; }}
  .fade {{ animation: fade .8s ease-out both; }}
  .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .2s; }} .d3 {{ animation-delay: .3s; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
</style>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{t['grid']}" stroke-width="1"/>
  </pattern>
  <radialGradient id="fadeMask" cx="20%" cy="0%" r="90%">
    <stop offset="0" stop-color="#fff" stop-opacity="1"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  <mask id="m"><rect width="{w}" height="{h}" fill="url(#fadeMask)"/></mask>
  <clipPath id="clip"><rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12"/></clipPath>
</defs>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{t['card']}" stroke="{t['border']}"/>
<g clip-path="url(#clip)"><rect width="{w}" height="{h}" fill="url(#grid)" mask="url(#m)"/></g>

<g class="fade">
  <rect x="40.5" y="40.5" width="232" height="27" rx="13.5" fill="{t['muted_bg']}" stroke="{t['border']}"/>
  <circle cx="58" cy="54" r="3.5" fill="{t['accent']}"/>
  <circle cx="58" cy="54" r="3.5" fill="none" stroke="{t['accent']}">
    <animate attributeName="r" values="3.5;8" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".8;0" dur="2s" repeatCount="indefinite"/>
  </circle>
  <text x="70" y="58.5" class="sans" font-size="12.5" font-weight="500" fill="{t['fg']}">Software Engineer · ReDiX</text>
</g>

<text x="38" y="128" class="sans fade d1" font-size="44" font-weight="700" letter-spacing="-1.6" fill="{t['fg']}">Michele Marcucci</text>
<g class="fade d2">
  <text x="40" y="164" class="sans" font-size="16" fill="{t['muted']}">Software Engineer from Italy, building with</text>
  <text x="40" y="188" class="sans" font-size="16" fill="{t['muted']}">C#, Java, Python and a lot of curiosity for AI.</text>
</g>
<g class="fade d3">
  <path d="M40 216.5H420" stroke="{t['border']}"/>
  {icon("pin", 40, 236, 15, t['muted'])}
  <text x="62" y="248" class="sans" font-size="13.5" fill="{t['muted']}">Italy</text>
  {icon("briefcase", 118, 236, 15, t['muted'])}
  <text x="140" y="248" class="sans" font-size="13.5" fill="{t['muted']}">ReDiX Informatica</text>
  {icon("coffee", 280, 236, 15, t['muted'])}
  <text x="302" y="248" class="sans" font-size="13.5" fill="{t['muted']}">Gaming &amp; travel</text>
</g>

<g class="fade d2">
  <rect x="460.5" y="40.5" width="339" height="219" rx="10" fill="{t['muted_bg']}" stroke="{t['border']}"/>
  <path d="M461 80.5H799" stroke="{t['border']}"/>
  <text x="480" y="65" class="mono" fill="{t['fg']}">michele.ts</text>
  <path d="M478 80h80" stroke="{t['fg']}" stroke-width="1.5"/>
  <text x="575" y="65" class="mono" fill="{t['subtle']}">README.md</text>
  {''.join(lines)}
  <rect x="518" y="{112 + 6 * 21 - 12}" width="7" height="15" fill="{t['fg']}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>
</g>
"""
    return svg(w, h, body, "Michele Marcucci, Software Engineer")


# --------------------------------------------------------------------------- now cards
def cards(t):
    w, h = 840, 268
    items = [
        ("bot", "Working on", "AI projects and the tooling around them."),
        ("book", "Learning", "Java, Python and Swift, one commit at a time."),
        ("gamepad", "Would love to learn", "Game programming, from engine to gameplay."),
        ("message", "Ask me about", "Telegram bots: I have built quite a few."),
    ]
    cw, ch, gap = 410, 124, 20
    parts = [f"<style>.sans {{ font-family: {SANS}; }}</style>"]
    for i, (ic, title, desc) in enumerate(items):
        x = (i % 2) * (cw + gap)
        y = (i // 2) * (ch + gap)
        parts.append(
            f'<rect x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>'
            f'<rect x="{x + 24.5}" y="{y + 24.5}" width="35" height="35" rx="8" fill="{t["muted_bg"]}" stroke="{t["border"]}"/>'
            + icon(ic, x + 33, y + 33, 18, t["fg"])
            + f'<text x="{x + 24}" y="{y + 86}" class="sans" font-size="15" font-weight="600" fill="{t["fg"]}" letter-spacing="-.2">{title}</text>'
            f'<text x="{x + 24}" y="{y + 107}" class="sans" font-size="13.5" fill="{t["muted"]}">{desc}</text>'
        )
    return svg(w, h, "".join(parts), "What I am up to")


# --------------------------------------------------------------------------- stack badges
def stack(t):
    tags = ["C#", ".NET", "Java", "Python", "Swift", "SQL", "Git", "Telegram Bots", "AI / LLM"]
    x, y, hgt = 0, 0, 30
    parts = [f"<style>.sans {{ font-family: {SANS}; }}</style>"]
    for tag in tags:
        tw = int(len(tag) * 7.4) + 36
        parts.append(
            f'<rect x="{x + .5}" y="{y + .5}" width="{tw - 1}" height="{hgt - 1}" rx="6" fill="{t["muted_bg"]}" stroke="{t["border"]}"/>'
            f'<circle cx="{x + 14}" cy="{y + 15}" r="3" fill="{t["muted"]}"/>'
            f'<text x="{x + 24}" y="{y + 19.5}" class="sans" font-size="12.5" font-weight="500" fill="{t["fg"]}">{tag}</text>'
        )
        x += tw + 8
    return svg(x - 8, hgt, "".join(parts), "Tech stack")


# --------------------------------------------------------------------------- buttons
def button(t, label, ic, primary):
    w = int(len(label) * 7.6) + 62
    h = 38
    fill, fg = (t["primary"], t["primary_fg"]) if primary else (t["card"], t["fg"])
    stroke = "none" if primary else t["border"]
    body = (
        f"<style>.sans {{ font-family: {SANS}; }}</style>"
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{fill}" stroke="{stroke}"/>'
        + icon(ic, 16, 11, 16, fg)
        + f'<text x="40" y="24" class="sans" font-size="14" font-weight="500" fill="{fg}">{label}</text>'
    )
    return svg(w, h, body, label)


def section(t, label):
    w, h = 840, 24
    body = (
        f"<style>.sans {{ font-family: {SANS}; }}</style>"
        f'<text x="0" y="16" class="sans" font-size="12" font-weight="600" letter-spacing="1.4" fill="{t["muted"]}">{label.upper()}</text>'
        f'<path d="M{len(label) * 9.2 + 14} 12.5H{w}" stroke="{t["border"]}"/>'
    )
    return svg(w, h, body, label)


def main():
    for name, t in THEMES.items():
        files = {
            "header": header(t),
            "now": cards(t),
            "stack": stack(t),
            "btn-website": button(t, "michelemarcucci.me", "globe", True),
            "btn-telegram": button(t, "Telegram", "send", False),
            "btn-github": button(t, "Follow", "github", False),
            "section-about": section(t, "About"),
            "section-stack": section(t, "Stack"),
            "section-stats": section(t, "GitHub activity"),
        }
        for key, content in files.items():
            (OUT / f"{key}-{name}.svg").write_text(content, encoding="utf-8")
    print("assets generated in", OUT)


if __name__ == "__main__":
    main()
