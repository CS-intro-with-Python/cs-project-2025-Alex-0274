import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

db = SQLAlchemy()


def create_app(test_config: dict | None = None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///todo.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    if test_config:
        app.config.update(test_config)

    logging.basicConfig(
        level=app.config.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    db.init_app(app)

    Swagger(app, template={
        "info": {
            "title": "ToDo API",
            "description": "Minimal REST API for ToDo project (toggle/delete/list/create/update).",
            "version": "1.0.0",
        }
    })

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app
