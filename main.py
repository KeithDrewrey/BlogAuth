from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from django.utils.http import url_has_allowed_host_and_scheme
from flask_gravatar import Gravatar
from sqlalchemy.ext.declarative import declarative_base

#db.session.execute(stmt)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'



##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    indiv_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)

    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    posts = db.relationship('BlogPost', backref='person', lazy=True)
    comments = db.relationship("Comment", backref="commenter", lazy=True)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False, )
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(20), nullable=False)

keith = "keith"

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'),
        nullable=False)
    post_comments = db.relationship("BlogPost", backref="comments", lazy=True)




with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    print("userloader")
    return User.query.get(user_id)


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            date=date.today().strftime("%B %d, %Y")
        )
        print(new_user.email, new_user.password, new_user.name)
        db.session.add(new_user)
        db.session.commit()
        flash("record uploaded")
        return render_template("index.html")

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        session["email"] = email
        print("database:", user.email, "formGet:", email)
        if user.email == email and user.password == password:
            login_user(user)

            # next = request.args.get('next')
            # if not url_has_allowed_host_and_scheme(next, request.host):
            #     return abor t(400)
            flash(message="you're in!")
            print("flash fired")
            #db.session.flush()
            return redirect(url_for('get_all_posts'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods = ["GET", "POST"])
def show_post(post_id):
    comments = Comment.query.filter_by(blog_id=post_id).all()
    person = User.query.filter_by(email=session["email"]).first()
    person = person.id
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text = form.body.data,
            commenter_id = person,
            blog_id = requested_post.id,)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("post.html", form=form, post=requested_post, all_comments = comments)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["POST", "GET"])
@login_required
def add_new_post():
    person = User.query.filter_by(email = session["email"]).first()
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            indiv_id = person.id,
            author=person.name,
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            #author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
