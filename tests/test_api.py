"""HTTP-level checks: status codes, error mapping and the rate limiter.

test_parity.py covers what the operations compute; this covers what the API
does around them. Run with: python tests/test_api.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"PASS  {label}")
    else:
        failures.append(label)
        print(f"FAIL  {label}{'  ' + detail if detail else ''}")


def process(text, option, options=None, **kwargs):
    return client.post(
        "/api/process",
        json={"text": text, "option": option, "options": options or {}},
        **kwargs,
    )


def reset_rate_limit():
    main._hits.clear()


# --- basics ---------------------------------------------------------------

reset_rate_limit()
r = process("a\nb\na", "remove_duplicates")
check("valid request returns 200", r.status_code == 200, str(r.status_code))
check("valid request returns the processed text", r.json()["processed_text"] == "a\nb")

r = process("  a  ", "no_such_operation")
check("unknown operation returns 400", r.status_code == 400, str(r.status_code))
check(
    "unknown operation lists the valid ones",
    "valid_options" in (r.json().get("detail") or {}),
)

r = process("x" * (main.MAX_CHARS + 1), "trim_lines")
check("oversized input returns 413", r.status_code == 413, str(r.status_code))

r = process("   ", "remove_duplicates")
check("blank input returns 200 and empty text", r.status_code == 200 and r.json()["processed_text"] == "")


# --- OperationError is translated, not leaked ------------------------------

reset_rate_limit()
r = process("not base64!!", "base64_decode")
check("invalid Base64 returns 400", r.status_code == 400, str(r.status_code))
check("invalid Base64 explains why", r.json()["detail"] == main.BASE64_ERROR)

r = process("%zz", "url_decode")
check("invalid percent-encoding returns 400", r.status_code == 400, str(r.status_code))
check("invalid percent-encoding explains why", r.json()["detail"] == main.URL_ERROR)

def raised(fn, *args):
    """Return the exception a call raises, or None."""
    try:
        fn(*args)
    except Exception as exc:
        return exc
    return None


# The point of OperationError: the text layer must not import the web layer's
# exception type, so it stays usable outside FastAPI.
check(
    "operations raise OperationError, not HTTPException",
    type(raised(main.op_base64_decode, "!!", {})) is main.OperationError,
)


# --- rate limiting ---------------------------------------------------------

reset_rate_limit()
statuses = [process("a", "trim_lines").status_code for _ in range(main.RATE_LIMIT_REQUESTS)]
check(
    f"first {main.RATE_LIMIT_REQUESTS} requests pass",
    set(statuses) == {200},
    str(sorted(set(statuses))),
)

r = process("a", "trim_lines")
check("request over the limit returns 429", r.status_code == 429, str(r.status_code))
check("429 carries Retry-After", r.headers.get("retry-after") is not None)

r = client.get("/api/health")
check("health check is not rate limited", r.status_code == 200, str(r.status_code))

reset_rate_limit()
r = process("a", "trim_lines", headers={"X-Forwarded-For": "203.0.113.9"})
check("a different client gets its own budget", r.status_code == 200, str(r.status_code))


# --- result ----------------------------------------------------------------

print()
if failures:
    print(f"{len(failures)} check(s) failed:")
    for name in failures:
        print(f"  - {name}")
    sys.exit(1)

print("All API checks passed")
