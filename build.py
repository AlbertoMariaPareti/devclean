#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevClean static site generator.

Generates every HTML page, plus sitemap.xml, robots.txt and ads.txt, from the
content definitions in src/content.py.

Usage:
    python build.py

Everything it writes is plain static HTML: the output directory can be served
by GitHub Pages, Netlify, or any web server, with no runtime dependency.

The only settings you normally need to change are in the CONFIG block below.
"""

import html
import json
import os
import re
import shutil
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from content import TOOLS, GUIDES  # noqa: E402

# ==========================================================================
# CONFIG — the handful of values you may want to change
# ==========================================================================

# Where the site will live. Used for canonical URLs, Open Graph tags and the
# sitemap. Change this (and nothing else) when you move to a custom domain.
SITE_URL = "https://albertomariapareti.github.io/devclean"

SITE_NAME = "DevClean"
SITE_TAGLINE = "Free online text and code cleaning tools"
AUTHOR = "Alberto Maria Pareti"
CONTACT_EMAIL = "albertomariapareti@hotmail.com"

# Google Analytics 4 measurement ID. Empty string disables analytics entirely.
GA_MEASUREMENT_ID = "G-XRYP95S3EV"

# ---------------------------------------------------------------- AdSense --
# Leave ADSENSE_CLIENT empty until your AdSense account is approved.
#
# While it is empty the pages carry no ad markup at all — which is what you
# want during review, because empty "Advertisement" boxes are a documented
# reason for rejection. Once approved, paste your publisher ID here (the
# "ca-pub-..." string), fill in the slot IDs, run `python build.py` again,
# and every page gets real ad units in the reserved slots.
ADSENSE_CLIENT = ""          # e.g. "ca-pub-1234567890123456"
ADSENSE_SLOT_TOP = ""        # e.g. "1234567890"
ADSENSE_SLOT_INLINE = ""
ADSENSE_SLOT_BOTTOM = ""

# Optional support link shown in the footer. Empty string hides it.
SUPPORT_URL = ""             # e.g. "https://buymeacoffee.com/yourname"

# Public API base URL, advertised on the API page. Empty hides the API page.
API_BASE_URL = "https://devclean-backend.onrender.com"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
TODAY = date.today().isoformat()

# ==========================================================================
# Small helpers
# ==========================================================================


def esc(text):
    """Escape a string for use inside an HTML attribute or text node."""
    return html.escape(str(text), quote=True)


def strip_tags(markup):
    """Rough tag stripper, used to build plain-text FAQ answers for JSON-LD."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", markup)).strip()


def rel(depth):
    """Relative prefix back to the site root from a page `depth` levels deep."""
    return "../" * depth if depth else ""


