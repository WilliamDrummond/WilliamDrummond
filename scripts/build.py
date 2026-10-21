"""Builds the profile SVG banners. Run from the repo root: python3 scripts/build.py

Palette and fonts match williamdrummond.com.au (Familjen Grotesk + DM Mono, embedded in base.css).
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
BASE_CSS = (ROOT / "scripts" / "base.css").read_text()

BG, CARD, LINE = "#05070C", "#0E1420", "#1B2333"
TEXT, MUTED = "#F1F4FA", "#8C95A6"
BLUE, SKY, ICE, PEACH = "#2F6BFF", "#8DB0FF", "#C9E4FF", "#FFB59A"
MONO_ADVANCE = 0.6  # DM Mono advance width, in em


def frame(p, w, h, title, desc, css, body, glow=(260, 120, 520)):
    """Shared card: grid background, blue glow, gradient edge."""
    gx, gy, gr = glow
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><desc>{escape(desc)}</desc>
<defs><style>
{BASE_CSS}{css}</style>
<pattern id="{p}g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
<pattern id="{p}G" width="160" height="160" patternUnits="userSpaceOnUse"><path d="M160 0H0V160" fill="none" stroke="#ffffff" stroke-opacity=".05"/></pattern>
<linearGradient id="{p}edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity=".7"/><stop offset=".35" stop-color="{LINE}"/><stop offset=".7" stop-color="{LINE}"/><stop offset="1" stop-color="{PEACH}" stop-opacity=".6"/></linearGradient>
<linearGradient id="{p}heat" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SKY}"/><stop offset=".5" stop-color="{ICE}"/><stop offset="1" stop-color="{PEACH}"/></linearGradient>
<radialGradient id="{p}glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<filter id="{p}blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
<clipPath id="{p}card"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#{p}card)">
<rect width="{w}" height="{h}" fill="{BG}"/>
<rect width="{w}" height="{h}" fill="url(#{p}g)"/>
<rect width="{w}" height="{h}" fill="url(#{p}G)"/>
<circle cx="{gx}" cy="{gy}" r="{gr}" fill="url(#{p}glow)"/>
{body}
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="none" stroke="url(#{p}edge)" stroke-width="2"/>
</svg>
"""


def heading(kicker, title):
    return (f'<text x="40" y="52" class="m" font-size="13" font-weight="700" letter-spacing="3.5" fill="{BLUE}">// {escape(kicker)}</text>\n'
            f'<text x="40" y="96" class="d" font-size="38" fill="{TEXT}">{escape(title)}</text>')


def typing(roles, x, y, size, cycle):
    """Each role types in, holds, then deletes, in its own slot of the cycle."""
    cw = size * MONO_ADVANCE
    slot = cycle / len(roles)
    out = []
    for i, role in enumerate(roles):
        n = len(role)
        steps = list(range(n + 1)) + [n] * 6 + list(range(n, -1, -1))
        times = [0.0]
        t = 0.0
        for k in range(1, len(steps)):
            t += 0.07 if k <= n else (0.25 if k <= n + 6 else 0.035)
            times.append(t)
        times = [min(v / cycle, 1) for v in times]
        widths = ";".join(f"{s * cw + 1:.1f}" for s in steps) + ";1.0"
        kt = ";".join(f"{v:.5f}" for v in times) + ";1"
        cursor = ";".join(f"{x + 2 + s * cw:.1f}" for s in steps) + f";{x + 2:.1f}"
        end = times[-1]
        begin = f"{i * slot - 1.6:.1f}s"
        anim = f'dur="{cycle}s" begin="{begin}" repeatCount="indefinite" calcMode="discrete"'
        out.append(
            f'<clipPath id="tc{i}"><rect x="{x}" y="{y - 30}" width="0" height="40"><animate attributeName="width" {anim} keyTimes="{kt}" values="{widths}"/></rect></clipPath>\n'
            f'<text x="{x}" y="{y}" class="m" font-size="{size}" font-weight="500" fill="{TEXT}" clip-path="url(#tc{i})">{escape(role)}</text>\n'
            f'<g opacity="0"><animate attributeName="opacity" {anim} keyTimes="0;{end:.5f}" values="1;0"/>'
            f'<rect class="blink" x="{x + 2}" y="{y - 24}" width="13" height="28" fill="{BLUE}"><animate attributeName="x" {anim} keyTimes="{kt}" values="{cursor}"/></rect></g>')
    return "\n".join(out)


