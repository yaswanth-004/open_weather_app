from flask import Flask , Blueprint

pb=Blueprint('blog',__name__)
from app.Blog import route