def write(path, content):
    full = os.path.join(OUT_DIR, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    return full


# ==========================================================================
# Shared fragments
# ==========================================================================


def analytics_tag():
    if not GA_MEASUREMENT_ID:
        return ""
    return f"""  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_MEASUREMENT_ID}');
  </script>
"""


def adsense_head():
    if not ADSENSE_CLIENT:
        return "  <!-- AdSense: set ADSENSE_CLIENT in build.py once your account is approved -->\n"
    return (
        f'  <script async src="https://pagead2.googlesyndication.com/pagead/js/'
        f'adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>\n'
    )


def ad_slot(position):
    """Render one ad slot. Produces nothing but a comment until AdSense is on."""
    slot_id = {
        "top": ADSENSE_SLOT_TOP,
        "inline": ADSENSE_SLOT_INLINE,
        "bottom": ADSENSE_SLOT_BOTTOM,
    }.get(position, "")

    if not ADSENSE_CLIENT or not slot_id:
        return f"      <!-- ad slot: {position} -->\n"

    extra = " ad-slot--inline" if position == "inline" else ""
    return f"""      <aside class="ad-slot{extra}">
        <span class="ad-label">Advertisement</span>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{ADSENSE_CLIENT}"
             data-ad-slot="{slot_id}"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
      </aside>
"""


def header(depth, ):
    r = rel(depth)
    return f"""  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="{r}index.html">
        <span class="brand-mark" aria-hidden="true">D</span>{SITE_NAME}
      </a>
      <nav class="nav" aria-label="Main">
        <a href="{r}index.html#tools">Tools</a>
        <a href="{r}guides/index.html">Guides</a>
        <a class="nav-hide-sm" href="{r}api.html">API</a>
        <a class="nav-hide-sm" href="{r}about.html">About</a>
        <button class="theme-toggle" type="button" aria-label="Switch theme">☀</button>
      </nav>
    </div>
  </header>
"""


def footer(depth):
    r = rel(depth)
    tool_links = "\n".join(
        f'          <li><a href="{r}tools/{t["slug"]}.html">{esc(t["title"])}</a></li>'
        for t in TOOLS[:5]
    )
    guide_links = "\n".join(
        f'          <li><a href="{r}guides/{g["slug"]}.html">{esc(g["title"][:38])}…</a></li>'
        for g in GUIDES
    )
    support = (
        f'      <a href="{esc(SUPPORT_URL)}" rel="noopener">Support this project</a>\n'
        if SUPPORT_URL else ""
    )
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-cols">
        <div>
          <h4>Popular tools</h4>
          <ul>
{tool_links}
            <li><a href="{r}index.html#tools">All tools →</a></li>
          </ul>
        </div>
        <div>
          <h4>Guides</h4>
          <ul>
{guide_links}
          </ul>
        </div>
        <div>
          <h4>Project</h4>
          <ul>
            <li><a href="{r}about.html">About</a></li>
            <li><a href="{r}api.html">Developer API</a></li>
            <li><a href="{r}privacy.html">Privacy policy</a></li>
            <li><a href="https://github.com/AlbertoMariaPareti/devclean" rel="noopener">Source on GitHub</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© {date.today().year} {esc(AUTHOR)}</span>
        <span>All processing happens in your browser.</span>
{support}        <span class="spacer"></span>
        <span>Updated {TODAY}</span>
      </div>
    </div>
  </footer>
"""


def page(depth, title, description, body, canonical_path,
         extra_head="", json_ld=None, body_attrs=""):
    """Assemble a complete HTML document."""
    r = rel(depth)
    canonical = f"{SITE_URL}/{canonical_path}".replace("/index.html", "/")
    ld = ""
    if json_ld:
        for block in json_ld:
            ld += ('  <script type="application/ld+json">'
                   + json.dumps(block, ensure_ascii=False, separators=(",", ":"))
                   + "</script>\n")

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(SITE_NAME)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_URL}/assets/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">

  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧹</text></svg>">
  <link rel="stylesheet" href="{r}assets/style.css">
  <link rel="sitemap" type="application/xml" href="{SITE_URL}/sitemap.xml">

  <script>
    // Apply the saved theme before first paint to avoid a flash of the wrong colours.
    (function () {{
      try {{
        var t = localStorage.getItem('devclean-theme');
        if (!t) t = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', t);
      }} catch (e) {{}}
    }})();
  </script>
{analytics_tag()}{adsense_head()}{extra_head}{ld}</head>
<body{body_attrs}>
{header(depth)}
  <main id="main">
{body}
  </main>
{footer(depth)}
  <script src="{r}assets/tools.js"></script>
  <script src="{r}assets/app.js"></script>
</body>
</html>
"""


# ==========================================================================
# Tool widget
# ==========================================================================


def render_settings(settings):
    if not settings:
        return ""
    rows = []
    for s in settings:
        opt = esc(s["opt"])
        label = esc(s["label"])
        if s["type"] == "checkbox":
            checked = " checked" if s.get("checked") else ""
            rows.append(
                f'        <label><input type="checkbox" data-opt="{opt}"{checked}> {label}</label>'
            )
        elif s["type"] == "number":
            attrs = f' value="{s.get("value", 0)}"'
            if "min" in s:
                attrs += f' min="{s["min"]}"'
            if "max" in s:
                attrs += f' max="{s["max"]}"'
            rows.append(
                f'        <label>{label} <input type="number" data-opt="{opt}"{attrs}></label>'
            )
        else:
            ph = f' placeholder="{esc(s.get("placeholder", ""))}"' if s.get("placeholder") else ""
            rows.append(
                f'        <label>{label} <input type="text" data-opt="{opt}"{ph}></label>'
            )
    return '      <div class="settings">\n' + "\n".join(rows) + "\n      </div>\n"


def render_tool(tool):
    ops = tool["ops"]
    chips = ""
    if len(ops) > 1:
        items = []
        for i, (op_id, label) in enumerate(ops):
            checked = " checked" if i == 0 else ""
            items.append(
                f'        <label class="chip"><input type="radio" name="op" '
                f'value="{esc(op_id)}"{checked}><span>{esc(label)}</span></label>'
            )
        chips = '      <div class="options" role="radiogroup" aria-label="Operation">\n' \
                + "\n".join(items) + "\n      </div>\n"
    else:
        chips = f'      <input type="hidden" name="op" value="{esc(ops[0][0])}">\n'

    sample_btn = ""
    if tool.get("sample"):
        sample_btn = (f'        <button type="button" id="sample" class="btn-ghost" '
                      f'data-sample="{esc(tool["sample"])}">Load example</button>\n')

    return f"""      <div class="tool">
        <label class="field-label" for="input">
          <span>Your text</span>
          <span class="hint" id="input-meta"></span>
        </label>
        <textarea id="input" spellcheck="false" placeholder="Paste your text here — or drop a text file onto this box."></textarea>

{chips}{render_settings(tool.get("settings"))}        <div class="actions">
          <button type="button" id="process" class="btn-primary">{esc(ops[0][1])}</button>
          <button type="button" id="copy">Copy</button>
          <button type="button" id="download" class="btn-ghost">Download</button>
          <button type="button" id="clear" class="btn-ghost">Clear</button>
{sample_btn}          <span class="status" id="status" role="status" aria-live="polite"></span>
        </div>

        <div class="output-block">
          <label class="field-label" for="output">
            <span>Result</span>
            <span class="hint" id="output-meta"></span>
          </label>
          <textarea id="output" readonly spellcheck="false" placeholder="The result appears here. Nothing is uploaded — the work happens in this tab."></textarea>
        </div>
      </div>
"""


def faq_html(faq):
    if not faq:
        return ""
    items = []
    for q, a in faq:
        items.append(f"""      <details>
        <summary>{esc(q)}</summary>
        <div><p>{a}</p></div>
      </details>""")
    return ('    <h2>Frequently asked questions</h2>\n    <div class="faq">\n'
            + "\n".join(items) + "\n    </div>\n")


def breadcrumb(depth, trail):
    r = rel(depth)
    parts = [f'<a href="{r}index.html">Home</a>']
    for label, href in trail[:-1]:
        parts.append(f'<a href="{r}{href}">{esc(label)}</a>')
    parts.append(esc(trail[-1][0]))
    return ('    <nav class="breadcrumb" aria-label="Breadcrumb">'
            + '<span>/</span>'.join(parts) + "</nav>\n")


# ==========================================================================
# JSON-LD blocks
# ==========================================================================


def ld_faq(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)},
            }
            for q, a in faq
        ],
    }


