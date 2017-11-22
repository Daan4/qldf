from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config):
    """Create and initialise the object"""
    # Flask
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(config)
    # SQLAlchemy
    db.init_app(app)
    # Register blueprints
    from qldf.views import bp_root, setup_error_routing
    app.register_blueprint(bp_root)
    # Setup routing for html error pages
    setup_error_routing(app)
    return app
