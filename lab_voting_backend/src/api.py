import os
import uuid
from flask import Flask, send_from_directory, session
from flask_cors import CORS

from src.models.voting import db
from src.routes.voting import voting_bp

BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="",  # allows /assets/... to resolve
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database config
database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/voting.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables (simple approach; OK for small apps)
with app.app_context():
    db.create_all()

# Blueprints
app.register_blueprint(voting_bp, url_prefix="/api")

# ---------- API ----------
@app.get("/api/health")
def health():
    return {"ok": True}, 200

@app.get("/api/me")
def me():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return {"ok": True, "user_id": session["user_id"]}, 200

# ---------- FRONTEND ----------
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")
