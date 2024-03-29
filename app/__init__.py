from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager
from flask_ckeditor import CKEditor

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)


db = SQLAlchemy(app)
ckeditor = CKEditor(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view='login'

from app import routes, models, forms