def hero():
    roles = ["Forward Deployed Engineer", "AI agents and automation", "Embedded with the team", "Ship fast, then iterate"]
    name = "Will Drummond"
    stats = [("8+", "Years experience"), ("30+", "Automations built"), ("60+", "Apps shipped")]
    stat_svg = "".join(
        f'<text x="{64 + i * 200}" y="472" class="d" font-size="40" fill="url(#hheat)">{n}</text>'
        f'<text x="{64 + i * 200}" y="498" class="m" font-size="12" letter-spacing="1.5" fill="{MUTED}">{escape(l.upper())}</text>'
        for i, (n, l) in enumerate(stats))

    # The forward deployed loop: four stages round a ring, a dot travels it and lights each stage.
    cx, cy, r, dur = 990, 272, 150, 8
    stages = [
        ("EMBED", "sit with the team", cx, cy - r, BLUE),
        ("DISCOVER", "find the lost hours", cx + r, cy, SKY),
        ("BUILD", "agents, flows, apps", cx, cy + r, PEACH),
        ("SHIP", "in front of users", cx - r, cy, ICE),
    ]
    nodes = []
    for i, (label, sub, nx, ny, col) in enumerate(stages):
        bw, bh = 156, 58
        begin = f"{i * dur / 4:.1f}s"
        nodes.append(
            f'<g><rect x="{nx - bw / 2}" y="{ny - bh / 2}" width="{bw}" height="{bh}" rx="10" fill="{CARD}" stroke="{col}" stroke-opacity=".35" stroke-width="1.6">'
            f'<animate attributeName="stroke-opacity" dur="{dur}s" begin="{begin}" repeatCount="indefinite" keyTimes="0;.04;.22;1" values=".35;1;.35;.35"/></rect>'
            f'<text x="{nx}" y="{ny - 4}" text-anchor="middle" class="m" font-size="13" font-weight="700" letter-spacing="2.5" fill="{col}">{label}</text>'
            f'<text x="{nx}" y="{ny + 17}" text-anchor="middle" class="b" font-size="14" fill="{MUTED}">{escape(sub)}</text></g>')
    ring = f"M{cx} {cy - r}A{r} {r} 0 1 1 {cx - 0.01} {cy - r}Z"
    viewport = f"""<rect x="740" y="36" width="500" height="468" rx="10" fill="#0d1116" fill-opacity=".85" stroke="{LINE}"/>
<path d="M760 70v-18h18 M1220 70v-18h-18 M760 470v18h18 M1220 470v18h-18" fill="none" stroke="{MUTED}" stroke-width="2.5"/>
<text x="790" y="68" class="m" font-size="11" font-weight="700" letter-spacing="2.5" fill="{ICE}">HOW I WORK</text>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="2"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BLUE}" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="3 7"/>
<circle r="6" fill="{SKY}"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{ring}"/></circle>
<circle r="14" fill="{BLUE}" opacity=".25"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{ring}"/></circle>
{chr(10).join(nodes)}
<text x="{cx}" y="{cy - 6}" text-anchor="middle" class="d" font-size="30" fill="{TEXT}">Forward</text>
<text x="{cx}" y="{cy + 28}" text-anchor="middle" class="d" font-size="30" fill="url(#hheat)">Deployed</text>
<text x="{cx}" y="484" text-anchor="middle" class="m" font-size="12" letter-spacing="1.5" fill="{MUTED}">REPEAT UNTIL IT PAYS BACK</text>"""

    body = f"""<text x="64" y="138" class="m rise" font-size="15" letter-spacing="4" fill="{MUTED}" style="animation-delay:.15s">HELLO, I'M</text>
<g class="rise" style="animation-delay:.25s">
<text x="70" y="252" class="d" font-size="88" letter-spacing="-2" fill="#000" opacity=".6">{name}</text>
<text x="64" y="246" class="d" font-size="88" letter-spacing="-2" fill="url(#hheat)" filter="url(#hblur)" opacity=".55">{name}</text>
<text x="64" y="246" class="d" font-size="88" letter-spacing="-2" fill="url(#hheat)">{name}</text>
<clipPath id="nameclip"><text x="64" y="246" class="d" font-size="88" letter-spacing="-2">{name}</text></clipPath>
<g clip-path="url(#nameclip)"><rect class="shine" x="0" y="140" width="80" height="120" fill="#fff" opacity=".35" transform="skewX(-20)"/></g>
</g>
<g class="rise" style="animation-delay:.35s">
<rect x="64" y="266" width="48" height="5" fill="{SKY}"/><rect x="116" y="266" width="48" height="5" fill="{BLUE}"/><rect x="168" y="266" width="48" height="5" fill="{PEACH}"/>
</g>
<text x="64" y="326" class="m" font-size="26" font-weight="700" fill="{BLUE}">&gt;</text>
{typing(roles, 100, 326, 26, 16)}
<g class="rise" style="animation-delay:.5s">
<text x="64" y="384" class="b" font-size="20" fill="{MUTED}">I sit with the people doing the work, find the problem worth</text>
<text x="64" y="412" class="b" font-size="20" fill="{MUTED}">solving, and ship the agent, automation or app that fixes it.</text>
</g>
<g class="rise" style="animation-delay:.65s">{stat_svg}</g>
{viewport}"""
    css = """@keyframes shine{0%{transform:translateX(-700px)}60%,100%{transform:translateX(900px)}}
.shine{animation:shine 6s ease-in-out infinite 1s}"""
    return frame("h", 1280, 540, "Will Drummond, Forward Deployed Engineer",
                 "Animated hero: name, cycling roles, a short pitch, headline numbers and the embed, discover, build, ship loop.",
                 css, body)


