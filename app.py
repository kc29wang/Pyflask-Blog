from flask import Flask, redirect, session, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Creat a route decorator
@app.route("/")

def index():
    first_name = "John" 
    return render_template("index.html", first_name=first_name )

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