def ld_breadcrumb(trail):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"}]
    for i, (label, href) in enumerate(trail, start=2):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": label,
            "item": f"{SITE_URL}/{href}".replace("/index.html", "/"),
        })
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def ld_software(tool):
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": f"{tool['title']} — {SITE_NAME}",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Any (web browser)",
        "url": f"{SITE_URL}/tools/{tool['slug']}.html",
        "description": tool["meta_desc"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }


def ld_article(guide):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": guide["title"],
        "description": guide["meta_desc"],
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "datePublished": TODAY,
        "dateModified": TODAY,
        "mainEntityOfPage": f"{SITE_URL}/guides/{guide['slug']}.html",
    }


# ==========================================================================
# Page builders
# ==========================================================================


def build_home():
    cards = "\n".join(
        f"""      <li><a class="tool-card" href="tools/{t['slug']}.html">
        <strong>{esc(t['title'])}</strong>
        <span>{esc(t['card'])}</span>
      </a></li>"""
        for t in TOOLS
    )
    guide_cards = "\n".join(
        f"""      <li><a class="tool-card" href="guides/{g['slug']}.html">
        <strong>{esc(g['title'])}</strong>
        <span>{esc(g['description'])}</span>
      </a></li>"""
        for g in GUIDES
    )

    body = f"""    <div class="wrap">
      <h1>Text cleaning tools that never upload your text</h1>
      <p class="lede">{len(TOOLS)} focused tools for cleaning, converting and inspecting
      text. Everything runs inside your browser, so your data never reaches a
      server — and nothing breaks when you are offline.</p>

{ad_slot("top")}
      <h2 id="tools">All tools</h2>
      <ul class="tool-grid">
{cards}
      </ul>

      <div class="prose">
        <h2>Why these tools work differently</h2>
        <p>Most online text utilities send whatever you paste to a server, process
        it there, and send the result back. That is invisible from the interface,
        and for a shopping list it does not matter. For a customer export, a
        configuration file or an authentication token, it matters a great deal.</p>

        <p>DevClean ships the processing code to your browser instead and runs it
        locally. Your text is never transmitted, which removes the privacy question
        entirely and has a pleasant side effect: results are instant, because there
        is no network round trip and no server waking up from sleep.</p>

        <p>You do not have to take that on trust. Open your browser's developer
        tools, switch to the Network tab, and run any tool on this site — no request
        appears. Or load a page, disconnect from the internet, and keep working.</p>

{ad_slot("inline")}
        <h2>Guides</h2>
        <p>Longer pieces on the problems these tools exist to solve.</p>
      </div>

      <ul class="tool-grid">
{guide_cards}
      </ul>

      <div class="prose">
        <h2>Frequently asked questions</h2>
      </div>
      <div class="faq">
        <details><summary>Is DevClean free?</summary><div><p>Yes, every tool is free
        and there is no account to create. The site is supported by advertising.</p></div></details>
        <details><summary>Is my data stored or sent anywhere?</summary><div><p>No. All
        processing happens in your browser using JavaScript. Your text is never
        transmitted to any server, and nothing is stored beyond your current tab.</p></div></details>
        <details><summary>How much text can I process at once?</summary><div><p>Up to
        200,000 characters per run, which is roughly 30,000 words or 20,000 list
        items. For larger files, split the input or use the command-line
        alternatives described in the guides.</p></div></details>
        <details><summary>Do the tools work offline?</summary><div><p>Yes. Once a page
        has loaded, it keeps working with no connection, because there is nothing to
        fetch.</p></div></details>
        <details><summary>Is there an API?</summary><div><p>Yes — a small HTTP API is
        available for automating these operations in scripts and pipelines. See the
        <a href="api.html">API page</a>.</p></div></details>
      </div>

{ad_slot("bottom")}
    </div>
"""

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": SITE_URL + "/",
            "description": SITE_TAGLINE,
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Is DevClean free?",
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": "Yes, every tool is free and there is no account to create. The site is supported by advertising."}},
                {"@type": "Question", "name": "Is my data stored or sent anywhere?",
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": "No. All processing happens in your browser using JavaScript. Your text is never transmitted to any server."}},
                {"@type": "Question", "name": "How much text can I process at once?",
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": "Up to 200,000 characters per run, roughly 30,000 words or 20,000 list items."}},
                {"@type": "Question", "name": "Do the tools work offline?",
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": "Yes. Once a page has loaded it keeps working with no connection, because there is nothing to fetch."}},
            ],
        },
    ]

    write("index.html", page(
        0,
        f"{SITE_NAME} — {SITE_TAGLINE}",
        "Free browser-based tools to remove duplicate lines, clean extra spaces, "
        "convert lists to JSON, change text case, encode Base64 and more. Nothing is uploaded.",
        body, "index.html", json_ld=ld,
    ))


