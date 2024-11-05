from flask import Blueprint, render_template, request, flash
from.models import User
from werkzeug.security import generate_password_hash, check_password_hash #One way

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    data = request.form
    print(data)
    return render_template("login.html")

@auth.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST': #POST is used to send data to a server to create/update a resource
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if len(email) < 4:
            flash('Insufficient characters for email', category = 'error')
        elif email.__contains__('@') == False:
            flash('Email must contain an alias \'@\'', category = 'error')
        elif len(firstName) < 2:
            flash('First name must contain more than 1 character', category = 'error')
        elif len(lastName) < 2:
            flash('Last name must contain more than 1 character', category = 'error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category = 'error')
        elif password1 != password2:
            flash('Re-entered password does not match', category = 'error')
        else:
            flash('Your account is created!',category='success')
            
    return render_template("signup.html")