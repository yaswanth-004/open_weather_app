from flask import Blueprint

api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api-docs')

from app.api_docs import route