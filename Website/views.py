from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from Website.models import Movie, Genre, Actor, Director, MovieGenre, MovieActor, MovieDirector, User
import plotly.express as px
import plotly.io as pio
import pandas as pd
from dotenv import load_dotenv
from os import environ
from . import db

load_dotenv()

views = Blueprint('views', __name__)  # Define blueprint

def get_movie_data():
    #Query all required columns from the database
    query = db.session.query(
        Actor.name.label('actor_name'),
        Director.name.label('director_name'),
        Genre.name.label('genre_name'), 
        Movie.title,
        Movie.overview, 
        Movie.status,
        Movie.release_year,
        Movie.popularity,        
        Movie.vote_average, 
        Movie.vote_count,
        Movie.runtime,
        Movie.adult, 
        Movie.overview_sentiment,
        Movie.all_combined_keywords,
        Movie.Star1,
        Movie.Star2,
        Movie.Star3,
        Movie.Star4    
       ).join(MovieActor, Movie.movie_id == MovieActor.movie_id)\
        .join(Actor, Actor.actor_id == MovieActor.actor_id)\
        .join(MovieDirector, Movie.movie_id == MovieDirector.movie_id)\
        .join(Director, Director.director_id == MovieDirector.director_id)\
        .join(MovieGenre, Movie.movie_id == MovieGenre.movie_id)\
        .join(Genre, Genre.genre_id == MovieGenre.genre_id)\
        .all()
        
    #Create a DataFrame from the query results
    data = [{
        'actor_name': row[0],
        'director_name': row[1],
        'genre_name': row[2],
        'title': row[3],
        'overview': row[4],
        'status': row[5],
        'release_year': row[6],
        'popularity': row[7],
        'vote_average': row[8],
        'vote_count': row[9],
        'runtime': row[10],
        'adult': row[11],
        'overview_sentiment': row[12],
        'all_combined_keywords': row[13],
        'Star1': row[14],
        'Star2': row[15],
        'Star3': row[16],
        'Star4': row[17]
    } for row in query]
    df = pd.DataFrame(data)
    
    return df
    
@views.route('/testing.html')
def testing():
    return render_template("testing.html", text="Hi, my name is", user="ALi", boolean=True)

@views.route('/')  # Root function
def base():
    return render_template("homepage.html")

@views.route('/basic.html')
def basic():
    df = get_movie_data()
    
    return render_template("basic.html")

@views.route('/intermediate.html', methods=['GET', 'POST'])
def intermediate():
    df = get_movie_data()
    ##CHART 1: Number of Movie Releases by Genre Over Time
    df1 = df.groupby(['release_year', 'genre']).size().reset_index(name='coutn')
    fig1 = px.area(df1, x="release_year", y="count", color="genre", line_group="genre", title='Number of Movie Releases by Genre Over Time')
    fig1.update_xaxes(dtick = 1)  # Update x-axis to set the interval to one year
    chart1 = pio.to_html(fig1, full_html=False)
    
    ##CHART 2: Average Movie Runtime by year
    df2 = df.groupby('release_year').runtime.mean().reset_index()
    fig2 = px.line(df2, x="release_year", y="runtime", title='Average Movie Runtime by Year')
    fig2.update_xaxes(dtick = 1)
    chart2 = pio.to_html(fig2, full_html=False)
    
    ##CHART 3: Frequent Actors/Actresses Across Genres
    
    
    ##CHART 4:
    
    
    ##CHART 5:
    
    
    return render_template("intermediate.html", chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4, chart5=chart5)

@views.route('/advanced.html')
def advanced():
    df = get_movie_data()
    
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