def build_tool_page(tool):
    trail = [("Tools", "index.html#tools"), (tool["title"], f"tools/{tool['slug']}.html")]
    related = [t for t in TOOLS if t["slug"] != tool["slug"]][:5]
    related_html = "\n".join(
        f'        <li><a href="{t["slug"]}.html">{esc(t["title"])}</a></li>' for t in related
    )

    body = f"""    <div class="wrap">
{breadcrumb(1, trail)}      <h1>{esc(tool['h1'])}</h1>
      <p class="lede">{esc(tool['lede'])}</p>

{render_tool(tool)}
{ad_slot("top")}
      <div class="prose">
{tool['body']}
      </div>

{ad_slot("inline")}
      <div class="prose">
{faq_html(tool['faq'])}      </div>

      <div class="related">
        <h2>Other tools</h2>
        <ul>
{related_html}
        </ul>
      </div>

{ad_slot("bottom")}
    </div>
"""

    write(f"tools/{tool['slug']}.html", page(
        1, tool["meta_title"], tool["meta_desc"], body,
        f"tools/{tool['slug']}.html",
        json_ld=[ld_software(tool), ld_faq(tool["faq"]), ld_breadcrumb(trail)],
        body_attrs=f' data-default-op="{esc(tool["ops"][0][0])}"',
    ))


