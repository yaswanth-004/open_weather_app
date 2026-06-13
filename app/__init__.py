from flask import Flask, redirect, url_for
from app.database.db import db, bcrypt
from app.auth import bp as auth_bp
from app.Blog import pb as blog_bp
from app.weather.route import weather_bp
from app.profile.route import profile_bp
from app.api_docs import api_docs_bp  # ← add this import

# inside create_app():
  # ← add this line
from config import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    bcrypt.init_app(app)   # ← you were missing this
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_docs_bp) 

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        print("Database ready")

    return app