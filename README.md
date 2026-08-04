# DevClean

[![CI](https://github.com/AlbertoMariaPareti/devclean/actions/workflows/ci.yml/badge.svg)](https://github.com/AlbertoMariaPareti/devclean/actions/workflows/ci.yml)
[![Live site](https://img.shields.io/badge/live-albertomariapareti.github.io%2Fdevclean-1f4e79)](https://albertomariapareti.github.io/devclean/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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
├── .github/workflows/
│   └── ci.yml           # Lint, parity, API and site checks on every push
├── assets/
│   ├── tools.js         # Processing engine — pure functions, no DOM, no network
│   ├── app.js           # UI layer, shared by every tool page
│   └── style.css        # Single stylesheet, dark/light theme
├── src/
│   └── content.py       # All page copy: tool definitions and guide articles
├── tests/
│   ├── test_parity.py   # Asserts the JS engine and Python API agree exactly
│   ├── test_api.py      # Status codes, error mapping, rate limiting
│   └── test_site.py     # Link, metadata, JSON-LD and accessibility checks
├── build.py             # Static site generator → docs/
├── main.py              # FastAPI service (the optional automation API)
├── ruff.toml            # Lint configuration
├── requirements.txt     # Runtime dependencies for the API
├── requirements-dev.txt # ...plus what the tests need
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

**Limits.** Requests are capped at 200,000 characters and **60 requests per minute per IP** on `/api/process`; over the limit the API answers `429` with a `Retry-After` header. The limit is held in memory in the process, so it resets on restart and does not coordinate across replicas — enough for one small instance, and the wrong place for it in a scaled deployment, where it belongs in the proxy. The website is not affected: it never calls the API.

**Errors.** Invalid input returns `400` with a message identical to the one the browser tool shows for the same input (`tests/test_parity.py` asserts this). The operations themselves are plain functions that raise `OperationError` — they don't import anything from FastAPI, so they can be used from a script or a notebook without dragging the web layer along. The route is what turns that into a status code.

Run it locally:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Tests

```bash
pip install -r requirements-dev.txt

python tests/test_parity.py   # JS engine vs Python API, operation by operation
python tests/test_api.py      # status codes, error mapping, rate limiting
python tests/test_site.py     # run after build.py
```

All three run on every push via [GitHub Actions](.github/workflows/ci.yml), together with `ruff` and a check that the committed `docs/` still matches what `build.py` produces.

**`test_parity.py`** runs 47 cases through both the browser engine (`assets/tools.js`, executed under Node) and the API (`main.py`) and asserts byte-identical output — including the failures: an invalid Base64 string must be rejected on both sides with the same message. The two implementations exist for different reasons and it would be easy for them to drift; this makes drift a test failure. It has already caught three real divergences: Python rejected Base64 with stripped padding that the browser accepted, `url_decode` ignored the `component` option entirely, and malformed percent-escapes were silently mangled by `urllib` instead of raising.

**`test_api.py`** covers the HTTP layer that parity does not see: 400 on unknown operations and invalid input, 413 over the size cap, 429 past the rate limit with `Retry-After`, and that the operations raise `OperationError` rather than `HTTPException`.

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

[MIT](LICENSE) — © 2026 Alberto Maria Pareti.