def stack():
    groups = [
        ("AI AND AGENTS", BLUE, ["Claude API", "Claude Code", "MCP connectors", "Agent routines", "RAG pipelines", "Azure AI Foundry", "Copilot Studio"]),
        ("MICROSOFT AUTOMATION", SKY, ["Power Automate", "Power BI and DAX", "Azure Logic Apps", "SharePoint", "Microsoft 365 admin"]),
        ("WEB AND CODE", PEACH, ["TypeScript", "JavaScript", "React", "three.js", "Python", "SQL", "HTML and CSS"]),
        ("CLOUD AND DELIVERY", ICE, ["Cloudflare Pages", "Workers", "D1 and R2", "Git", "CI/CD"]),
    ]
    w, gap, top = 285, 20, 128
    cards = []
    for i, (label, col, items) in enumerate(groups):
        x = 40 + i * (w + gap)
        rows = "".join(
            f'<rect x="{x + 26}" y="{top + 86 + j * 34}" width="6" height="6" fill="{col}"/>'
            f'<text x="{x + 44}" y="{top + 93 + j * 34}" class="b" font-size="18" fill="{TEXT}">{escape(it)}</text>'
            for j, it in enumerate(items))
        cards.append(
            f'<g class="rise" style="animation-delay:{0.1 + i * 0.12:.2f}s">'
            f'<rect x="{x}" y="{top}" width="{w}" height="312" rx="12" fill="{CARD}" stroke="{LINE}"/>'
            f'<path d="M{x} {top + 12}a12 12 0 0 1 12-12h80" fill="none" stroke="{col}" stroke-width="3"/>'
            f'<text x="{x + 26}" y="{top + 44}" class="m" font-size="12" font-weight="700" letter-spacing="2.5" fill="{col}">{label}</text>'
            f'<path d="M{x + 26} {top + 62}H{x + w - 26}" stroke="{LINE}"/>{rows}</g>')
    creds = "AWS Certified Cloud Practitioner  ·  Grad Cert Data Science, Deakin  ·  B. Civil Engineering, Monash"
    body = f"""{heading("TOOLKIT", "What I build with")}
{chr(10).join(cards)}
<text x="40" y="482" class="m" font-size="13" fill="{MUTED}">{escape(creds)}</text>"""
    return frame("s", 1280, 510, "Tools I build with",
                 "Toolkit in four groups: AI and agents, Microsoft automation, web and code, cloud and delivery; plus certifications.",
                 "", body, glow=(250, 300, 300))


