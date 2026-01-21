import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from src.models.voting import db
from src.routes.voting import voting_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # CORS (tighten origins in production if you know the frontend domain)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # DB init
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        db_path = os.environ.get("SQLITE_PATH", "/tmp/voting.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    @app.before_request
    def init_db_once():
       if not getattr(app, "_db_initialized", False):
          with app.app_context():
               db.create_all()
          app._db_initialized = True


    # API
    app.register_blueprint(voting_bp, url_prefix="/api")

    # Static / SPA fallback
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_static(path):
        static_folder_path = app.static_folder
        if not static_folder_path or not os.path.exists(static_folder_path):
            return "Static folder not configured", 404
        if path and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
        return "index.html not found", 404

    return app

app = create_app()
@app.get("/api/health")
def health():
    return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
