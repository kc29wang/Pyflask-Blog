# from flask import Flask, flash, redirect, session, render_template, request, url_for
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
# from wtforms.validators import DataRequired, EqualTo, Length
# from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
# from os import path
# from datetime import datetime
# from flask_migrate import Migrate
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import date
# from wtforms.widgets import TextArea
# from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "PIEFLASK"
# if __name__=='__main__':
#     app.run(debug=True)

# Add Database (SQLite3)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Add Database (MySQL)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:12345@127.0.0.1/our_users"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure SQLite database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Flask loggin stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(200), nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    #Creat a String
    def __repr__(self):
        return '<name %r>' % self.name

# Creeat a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# Creat a posts form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget = TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Delete post page
@app.route('/posts/delete/<int:id>', methods=["GET", "POST"])
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post Deleted Successfully!")
        # Grab all posts from the db
        posts = Posts.query.order_by(Posts.date_posted.desc())
        return render_template("posts.html", posts=posts)
    except:
        flash("There was a problem deleting post.")
        # Grab all posts from the db
        posts = Posts.query.order_by(Posts.date_posted.desc())
        return render_template("posts.html", posts=posts)

# Edit post page
@app.route('/posts/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title=form.title.data
        post.author=form.author.data
        post.slug=form.slug.data
        post.content=form.content.data
        # Update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post',id=post.id))
    form.title.data=post.title
    form.author.data=post.author
    form.slug.data=post.slug
    form.content.data=post.content
    return render_template("edit_post.html", form=form)

# Add post page
@app.route('/add-post', methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        form.title.data=""
        form.content.data=""
        form.author.data=""
        form.slug.data=""
        
        # Add post data to db
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully!")
        return redirect(url_for('post',id=post.id))

    return render_template("add_post.html", form=form)


@app.route('/posts')
@login_required
def posts():
    # Grab all the posts from db    
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("posts.html", posts=posts)


# JSON practice
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Pepperoni",
        "John2": "Pepperoni2",
        "John3": "Pepperoni3"
    }
    return favorite_pizza
    #return {"Date": date.today()}


# Creat a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmation', message="Password does not match")])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")

    
# Creat a pw class
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Creat a route decorator
@app.route("/")
def index():
    # Grab all the posts from db    
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("index.html", posts=posts)


# localhost:5000/user/John
@app.route("/user/<name>")
def user(name):        
    return render_template("user.html", name=name)

# Creat custom error pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

    
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data=''
        flash("Form Submitted Successfully!")
    return render_template("name.html", name=name, form=form)

    
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None   
    username = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.username.data=''
        form.email.data=''
        form.favorite_color.data=''
        form.password.data=''
        login_user(user)
        flash("User Registered Successfully!")
        return render_template("Dashboard.html")
    our_users=Users.query.order_by(Users.date_added)    
    return render_template("add_user.html", name=name, form=form, our_users=our_users)

# Update database record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        try:
            name_to_update.name =  request.form['name']
            name_to_update.email =  request.form['email']
            name_to_update.username =  request.form['username']
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template ('dashboard.html')
        except:
            flash("An error occurred! Please try again")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

# Update database record
@app.route("/change_pw/<int:id>", methods=["GET", "POST"])
def change_pw(id):
    form = UserForm()
    # Lookup user by id
    user_to_check = Users.query.filter_by(id=id).first()
    #name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        # Check hashed password
        passed = check_password_hash(user_to_check.password_hash, request.form['old_pw'])
        if not passed:
            flash("The old password provided is not correct!")
            return render_template("change_pw.html", id=id)

        if request.form['new_pw'] == request.form['confirm_pw']:
            user_to_check.password_hash = generate_password_hash(request.form['new_pw'])
            db.session.commit()
            flash("Password Changed Successfully!")
            return render_template ('dashboard.html')
        else: 
            flash("The new passwords you provided do not match!")
            return render_template("change_pw.html", id=id)
    else:
        return render_template("change_pw.html", id=id)

        
# Delete database record
@app.route("/delete/<int:id>")
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
        our_users=Users.query.order_by(Users.date_added)
        return render_template("add_user.html", name=name, form=form, our_users=our_users)
    except:        
        flash("Problem deleting user!")
        our_users=Users.query.order_by(Users.date_added)
        return render_template("add_user.html", name=name, form=form, our_users=our_users)

# Creat pw test page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data=''
        form.password_hash.data=''

        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

# Creat login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Creat login page
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check pw hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfully!")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid Password!")
        else:
            flash("User does not exist!")
    return render_template ('login.html', form=form)


# Creat logout page
@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()            
    flash("You have been logged out!")
    return redirect(url_for('login'))


# Creat dashboard page
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template ('dashboard.html')