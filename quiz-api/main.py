import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

ASSISTANT_URL = os.getenv("ASSISTANT_URL", "http://open-webui:8080")
ASSISTANT_API_KEY = os.getenv("ASSISTANT_API_KEY", "")
MODEL = "models/gemini-3.5-flash"

app = FastAPI(title="Quiz API")


class QuizRequest(BaseModel):
    knowledge_id: str
    sujet: str = "le cours"
    nombre: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/quiz")
async def generer_quiz(req: QuizRequest):
    prompt = (
        f"A partir des documents fournis, cree {req.nombre} questions "
        f"a choix multiples en francais sur : {req.sujet}. "
        "Chaque question a 4 options et une seule bonne reponse. "
        "Donne aussi la bonne reponse et une explication courte."
    )

    charge = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "files": [{"type": "collection", "id": req.knowledge_id}],
    }

    async with httpx.AsyncClient(timeout=120) as client:
        reponse = await client.post(
            f"{ASSISTANT_URL}/api/chat/completions",
            headers={"Authorization": f"Bearer {ASSISTANT_API_KEY}"},
            json=charge,
        )

    contenu = reponse.json()["choices"][0]["message"]["content"]
    return {"sujet": req.sujet, "quiz": contenu}
