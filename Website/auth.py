from flask import Blueprint, render_template, request, flash
from.models import User
from werkzeug.security import generate_password_hash, check_password_hash #One way

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route("/sign-up")
def register():
    return render_template("signup.html")