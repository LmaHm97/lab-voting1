import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask import session
from src.models.voting import db
from src.routes.voting import voting_bp
import uuid




@app.get("/api/me")
def me():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return {"ok": True, "user_id": session["user_id"]}, 200

BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path=""   # THIS IS CRITICAL
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database
database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/voting.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# API routes
app.register_blueprint(voting_bp, url_prefix="/api")

# -------- FRONTEND --------

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# Health check
@app.get("/api/health")
def health():
    return {"ok": True}
