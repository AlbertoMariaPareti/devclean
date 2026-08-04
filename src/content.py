"""
DevClean — site content.

All page copy lives here so build.py stays pure templating logic.
Every tool page targets one distinct search intent; text is written once
and never duplicated across pages (duplicate boilerplate is the single most
common reason thin tool sites fail AdSense review and rank poorly).
"""

# --------------------------------------------------------------------------
# Tools. Each entry becomes /tools/<slug>.html
#
#   ops       — list of (operation_id, button_label). One = no chip row.
#   settings  — extra controls rendered above the buttons.
#   body      — HTML content shown under the tool (unique per page).
#   faq       — list of (question, answer_html); also emitted as FAQPage JSON-LD.
# --------------------------------------------------------------------------

TOOLS = [
    {
        "slug": "remove-duplicate-lines",
        "title": "Remove Duplicate Lines",
        "meta_title": "Remove Duplicate Lines Online — Free Deduplication Tool",
        "meta_desc": (
            "Paste a list and remove duplicate lines instantly, keeping the original "
            "order. Case-insensitive matching optional. Runs in your browser — no upload."
        ),
        "keyword": "remove duplicate lines",
        "card": "Strip repeated lines from a list while keeping the original order.",
        "h1": "Remove Duplicate Lines",
        "lede": (
            "Paste a list, get it back with every repeated line removed. The first "
            "occurrence of each line is kept in its original position."
        ),
        "ops": [
            ("remove_duplicates", "Remove duplicates"),
            ("keep_duplicates", "Show only duplicates"),
        ],
        "settings": [
            {"type": "checkbox", "opt": "ignoreCase", "label": "Ignore case"},
            {"type": "checkbox", "opt": "ignoreWhitespace", "label": "Ignore leading/trailing spaces"},
        ],
        "sample": "apple\\nbanana\\napple\\ncherry\\nBanana\\ncherry\\ndate",
        "body": """
<h2>What this tool does</h2>
<p>Deduplication sounds trivial until you try it on real data. The two things
people usually get wrong are order and near-matches. This tool keeps the
<strong>first</strong> occurrence of every line exactly where it was, rather than
sorting the list as a side effect, because in most real lists the order carries
meaning — priority, chronology, or simply the order a colleague typed things in.</p>

<p>The two optional toggles handle near-matches. <em>Ignore case</em> treats
<code>Banana</code> and <code>banana</code> as the same entry, which is what you
almost always want for names, tags and email addresses. <em>Ignore leading and
trailing spaces</em> catches the invisible culprit behind most "but these look
identical!" moments: a stray space picked up from a spreadsheet cell or a copied
table column.</p>

<h2>Show only duplicates</h2>
<p>The second mode inverts the job: instead of removing repeats it shows you
<em>only</em> the lines that appear more than once, one entry per repeated value.
This is the fast way to answer "which entries are duplicated?" before you decide
what to do about them — useful when you are auditing a mailing list, checking for
double-booked IDs, or looking for accidentally re-imported rows.</p>

<h2>When you would reach for this</h2>
<ul>
  <li><strong>Mailing lists and CRM exports.</strong> Merged exports from two sources
  almost always overlap. Deduplicating before import stops you from emailing the
  same person twice and, on most platforms, from paying for the same contact twice.</li>
  <li><strong>Log files.</strong> A repeated stack trace tells you an error is
  frequent, but when you are trying to work out how many <em>distinct</em> errors
  you have, collapsing to unique lines turns thousands of lines into a readable
  handful.</li>
  <li><strong>Keyword and tag lists.</strong> Keyword research tools produce
  overlapping sets by design; deduplicating with case-insensitivity on is usually
  the first step before any analysis.</li>
  <li><strong>Config and dependency files.</strong> Duplicate entries are often
  harmless but occasionally shadow each other in confusing ways. Spotting them is
  easier than debugging them.</li>
</ul>

<div class="callout">
<p><strong>A note on very large lists.</strong> Because everything runs locally, the
practical limit is your browser's memory rather than an upload cap. Lists in the
tens of thousands of lines process in well under a second on ordinary hardware.</p>
</div>

<h2>How it compares to the alternatives</h2>
<p>In a spreadsheet you would use <em>Data → Remove duplicates</em>, which works
well but forces your data into a column and often reformats it on the way in and
out — numbers become dates, leading zeros vanish. On the command line
<code>sort -u</code> is one keystroke but it sorts, destroying the original order;
the order-preserving version is <code>awk '!seen[$0]++'</code>, which is precise
but not something most people keep in their head. This tool is the middle ground:
order-preserving by default, nothing to remember, nothing to install.</p>
""",
        "faq": [
            ("Does removing duplicates change the order of my lines?",
             "No. The first occurrence of each line stays exactly where it was, and later "
             "repeats are dropped. If you want a sorted result, run the output through the "
             "sort tool afterwards."),
            ("Can it treat uppercase and lowercase as the same line?",
             "Yes. Turn on <em>Ignore case</em> and <code>Apple</code>, <code>APPLE</code> "
             "and <code>apple</code> collapse into a single entry — the first spelling that "
             "appeared is the one kept."),
            ("Why do two lines that look identical survive deduplication?",
             "Almost always invisible whitespace: a trailing space, a tab, or a non-breaking "
             "space pasted from a web page. Turn on <em>Ignore leading/trailing spaces</em>, "
             "or clean the text first with the extra-spaces tool."),
            ("Is my data uploaded anywhere?",
             "No. The deduplication runs entirely in your browser using JavaScript. Your text "
             "is never sent to a server, which also means the tool keeps working offline once "
             "the page has loaded."),
        ],
    },
    {
        "slug": "remove-extra-spaces",
        "title": "Remove Extra Spaces",
        "meta_title": "Remove Extra Spaces & Blank Lines from Text — Free Online Tool",
        "meta_desc": (
            "Collapse double spaces, strip trailing whitespace and delete empty lines "
            "in one click. Indentation is preserved. Free, private, browser-based."
        ),
        "keyword": "remove extra spaces",
        "card": "Collapse double spaces, trailing whitespace and empty lines.",
        "h1": "Remove Extra Spaces and Blank Lines",
        "lede": (
            "Clean up text that has been copied between apps: repeated spaces collapse "
            "to one, trailing whitespace disappears, and blank lines are removed."
        ),
        "ops": [
            ("clean_spaces", "Clean everything"),
            ("trim_lines", "Trim line ends only"),
            ("collapse_blank_lines", "Collapse blank lines"),
            ("remove_blank_lines", "Delete all blank lines"),
        ],
        "settings": [
            {"type": "checkbox", "opt": "keepIndent", "label": "Preserve indentation", "checked": True},
        ],
        "sample": "  Hello    world  \\n\\n\\n\\tThis   line\\t\\thas tabs\\n\\n   Trailing spaces here   ",
        "body": """
<h2>Four levels of cleaning</h2>
<p>"Extra whitespace" covers several different problems, and fixing all of them at
once is not always what you want. That is why this page offers four modes rather
than a single button.</p>

<table>
  <thead><tr><th>Mode</th><th>What it changes</th></tr></thead>
  <tbody>
    <tr><td>Clean everything</td><td>Collapses runs of spaces and tabs, strips trailing whitespace, removes every blank line</td></tr>
    <tr><td>Trim line ends only</td><td>Removes leading and trailing whitespace from each line, leaves the rest untouched</td></tr>
    <tr><td>Collapse blank lines</td><td>Turns runs of two or more blank lines into exactly one, keeping paragraph breaks</td></tr>
    <tr><td>Delete all blank lines</td><td>Removes every empty line, producing a solid block</td></tr>
  </tbody>
</table>

<h2>Why indentation is preserved by default</h2>
<p>Most whitespace cleaners collapse <em>all</em> repeated spaces, including the
ones at the start of a line. For prose that is fine. For anything
indentation-sensitive — Python, YAML, Markdown lists, nested JSON — it is
destructive, and the damage is not obvious until the file fails to parse.</p>

<p>DevClean therefore separates leading whitespace from the rest of the line. The
indentation stays exactly as it was; only the spaces <em>inside</em> the line get
collapsed. If you genuinely want a flat, fully-collapsed result, switch off
<em>Preserve indentation</em>.</p>

<h2>Where the mess comes from</h2>
<p>Text picks up junk whitespace whenever it crosses an application boundary.
Copying from a PDF inserts spaces where the layout engine had letter-spacing.
Pasting from Word brings non-breaking spaces that look identical to normal ones
but do not match a plain space in search-and-replace. Exporting from a spreadsheet
pads cells to align columns. Wrapping an email at 72 characters leaves trailing
spaces at every break. None of these are visible, and all of them break exact
comparisons later on.</p>

<div class="callout">
<p><strong>Tip:</strong> if you are about to compare two lists, deduplicate them,
or import them into a database, run this tool first. A large share of "these
should have matched" problems are one invisible trailing space.</p>
</div>

<h2>Collapsing versus deleting blank lines</h2>
<p>The distinction matters more than it looks. In prose, blank lines are paragraph
boundaries: deleting them all fuses your paragraphs into a wall of text, whereas
collapsing runs of them to one keeps the structure while removing the gaps. In a
list of values the opposite is true — every blank line is noise and you want them
all gone. Pick the mode that matches what the blank lines actually mean in your
document.</p>
""",
        "faq": [
            ("Will this break my code indentation?",
             "Not with <em>Preserve indentation</em> switched on, which is the default. "
             "Leading spaces and tabs are left byte-for-byte intact; only whitespace inside "
             "the line is collapsed. Switch the option off if you deliberately want a flat result."),
            ("What is the difference between collapsing and deleting blank lines?",
             "Collapsing turns runs of two or more blank lines into exactly one, so paragraph "
             "breaks survive. Deleting removes every blank line, which is what you want for a "
             "list of values but not for prose."),
            ("Does it handle tabs as well as spaces?",
             "Yes. Runs of spaces and tabs are both collapsed. If you specifically want to "
             "convert between the two rather than collapse them, use the tabs-to-spaces converter."),
            ("Does it remove non-breaking spaces pasted from Word?",
             "Trailing non-breaking spaces are stripped along with other trailing whitespace. "
             "For non-breaking spaces in the middle of a line, run the text through the HTML "
             "entity tools first, which convert <code>&amp;nbsp;</code> to a regular space."),
        ],
    },
    {
        "slug": "list-to-json-array",
        "title": "List to JSON Array",
        "meta_title": "Convert a List to a JSON Array Online — Free Converter",
        "meta_desc": (
            "Turn a plain list of lines into a valid, properly escaped JSON array. "
            "Optional numeric detection and compact output. No signup, no upload."
        ),
        "keyword": "list to json array",
        "card": "Turn one-item-per-line lists into a valid JSON array.",
        "h1": "Convert a List to a JSON Array",
        "lede": (
            "Paste one item per line and get back a valid JSON array with correct "
            "escaping — quotes, backslashes and Unicode all handled for you."
        ),
        "ops": [
            ("to_json_array", "To JSON array"),
            ("to_json_object", "To JSON object"),
            ("csv_to_json", "CSV to JSON"),
        ],
        "settings": [
            {"type": "checkbox", "opt": "numeric", "label": "Detect numbers"},
            {"type": "checkbox", "opt": "compact", "label": "Compact (one line)"},
        ],
        "sample": "red\\ngreen\\nblue\\nHe said \\\"hello\\\"\\n42",
        "body": """
<h2>Escaping is the part worth automating</h2>
<p>Wrapping lines in quotes and adding commas is easy enough to do by hand — until
one of your values contains a quotation mark, a backslash, a tab, or an emoji. At
that point hand-built JSON stops parsing, and the error message points at a line
number that is rarely where the real problem is.</p>

<p>This converter runs your list through the browser's own JSON serialiser, the
exact same implementation that will later parse it. Quotes become <code>\\"</code>,
backslashes double up, control characters become escape sequences, and Unicode
passes through intact. If it comes out of this tool, it will parse.</p>

<h2>Three shapes, one input</h2>
<p><strong>JSON array</strong> takes one value per line and produces
<code>["red", "green", "blue"]</code>. Blank lines are dropped and each value is
trimmed, because a leading space in a JSON string is almost never intentional.</p>

<p><strong>JSON object</strong> reads <code>key: value</code> or
<code>key,value</code> pairs, one per line, and produces a single object. Handy for
turning a two-column paste into a lookup table or a config block.</p>

<p><strong>CSV to JSON</strong> treats the first line as a header row and produces
an array of objects, one per data row. Quoted cells containing commas are handled
correctly, as are doubled quotes inside a quoted cell, so a real spreadsheet export
survives the trip.</p>

<h2>Numbers, and why they are opt-in</h2>
<p>By default every value comes out as a string, including things that look like
numbers. That is deliberate: identifiers such as ZIP codes, phone numbers, product
SKUs and version strings frequently look numeric but must stay text —
<code>"01234"</code> is a valid postcode, <code>1234</code> is not the same thing,
and <code>1.10</code> becomes <code>1.1</code> the moment it is treated as a number.</p>

<p>When your list really is numeric, tick <em>Detect numbers</em> and any value
that parses cleanly as a number is emitted unquoted. Mixed lists are handled
per-value, so a list of measurements with an occasional <code>N/A</code> keeps the
numbers numeric and the text as text.</p>

<h2>Typical uses</h2>
<ul>
  <li>Seeding a dropdown, an enum or a test fixture from a list someone sent you in an email.</li>
  <li>Building an <code>IN (...)</code> equivalent for an API that expects a JSON array of IDs.</li>
  <li>Converting a column copied from a spreadsheet into a request body without opening an editor.</li>
  <li>Turning a list of feature flags or allowed values into a config file entry.</li>
</ul>
""",
        "faq": [
            ("How are quotes and special characters handled?",
             "Automatically. The conversion uses the browser's native JSON serialiser, so "
             "quotation marks, backslashes, tabs, newlines and Unicode characters are all "
             "escaped correctly and the result is guaranteed to parse."),
            ("Why are my numbers wrapped in quotes?",
             "Because that is the safe default — it protects identifiers such as ZIP codes and "
             "SKUs that would lose leading zeros or trailing decimals if treated as numbers. "
             "Tick <em>Detect numbers</em> to emit numeric values unquoted."),
            ("Can it convert a CSV export?",
             "Yes, with the CSV to JSON mode. The first line is read as the header row and each "
             "following row becomes an object. Quoted cells containing commas are parsed correctly."),
            ("Is there a size limit?",
             "The interface accepts up to 200,000 characters per run, which is roughly 20,000 "
             "typical list items. Split larger inputs into batches."),
        ],
    },
    {
        "slug": "case-converter",
        "title": "Case Converter",
        "meta_title": "Text Case Converter — Upper, Lower, Title, camelCase, snake_case",
        "meta_desc": (
            "Convert text between UPPERCASE, lowercase, Title Case, Sentence case, "
            "camelCase, PascalCase, snake_case, kebab-case and CONSTANT_CASE."
        ),
        "keyword": "case converter",
        "card": "Switch between UPPER, lower, Title, camelCase, snake_case and more.",
        "h1": "Text Case Converter",
        "lede": (
            "Nine case styles, including the programming conventions: camelCase, "
            "PascalCase, snake_case, kebab-case and CONSTANT_CASE."
        ),
        "ops": [
            ("upper_case", "UPPERCASE"),
            ("lower_case", "lowercase"),
            ("title_case", "Title Case"),
            ("sentence_case", "Sentence case"),
            ("camel_case", "camelCase"),
            ("pascal_case", "PascalCase"),
            ("snake_case", "snake_case"),
            ("kebab_case", "kebab-case"),
            ("constant_case", "CONSTANT_CASE"),
        ],
        "settings": [],
        "sample": "user profile image URL\\nHTTPResponse code\\nfirst_name\\nlastLoginAt",
        "body": """
<h2>The two families of case conversion</h2>
<p>The first four styles are typographic: they change letter casing but leave your
words, spaces and punctuation where they are. <em>Sentence case</em> lowercases
everything and then capitalises the first letter after each sentence-ending
punctuation mark, which is the usual fix for text that arrived in ALL CAPS.
<em>Title Case</em> capitalises every word — quick and predictable, though note it
does not apply the editorial convention of leaving short words like "of" and "the"
lowercase, because that rule varies by style guide and by language.</p>

<p>The last five are identifier styles used in code. These do more than change
case: they split your text into words first and then rejoin it with the right
separator. That means all five conversions work from any starting point —
<code>first_name</code>, <code>firstName</code>, <code>first-name</code> and
<code>First Name</code> all normalise to the same word list before being rebuilt.</p>

<h2>Which identifier style goes where</h2>
<table>
  <thead><tr><th>Style</th><th>Example</th><th>Commonly used for</th></tr></thead>
  <tbody>
    <tr><td>camelCase</td><td><code>lastLoginAt</code></td><td>JavaScript and Java variables, JSON keys</td></tr>
    <tr><td>PascalCase</td><td><code>LastLoginAt</code></td><td>Class and component names, C# members</td></tr>
    <tr><td>snake_case</td><td><code>last_login_at</code></td><td>Python, Ruby, SQL columns</td></tr>
    <tr><td>kebab-case</td><td><code>last-login-at</code></td><td>URLs, CSS classes, CLI flags, file names</td></tr>
    <tr><td>CONSTANT_CASE</td><td><code>LAST_LOGIN_AT</code></td><td>Environment variables and constants</td></tr>
  </tbody>
</table>

<h2>Acronyms are handled properly</h2>
<p>Naive camelCase converters mangle acronyms: <code>HTTPResponse</code> becomes
<code>hTTPResponse</code>, and <code>parseXMLFile</code> loses its word boundaries
entirely. This converter detects the transition from a run of capitals into a
capitalised word, so <code>HTTPResponse</code> splits into
<code>HTTP</code> + <code>Response</code> and converts to
<code>httpResponse</code> or <code>http_response</code> as expected.</p>

<h2>Line-by-line conversion</h2>
<p>Identifier conversions apply to each line independently, so you can paste a
whole column of database field names and convert them all in one pass rather than
one at a time. The typographic styles work across the whole text at once, which is
what you want for prose.</p>
""",
        "faq": [
            ("Can I convert a whole list of names at once?",
             "Yes. The identifier styles — camelCase, PascalCase, snake_case, kebab-case and "
             "CONSTANT_CASE — convert each line separately, so you can paste an entire column "
             "of field names and convert them in a single pass."),
            ("How are acronyms like HTTP or XML handled?",
             "They are detected as complete words. <code>HTTPResponse</code> becomes "
             "<code>httpResponse</code> in camelCase and <code>http_response</code> in "
             "snake_case, rather than being split letter by letter."),
            ("What is the difference between Title Case and Sentence case?",
             "Title Case capitalises the first letter of every word. Sentence case lowercases "
             "everything and then capitalises only the first letter of each sentence — the usual "
             "way to rescue text typed in ALL CAPS."),
            ("Does it work with accented and non-English characters?",
             "Typographic conversions do, since they use the browser's Unicode-aware case "
             "mapping. Identifier styles strip characters outside A–Z and 0–9, because most "
             "programming languages and URL schemes expect ASCII identifiers."),
        ],
    },
    {
        "slug": "sort-lines",
        "title": "Sort Lines",
        "meta_title": "Sort Lines Alphabetically Online — Free Text Line Sorter",
        "meta_desc": (
            "Sort lines A–Z or Z–A with natural number ordering, sort by length, "
            "reverse or shuffle. Numbering and prefix/suffix tools included."
        ),
        "keyword": "sort lines alphabetically",
        "card": "Sort A–Z, by length, reverse or shuffle. Numbering included.",
        "h1": "Sort Lines Alphabetically",
        "lede": (
            "Alphabetical sorting with proper natural ordering, plus sort by length, "
            "reverse, shuffle, line numbering and bulk prefix/suffix."
        ),
        "ops": [
            ("sort_asc", "A → Z"),
            ("sort_desc", "Z → A"),
            ("sort_length", "Shortest first"),
            ("sort_length_desc", "Longest first"),
            ("reverse_lines", "Reverse order"),
            ("shuffle_lines", "Shuffle"),
            ("number_lines", "Number lines"),
            ("add_prefix_suffix", "Add prefix/suffix"),
        ],
        "settings": [
            {"type": "text", "opt": "prefix", "label": "Prefix", "placeholder": '"'},
            {"type": "text", "opt": "suffix", "label": "Suffix", "placeholder": '",'},
            {"type": "number", "opt": "start", "label": "Start at", "value": 1},
        ],
        "sample": "item10\\nitem2\\nItem1\\nbanana\\napple\\nitem20",
        "body": """
<h2>Natural sorting, not ASCII sorting</h2>
<p>A plain alphabetical sort puts <code>item10</code> before <code>item2</code>,
because it compares character by character and <code>1</code> sorts before
<code>2</code>. That is correct by the letter of the algorithm and wrong by every
human expectation.</p>

<p>This tool sorts <em>naturally</em>: runs of digits are compared as numbers, so
you get <code>item2</code>, <code>item10</code>, <code>item20</code> in the order
you would write them yourself. Sorting is also case-insensitive and
accent-aware, using your browser's locale rules — so in a list of Italian names
<code>Ácari</code> lands next to <code>Acari</code> rather than being exiled to the
end of the list, which is what a raw byte comparison would do.</p>

<h2>The other five modes</h2>
<p><strong>Sort by length</strong> is an underrated diagnostic. Sorting shortest
first surfaces the empty and near-empty rows that indicate a broken export; sorting
longest first brings the runaway rows — the ones with an unescaped delimiter that
swallowed the rest of the file — straight to the top.</p>

<p><strong>Reverse</strong> flips the existing order without sorting, which is the
right tool for chronological logs where the order is already meaningful and you
simply want the newest entries first.</p>

<p><strong>Shuffle</strong> randomises the order using a Fisher–Yates shuffle, so
every arrangement is equally likely. Useful for picking a random winner, randomising
question order, or creating an unbiased sample from a list.</p>

<p><strong>Number lines</strong> prefixes each line with a counter, starting from
whichever number you choose. <strong>Add prefix/suffix</strong> wraps every line in
the strings you supply — the fastest way to turn a bare column into quoted,
comma-separated values ready to paste into code.</p>

<div class="callout">
<p><strong>Combining tools:</strong> deduplicate first, then sort. Doing it in the
other order works too, but deduplicating a sorted list and then sorting again is
one step more than you need.</p>
</div>

<h2>A note on trailing newlines</h2>
<p>If your text ends with a newline, that final empty line is preserved at the
bottom rather than being sorted up to the top as an empty string. It is a small
detail, but it stops a sorted file from acquiring a stray blank first line every
time you run it.</p>
""",
        "faq": [
            ("Does it sort numbers correctly?",
             "Yes. Sorting is natural, so <code>item2</code> comes before <code>item10</code> "
             "rather than after it. Digit runs inside a line are compared numerically instead "
             "of character by character."),
            ("Is the sort case-sensitive?",
             "No. <code>Apple</code> and <code>apple</code> sort next to each other rather than "
             "in separate blocks, which matches how people expect a list to be ordered. Accented "
             "characters are also sorted according to your browser's locale rules."),
            ("How random is the shuffle?",
             "It uses a Fisher–Yates shuffle, which gives every possible ordering an equal "
             "probability. It is suitable for picking winners or randomising a sample, though "
             "not for cryptographic purposes."),
            ("Can I quote every line for pasting into code?",
             "Yes — use <em>Add prefix/suffix</em> with a prefix of <code>\"</code> and a suffix "
             "of <code>\",</code>. For proper JSON, the list-to-JSON-array tool handles escaping "
             "as well."),
        ],
    },
    {
        "slug": "tabs-to-spaces",
        "title": "Tabs to Spaces",
        "meta_title": "Convert Tabs to Spaces (and Back) Online — Free Converter",
        "meta_desc": (
            "Convert tab indentation to spaces or spaces back to tabs, with a "
            "configurable tab width. Tab stops are respected, so alignment survives."
        ),
        "keyword": "convert tabs to spaces",
        "card": "Convert indentation between tabs and spaces, tab stops respected.",
        "h1": "Convert Tabs to Spaces",
        "lede": (
            "Switch indentation between tabs and spaces with a tab width you choose. "
            "Tab stops are calculated properly, so aligned columns stay aligned."
        ),
        "ops": [
            ("tabs_to_spaces", "Tabs → spaces"),
            ("spaces_to_tabs", "Spaces → tabs"),
        ],
        "settings": [
            {"type": "number", "opt": "tabSize", "label": "Tab width", "value": 4, "min": 1, "max": 16},
        ],
        "sample": "def example():\\n\\tif True:\\n\\t\\treturn 1\\nname\\tage\\trole\\nAda\\t36\\tengineer",
        "body": """
<h2>Tab stops, not blind replacement</h2>
<p>Almost every online converter replaces each tab character with a fixed number of
spaces. That is correct only when the tab is the first thing on the line. A tab in
the middle of a line does not mean "insert four spaces" — it means "advance to the
next tab stop", which is a different number of spaces depending on where you
already are.</p>

<p>The practical consequence shows up in aligned data. Take a line reading
<code>name→age→role</code> with tabs between the fields: blind replacement produces
ragged columns, because <code>name</code> and <code>age</code> are different
lengths. This converter computes the real distance to the next tab stop, so columns
that lined up before still line up afterwards.</p>

<h2>Going the other way</h2>
<p>Converting spaces back to tabs only touches <strong>leading</strong> whitespace.
This is deliberate. Spaces inside a line are usually meaningful — they are part of
a sentence, a string literal, or a deliberate alignment — and converting them to
tabs would corrupt the content. Indentation is the part you actually want
tab-ified, so that is the only part that changes.</p>

<h2>Why this keeps coming up</h2>
<ul>
  <li><strong>Python.</strong> Mixing tabs and spaces in the same block is a
  <code>TabError</code> in Python 3. Since the two look identical on screen, the
  fastest fix is to convert the whole file one way and move on.</li>
  <li><strong>YAML.</strong> Tab characters are not permitted for indentation at
  all. A single tab pasted in from elsewhere breaks the entire document, usually
  with an error pointing somewhere unhelpful.</li>
  <li><strong>Makefiles.</strong> The opposite rule: recipe lines <em>must</em>
  start with a real tab. An editor that helpfully converted your tabs to spaces
  produces the famous "missing separator" error.</li>
  <li><strong>Team style rules.</strong> Most linters enforce one or the other.
  Converting before you commit avoids a diff full of whitespace-only changes.</li>
</ul>

<div class="callout">
<p><strong>Which should you use?</strong> There is no universal answer, but there
is a useful tiebreaker: tabs let each reader choose their own indent width, which
is a genuine accessibility benefit for developers who need large indentation to
track nesting. Spaces guarantee that alignment looks identical everywhere. Pick
whichever your project already uses and stay consistent.</p>
</div>
""",
        "faq": [
            ("What tab width should I use?",
             "Four is the most common default and what most editors assume. Python's style "
             "guide specifies four spaces; Go uses tabs; many JavaScript projects use two. "
             "If your project has a linter configuration, match it."),
            ("Will this break alignment in my tables?",
             "No. Tabs are expanded to the next tab stop rather than replaced with a fixed "
             "number of spaces, so tab-separated columns stay aligned after conversion."),
            ("Why does spaces-to-tabs only change the start of the line?",
             "Because spaces inside a line are usually part of the content — words in a "
             "sentence, or a string literal. Converting those to tabs would change your data, "
             "so only leading indentation is touched."),
            ("Can I convert a tab-separated file to something else?",
             "For TSV data, use the CSV-to-JSON tool and set the delimiter to a tab. This "
             "converter is for indentation rather than data conversion."),
        ],
    },
    {
        "slug": "base64-encode-decode",
        "title": "Base64 Encode / Decode",
        "meta_title": "Base64 Encode and Decode Online — Free UTF-8 Safe Tool",
        "meta_desc": (
            "Encode text to Base64 or decode Base64 back to text, with full UTF-8 "
            "support for accents, emoji and non-Latin scripts. Runs in your browser."
        ),
        "keyword": "base64 encode decode",
        "card": "Encode and decode Base64 with correct UTF-8 handling.",
        "h1": "Base64 Encode and Decode",
        "lede": (
            "Convert text to Base64 and back. Full UTF-8 support, so accented "
            "characters, emoji and non-Latin scripts survive the round trip intact."
        ),
        "ops": [
            ("base64_encode", "Encode"),
            ("base64_decode", "Decode"),
        ],
        "settings": [],
        "sample": "Città già — 日本語 — 🎉",
        "body": """
<h2>What Base64 is for</h2>
<p>Base64 turns arbitrary bytes into a string of 64 safe characters
(<code>A–Z</code>, <code>a–z</code>, <code>0–9</code>, <code>+</code> and
<code>/</code>, with <code>=</code> as padding). The point is transport, not
storage: it lets binary data travel through channels that only reliably carry
plain text — email bodies, JSON string fields, URLs, HTTP headers, HTML
attributes.</p>

<p>The cost is size. Base64 encodes three bytes as four characters, so the output
is about 33% larger than the input. That is fine for a small icon inlined in a
stylesheet and a poor idea for a large file.</p>

<h2>The UTF-8 trap</h2>
<p>Many browser-based Base64 tools call <code>btoa()</code> directly, which only
accepts characters in the Latin-1 range. Feed it an accented letter, an emoji, or
any non-Latin script and it throws an error — or worse, silently mangles the
text. This is why so many quick Base64 tools fail on the word
<code>città</code>.</p>

<p>This tool encodes your text to UTF-8 bytes first and Base64-encodes those bytes,
then reverses the process exactly on decode. Accents, CJK characters, Cyrillic,
Arabic, and emoji all round-trip without loss.</p>

<h2>Base64 is not encryption</h2>
<p>This matters enough to state plainly: Base64 provides <strong>no security
whatsoever</strong>. It is a reversible encoding with no key, and anyone can decode
it in one step — including on this page. Encoding a password, an API token or
personal data in Base64 does not protect it; it only makes it slightly less
readable at a glance. If you need confidentiality, you need actual encryption.</p>

<div class="callout">
<p><strong>Related but different:</strong> <em>base64url</em> replaces
<code>+</code> and <code>/</code> with <code>-</code> and <code>_</code> so the
result is safe inside a URL. It is what JSON Web Tokens use. Standard Base64
decoded here will handle the character set it is given, but if you are working
with JWTs, be aware the segments use the URL-safe variant.</p>
</div>

<h2>Common situations</h2>
<ul>
  <li>Reading the payload of a JWT to see what claims it carries.</li>
  <li>Inlining a small image or font in a <code>data:</code> URL.</li>
  <li>Decoding an HTTP Basic authentication header to check which user it names.</li>
  <li>Moving a small configuration blob through a form field that strips newlines.</li>
</ul>
""",
        "faq": [
            ("Does this handle accented characters and emoji?",
             "Yes. Text is converted to UTF-8 bytes before encoding and decoded back the same "
             "way, so accents, emoji and non-Latin scripts round-trip without loss — unlike "
             "tools that call the browser's <code>btoa()</code> directly."),
            ("Is Base64 a form of encryption?",
             "No. It is a reversible encoding with no key, and anyone can decode it instantly. "
             "It offers no confidentiality at all — never use it to protect passwords, tokens "
             "or personal data."),
            ("Why does my Base64 string fail to decode?",
             "Usually the string has been truncated, has had line breaks or spaces introduced, "
             "or is missing its <code>=</code> padding. It may also be the URL-safe variant, "
             "which uses <code>-</code> and <code>_</code> instead of <code>+</code> and <code>/</code>."),
            ("Can I encode a file?",
             "This tool works on text. Drag a text file onto the input box and it will load, "
             "but binary files such as images need a dedicated file-to-Base64 converter."),
        ],
    },
    {
        "slug": "url-encode-decode",
        "title": "URL Encode / Decode",
        "meta_title": "URL Encode and Decode Online — Percent Encoding Tool",
        "meta_desc": (
            "Percent-encode text for safe use in URLs and query strings, or decode "
            "an encoded URL back to readable text. Component and full-URL modes."
        ),
        "keyword": "url encode decode",
        "card": "Percent-encode text for query strings, or decode it back.",
        "h1": "URL Encode and Decode",
        "lede": (
            "Percent-encode text so it survives inside a URL, or decode an "
            "unreadable URL back into plain text."
        ),
        "ops": [
            ("url_encode", "Encode"),
            ("url_decode", "Decode"),
        ],
        "settings": [
            {"type": "checkbox", "opt": "component", "label": "Component mode (encode / and ?)", "checked": True},
        ],
        "sample": "https://example.com/search?q=caffè & latte&page=2",
        "body": """
<h2>Why URLs need encoding at all</h2>
<p>A URL has structure, and a handful of characters carry that structure:
<code>?</code> starts the query string, <code>&amp;</code> separates parameters,
<code>=</code> joins a name to its value, <code>#</code> begins the fragment,
<code>/</code> divides path segments. When one of those characters appears inside a
<em>value</em>, it has to be disguised — otherwise the parser reads it as
structure and your URL means something you did not intend.</p>

<p>Percent-encoding does the disguising: each byte becomes <code>%</code> followed
by two hexadecimal digits. A space becomes <code>%20</code>, an ampersand becomes
<code>%26</code>, and the accented <code>è</code> becomes <code>%C3%A8</code> —
two bytes, because it is UTF-8.</p>

<h2>Component mode versus full-URL mode</h2>
<p>This distinction causes more bugs than any other part of URL handling, and the
rule is simple once stated.</p>

<p><strong>Component mode</strong> (the default) encodes everything that is not
strictly safe, including <code>/</code>, <code>?</code>, <code>&amp;</code> and
<code>=</code>. Use it for a <em>piece</em> of a URL: one query parameter value,
one path segment. This is the mode you want when inserting user input into a URL.</p>

<p><strong>Full-URL mode</strong> leaves the structural characters alone and only
encodes things that could never be structure, such as spaces and accented letters.
Use it when you have a complete URL that merely needs tidying — encoding it in
component mode would destroy it, turning every <code>/</code> into
<code>%2F</code>.</p>

<div class="callout">
<p><strong>Rule of thumb:</strong> if you are encoding <em>part</em> of a URL, use
component mode. If you are encoding a <em>whole</em> URL, switch component mode
off.</p>
</div>

<h2>The plus-sign ambiguity</h2>
<p>In query strings, a <code>+</code> traditionally means a space — a legacy of
HTML form submission. In a path segment it means a literal plus. That ambiguity is
why an email address like <code>user+tag@example.com</code> sometimes arrives with
the tag turned into a space. When decoding, this tool treats <code>+</code> as a
space, matching query-string behaviour; if you need a literal plus in a value,
encode it as <code>%2B</code>.</p>

<h2>Where it shows up</h2>
<ul>
  <li>Building a search URL that contains spaces, quotes or non-English characters.</li>
  <li>Reading an OAuth redirect URL to see what the <code>redirect_uri</code> and <code>state</code> actually contain.</li>
  <li>Debugging analytics campaign links where a stray unencoded <code>&amp;</code> has truncated the parameters.</li>
  <li>Putting a full URL inside another URL as a parameter, which requires encoding it as a component.</li>
</ul>
""",
        "faq": [
            ("What is the difference between the two modes?",
             "Component mode encodes the URL's structural characters (<code>/</code>, "
             "<code>?</code>, <code>&amp;</code>, <code>=</code>) and is for encoding a single "
             "parameter value or path segment. Full-URL mode leaves them intact and is for "
             "tidying a complete URL."),
            ("Why does a space sometimes become + and sometimes %20?",
             "Both are valid in a query string. <code>+</code> comes from HTML form encoding, "
             "<code>%20</code> from the URL standard. In a path segment only <code>%20</code> is "
             "correct. This tool produces <code>%20</code> and accepts either when decoding."),
            ("Why did my email address lose its plus sign?",
             "Because a decoder read the <code>+</code> as a space, which is the query-string "
             "convention. To keep a literal plus in a value, encode it as <code>%2B</code> "
             "before putting it in a URL."),
            ("Why is one accented letter turning into six characters?",
             "Each character is encoded as its UTF-8 bytes, and accented letters take two bytes, "
             "so <code>è</code> becomes <code>%C3%A8</code>. Characters outside the Latin range "
             "can take three or four bytes. This is correct and decodes back cleanly."),
        ],
    },
    {
        "slug": "remove-html-tags",
        "title": "Remove HTML Tags",
        "meta_title": "Remove HTML Tags from Text Online — Free HTML Stripper",
        "meta_desc": (
            "Strip HTML tags and keep only readable text, with paragraph structure "
            "preserved and entities decoded. Also escapes and unescapes HTML."
        ),
        "keyword": "remove html tags",
        "card": "Strip tags to plain text, or escape and unescape HTML entities.",
        "h1": "Remove HTML Tags from Text",
        "lede": (
            "Turn a block of HTML into readable plain text. Paragraph breaks are "
            "kept, entities are decoded, and scripts and styles are discarded."
        ),
        "ops": [
            ("strip_html", "Strip tags"),
            ("html_escape", "Escape HTML"),
            ("html_unescape", "Unescape entities"),
        ],
        "settings": [],
        "sample": "<div><h2>Title</h2><p>First &amp; second paragraph.</p><script>alert(1)</script><ul><li>One</li><li>Two</li></ul></div>",
        "body": """
<h2>Parsing, not pattern matching</h2>
<p>The obvious way to strip HTML is to delete everything between angle brackets.
It works on tidy markup and fails on everything else — an attribute containing a
<code>&gt;</code>, an unclosed tag, a comment containing markup, or a
<code>&lt;script&gt;</code> block whose contents are left behind as visible
gibberish.</p>

<p>This tool hands your input to the browser's own HTML parser instead, the same
engine that renders pages, and then reads back the text. Malformed markup is
handled the way a browser would handle it, and the result is what a reader would
actually see.</p>

<h2>Structure is preserved</h2>
<p>Naively extracting text collapses everything into one long line, because HTML
uses tags rather than newlines for structure. Here, block-level elements —
paragraphs, headings, list items, table rows, <code>&lt;br&gt;</code> — become line
breaks, so a stripped article still reads as paragraphs and a stripped list still
reads as a list. Runs of blank lines are collapsed to one so the result does not
end up full of gaps.</p>

<p><code>&lt;script&gt;</code>, <code>&lt;style&gt;</code> and
<code>&lt;noscript&gt;</code> blocks are removed entirely. Their contents are code,
not content, and leaving them in is the most common flaw in simple HTML strippers.</p>

<h2>Entities are decoded</h2>
<p>Stripping tags without decoding entities leaves you with <code>&amp;amp;</code>
where an ampersand should be and <code>&amp;nbsp;</code> where a space should be.
Both are decoded here, so the output is genuinely plain text rather than
half-decoded HTML.</p>

<h2>The two inverse operations</h2>
<p><strong>Escape HTML</strong> does the opposite job: it converts
<code>&lt;</code>, <code>&gt;</code>, <code>&amp;</code> and quotes into entities so
that a snippet of code can be displayed on a page as text rather than being
interpreted as markup. This is what you need when you want to show an HTML example
inside an HTML document.</p>

<p><strong>Unescape entities</strong> converts them back. It is the fix for text
that has been escaped twice somewhere in a pipeline and now shows
<code>&amp;amp;lt;</code> to your readers.</p>

<div class="callout">
<p><strong>On safety:</strong> the parsing here does not execute scripts or load
external resources, so pasting untrusted HTML is safe. Do note that escaping for
display is only one part of preventing injection attacks — server-side handling
matters just as much.</p>
</div>
""",
        "faq": [
            ("Will the paragraph structure survive?",
             "Yes. Paragraphs, headings, list items, table rows and line breaks are converted "
             "into newlines, so the plain-text result keeps the shape of the original document "
             "instead of collapsing into one line."),
            ("What happens to JavaScript and CSS in the page?",
             "Script, style and noscript blocks are removed completely rather than having their "
             "contents dumped into the output, which is what most regex-based strippers do."),
            ("Are HTML entities converted back to characters?",
             "Yes. <code>&amp;amp;</code> becomes <code>&amp;</code>, <code>&amp;nbsp;</code> "
             "becomes a normal space, and so on, so the output is genuinely plain text."),
            ("Is it safe to paste HTML from an untrusted source?",
             "Yes. The markup is parsed in an inert document that does not execute scripts or "
             "load external resources, and nothing is sent anywhere."),
        ],
    },
    {
        "slug": "word-character-counter",
        "title": "Word & Character Counter",
        "meta_title": "Word and Character Counter — With Reading Time and Line Count",
        "meta_desc": (
            "Count words, characters with and without spaces, lines, sentences and "
            "paragraphs, plus reading and speaking time. Also extracts emails and URLs."
        ),
        "keyword": "word character counter",
        "card": "Count words, characters, lines, sentences and reading time.",
        "h1": "Word and Character Counter",
        "lede": (
            "A full breakdown of your text: words, unique words, characters with and "
            "without spaces, lines, sentences, paragraphs and estimated reading time."
        ),
        "ops": [
            ("text_stats", "Count everything"),
            ("extract_emails", "Extract emails"),
            ("extract_urls", "Extract URLs"),
            ("extract_numbers", "Extract numbers"),
        ],
        "settings": [],
        "sample": "Writing well is rewriting. Contact us at hello@example.com or visit https://example.com for the full guide.\\n\\nThe second paragraph adds 12 more words to the count.",
        "body": """
<h2>What gets counted</h2>
<p>Character counts come in two flavours because platforms disagree about which
one they mean. <em>Characters</em> includes every space and line break;
<em>characters without spaces</em> strips all whitespace. Social platforms and SMS
gateways generally count the first; some academic and print limits use the second.
When a limit matters, check which one applies before trusting a number.</p>

<p>Words are counted as runs separated by whitespace, which is the same rule word
processors use. <em>Unique words</em> counts distinct words ignoring case and
punctuation, which is a quick readability signal: a low ratio of unique to total
words usually means repetitive writing.</p>

<h2>Reading and speaking time</h2>
<p>Reading time is estimated at 225 words per minute, a widely used average for
adult silent reading of general prose. Treat it as an order-of-magnitude figure:
technical material with code samples reads considerably slower, and a skim reader
moves much faster.</p>

<p>Speaking time uses 130 words per minute, roughly the pace of clear presentation
delivery. It is the more useful of the two when you are timing a talk, a
voiceover script or a video narration — most people over-write their first draft
by a factor of two, and seeing the number early saves a painful edit later.</p>

<h2>Sentences and paragraphs</h2>
<p>Sentences are counted by terminal punctuation, so abbreviations such as
"e.g." and "Dr." will inflate the number slightly. Paragraphs are counted as blocks
separated by blank lines, which matches how plain-text and Markdown documents are
structured. Both figures are best used comparatively — is this draft denser than
the last one? — rather than as exact measurements.</p>

<h2>The extraction modes</h2>
<p>The same page also pulls specific things out of a block of text. <strong>Extract
emails</strong> finds every email address and returns a deduplicated list, which is
the quickest way to recover addresses from a pasted thread or a signature block.
<strong>Extract URLs</strong> does the same for links. <strong>Extract
numbers</strong> pulls out numeric values, including decimals and negatives, ready
to paste into a spreadsheet.</p>

<div class="callout">
<p><strong>Privacy note:</strong> extracting contact details from text you have a
legitimate reason to process is one thing; harvesting addresses for unsolicited
email is both ineffective and, in most jurisdictions, illegal. This runs locally
and stores nothing, but that is a technical guarantee rather than a legal one.</p>
</div>
""",
        "faq": [
            ("Which character count do social platforms use?",
             "Almost all of them count every character including spaces, so use the plain "
             "<em>characters</em> figure. Some print and academic limits use the count without "
             "spaces, so check which one your limit refers to."),
            ("How accurate is the reading time?",
             "It is an estimate based on 225 words per minute for silent reading. Dense technical "
             "writing reads slower and skimming is much faster, so treat it as a rough guide "
             "rather than a measurement."),
            ("Why is the sentence count slightly high?",
             "Sentences are detected by terminal punctuation, so abbreviations such as \"e.g.\" "
             "or \"Dr.\" are counted as sentence endings. The figure is most useful for comparing "
             "drafts rather than as an exact count."),
            ("Does the counter update as I type?",
             "The character and line count under the input box updates live. The full breakdown "
             "is produced when you run the tool, so that large documents do not slow down typing."),
        ],
    },
]


