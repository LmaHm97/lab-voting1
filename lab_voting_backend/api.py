import os
from flask import Flask
from flask_cors import CORS

from src.models.voting import db
from src.routes.voting import voting_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/voting.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(voting_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return {"service": "lab-voting-backend", "status": "running"}, 200

    @app.get("/api/health")
    def health():
        return {"ok": True}, 200

    return app

app = create_app()
