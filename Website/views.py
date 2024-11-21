from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from Website.models import User
from . import db

views = Blueprint('views', __name__)  # Define blueprint

@views.route('/testing.html')
def testing():
    return render_template("testing.html", text="Hi, my name is", user="ALi", boolean=True)

@views.route('/')  # Root function
def base():
    return render_template("homepage.html")

@views.route('/basic.html')
def basic():
    return render_template("basic.html")

@views.route('/intermediate.html')
def intermediate():
    return render_template("intermediate.html")

@views.route('/advanced.html')
def advanced():
    return render_template("advanced.html")

@views.route('/favourites.html')
def favourites():
    return render_template("favourites.html")

@views.route('/personalized.html')
def personalized():
    return render_template("personalized.html")

@views.route('/settings.html')
def settings_page():
    return render_template("settings.html")

@views.route('/profile.html')
def profile_page():
    return render_template("profile.html")

@views.route('/movie_details.html')
def movie_details_page():
    return render_template("movie_details.html")

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.base'))
        else:
            flash('Login failed. Check your email and password.', category='error')
    return render_template("login.html")

@views.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if len(email) < 4:
            flash('Insufficient characters for email', category='error')
        elif '@' not in email:
            flash('Email must contain an alias \'@\'', category='error')
        elif len(firstName) < 2:
            flash('First name must contain more than 1 character', category='error')
        elif len(lastName) < 2:
            flash('Last name must contain more than 1 character', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Re-entered password does not match', category='error')
        else:
            new_user = User(first_name=firstName, last_name=lastName, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Your account is created!', category='success')
            return redirect(url_for('views.login'))
    return render_template("signup.html")

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))

@views.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Handle forgot password logic here
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')