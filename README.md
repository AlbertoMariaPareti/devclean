# DevClean

**Free Online Text & Code Cleaner Tool**

DevClean is a tiny, lightweight utility for cleaning up messy text and CSV/plain-text data in your browser — no signup, no data stored on any server. Paste your text, pick an action, and get a clean result back instantly.

🔗 **Live demo:** https://albertomariapareti.github.io/devclean/front.html

## Features

DevClean currently supports three text-cleaning operations:

- **Clean Extra Spaces & Empty Lines** — collapses repeated spaces/tabs and removes redundant blank lines.
- **Remove Duplicate Lines** — strips duplicate lines while preserving the original order.
- **Convert List to JSON Array** — turns a plain list of lines into a formatted JSON array.

Other characteristics:

- Handles up to 200,000 characters per request.
- Processes text on the fly — nothing is stored server-side.
- Simple, dependency-free frontend (plain HTML/CSS/JS).

## Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python), served with Uvicorn
- **Frontend:** Static HTML/JS (`front.html`), no build step required

## Project Structure

```
devclean/
├── main.py           # FastAPI backend — exposes POST /api/process
├── front.html         # Frontend UI (paste text, choose action, get result)
├── privacy.html        # Privacy policy page
├── requirements.txt    # Python dependencies (fastapi, uvicorn)
└── .gitignore
```

## Running Locally

### Backend

```bash
# 1. Clone the repo
git clone https://github.com/AlbertoMariaPareti/devclean.git
cd devclean

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend

Serve `front.html` with any static server on port `5500` (e.g. VS Code's "Live Server" extension), since that's the origin currently whitelisted in the backend's CORS settings (`http://localhost:5500` / `http://127.0.0.1:5500`). Opening the file directly (`file://`) will not work due to CORS.

## API Usage

The backend exposes a single endpoint:

```
POST /api/process
Content-Type: application/json

{
  "text": "your text here",
  "option": "clean_spaces" | "remove_duplicates" | "to_json_keys"
}
```

**Response:**

```json
{
  "processed_text": "..."
}
```

Example with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "hello\nhello\nworld", "option": "remove_duplicates"}'
```

## Privacy

DevClean does not store submitted text on any server — everything is processed in memory for the duration of the request. See [`privacy.html`](./privacy.html) for details.

## Feedback & Ideas

This is an early, actively-developed project. If you have ideas for other text-cleaning options that would be useful (e.g. case conversion, line sorting, trimming specific characters), feel free to open an issue or start a discussion!

## License

No license has been specified yet for this project. All rights reserved by the author unless stated otherwise.
