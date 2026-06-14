import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config['SECRET_KEY'] = 'dev-key-12345'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app