def build_guide_page(guide):
    trail = [("Guides", "guides/index.html"), (guide["title"], f"guides/{guide['slug']}.html")]
    others = [g for g in GUIDES if g["slug"] != guide["slug"]]
    others_html = "\n".join(
        f'        <li><a href="{g["slug"]}.html">{esc(g["title"])}</a></li>' for g in others
    )

    body = f"""    <div class="wrap">
{breadcrumb(1, trail)}      <article class="prose">
        <h1>{esc(guide['title'])}</h1>
        <p class="meta-line">{guide['reading_time']} min read · Updated {TODAY}</p>

{ad_slot("top")}
{guide['body']}
      </article>

{ad_slot("inline")}
      <div class="related">
        <h2>More guides</h2>
        <ul>
{others_html}
        </ul>
      </div>

{ad_slot("bottom")}
    </div>
"""

    write(f"guides/{guide['slug']}.html", page(
        1, guide["meta_title"], guide["meta_desc"], body,
        f"guides/{guide['slug']}.html",
        json_ld=[ld_article(guide), ld_breadcrumb(trail)],
    ))


def build_guides_index():
    cards = "\n".join(
        f"""      <li><a class="tool-card" href="{g['slug']}.html">
        <strong>{esc(g['title'])}</strong>
        <span>{esc(g['description'])} · {g['reading_time']} min read</span>
      </a></li>"""
        for g in GUIDES
    )
    body = f"""    <div class="wrap">
{breadcrumb(1, [("Guides", "guides/index.html")])}      <h1>Guides</h1>
      <p class="lede">Longer articles on cleaning and converting text data —
      the reasoning behind the tools, and the alternatives worth knowing.</p>

{ad_slot("top")}
      <ul class="tool-grid">
{cards}
      </ul>

{ad_slot("bottom")}
    </div>
"""
    write("guides/index.html", page(
        1, f"Guides — {SITE_NAME}",
        "Practical guides on cleaning messy text data, removing duplicates, working "
        "with JSON arrays and why client-side tools protect your privacy.",
        body, "guides/index.html",
        json_ld=[ld_breadcrumb([("Guides", "guides/index.html")])],
    ))


