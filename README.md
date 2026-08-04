# DevClean

**Free online text and code cleaning tools — nothing you paste ever leaves your browser.**

🔗 **Live site:** https://albertomariapareti.github.io/devclean/

DevClean is a collection of 10 focused tools for cleaning, converting and inspecting text: removing duplicate lines, collapsing whitespace, converting lists to JSON, changing case, encoding Base64, stripping HTML and more.

Every operation runs as JavaScript **in your browser**. Your text is never uploaded, which means the tools are private by construction, instant (no network round trip), and fully functional offline once a page has loaded.

---

## Tools

| Tool | What it does |
|---|---|
| [Remove Duplicate Lines](https://albertomariapareti.github.io/devclean/tools/remove-duplicate-lines.html) | Strip repeated lines, preserving original order |
| [Remove Extra Spaces](https://albertomariapareti.github.io/devclean/tools/remove-extra-spaces.html) | Collapse double spaces, trailing whitespace, blank lines |
| [List to JSON Array](https://albertomariapareti.github.io/devclean/tools/list-to-json-array.html) | Lines → valid JSON array, object, or CSV → JSON |
| [Case Converter](https://albertomariapareti.github.io/devclean/tools/case-converter.html) | UPPER, lower, Title, Sentence, camelCase, PascalCase, snake_case, kebab-case, CONSTANT_CASE |
| [Sort Lines](https://albertomariapareti.github.io/devclean/tools/sort-lines.html) | Natural A–Z sorting, by length, reverse, shuffle, number, prefix/suffix |
| [Tabs to Spaces](https://albertomariapareti.github.io/devclean/tools/tabs-to-spaces.html) | Convert indentation both ways, respecting tab stops |
| [Base64 Encode/Decode](https://albertomariapareti.github.io/devclean/tools/base64-encode-decode.html) | UTF-8 safe — handles accents, CJK and emoji |
| [URL Encode/Decode](https://albertomariapareti.github.io/devclean/tools/url-encode-decode.html) | Percent encoding, component and full-URL modes |
| [Remove HTML Tags](https://albertomariapareti.github.io/devclean/tools/remove-html-tags.html) | Strip to plain text, escape and unescape entities |
| [Word & Character Counter](https://albertomariapareti.github.io/devclean/tools/word-character-counter.html) | Full statistics, plus email/URL/number extraction |

Plus four long-form [guides](https://albertomariapareti.github.io/devclean/guides/) on cleaning text data.

---

## Project structure

```
devclean/
├── assets/
│   ├── tools.js         # Processing engine — pure functions, no DOM, no network
│   ├── app.js           # UI layer, shared by every tool page
│   └── style.css        # Single stylesheet, dark/light theme
├── src/
│   └── content.py       # All page copy: tool definitions and guide articles
├── tests/
│   ├── test_parity.py   # Asserts the JS engine and Python API agree exactly
│   └── test_site.py     # Link, metadata, JSON-LD and accessibility checks
├── build.py             # Static site generator → docs/
├── main.py              # FastAPI service (the optional automation API)
├── requirements.txt
└── docs/                # GENERATED — this is what GitHub Pages serves
```

`docs/` is generated output. Never edit it by hand; edit the source and rebuild.

---

## Building the site

```bash
python build.py
```

That regenerates everything into `docs/`: all 21 pages, `sitemap.xml`, `robots.txt`, `ads.txt` and the Open Graph share image. There are no dependencies — it uses only the Python standard library.

To preview locally:

```bash
python -m http.server 8000 --directory docs
# then open http://localhost:8000
```

### GitHub Pages setup

In the repository settings, under **Pages**, set the source to **Deploy from a branch**, branch `main`, folder **`/docs`**. Pushing to `main` then publishes automatically.

The old entry point `front.html` is preserved as a redirect to `index.html`, so any existing links and search-engine results keep working.

---

## Configuration

Everything you would normally change lives in the `CONFIG` block at the top of `build.py`:

| Setting | Purpose |
|---|---|
| `SITE_URL` | Used for canonical URLs, Open Graph tags and the sitemap. Change this one value when moving to a custom domain. |
| `GA_MEASUREMENT_ID` | Google Analytics 4 ID. Empty string removes analytics entirely. |
| `ADSENSE_CLIENT` | Your `ca-pub-…` publisher ID. **Empty until approved** — see below. |
| `ADSENSE_SLOT_*` | The three ad unit slot IDs (top, inline, bottom). |
| `SUPPORT_URL` | Optional donation link shown in the footer. Empty hides it. |
| `API_BASE_URL` | Where the public API is hosted, shown on the API page. |

### Enabling AdSense

The ad slots are already positioned on every page but produce **no markup at all** while `ADSENSE_CLIENT` is empty. This is deliberate: empty boxes labelled "Advertisement" are a documented reason for AdSense review rejection, so the site should go through review without them.

Once your account is approved:

1. Set `ADSENSE_CLIENT` to your `ca-pub-…` ID.
2. Create three display ad units in AdSense and paste their slot IDs into `ADSENSE_SLOT_TOP`, `ADSENSE_SLOT_INLINE` and `ADSENSE_SLOT_BOTTOM`.
3. Run `python build.py` and commit.

Every page picks up real ad units in the reserved slots, and `ads.txt` is generated with your publisher ID automatically. The slots reserve their height in CSS so a loading ad cannot shift the page — layout shift is a Core Web Vitals ranking factor.

---

## The API

The website does **not** use this service. It exists for automating the same operations in scripts, build steps and scheduled jobs.

```bash
curl -X POST https://devclean-backend.onrender.com/api/process \
  -H "Content-Type: application/json" \
  -d '{"text":"a\nb\na","option":"remove_duplicates","options":{"ignoreCase":true}}'
```

```json
{ "processed_text": "a\nb", "operation": "remove_duplicates" }
```

- `GET /api/operations` — list all 40 operation ids
- `GET /api/health` — health check, also useful for waking a sleeping free-tier instance
- `GET /docs` — interactive OpenAPI documentation

Run it locally:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Tests

```bash
python tests/test_parity.py   # JS engine vs Python API, operation by operation
python tests/test_site.py     # run after build.py
```

**`test_parity.py`** runs 41 cases through both the browser engine (`assets/tools.js`, executed under Node) and the API (`main.py`) and asserts byte-identical output. The two implementations exist for different reasons and it would be easy for them to drift; this makes drift a test failure.

**`test_site.py`** checks the generated site for broken internal links, duplicate or missing titles, descriptions and canonical URLs, pages with the wrong number of `<h1>` elements, malformed JSON-LD, form controls without an accessible name, and sitemap consistency.

---

## Design decisions

**Why client-side?** Every operation here is a pure function of text the user already has. A server could contribute nothing except latency and a copy of the user's data. Removing it made the tools instant, eliminated the free-tier cold start that made the first visitor of the day wait up to a minute, and turned the privacy claim into something verifiable rather than promised — open the Network tab and watch, or disconnect from the internet and keep working.

**Why a build step for a static site?** 21 pages share one header, footer and navigation. Without a generator, adding a nav item means editing 21 files. The output is still plain static HTML with no runtime dependency.

**Why separate pages per tool?** Each tool answers a different search query. One page targeting ten intents ranks for none of them well; ten pages each targeting one intent is how this kind of site actually gets found.

---

## Privacy

Text entered into any tool is processed locally and never transmitted. The site uses Google Analytics for page-view statistics (which records *which* operation was run, never the text it was run on) and displays advertising. Full details in the [privacy policy](https://albertomariapareti.github.io/devclean/privacy.html).

---

## Contributing

Bug reports and suggestions for new tools are welcome via [issues](https://github.com/AlbertoMariaPareti/devclean/issues).

Adding a tool means: implement the operation in `assets/tools.js`, mirror it in `main.py`, add a case to `tests/test_parity.py`, then add the page definition to `src/content.py` and rebuild.

---

## License

No license has been specified yet. All rights reserved by the author unless stated otherwise.
