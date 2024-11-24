from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from Website.models import Movie, Genre, Actor, Director, MovieGenre, MovieActor, MovieDirector, User
from Website.movie_api import fetch_api_data, process_movie_data, feature_extraction
from Website.auth import validate_user_details
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from . import db
import requests
import plotly.express as px
import plotly.io as pio
import pandas as pd
from wordcloud import WordCloud
from datetime import datetime

# Define blueprint
views = Blueprint('views', __name__)  

#Define the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Website', 'static', 'profile_pics')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Helper function to get movie data
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
        Movie.production_country,
        Movie.Star1,
        Movie.Star2,
        Movie.Star3,
        Movie.Star4    
       ).join(MovieActor, Movie.movie_id == MovieActor.c.movie_id)\
        .join(Actor, Actor.actor_id == MovieActor.c.actor_id)\
        .join(MovieDirector, Movie.movie_id == MovieDirector.c.movie_id)\
        .join(Director, Director.director_id == MovieDirector.c.director_id)\
        .join(MovieGenre, Movie.movie_id == MovieGenre.c.movie_id)\
        .join(Genre, Genre.genre_id == MovieGenre.c.genre_id)\
        .all()
        
    # if user_id:
    #     query = query.outerjoin(favorite_movies, (Movie.movie_id == favorite_movies.c.movie_id) & (favorite_movies.c.user_id == user_id))\
    #                  .outerjoin(recommended_movies, (Movie.movie_id == recommended_movies.c.movie_id) & (recommended_movies.c.user_id == user_id))
    
    # result = query.all()
        
    #Create a DataFrame from the query results
    data = [{
        'actor': row[0],
        'director': row[1],
        'genre': row[2],
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
        'production_country': row[14],
        'Star1': row[15],
        'Star2': row[16],
        'Star3': row[17],
        'Star4': row[18]
    } for row in query]

    df = pd.DataFrame(data)
    return df
    
# @views.route('/testing.html')
# def testing():
#     return render_template("testing.html", text="Hi, my name is", user="ALi", boolean=True)

@views.route('/profile.html', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        current_password = request.form.get('current-password')
        new_password = request.form.get('new-password')
        profile_picture = request.files.get('profile-picture')
        
        # Retain existing values if form fields are empty
        email = email or current_user.email
        username = username or current_user.username
        firstName = firstName or current_user.firstName
        lastName = lastName or current_user.lastName
        
        # Validate user details
        if validate_user_details(firstName, lastName, username, email):
            # Check to see if user wanna change password
            if new_password:
                if len(new_password) >= 7:
                    if check_password_hash(current_user.password, current_password): 
                        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                    else:
                        flash('Current password is invalid', category='error')
                        return redirect(url_for('views.profile_page'))
                else:
                    flash('Password must be at least 7 characters', category='error')
                    return redirect(url_for('views.profile_page'))
            
            # Check if profile picture is uploaded      
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                profile_picture.save(file_path)
                current_user.profile_picture = filename

            current_user.email = email
            current_user.username = username
            current_user.firstName = firstName
            current_user.lastName = lastName
            db.session.commit()
            flash('Your profile details have been updated successfully!', category='success')
        else:
            flash('Profile update failed. Please check your details.', category='error')
            return redirect(url_for('views.profile_page'))  

    return render_template("profile.html", user=current_user)

@views.route('/favourites.html')
@login_required
def favourites():
    return render_template("favourites.html")

@views.route('/personalized.html')
@login_required
def personalized():
    return render_template("personalized.html")

@views.route('/')  # Root function
def homepage():
    return render_template("homepage.html")

@views.route('/basic.html', methods=['GET', 'POST'])
def basic():
    df = get_movie_data()
    ##CHART 1: Top 10 Most Popular Movies (By vote_count and Popularity)
    df1 = df.groupby('title').agg({'vote_count': 'sum', 'popularity': 'mean'}).sort_values(by=['vote_count', 'popularity'], ascending=False).head(10)
    fig1 = px.bar(df1, x='vote_count', y=df1.index, orientation='h')
    chart1 = pio.to_html(fig1, full_html=False)
    
    ##CHART 2: Top 10 Most Prolific Directors (By vote_count and popularity)
    df2 = df.groupby('director').agg({'vote_count': 'sum', 'popularity': 'mean'}).sort_values(by=['vote_count', 'popularity'], ascending=False).head(10)
    fig2 = px.treemap(df2, path=['Director'], values='vote_count', color='popularity')
    chart2 = pio.to_html(fig2, full_html=False)
    
    ##CHART 3: Genre Distribution
    df3 = df.groupby('genre').size().reset_index(name="count")
    fig3 = px.pie(df2, values="count", names="genre")
    chart3 = pio.to_html(fig3, full_html=False) 
    
    ##CHART 4: Total Number of Movies Released Per Year
    df4 = df.groupby('release_year').size().reset_index(name="count")
    fig4 = px.line(df4, x='release_year', y='count')
    chart4 = pio.to_html(fig4, full_html=False)
    
    ##CHART 5: Adult vs Non-Adult Movies Count
    df5 = df.groupby('adult').size().reset_index(name="count")
    fig4 = px.bar(df5, x='adult', y='count')
    chart5 = pio.to_html(fig4, full_html=False)
    
    ##CHART 6: Most Starred Actors/Actresses (Star1, Star2, Star3, Star4)
    df6 = pd.concat([df['Star1'], df['Star2'], df['Star3'], df['Star4']]).value_counts().reset_index()
    df6.columns = ['actor', 'count']
    wordCloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df6['actor']))
    fig6 = px.imshow(wordCloud)
    chart6 = pio.to_html(fig6, full_html=False)
    
    return render_template("basic.html", chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4, chart5=chart5, chart6=chart6)