def build_about():
    body = f"""    <div class="wrap">
{breadcrumb(0, [("About", "about.html")])}      <div class="prose">
        <h1>About DevClean</h1>

        <p>DevClean is a small collection of text-cleaning tools built and
        maintained by {esc(AUTHOR)}, an independent developer. It started as a single
        page for removing duplicate lines from lists, written because the existing
        options all wanted to upload the list somewhere first.</p>

        <h2>What it is for</h2>
        <p>The tools cover the unglamorous work that sits between getting data and
        using it: collapsing whitespace that arrived from a PDF, deduplicating a
        merged contact export, converting a column into a JSON array, decoding a
        Base64 token to see what is inside it. Each one is a small job that appears
        constantly and is tedious to do by hand.</p>

        <h2>How it works</h2>
        <p>Every operation runs as JavaScript inside your browser. When you press
        the button, no network request is made: the text is transformed in memory on
        your own machine and displayed back to you. This is verifiable — open your
        browser's developer tools, watch the Network tab, and run any tool. Nothing
        appears.</p>

        <p>That design has three consequences. Your data stays private by
        construction rather than by policy. Results are instant, because there is no
        round trip. And the tools keep working with no internet connection once the
        page has loaded.</p>

        <h2>Open source</h2>
        <p>The complete source is on
        <a href="https://github.com/AlbertoMariaPareti/devclean" rel="noopener">GitHub</a>,
        including the processing engine, so you can read exactly what each operation
        does rather than taking the description on trust. Bug reports and suggestions
        for new tools are welcome through the issue tracker.</p>

        <h2>How it is funded</h2>
        <p>DevClean is free and has no account system. Running costs are covered by
        advertising displayed alongside the tools. Ads are placed so they do not
        interfere with using the site, and no advertiser has any access to the text
        you paste — that text never leaves your browser, so there is nothing to
        share even in principle.</p>

        <h2>Contact</h2>
        <p>For questions, corrections or requests, email
        <a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a> or open an
        issue on GitHub.</p>
      </div>
{ad_slot("bottom")}
    </div>
"""
    write("about.html", page(
        0, f"About — {SITE_NAME}",
        f"DevClean is a set of free, browser-based text cleaning tools built by {AUTHOR}. "
        "Open source, privacy-preserving, no uploads.",
        body, "about.html",
        json_ld=[ld_breadcrumb([("About", "about.html")])],
    ))


def build_privacy():
    body = f"""    <div class="wrap">
{breadcrumb(0, [("Privacy", "privacy.html")])}      <div class="prose">
        <h1>Privacy policy</h1>
        <p class="meta-line">Last updated {TODAY}</p>

        <h2>The text you paste</h2>
        <p><strong>Text you enter into any tool on this site is never transmitted
        anywhere.</strong> All processing happens locally in your browser using
        JavaScript. The text is held in your browser's memory for as long as the page
        is open and is discarded when you close or reload the tab. It is not sent to
        a server, not written to a database, not logged, and not accessible to us or
        to any third party.</p>

        <p>You can verify this: open your browser's developer tools, switch to the
        Network tab, and use any tool. No request is made. Alternatively, load a page
        and then disconnect from the internet — the tools continue to work.</p>

        <h2>Analytics</h2>
        <p>This site uses Google Analytics to understand which pages are visited and
        how many people use them. Analytics records page views, approximate location
        derived from IP address, browser and device type, and referring site. It also
        records which tool operation was run — the name of the operation only, never
        the text it was run on.</p>
        <p>Google Analytics sets cookies to distinguish returning visitors. You can
        opt out with Google's
        <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener nofollow">browser
        add-on</a>, or by blocking analytics scripts in your browser or an extension.
        The tools work identically either way.</p>

        <h2>Advertising</h2>
        <p>This site displays advertising to cover its running costs. Advertising
        partners may set cookies or use similar technologies to measure ad
        performance and, where permitted, to show more relevant ads. These partners
        receive standard request information such as your IP address, browser type
        and the page being viewed.</p>
        <p><strong>Advertising partners have no access to the text you paste into the
        tools.</strong> That text never leaves your browser, so there is nothing to
        share with anyone.</p>
        <p>You can manage personalised advertising through
        <a href="https://myadcenter.google.com/" rel="noopener nofollow">Google's Ad
        Settings</a>, and review how Google uses data from partner sites at
        <a href="https://policies.google.com/technologies/partner-sites" rel="noopener nofollow">
        policies.google.com/technologies/partner-sites</a>.</p>

        <h2>Local storage</h2>
        <p>The site stores one item in your browser's local storage: your choice of
        light or dark theme. It contains no personal information, is never sent
        anywhere, and can be cleared at any time through your browser settings.</p>

        <h2>Hosting</h2>
        <p>The site is served as static files by GitHub Pages. As with any web host,
        GitHub processes standard server request data, including IP addresses, to
        deliver the pages. See
        <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener nofollow">GitHub's
        privacy statement</a>.</p>

        <h2>Your rights</h2>
        <p>Because the tools do not collect or store your text, there is no personal
        data of that kind to access, correct or delete. For analytics and advertising
        data, which are handled by Google, use the opt-out mechanisms linked above.
        If you are in the EU or UK and have a question about data handled by this
        site, email <a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a>.</p>

        <h2>Children</h2>
        <p>This site is a general-purpose developer utility and is not directed at
        children under 13. No information is knowingly collected from them.</p>

        <h2>Changes</h2>
        <p>If this policy changes, the date at the top of this page will be updated.
        Material changes will be noted here.</p>

        <h2>Contact</h2>
        <p>Questions about this policy:
        <a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a>.</p>
      </div>
    </div>
"""
    write("privacy.html", page(
        0, f"Privacy policy — {SITE_NAME}",
        "DevClean processes all text locally in your browser and never uploads it. "
        "Details on analytics, advertising cookies and your options.",
        body, "privacy.html",
    ))


