from flask import Blueprint, render_template, request, flash, redirect, url_for, get_flashed_messages
from . import db
from.models import User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash #One way
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

auth = Blueprint('auth', __name__)

def validate_user_details(firstName, lastName, username, email, password1="", password2="", sign_up=False):
    if len(firstName or lastName) < 2:
        flash('First or Last name must contain more than 1 character', category='error')
        return False
    elif len(username) < 2:
        flash('Username must contain more than 1 character', category='error')
        return False
    elif len(email) < 5:
        flash('Insufficient characters for email', category='error')
        return False
    elif '@' not in email or '.' not in email:
        flash('Email contains missing element, \'@\' or \'.\'', category='error')
        return False
    
    if sign_up:
        # Check if email or username already exists
        user_by_email = User.query.filter_by(email=email).first()
        user_by_username = User.query.filter_by(username=username).first()
        
        if user_by_username:
            flash('Username already exists', category='error')
            return False
        elif user_by_email:
            flash('Email already exists', category='error')
            return False
        elif password1 != password2:
            flash('Re-entered password does not match', category='error')
            return False
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
            return False

    return True
    

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('views.basic'))
        
        flash('Login failed. Check your email and password.', category='error')
        
    return render_template("login.html")

# s = URLSafeTimedSerializer("Thisasecret")
# def send_confirmation_email(user_email):
#     token = s.dumps(user_email, salt='email-confirm')
#     confirm_url = url_for('auth.confirm_email', token=token, _external=True)
#     html = render_template('activate.html', confirm_url=confirm_url)
#     subject = "Please confirm your email"
#     msg = Message(subject, recipients=[user_email], html=html)
#     try: 
#         Mail.send(msg)
#         return True
#     except Exception as e: 
#         print(f"Failed to send email: {e}")
#         return False

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        rePassword = request.form.get('rePassword')
        
        if validate_user_details(firstName, lastName, username, email, password, rePassword, sign_up=True):
            new_user = User(firstName=firstName, lastName=lastName, username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Your account is created!', category='success')
            return redirect(url_for('auth.login'))
    return render_template("signup.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Handle forgot password logic here
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')