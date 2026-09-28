from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import WEB_DIR
from .database import Base, engine
from .routers import attempts, auth, simulations
from .services.content import load_simulations

Base.metadata.create_all(engine)
load_simulations()

app = FastAPI(title="ARLearn")

app.include_router(auth.router)
app.include_router(simulations.router)
app.include_router(attempts.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
