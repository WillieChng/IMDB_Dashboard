from flask import Blueprint, render_template, request, flash
from.models import User
from werkzeug.security import generate_password_hash, check_password_hash #One way

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    data = request.form
    print(data)
    return render_template("login.html")

@auth.route("/sign-up", methods=['GET', 'POST'])
def register():
    return render_template("signup.html")