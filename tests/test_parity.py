"""Cross-check: the JS engine and the Python API must agree on every operation."""
import json, subprocess
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main

CASES = [
    ("clean_spaces", "  a    b  \n\n\n  c\t\td", {}),
    ("trim_lines", "  a  \n  b  ", {}),
    ("collapse_blank_lines", "\n\na\n\n\n\nb\n\n", {}),
    ("remove_blank_lines", "\na\n\nb\n", {}),
    ("remove_duplicates", "a\nb\nA\na\nc", {}),
    ("remove_duplicates", "a\nb\nA\na\nc", {"ignoreCase": True}),
    ("keep_duplicates", "a\nb\na\nc\nb", {}),
    ("to_json_array", 'one\ntwo\nHe said "hi"\n42', {}),
    ("to_json_array", "1\n2\n3.5\nabc", {"numeric": True}),
    ("to_json_object", "name: Ada\nrole: engineer", {}),
    ("csv_to_json", 'name,age\n"Doe, John",30\nAda,36', {}),
    ("upper_case", "città test", {}),
    ("lower_case", "CITTÀ TEST", {}),
    ("title_case", "hello WORLD foo", {}),
    ("sentence_case", "HELLO. THERE world", {}),
    ("camel_case", "HTTPResponse code\nfirst_name", {}),
    ("pascal_case", "hello_world\nfoo-bar", {}),
    ("snake_case", "helloWorldFoo\nXMLParser", {}),
    ("kebab_case", "Hello World\nlastLoginAt", {}),
    ("constant_case", "hello world", {}),
    ("sort_asc", "item10\nitem2\nItem1\nbanana\napple", {}),
    ("sort_desc", "b\na\nc", {}),
    ("sort_length", "ccc\na\nbb", {}),
    ("sort_length_desc", "ccc\na\nbb", {}),
    ("reverse_lines", "1\n2\n3", {}),
    ("number_lines", "a\nb\nc", {}),
    ("number_lines", "a\nb", {"start": 5, "separator": ") "}),
    ("add_prefix_suffix", "a\nb", {"prefix": '"', "suffix": '",'}),
    ("tabs_to_spaces", "\tx\nab\ty\ndef f():\n\t\treturn", {"tabSize": 4}),
    ("spaces_to_tabs", "        x\n    y", {"tabSize": 4}),
    ("base64_encode", "Città già — 日本語 — 🎉", {}),
    ("base64_decode", "Q2l0dMOgIGdpw6A=", {}),
    ("url_encode", "https://x.com/a b?q=cafè&p=2", {}),
    ("url_decode", "a+b%26c%20d", {}),
    ("html_escape", '<b>a & "b"</b>', {}),
    ("html_unescape", "&lt;b&gt;a &amp; b&lt;/b&gt;&nbsp;x", {}),
    ("strip_html", "<div><h2>T</h2><p>A &amp; B</p><script>bad()</script><ul><li>1</li><li>2</li></ul></div>", {}),
    ("extract_emails", "a@b.com x A@B.COM y c@d.io", {}),
    ("extract_urls", "see https://a.com/x and http://b.io", {}),
    ("extract_numbers", "1 and -2.5 and 1", {}),
    ("text_stats", "Hello world. Bye now.\n\nSecond para here.", {}),
]

node_script = """
const D = require(process.argv[2]);
const cases = JSON.parse(process.argv[1]);
const out = cases.map(c => {
  try { return { ok: true, v: D.run(c[0], c[1], c[2]) }; }
  catch (e) { return { ok: false, v: String(e.message) }; }
});
process.stdout.write(JSON.stringify(out));
"""

js_raw = subprocess.run(
    ["node", "-e", node_script, json.dumps(CASES), os.path.join(ROOT, "assets", "tools.js")],
    capture_output=True, text=True, cwd=ROOT,
)
if js_raw.returncode != 0:
    print("node failed:", js_raw.stderr); sys.exit(1)
js_results = json.loads(js_raw.stdout)

fails = 0
for (op, text, opts), js in zip(CASES, js_results):
    try:
        py = main.OPERATIONS[op](text, opts)
        py_ok = True
    except Exception as e:
        py, py_ok = str(e), False

    same = js["ok"] == py_ok and js["v"] == py
    label = f"{op:22s} {str(opts)[:28]:28s}"
    if same:
        print(f"MATCH  {label}")
    else:
        fails += 1
        print(f"DIFF   {label}")
        print(f"        js: {js['v']!r}")
        print(f"        py: {py!r}")

print()
print(f"{len(CASES) - fails}/{len(CASES)} operations agree between browser and API")
sys.exit(1 if fails else 0)
