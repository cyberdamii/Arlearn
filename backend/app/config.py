import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "content").exists():
    ROOT = ROOT.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{ROOT / 'arlearn.db'}")
CONTENT_DIR = Path(os.environ.get("CONTENT_DIR", ROOT / "content" / "simulations"))
WEB_DIR = Path(os.environ.get("WEB_DIR", ROOT / "web"))
TOKEN_MINUTES = int(os.environ.get("TOKEN_MINUTES", "720"))