@views.route('/intermediate.html', methods=['GET', 'POST'])
def intermediate():
    df = get_movie_data()
    
    ##CHART 1: Number of Movie Releases by Genre Over Time
    df1 = df.groupby(['release_year', 'genre']).size().reset_index(name='count')
    fig1 = px.area(df1, x="release_year", y="count", color="genre", line_group="genre")
    fig1.update_xaxes(dtick = 1)  # Update x-axis to set the interval to one year
    chart1 = pio.to_html(fig1, full_html=False)
    
    ##CHART 2: Average Movie Runtime by year
    df2 = df.groupby('release_year').runtime.mean().reset_index()
    fig2 = px.box(df2, x="release_year", y="runtime", hover_data=["release_year", "runtime"])
    fig2.update_xaxes(dtick = 1)
    chart2 = pio.to_html(fig2, full_html=False)
    
    ##CHART 3: Top 10 Starred Actors/Actresses Across Genres
    df3 = pd.concat([df['Star1'], df['Star2'], df['Star3'], df['Star4']]).value_counts().reset_index()
    df3.columns = ['actor', 'count']
    df3 = df.groupby(["actor", "genres"])["count"].sum().reset_index()
    df3 = df3.pivot(index="actor", columns="genre", values="count")["count"].fillna(0)
    fig3 = px.imshow(df3, x=df3.columns, y=df3.index)
    fig3.update_layout(width=500, height=500)
    fig3.show()
    chart3 = pio.to_html(fig3, full_html=False)
    
    ##CHART 4: Most Associated Cast Members for Top 10 Directors
    df4 = df.groupby(['director', 'actor']).size().reset_index(name='count')
    fig4 = px.sunburst(df4, path=['director', 'actor'], values='count')
    chart4 = pio.to_html(fig4, full_html=False)
    
    ##CHART 5: Average Popularity and Sentiment of Movies by Genre
    df5 = df.groupby('genre').agg({'popularity': 'mean', 'overview_sentiment': 'mean'}).reset_index()
    fig5 = px.scatter(df5, x='popularity', y='overview_sentiment', color = 'genre', hover_data = ['genre'])
    chart5 = pio.to_html(fig5, full_html=False)
    
    ##CHART 6: Popularity Success of Genres by Director
    df6 = df.groupby(['director', 'genre']).popularity.mean().reset_index()
    fig6 = px.bar(df6, x='director', y='genre', color='popularity')
    chart6 = pio.to_html(fig6, full_html=False)
    
    return render_template("intermediate.html", chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4, chart5=chart5, chart6=chart6)

@views.route('/advanced.html', methods=['GET', 'POST'])
def advanced():    
    ##CHART 1: Number of Movies by Production Country
    # df = get_movie_data()
    # df1 = df.groupby('production_country').size().reset_index(name='count')
    # fig1 = px.choropleth(df1, 
    #                      locations='production_country', 
    #                      locationmode='country names', 
    #                      color='count', 
    #                      hover_name='production_country'
    #                      )
    # chart1 = pio.to_html(fig1, full_html=False)
    
    ##CHART 2: Data Comparison Tools (Real-Time Popularity Tracker)
    all_movies = []
    for page in range(1,20):
        api_data = fetch_api_data(page)
        for movie in api_data['results']:
            movies = process_movie_data(movie)
            all_movies.append(movies)

    df2 = pd.DataFrame(all_movies)
    df2 = feature_extraction(df2)
    
    #Spider Chart 1
    fig2 = px.line_polar(df2, r=[df2['vote_average'], df2['popularity'], df2['vote_count'], df2['runtime'], df2['trend_score']], theta='title', line_close=True)
    chart2 = pio.to_html(fig2, full_html=False)
    
    #Spider Chart 2
    fig3 = px.line_polar(df2,r=[df2['vote_average'], df2['popularity'], df2['vote_count'], df2['runtime'], df2['trend_score']], theta='title', line_close=True)
    chart3 = pio.to_html(fig3, full_html=False)
    
    return render_template("advanced.html", chart1=chart1, chart2=chart2, chart3=chart3)

@views.route('/movie_details.html')
def movie_details_page():
    return render_template("movie_details.html")

@views.route('/settings.html')
def settings_page():
    return render_template("settings.html")