# --------------------------------------------------------------------------
# Guides. Each entry becomes /guides/<slug>.html
# These exist so the site has genuine reading material, not just tool pages.
# --------------------------------------------------------------------------

GUIDES = [
    {
        "slug": "cleaning-messy-data-before-import",
        "title": "Cleaning Messy Text Data Before You Import It",
        "meta_title": "How to Clean Messy Text Data Before Importing It",
        "meta_desc": (
            "A step-by-step order of operations for cleaning exported lists and CSV "
            "data: whitespace, duplicates, encoding and structure, in the right sequence."
        ),
        "description": "The right order of operations for cleaning an export, and why sequence matters.",
        "reading_time": 7,
        "body": """
<p>Every data import that goes wrong goes wrong in roughly the same way. The file
looks fine on screen, the import reports success, and then a week later somebody
notices there are two of everything, or that a column of postcodes has lost its
leading zeros. The problems were present in the source data all along; they were
simply invisible.</p>

<p>What follows is an order of operations for cleaning exported text data. The
order matters more than any individual step, because several of these operations
interfere with each other if done in the wrong sequence.</p>

<h2>1. Look at the file before you touch it</h2>

<p>Before cleaning anything, find out what you actually have. Three questions
answer most of it: how many lines are there, what does the first line contain, and
are the line endings consistent?</p>

<p>The line count tells you whether the export completed. A suspiciously round
number — exactly 1,000 or 5,000 rows — often means you hit a pagination limit and
are looking at a partial export. The first line tells you whether there is a header
row, which almost every subsequent step needs to know about. Line endings matter
because a file produced on Windows uses <code>\\r\\n</code> and one from macOS or
Linux uses <code>\\n</code>; mixed endings inside a single file are a reliable sign
that it has been edited by several tools in sequence, and they cause trailing
carriage returns to end up inside your values.</p>

<h2>2. Normalise whitespace first</h2>

<p>This step comes first because everything downstream depends on exact string
comparison, and whitespace is what breaks exact comparison.</p>

<p>Trailing spaces are the classic offender. They are invisible, they survive
copy-paste, and they mean that <code>"Milan "</code> and <code>"Milan"</code> are
two different values as far as any computer is concerned. Deduplication will not
catch them. Lookups against a reference table will fail on them. Grouping in a
pivot table will produce two rows that look identical.</p>

<p>Non-breaking spaces deserve a special mention. Text copied from a web page or a
Word document frequently contains U+00A0 instead of a regular space. It renders
identically, it is not matched by a search for a normal space, and it will quietly
defeat every cleanup you attempt until you specifically look for it.</p>

<p>The one thing to be careful about at this stage is indentation. If your data is
actually structured text — YAML, Python, Markdown — leading whitespace is content,
not noise, and a cleaner that collapses all runs of spaces will destroy it. Use a
tool that separates leading whitespace from the rest of the line.</p>

<h2>3. Fix encoding before you fix anything else textual</h2>

<p>If you see <code>Ã¨</code> where <code>è</code> should be, or <code>â€™</code>
where an apostrophe belongs, you are looking at mojibake: UTF-8 bytes that have
been interpreted as a single-byte encoding, usually Windows-1252. This is not a
find-and-replace problem, even though it is tempting to treat it as one. Every
accented character produces a different mangled sequence, and patching them one at
a time guarantees you will miss some.</p>

<p>The correct fix is to re-export or re-open the file with the right encoding
declared. If that is genuinely impossible, a systematic transcoding pass is the
next best option — but do it before deduplication, because mojibake creates
near-duplicates that differ only in their mangled characters, and deduplicating
first will leave you with both versions.</p>

<h2>4. Then deduplicate</h2>

<p>Deduplication belongs after whitespace and encoding cleanup, for the reason just
given: those two problems create pairs of records that are semantically identical
but textually different. Deduplicate too early and you keep both.</p>

<p>Decide deliberately whether matching should be case-sensitive. For email
addresses it should not be — the domain part is definitively case-insensitive, and
in practice the local part is treated that way by essentially every mail provider.
For anything that is a genuine identifier, such as a Base64 token or a
case-sensitive product code, it must be.</p>

<p>Also decide what "duplicate" means for your data. Two rows with the same email
address but different names may be a genuine duplicate with a typo in one copy, or
two people sharing a family address. Line-level deduplication cannot tell the
difference, so for records rather than simple lists, extract the key column first
and inspect what repeats before deleting anything.</p>

<h2>5. Convert structure last</h2>

<p>Only once the text is clean should you convert it into its target
structure — JSON, a database table, a spreadsheet import. Structure conversion is
the step that locks in whatever mistakes remain, because after it the data is no
longer a flat list you can easily re-clean.</p>

<p>The trap at this stage is type inference. Anything that helpfully guesses types
will convert <code>01234</code> to <code>1234</code>, <code>1.10</code> to
<code>1.1</code>, and a product code like <code>2024-01</code> to a date. All three
are lossy and none of them are reversible. When a value is an identifier rather
than a quantity, keep it as text — even when it consists entirely of digits. The
test is simple: would you ever do arithmetic with it? If not, it is text.</p>

<h2>6. Verify with counts, not with eyes</h2>

<p>Finish by checking numbers rather than scrolling. Compare the line count before
and after each step and make sure every change is one you intended. If
deduplication removed 4,000 of 10,000 rows, that is either a genuinely duplicated
export or a sign that you deduplicated on the wrong field — both are worth knowing
before you import.</p>

<p>Count how many rows have empty values in the fields that matter. Check that the
first and last rows still look like data rather than headers or footers. If you
started with a header row, confirm it is still there — or deliberately gone.</p>

<div class="callout">
<p><strong>The short version:</strong> whitespace, then encoding, then duplicates,
then structure, then verify by counting. Every one of those steps done out of
order creates work for the next one.</p>
</div>

<h2>A note on doing this in the browser</h2>

<p>For files up to a few megabytes, browser-based tools are a reasonable choice for
these steps, and they have one specific advantage worth naming: the data never
leaves your machine. That matters when the export contains customer records,
addresses or anything else you would rather not paste into a service whose
retention policy you have not read. It is also the reason DevClean processes
everything locally.</p>

<p>Beyond a few hundred thousand rows, move to a proper tool — a script, a database,
or a dedicated data-preparation application. The order of operations above stays
exactly the same; only the implementation changes.</p>
""",
    },
    {
        "slug": "duplicate-lines-explained",
        "title": "Five Ways to Remove Duplicate Lines, and When to Use Each",
        "meta_title": "How to Remove Duplicate Lines: Excel, Command Line, SQL and More",
        "meta_desc": (
            "Compare the practical ways to remove duplicate lines — spreadsheets, "
            "sort -u, awk, SQL and browser tools — and learn which preserves order."
        ),
        "description": "Spreadsheet, command line, SQL or browser — a comparison of the real options.",
        "reading_time": 6,
        "body": """
<p>Removing duplicates is one of those tasks with a dozen solutions, most of which
are subtly wrong for your particular case. The differences come down to three
questions: does it preserve the original order, does it handle near-matches, and
how much data can it cope with?</p>

<h2>The spreadsheet way</h2>

<p>Excel and Google Sheets both offer <em>Data → Remove duplicates</em>, and for a
one-off job on a few thousand rows it is hard to beat. It preserves order, it works
across multiple columns, and you can see what happened immediately.</p>

<p>The catch is what a spreadsheet does to your data on the way in. Paste a column
of values and it will helpfully interpret them: leading zeros disappear from
postcodes and account numbers, anything resembling a date becomes one, long numeric
IDs turn into scientific notation, and a value like <code>+39 02 1234</code> may be
read as a formula. None of these are recoverable after the fact. If your data is
purely textual and none of it looks numeric, this is fine. Otherwise, set the
column format to Text <em>before</em> pasting, or use something else.</p>

<h2>sort -u on the command line</h2>

<p><code>sort -u file.txt</code> is the shortest thing that works, and on large
files it is extremely fast — it handles files larger than memory by spilling to
disk. Every Unix-like system has it, including macOS and WSL.</p>

<p>The important caveat is in the name: it <em>sorts</em>. The output is
alphabetical, and the original order is gone. For a reference list that is fine or
even desirable. For a log file, a chronological export, or any list where position
carries meaning, it is destructive in a way that is not obvious until later.</p>

<h2>awk, when order matters</h2>

<p>The order-preserving equivalent is
<code>awk '!seen[$0]++' file.txt</code>. It keeps the first occurrence of each line
exactly where it was and drops the rest — the same behaviour as a well-behaved
browser tool, at command-line speed.</p>

<p>It is worth understanding rather than just copying. <code>seen</code> is an
associative array keyed by the whole line; <code>seen[$0]++</code> returns the
current count and then increments it, so the first time a line appears the
expression is <code>0</code>, which awk treats as false. The <code>!</code> inverts
it to true, and a bare true condition in awk means "print this line". Every
subsequent occurrence returns a non-zero count, which is true, inverted to false,
so nothing is printed.</p>

<p>The limitation is memory: the array holds every distinct line, so a file with
tens of millions of unique lines will exhaust RAM where <code>sort -u</code> would
not.</p>

<h2>SQL, when the data is already in a database</h2>

<p><code>SELECT DISTINCT</code> is the obvious answer and usually the right one for
whole-row duplicates. Where it gets more interesting is partial duplicates — rows
that are the same in the columns you care about but differ elsewhere, such as an
import timestamp.</p>

<p>For that case, window functions are the modern approach:</p>

<pre><code>SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY email ORDER BY created_at
  ) AS rn
  FROM contacts
) t WHERE rn = 1;</code></pre>

<p>This keeps the earliest row per email address and discards later ones. Changing
<code>ORDER BY created_at</code> to <code>created_at DESC</code> keeps the newest
instead. The advantage over <code>DISTINCT</code> is that you decide explicitly
which copy survives, rather than accepting whichever one the engine happens to
return.</p>

<h2>A browser tool</h2>

<p>The case for doing it in a browser is convenience and privacy: nothing to
install, nothing to remember, and with a client-side tool the data never leaves
your machine. Order is preserved, and options such as case-insensitive matching are
a checkbox rather than a flag you have to look up.</p>

<p>The limit is size. A browser will comfortably handle lists in the tens of
thousands of lines and struggle well before the point where <code>sort -u</code>
would break a sweat. Use it for the everyday case — a list from an email, a column
from a spreadsheet, a set of keywords — and reach for the command line when the
file gets large.</p>

<h2>Choosing</h2>

<table>
  <thead><tr><th>Method</th><th>Keeps order</th><th>Best for</th></tr></thead>
  <tbody>
    <tr><td>Spreadsheet</td><td>Yes</td><td>Small, purely textual data you are already editing</td></tr>
    <tr><td><code>sort -u</code></td><td>No</td><td>Very large files where order does not matter</td></tr>
    <tr><td><code>awk '!seen[$0]++'</code></td><td>Yes</td><td>Large files where order does matter</td></tr>
    <tr><td>SQL window function</td><td>You choose</td><td>Records where you pick which copy survives</td></tr>
    <tr><td>Browser tool</td><td>Yes</td><td>Everyday lists, sensitive data, no setup</td></tr>
  </tbody>
</table>

<h2>The problem underneath all of them</h2>

<p>Whichever method you pick, exact-match deduplication only removes lines that are
byte-for-byte identical. The duplicates that actually cause trouble usually are
not: <code>Mario Rossi</code> and <code>Rossi, Mario</code>, or the same address
with and without a trailing space.</p>

<p>Two habits help. First, normalise before you deduplicate — trim whitespace,
decide on a case convention, and fix encoding problems. Half of all "near
duplicates" turn out to be exact duplicates once the invisible characters are gone.
Second, for the genuinely fuzzy remainder, accept that no automatic tool will be
right every time; extract the candidates, look at them, and decide by hand. That is
slower, but it is the only approach that does not quietly delete real data.</p>
""",
    },
    {
        "slug": "json-arrays-in-practice",
        "title": "JSON Arrays in Practice: Escaping, Types and Common Mistakes",
        "meta_title": "JSON Arrays Explained — Escaping, Number Types and Common Errors",
        "meta_desc": (
            "Why hand-written JSON breaks, how escaping really works, when numbers "
            "should stay strings, and how to read a JSON parse error properly."
        ),
        "description": "Why hand-written JSON breaks, and how to read a parse error properly.",
        "reading_time": 6,
        "body": """
<p>JSON is small enough to learn in an afternoon and awkward enough to trip over
for years. Most of the trouble comes from three places: escaping, type coercion,
and error messages that point at the wrong line.</p>

<h2>Escaping is the whole problem</h2>

<p>A JSON string is delimited by double quotes, which immediately raises the
question of what happens when the value itself contains one. The answer is a
backslash: <code>"He said \\"hello\\""</code>. Simple enough — until the value
contains a backslash, which must itself be escaped as <code>\\\\</code>, and now you
are counting backslashes.</p>

<p>Windows file paths are where this bites hardest. The path
<code>C:\\Users\\Alberto</code> becomes
<code>"C:\\\\Users\\\\Alberto"</code> in JSON. Miss one and the parser sees
<code>\\U</code>, which is not a valid escape sequence, and rejects the document.</p>

<p>Control characters have their own escapes: <code>\\n</code> for a newline,
<code>\\t</code> for a tab, <code>\\r</code> for a carriage return. A literal
newline inside a JSON string is invalid, which surprises people who paste
multi-line text into a value and cannot see why it fails.</p>

<p>The practical conclusion is that hand-writing JSON containing arbitrary text is
a bad use of your time. Any generator — including the browser's own
<code>JSON.stringify</code>, which is what this site's converter uses — handles
every one of these cases correctly and takes no longer than typing the brackets
yourself.</p>

<h2>The trailing comma</h2>

<p>JSON does not allow a trailing comma after the last element. JavaScript does,
and so do most programming languages people are used to, which is why this is
comfortably the most common syntax error in hand-written JSON.</p>

<pre><code>["a", "b", "c",]   // invalid JSON
["a", "b", "c"]    // valid</code></pre>

<p>It is worth knowing that many editors and parsers are lenient about this,
including some that call themselves JSON parsers. A file that loads fine in your
editor can still be rejected by a strict parser at the other end, so "it worked
locally" is not evidence that the JSON is valid.</p>

<h2>Numbers, strings and lost information</h2>

<p>JSON has a number type, and using it is often a mistake. The moment a value
becomes a number, three things can happen to it: leading zeros are dropped, the
number of decimal places is normalised, and very large integers lose precision.</p>

<p>That last one is worth stating precisely, because it produces bugs that survive
for months. JSON numbers are typically parsed into IEEE 754 double-precision
floats, which represent integers exactly only up to 2<sup>53</sup> — about 9
quadrillion. Beyond that, values silently round. Snowflake IDs used by several
large platforms exceed this, which is exactly why those APIs return IDs as strings
alongside the numeric version.</p>

<p>The test is simple: would you ever perform arithmetic on this value? A price, a
quantity, a temperature — yes, those are numbers. An account number, a postcode, a
phone number, a version string, a database ID — no. Those are identifiers that
happen to be written with digits, and they belong in strings. Being able to sort
them numerically is not a good enough reason to convert.</p>

<h2>Arrays of what?</h2>

<p>JSON permits an array to contain mixed types, and there are situations where
that is genuinely the right model. In most cases, though, a mixed array is a sign
that something upstream is inconsistent — a field that is sometimes a string and
sometimes null, or a number that occasionally arrives as text.</p>

<p>The cost is paid by every consumer of the data, who now has to handle each
possible type. If you control the producer, pick one type per position and stick to
it. If you do not, normalise on arrival rather than scattering type checks
throughout your code.</p>

<h2>Reading a parse error</h2>

<p>A message like <em>Unexpected token } in JSON at position 1247</em> is more
useful than it looks, once you know how to read it. The position is a character
offset from the start of the document, not a line number, and — crucially — it is
where the parser <em>gave up</em>, not where the mistake is. A missing comma at
position 400 is not detected until the parser reaches something that cannot follow
what it has already read.</p>

<p>So the rule is: look at the reported position, then scan <em>backwards</em> for
the actual error. The usual suspects, in order of frequency, are a trailing comma,
a missing comma between elements, an unescaped quote inside a string, and a single
quote used where JSON requires a double.</p>

<h2>JSON is not JavaScript</h2>

<p>The name suggests otherwise, but JSON is a strict subset with meaningful
differences. Keys must be double-quoted strings — <code>{name: "x"}</code> is valid
JavaScript and invalid JSON. Single-quoted strings are not allowed. Comments are
not allowed, which is a genuine limitation for configuration files and the reason
formats such as JSON5 and JSONC exist. <code>undefined</code>, <code>NaN</code> and
<code>Infinity</code> have no representation at all.</p>

<p>If you need comments in a config file, you need a different format — YAML, TOML,
or a JSON variant that explicitly supports them. Adding <code>//</code> to a
<code>.json</code> file will work in your editor and fail in production, which is
the worst combination of outcomes.</p>

<div class="callout">
<p><strong>In short:</strong> generate JSON rather than typing it, keep
identifiers as strings, and when a parse error appears, read backwards from the
reported position rather than staring at it.</p>
</div>
""",
    },
    {
        "slug": "why-client-side-tools-matter",
        "title": "Why It Matters That a Text Tool Runs in Your Browser",
        "meta_title": "Client-Side vs Server-Side Text Tools — Privacy, Speed and Trust",
        "meta_desc": (
            "What actually happens when you paste text into an online tool, how to "
            "tell whether it uploads your data, and why local processing is faster."
        ),
        "description": "What happens to text you paste online, and how to check for yourself.",
        "reading_time": 5,
        "body": """
<p>Pasting text into a website is such a routine action that almost nobody stops to
ask where the text goes. For most online tools the answer is: to a server you know
nothing about, run by people you have never heard of, under a retention policy you
have not read.</p>

<p>Usually that is harmless. Occasionally it is not, and the difference is worth
being able to tell.</p>

<h2>Two architectures</h2>

<p>A <strong>server-side</strong> tool sends your text over the network. The server
processes it and sends a result back. Your text exists, at minimum, in that
server's memory; quite possibly in its access logs; and potentially in a database,
a backup, an error-tracking service, or a request log kept by a proxy or CDN in
between. Each of those is a normal, unremarkable piece of infrastructure, and each
one is a place your text now lives.</p>

<p>A <strong>client-side</strong> tool ships the processing code to your browser
and runs it there. The text is transformed in memory on your own machine and never
appears in a network request at all. There is no server to log it because the server
was never involved.</p>

<p>The distinction is invisible from the interface. Both look like a text box and a
button.</p>

<h2>When it actually matters</h2>

<p>For a shopping list, it does not. For several common cases, it does:</p>

<ul>
  <li><strong>Customer data.</strong> A list of names, email addresses or order
  references is personal data. Under the GDPR, sending it to a third-party service
  is a transfer to a processor, and doing so without a legal basis or a data
  processing agreement is a compliance problem regardless of how briefly the data
  is held.</li>
  <li><strong>Anything under NDA.</strong> Configuration files, internal
  documentation, unreleased product names. Pasting these into an unknown service is
  a disclosure, even if nobody ever looks at it.</li>
  <li><strong>Credentials and tokens.</strong> Decoding a JWT to check its claims is
  a completely routine debugging step — and if the tool is server-side, you have
  just handed a valid session token to a stranger.</li>
  <li><strong>Health, financial and legal text.</strong> Regulated categories where
  the standard of care is higher and the consequences of a leak are not merely
  reputational.</li>
</ul>

<h2>How to check for yourself</h2>

<p>You do not have to take any site's word for it, including this one. Open your
browser's developer tools with F12, switch to the Network tab, clear it, then run
the tool. If a request appears when you click the button, your text was sent
somewhere. If nothing appears, it was not.</p>

<p>A stronger version of the same test: load the page, then disconnect from the
internet entirely and try the tool again. A client-side tool keeps working. A
server-side one cannot.</p>

<p>Both checks take under a minute and are worth doing once for any tool you plan
to use with data that matters.</p>

<h2>The speed difference</h2>

<p>Privacy is the headline, but latency is what you notice day to day. A
server-side round trip costs the network time in both directions plus the server's
processing time — realistically 100 to 300 milliseconds on a good connection.</p>

<p>Free hosting adds a much larger penalty. Most free tiers put an idle service to
sleep after a period of inactivity, and waking it takes 30 to 60 seconds. The first
person to use the tool after a quiet spell waits the better part of a minute for an
operation that takes microseconds. That is not a hypothetical: it is the single
most common complaint about small hosted tools, and it disproportionately affects
first-time visitors, who conclude the site is broken and leave.</p>

<p>Client-side processing removes both costs. Typical text operations complete in
under a millisecond, which is fast enough to run as you type rather than on a
button press.</p>

<h2>What client-side cannot do</h2>

<p>It is not a universal answer. Anything that needs a secret — an API key, a
licensed dataset, a paid third-party service — has to run on a server, because
shipping the secret to the browser means giving it away. Anything that must be
consistent across users, such as a shared database, needs a server too. And very
large workloads eventually exceed what a browser tab can hold in memory.</p>

<p>The rule of thumb is that pure transformations of text the user already has
belong in the browser. Cleaning whitespace, removing duplicates, converting
formats, encoding and decoding — none of these need anything the user has not
already provided, so there is no technical reason to involve a server.</p>

<h2>Why DevClean works this way</h2>

<p>Every operation on this site is a pure function of the text you paste. There is
nothing a server could contribute except latency and a copy of your data, so the
processing happens in your browser and the text never leaves your machine.</p>

<p>That claim is verifiable rather than promissory. Open the Network tab and watch,
or turn off your connection and keep working — the tools carry on regardless. It is
a better guarantee than a privacy policy, because it does not depend on anyone
keeping their word.</p>
""",
    },
]
