import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="DevClean API")

# 5. Pulizia CORS (teniamo solo le porte frontend e il futuro dominio reale)
ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://your-domain.com",  # Sostituisci col tuo dominio
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class TextRequest(BaseModel):
    text: str
    option: str


@app.post("/api/process")
def process_text(req: TextRequest):
    if not req.text.strip():
        return {"processed_text": ""}

    if len(req.text) > 200000:
        raise HTTPException(
            status_code=413,
            detail="Text is too long (Maximum 200,000 characters allowed).",
        )

    result = req.text

    try:
        if req.option == "clean_spaces":
            result = re.sub(r"\n\s*\n", "\n", result)
            result = re.sub(r"[ \t]+", " ", result).strip()

        elif req.option == "remove_duplicates":
            lines = result.splitlines()
            seen = set()
            dedup_lines = [
                line for line in lines if not (line in seen or seen.add(line))
            ]
            result = "\n".join(dedup_lines)

        elif req.option == "to_json_keys":
            words = [w.strip() for w in result.splitlines() if w.strip()]
            result = json.dumps(words, indent=2, ensure_ascii=False)

        else:
            raise HTTPException(status_code=400, detail="Invalid option.")

        return {"processed_text": result}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Processing error: {str(e)}"
        )