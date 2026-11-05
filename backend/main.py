from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import detect, risk

app = FastAPI(title="FireGuard AI — Inference Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: batasi ke domain Vercel saat production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router, prefix="/detect", tags=["detect"])
app.include_router(risk.router, prefix="/predict-risk", tags=["risk"])


@app.get("/health")
def health():
    return {"status": "ok"}