def build_api():
    ops_rows = "\n".join(
        f"          <tr><td><code>{esc(op)}</code></td><td>{esc(label)}</td><td>{esc(t['title'])}</td></tr>"
        for t in TOOLS for op, label in t["ops"]
    )
    body = f"""    <div class="wrap">
{breadcrumb(0, [("API", "api.html")])}      <div class="prose">
        <h1>Developer API</h1>
        <p class="lede">The same operations as the website, over HTTP, for scripts
        and pipelines. Free to use, no key required.</p>

        <div class="callout">
          <p>The website itself does not use this API — it processes everything in
          your browser. The API exists for automation: cleaning files in a build
          step, normalising data in a scheduled job, or calling from a language
          without a convenient text-processing library.</p>
        </div>

        <h2>Endpoint</h2>
        <pre><code>POST {API_BASE_URL}/api/process
Content-Type: application/json

{{
  "text": "apple\\nbanana\\napple",
  "option": "remove_duplicates",
  "options": {{ "ignoreCase": true }}
}}</code></pre>

        <p>The response is a JSON object:</p>
        <pre><code>{{ "processed_text": "apple\\nbanana", "operation": "remove_duplicates" }}</code></pre>

        <h2>Example with curl</h2>
        <pre><code>curl -X POST {API_BASE_URL}/api/process \\
  -H "Content-Type: application/json" \\
  -d '{{"text":"a\\nb\\na","option":"remove_duplicates"}}'</code></pre>

        <h2>Example in Python</h2>
        <pre><code>import requests

r = requests.post(
    "{API_BASE_URL}/api/process",
    json={{"text": open("list.txt").read(), "option": "remove_duplicates"}},
    timeout=30,
)
print(r.json()["processed_text"])</code></pre>

        <h2>Available operations</h2>
        <p>Discover them at runtime with <code>GET {API_BASE_URL}/api/operations</code>,
        or use the table below.</p>
        <table>
          <thead><tr><th>option</th><th>Does</th><th>Web version</th></tr></thead>
          <tbody>
{ops_rows}
          </tbody>
        </table>

        <h2>Limits and errors</h2>
        <ul>
          <li>Maximum 200,000 characters per request — larger input returns HTTP 413.</li>
          <li>An unknown <code>option</code> returns HTTP 400 with the list of valid values.</li>
          <li><code>GET /api/health</code> returns <code>{{"status":"ok"}}</code> and is useful for waking a sleeping instance.</li>
        </ul>

        <div class="callout">
          <p><strong>Free hosting caveat:</strong> the public instance runs on a free
          tier that sleeps after inactivity, so the first request after a quiet period
          can take up to a minute. For production use, run your own instance — the
          server is a single Python file in the
          <a href="https://github.com/AlbertoMariaPareti/devclean" rel="noopener">repository</a>.</p>
        </div>

        <h2>Self-hosting</h2>
        <pre><code>git clone https://github.com/AlbertoMariaPareti/devclean.git
cd devclean
pip install -r requirements.txt
uvicorn main:app --reload</code></pre>
      </div>
{ad_slot("bottom")}
    </div>
"""
    write("api.html", page(
        0, f"Developer API — {SITE_NAME}",
        "Free HTTP API for text cleaning: remove duplicates, clean whitespace, "
        "convert to JSON, change case, encode Base64. No API key required.",
        body, "api.html",
        json_ld=[ld_breadcrumb([("API", "api.html")])],
    ))


