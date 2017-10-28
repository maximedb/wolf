from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from models import Game, User, Wolf, RoundType, Round, Vote

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
db = SQLAlchemy(app)

from project.views import *
from project.models import *

db.create_all()
