from flask import render_template
from app.api_docs import api_docs_bp

@api_docs_bp.route('/')
def index():
    return render_template('api_docs.html')