
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField

from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class PostForm(FlaskForm):
    title = StringField('title')
    body = CKEditorField('body')
    submit = SubmitField('post')

class BookForm(FlaskForm):
    title= StringField('title')
    ibsn= StringField('ibsn')
    author= StringField('author')