def work():
    projects = [
        ("AT CMP", BLUE, "Design standards agent",
         ["A Copilot Studio agent that answers engineers' questions", "from water design standards, grounded with RAG."],
         "Copilot Studio · Azure AI Foundry · RAG"),
        ("AT CMP", SKY, "RFI register automation",
         ["7+ Power Automate flows run a water authority RFI register", "and email each PM a weekly summary from Power BI."],
         "Power Automate · Power BI · SharePoint"),
        ("IN DAILY USE", PEACH, "Eren",
         ["My personal AI operating system: 60+ apps on one database,", "Claude agents on schedules, MCP links to mail and calendar."],
         "Cloudflare Workers · D1 · Claude API · MCP"),
        ("LIVE", ICE, "Photocard Holder Factory",
         ["Customers design a 3D-printable holder in the browser and", "export a multi-colour 3MF. Stripe licences, Google sign-in."],
         "Cloudflare Pages · D1 · R2 · Stripe"),
    ]
    cards = []
    for i, (tag, col, title, lines, tech) in enumerate(projects):
        x = 40 + (i % 2) * 610
        y = 128 + (i // 2) * 226
        tw = len(tag) * 11 * MONO_ADVANCE + len(tag) * 1.5 + 40
        delay = 0.10 + i * 0.12
        cards.append(f"""<g class="rise" style="animation-delay:{delay:.2f}s">
<rect x="{x}" y="{y}" width="590" height="206" rx="12" fill="{CARD}" stroke="{LINE}"/>
<path d="M{x} {y + 12}a12 12 0 0 1 12-12h80" fill="none" stroke="{col}" stroke-width="3"/>
<rect x="{x + 566 - tw:.1f}" y="{y + 24}" width="{tw:.1f}" height="26" rx="13" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".5"/>
<circle cx="{x + 580 - tw:.1f}" cy="{y + 37}" r="4" fill="{col}" class="pulse"/>
<text x="{x + 590 - tw:.1f}" y="{y + 41}" class="m" font-size="11" font-weight="700" letter-spacing="1.5" fill="{col}">{tag}</text>
<text x="{x + 28}" y="{y + 92}" class="d" font-size="34" fill="{TEXT}">{escape(title)}</text>
<text x="{x + 28}" y="{y + 124}" class="b" font-size="17" fill="{MUTED}">{escape(lines[0])}</text>
<text x="{x + 28}" y="{y + 148}" class="b" font-size="17" fill="{MUTED}">{escape(lines[1])}</text>
<path d="M{x + 28} {y + 168}H{x + 562}" stroke="{LINE}"/>
<text x="{x + 28}" y="{y + 190}" class="m" font-size="12.5" fill="{MUTED}">{escape(tech)}</text>
<rect class="bar" x="{x}" y="{y + 203}" width="590" height="3" fill="{col}" style="animation-delay:{delay + 0.4:.2f}s;transform:scaleX(0)"/>
</g>""")
    css = """@keyframes fill{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.bar{transform-box:fill-box;transform-origin:left;animation:fill 1.4s cubic-bezier(.2,.8,.2,1) forwards}"""
    body = f"""{heading("SELECTED WORK", "Things I've shipped")}
{"".join(cards)}"""
    return frame("w", 1280, 600, "Selected work",
                 "Four project cards: design standards agent, RFI register automation, Eren and Photocard Holder Factory.",
                 css, body, glow=(1280, 0, 520))


def connect():
    links = [
        ("WEB", BLUE, "Résumé and portfolio", "williamdrummond.com.au"),
        ("LINKEDIN", SKY, "William Drummond", "linkedin.com/in/williamjdrummond"),
    ]
    cards = []
    for i, (tag, col, title, sub) in enumerate(links):
        x = 560 + i * 340
        cards.append(f"""<g class="rise" style="animation-delay:{0.15 + i * 0.12:.2f}s">
<rect x="{x}" y="120" width="320" height="196" rx="12" fill="{CARD}" stroke="{LINE}"/>
<rect x="{x}" y="120" width="320" height="4" fill="{col}"/>
<text x="{x + 22}" y="160" class="m" font-size="12" font-weight="700" letter-spacing="3" fill="{col}">{tag}</text>
<text x="{x + 22}" y="222" class="d" font-size="26" fill="{TEXT}">{escape(title)}</text>
<text x="{x + 22}" y="250" class="m" font-size="12" fill="{MUTED}">{escape(sub)}</text>
<path d="M{x + 22} 282h40 M{x + 52} 274l10 8-10 8" fill="none" stroke="{col}" stroke-width="2.2"/>
</g>""")
    body = f"""{heading("CONTACT", "Let's connect")}
<text x="40" y="136" class="b" font-size="18" fill="{MUTED}">Open to forward deployed, AI and</text>
<text x="40" y="160" class="b" font-size="18" fill="{MUTED}">automation engineering roles.</text>
<text x="40" y="290" class="m" font-size="13" letter-spacing="1.5" fill="{MUTED}">MELBOURNE, AUSTRALIA</text>
{"".join(cards)}"""
    return frame("c", 1280, 360, "Connect with Will",
                 "Contact cards: website and LinkedIn.", "", body, glow=(250, 228, 300))


for fname, svg in [("hero.svg", hero()), ("stack.svg", stack()), ("workshop.svg", work()), ("connect.svg", connect())]:
    (ROOT / fname).write_text(svg)
    print(fname, len(svg))