def build_404():
    links = "\n".join(
        f'        <li><a href="/devclean/tools/{t["slug"]}.html">{esc(t["title"])}</a></li>'
        for t in TOOLS[:6]
    )
    body = f"""    <div class="wrap">
      <div class="prose">
        <h1>Page not found</h1>
        <p>That page does not exist — it may have been renamed or the link may be
        incomplete. Here are the most used tools:</p>
        <ul>
{links}
        </ul>
        <p><a href="/devclean/">Back to all tools →</a></p>
      </div>
    </div>
"""
    write("404.html", page(
        0, f"Page not found — {SITE_NAME}",
        "The page you are looking for does not exist.", body, "404.html",
    ))


def build_redirect():
    """front.html was the original entry point; keep old links working."""
    write("front.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redirecting — {SITE_NAME}</title>
  <link rel="canonical" href="{SITE_URL}/">
  <meta name="robots" content="noindex, follow">
  <meta http-equiv="refresh" content="0; url=./index.html">
  <script>location.replace('./index.html');</script>
</head>
<body>
  <p>This page has moved. <a href="./index.html">Continue to {SITE_NAME}</a>.</p>
</body>
</html>
""")


def build_sitemap():
    urls = [("", "1.0", "weekly"), ("about.html", "0.5", "monthly"),
            ("api.html", "0.7", "monthly"), ("privacy.html", "0.3", "yearly"),
            ("guides/", "0.8", "monthly")]
    urls += [(f"tools/{t['slug']}.html", "0.9", "monthly") for t in TOOLS]
    urls += [(f"guides/{g['slug']}.html", "0.7", "monthly") for g in GUIDES]

    entries = "\n".join(
        f"""  <url>
    <loc>{SITE_URL}/{path}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>"""
        for path, prio, freq in urls
    )
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
""")


def build_robots():
    write("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
""")


def build_ads_txt():
    if not ADSENSE_CLIENT:
        write("ads.txt", (
            "# Once AdSense approves your account, replace the line below with your\n"
            "# real publisher ID (the pub-... part of your ca-pub-... client ID).\n"
            "# google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n"
        ))
    else:
        pub = ADSENSE_CLIENT.replace("ca-", "")
        write("ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")


def build_og_image():
    """A simple generated share image, so links do not preview as a blank box."""
    write("assets/og-image.svg", f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0d1117"/>
  <rect x="0" y="0" width="1200" height="8" fill="#3fb950"/>
  <text x="80" y="270" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="86" font-weight="700" fill="#e6edf3">{SITE_NAME}</text>
  <text x="80" y="350" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="40" fill="#9aa7b4">{SITE_TAGLINE}</text>
  <text x="80" y="430" font-family="ui-monospace, Menlo, monospace" font-size="30" fill="#3fb950">Nothing is uploaded. Everything runs in your browser.</text>
  <text x="80" y="540" font-family="-apple-system, Segoe UI, Roboto, sans-serif" font-size="26" fill="#6e7b8a">{len(TOOLS)} tools · free · open source</text>
</svg>
""")


def build_nojekyll():
    # GitHub Pages skips files starting with an underscore unless this exists.
    write(".nojekyll", "")


# ==========================================================================
# Main
# ==========================================================================


def main():
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    # Copy static assets across untouched.
    src_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    shutil.copytree(src_assets, os.path.join(OUT_DIR, "assets"))

    build_home()
    for tool in TOOLS:
        build_tool_page(tool)
    build_guides_index()
    for guide in GUIDES:
        build_guide_page(guide)
    build_about()
    build_privacy()
    build_api()
    build_404()
    build_redirect()
    build_sitemap()
    build_robots()
    build_ads_txt()
    build_og_image()
    build_nojekyll()

    pages = sum(len(files) for _, _, files in os.walk(OUT_DIR))
    print(f"Built {pages} files into {OUT_DIR}/")
    print(f"  {len(TOOLS)} tool pages, {len(GUIDES)} guides")
    print(f"  AdSense: {'ENABLED (' + ADSENSE_CLIENT + ')' if ADSENSE_CLIENT else 'off — set ADSENSE_CLIENT to enable'}")


if __name__ == "__main__":
    main()
