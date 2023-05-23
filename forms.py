from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, EmailField
from wtforms.validators import Email
from flask_ckeditor import CKEditorField



##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[validators.DataRequired()])
    subtitle = StringField("Subtitle", validators=[validators.DataRequired()])
    img_url = StringField("Blog Image URL", validators=[validators.DataRequired(), validators.URL()])
    body = CKEditorField("Blog Content", validators=[validators.DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    email = EmailField("Enter your email", validators=[validators.DataRequired(), Email(message="please enter a valid email")])
    password = PasswordField("Enter a Password", [validators.DataRequired(), validators.Length(min=6, max=30, message="please enter a password with at least 6 chars")])
    name = StringField("Enter your name", validators=[validators.DataRequired(message="please enter a valid email")])
    submit = SubmitField("Submit Post")


class LoginForm(FlaskForm):
    email = EmailField("Enter your email", validators=[validators.DataRequired(), Email(message="please enter a valid email")])
    password = PasswordField("Enter a Password", [validators.DataRequired(), validators.Length(min=6, max=30, message="please enter a password with at least 6 chars")])
    submit = SubmitField("Submit Post")


class CommentForm(FlaskForm):
    body = CKEditorField("Add a comment", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")