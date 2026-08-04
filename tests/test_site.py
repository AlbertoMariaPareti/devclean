"""Post-build checks: links, metadata uniqueness, JSON-LD validity, accessibility basics."""
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


OUT = os.path.join(ROOT, "docs")
errors, warnings = [], []

pages = []
for root, _, files in os.walk(OUT):
    for f in files:
        if f.endswith(".html"):
            pages.append(os.path.join(root, f))
pages.sort()

titles, descs, canons = {}, {}, {}

class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.inputs = [], [], []
        self.in_title = False; self.title = ""
        self.desc = None; self.canonical = None
        self.h1 = 0; self.labels = set(); self.ids = []
        self.jsonld = []; self._in_ld = False; self._ld = ""
        self.lang = None; self._label_depth = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self.in_title = True
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "link":
            if a.get("rel") == "canonical": self.canonical = a.get("href")
            if a.get("rel") == "stylesheet": self.links.append(a.get("href"))
        if tag == "script" and a.get("src"): self.links.append(a["src"])
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True; self._ld = ""
        if tag == "meta" and a.get("name") == "description": self.desc = a.get("content")
        if tag == "img": self.imgs.append(a)
        if tag == "h1": self.h1 += 1
        if tag == "label":
            self._label_depth += 1
            if a.get("for"): self.labels.add(a["for"])
        if a.get("id"): self.ids.append(a["id"])
        if tag in ("input","textarea","select","button"):
            # An input nested inside <label> is implicitly labelled — valid HTML,
            # and the accessible name comes from the label's text.
            self.inputs.append((tag, a, self._label_depth > 0))
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "label" and self._label_depth: self._label_depth -= 1
        if tag == "script" and self._in_ld:
            self._in_ld = False; self.jsonld.append(self._ld)
    def handle_data(self, d):
        if self.in_title: self.title += d
        if self._in_ld: self._ld += d

for path in pages:
    rel_page = os.path.relpath(path, OUT)
    src = open(path, encoding="utf-8").read()
    c = Collector(); c.feed(src)

    if "noindex" in src:
        pass  # redirect stub, skip uniqueness checks
    else:
        t = c.title.strip()
        if not t: errors.append(f"{rel_page}: missing <title>")
        elif t in titles: errors.append(f"{rel_page}: duplicate title, same as {titles[t]}")
        else: titles[t] = rel_page
        if len(t) > 65: warnings.append(f"{rel_page}: title {len(t)} chars (>65 may truncate in Google)")

        d = (c.desc or "").strip()
        if not d: errors.append(f"{rel_page}: missing meta description")
        elif d in descs: errors.append(f"{rel_page}: duplicate description, same as {descs[d]}")
        else: descs[d] = rel_page
        if len(d) > 160: warnings.append(f"{rel_page}: description {len(d)} chars (>160)")

        if not c.canonical: errors.append(f"{rel_page}: missing canonical")
        elif c.canonical in canons: errors.append(f"{rel_page}: duplicate canonical with {canons[c.canonical]}")
        else: canons[c.canonical] = rel_page

        if c.h1 != 1: errors.append(f"{rel_page}: has {c.h1} <h1> (must be exactly 1)")

    if not c.lang: errors.append(f"{rel_page}: <html> missing lang")

    for img in c.imgs:
        if "alt" not in img: errors.append(f"{rel_page}: <img> without alt")

    # form controls need an accessible name
    for tag, a, wrapped in c.inputs:
        if tag in ("input","textarea","select") and a.get("type") not in ("hidden","radio","checkbox"):
            has = (wrapped or a.get("id") in c.labels
                   or a.get("aria-label") or a.get("aria-labelledby"))
            if not has: errors.append(f"{rel_page}: <{tag} id={a.get('id')}> has no accessible name")

    for block in c.jsonld:
        try: json.loads(block)
        except Exception as e: errors.append(f"{rel_page}: invalid JSON-LD ({e})")

    # internal links must resolve
    for href in c.links:
        if not href or href.startswith(("http://","https://","mailto:","data:","#")): continue
        target = href.split("#")[0].split("?")[0]
        if not target: continue
        if target.startswith("/"):
            resolved = os.path.join(OUT, target.lstrip("/").replace("devclean/","",1))
        else:
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
        if not os.path.exists(resolved):
            errors.append(f"{rel_page}: broken link -> {href}")

# sitemap must list exactly the indexable pages
sitemap = open(os.path.join(OUT,"sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>(.*?)</loc>", sitemap)
if len(locs) != len(set(locs)): errors.append("sitemap.xml: duplicate <loc> entries")
indexable = [p for p in pages if "noindex" not in open(p,encoding='utf-8').read()
             and not p.endswith("404.html")]
if len(locs) != len(indexable):
    warnings.append(f"sitemap has {len(locs)} urls but {len(indexable)} indexable pages exist")

print(f"Checked {len(pages)} pages\n")
for w in warnings: print("WARN   " + w)
if warnings: print()
for e in errors: print("ERROR  " + e)
print(f"\n{len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
