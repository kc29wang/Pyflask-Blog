from flask import Flask, flash, redirect, session, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from web_forms import LoginForm, PostForm, UserForm, PasswordForm, SearchForm
from flask_ckeditor import CKEditor
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# Configure application
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
app.config["SECRET_KEY"] = "PIEFLASK"
# if __name__=='__main__':
#     app.run(debug=True)

# Add Database (SQLite3)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Add Database (MySQL)
# Heroku database:
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://omlxzbxwelkcyt:2a00127f35f7fe95ddd20376ac4fb26dd969aded7bddf2668365c74e8bdd5167@ec2-3-220-207-90.compute-1.amazonaws.com:5432/d9n2pqqr1o08hd"
# Railway databse
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ISJWGbASWPhybOKlb99o@containers-us-west-139.railway.app:7146/railway"
# Local Database
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:12345@127.0.0.1/our_users"
app.config['UPLOAD_FOLDER'] = 'static/'
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

# Creeat a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key to link users
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100), nullable=True)
    about_author = db.Column(db.Text())
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(), nullable=True)
    # A user can have many posts
    posts = db.relationship('Posts', backref='poster')

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


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Delete post page
@app.route('/posts/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)        
    try:
        if current_user.id == post_to_delete.poster.id or current_user.username == "admin":
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post Deleted Successfully!")
            # Grab all posts from the db
            posts = Posts.query.order_by(Posts.date_posted.desc())
            return render_template("posts.html", posts=posts)
            
        flash("You are not authorized to delete this post")
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
        if current_user.id == post.poster.id or current_user.username == "admin":
            post.title=form.title.data
            # post.slug=form.slug.data
            post.content=form.content.data
            # Update database
            db.session.add(post)
            db.session.commit()
            flash("Post has been updated!")
            return redirect(url_for('post',id=post.id))
        flash("You are not authorized to edit this post")
        posts = Posts.query.order_by(Posts.date_posted.desc())
        return render_template("posts.html", posts=posts)
    
    if post.poster.id == current_user.id or current_user.username == "admin":
        form.title.data=post.title
        # form.slug.data=post.slug
        form.content.data=post.content
        return render_template("edit_post.html", form=form)    
    flash("You are not authorized to edit this post")
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("posts.html", posts=posts)

# Add post page
@app.route('/add-post', methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        
        post = Posts(title=form.title.data, content=form.content.data, poster_id=current_user.id)
        form.title.data=""
        form.content.data=""
        
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
    posts = Posts.query.filter_by(poster_id=current_user.id)
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


# Creat a route decorator
@app.route("/")
def index():
    # Grab all the posts from db    
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("index.html", posts=posts)


# localhost:5000/user/John
@app.route("/user/<int:id>")
def user(id):
    user = Users.query.get(id)
    posts = Posts.query.filter_by(poster_id=id)
    return render_template("user.html", user=user, posts=posts)

# Creat custom error pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

    
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None   
    username = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        user_email = Users.query.filter_by(email = form.email.data).first()
        if user is None and user_email is None:
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            form.name.data=''
            form.username.data=''
            form.email.data=''
            form.favorite_color.data=''
            form.password.data=''
            flash("User Registered Successfully!")
            return render_template("dashboard.html",form=form)
        elif not user is None:
            flash("Username not available!")
            return render_template("add_user.html", form=form)
        elif not user_email is None:
            flash("Email not available!")
            return render_template("add_user.html", form=form)

    if current_user.is_authenticated:
        return render_template("Dashboard.html",form=form)
    return render_template("add_user.html", form=form)

# Update database record
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
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
            return render_template ('dashboard.html',form=form)
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
            return render_template ('dashboard.html',form=form)
        else: 
            flash("The new passwords you provided do not match!")
            return render_template("change_pw.html", id=id)
    else:
        return render_template("change_pw.html", id=id)

        
# Delete database record
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    name = None
    form = UserForm()
    try:
        if id == current_user.id or current_user.username == "admin":
            user_to_delete = Users.query.get_or_404(id)
            db.session.delete(user_to_delete)
            db.session.commit()    
            logout_user()            
            flash("User deleted successfully!")
            return redirect(url_for('index'))
        flash("You are not authorized to delete this user!")
        return redirect(url_for('dashboard'))
    except:        
        flash("Problem deleting user!")
        return redirect(url_for('dashboard'))


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
                form = UserForm()
                return render_template ('dashboard.html',form=form)
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
    form = UserForm()
    user = Users.query.get_or_404(current_user.id)
    if request.method=="POST":
        # Grab image name
        pic_filename = secure_filename(form.profile_pic.data.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save image
        MYDIR = os.path.dirname(__file__)
        saver = request.files['profile_pic']
        saver.save(os.path.join(MYDIR + "/" + app.config['UPLOAD_FOLDER'], pic_name))
        # Change it to a string to save to db
        user.profile_pic = pic_name
        db.session.commit()
        flash("Profile Picture Updated!")
        return render_template ('dashboard.html', form=form, user=user)
    return render_template ('dashboard.html', form=form, user=user)

# Creat search function
@app.route('/search', methods=["POST"])
def search():   
    searched = None
    results = []
    form = SearchForm() 
    posts = db.session.query(Users, Posts)
    if form.validate_on_submit():
        searched = form.searched.data
        # Query the database
        results = posts.filter(or_(Posts.content.like('%' + searched + '%'), Posts.title.like('%' + searched + '%'), Users.name.like('%' + searched + '%'))).join(Users, Posts.poster_id==Users.id)
        # results = results.order_by(Posts.title).all()
    return render_template ('search.html', form=form, searched=searched, results=results)

# Pass stuff to Layout
@app.context_processor
def layout():
    form = SearchForm()
    return dict(form=form)

@app.route('/admin')
@login_required
def admin():
    if current_user.username == "admin":
        our_users=Users.query.order_by(Users.date_added)    
        return render_template("admin.html", our_users=our_users)
    else:
        flash("Sorry you must be an admin to access Admin page.")
        return redirect(url_for('index'))