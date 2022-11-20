from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


# Creat a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmation', message="Password does not match")])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    profile_pic = FileField("Profile Picture")
    submit = SubmitField("Submit")
    
# Creat login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Creat search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Creat a pw class
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Creat a posts form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget = TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    # slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")