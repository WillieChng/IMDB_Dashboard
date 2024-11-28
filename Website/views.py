from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_caching import Cache
from flask_login import current_user, login_required
from Website.models import Movie, Genre, Actor, Director, MovieGenre, MovieActor, MovieDirector, User
from Website.movie_api import fetch_api_data, process_movie_data, feature_extraction
from Website.auth import validate_user_details
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from . import db, cache
import requests
import plotly.express as px
import plotly.io as pio
import pandas as pd
from wordcloud import WordCloud
import numpy as np
from datetime import datetime
from sqlalchemy.orm import joinedload
import plotly.graph_objects as go

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
        Movie.production_countries,
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
        'production_countries': row[14],
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

@views.route('/personalized.html')
@login_required
def personalized():
    # Get user's favorite genres
    favourite_movies = current_user.user_favourites
    genre_counts = {}
    for movie in favourite_movies:
        for genre in movie.genres:
            if genre.name in genre_counts:
                genre_counts[genre.name] += 1
            else:
                genre_counts[genre.name] = 1

    # Sort genres by count and get top 3 genres
    sorted_genres = sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)
    top_genres = [genre[0] for genre in sorted_genres[:3]]
    
    if not top_genres:
        # Handle case with no favorite genres
        flash('You have no favorite genres yet. Please add some favorite movies to get personalized recommendations.', 'info')
        return redirect(url_for('views.user_favourites'))

    # Fetch recommendations based on top genres
    recommendations = Movie.query.join(Movie.genres).filter(Genre.name.in_(top_genres)).order_by(Movie.popularity.desc()).limit(3).all()

    return render_template("personalized.html", top_genres=top_genres, recommendations=recommendations)

@views.route('/')  # Root function
def homepage():
    return render_template("homepage.html")

@views.route('/basic.html', methods=['GET', 'POST'])
@cache.cached(timeout=300)
@login_required
def basic():
    # Optimize the query by using joinedload to reduce the number of queries
    query = db.session.query(Movie).options(
        joinedload(Movie.actors),
        joinedload(Movie.directors),
        joinedload(Movie.genres)
    ).limit(100).all()

    data = [{
        'title': row.title,
        'overview': row.overview,
        'status': row.status,
        'release_year': row.release_year,
        'popularity': row.popularity,
        'vote_average': row.vote_average,
        'vote_count': row.vote_count,
        'runtime': row.runtime,
        'adult': row.adult,
        'overview_sentiment': row.overview_sentiment,
        'all_combined_keywords': row.all_combined_keywords,
        'production_countries': row.production_countries,
        'Star1': row.Star1,
        'Star2': row.Star2,
        'Star3': row.Star3,
        'Star4': row.Star4,
        'actors': [actor.name for actor in row.actors],
        'directors': [director.name for director in row.directors],
        'genres': ', '.join([genre.name for genre in row.genres])  # Convert list of genres to a comma-separated string
    } for row in query]
    
    

    df = get_movie_data()
    ##CHART 1: Top 10 Most Popular Movies (By vote_count and Popularity)
    df1 = df.groupby('title').agg({'vote_count': 'sum', 'popularity': 'mean'}).sort_values(by=['vote_count', 'popularity'], ascending=False).head(10)
    fig1 = px.bar(df1, x='vote_count', y=df1.index, orientation='h', width=600, height=400)
    chart1 = pio.to_html(fig1, full_html=False)

    ##CHART 2: Top 10 Most Prolific Directors (By vote_count and popularity)
    df2 = df.groupby('director').agg({'vote_count': 'sum', 'popularity': 'mean'}).sort_values(by=['vote_count', 'popularity'], ascending=False).head(10).reset_index()
    fig2 = px.treemap(df2, path=['director'], values='vote_count', color='popularity', width=640, height=300)
    chart2 = pio.to_html(fig2, full_html=False)

    ##CHART 3: Genre Distribution
    df3 = df.groupby('genre').size().reset_index(name="count")
    fig3 = px.pie(df3, values="count", names="genre", width=570, height=380)
    chart3 = pio.to_html(fig3, full_html=False) 

    ##CHART 4: Total Number of Movies Released Per Year
    df4 = df.groupby('release_year').size().reset_index(name="count")
    fig4 = px.line(df4, x='release_year', y='count', width=1250, height=400)
    chart4 = pio.to_html(fig4, full_html=False)

    ##CHART 5: Adult vs Non-Adult Movies Count
    df5 = df.groupby('adult').size().reset_index(name="count")
    fig5 = px.bar(df5, x='adult', y='count', width=550, height=400)
    chart5 = pio.to_html(fig5, full_html=False)

    ##CHART 6: Most Starred Actors/Actresses (Star1, Star2, Star3, Star4)
    df6 = pd.concat([df['Star1'], df['Star2'], df['Star3'], df['Star4']]).value_counts().reset_index()
    df6.columns = ['actor', 'count']
    wordCloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df6['actor']))
    fig6 = px.imshow(wordCloud, width=600, height=400)
    chart6 = pio.to_html(fig6, full_html=False)

    return render_template("basic.html", chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4, chart5=chart5, chart6=chart6)

  

@views.route('/intermediate.html', methods=['GET', 'POST'])
@cache.cached(timeout=300)
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
        df3.columns = ['actor', 'vote_count']
        df3 = df.groupby(["actor", "genre"])["vote_count"].sum().reset_index()
        df3 = df3.pivot(index="actor", columns="genre", values="vote_count").fillna(0)
        fig3 = px.imshow(df3, x=df3.columns, y=df3.index)
        fig3.update_layout(width=500, height=500)
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
    



@views.route('/advance.html', methods=['GET', 'POST'])
@cache.cached(timeout=300)
def advance():    
    ##CHART 1: Map visualization of movie production countries
    df = get_movie_data()
    df1 = df.groupby('production_countries').size().reset_index(name='vote_count')
    fig1 = px.choropleth(df1, 
                         locations='production_countries', 
                         locationmode='country names', 
                         color='vote_count', 
                         hover_name='production_countries'
                         )
    chart1 = pio.to_html(fig1, full_html=False)
    
    all_movies = []
    for page in range(1, 20):
        api_data = fetch_api_data(page)
        if api_data:
            if 'results' in api_data:
                for movie in api_data['results']:
                    movies = process_movie_data(movie)
                    all_movies.append(movies)
            else:
                print(f"'results' key not found in API response for page {page}")
        else:
            print(f"Failed to fetch data for page {page}")
    
    df2 = pd.DataFrame(all_movies)
    df2 = feature_extraction(df2)        

    df2_long = df2.melt(id_vars=['title'], value_vars=['vote_average', 'popularity', 'vote_count', 'runtime', 'trend_score'], var_name='metric', value_name='value')
    
    fig1 = go.Figure()
    fig2 = go.Figure()
    
    for title in df2_long['title'].unique():
        subset = df2_long[df2_long['title'] == title]
        fig1.add_trace(go.Scatterpolar(
            r=subset['value'],
            theta=subset['metric'],
            name=title,
            mode='lines',
            line=dict(color='blue', dash='solid')  # Valid properties
        ))
        fig2.add_trace(go.Scatterpolar(
            r=subset['value'],
            theta=subset['metric'],
            name=title,
            mode='lines',
            line=dict(color='blue', dash='solid')  # Valid properties
        ))
        
    fig1.update_layout(polar=dict(angularaxis=dict(rotation=90)), title="Spider Chart 1")
    fig2.update_layout(polar=dict(angularaxis=dict(rotation=90)), title="Spider Chart 2")

    chart2 = pio.to_html(fig1, full_html=False)
    chart3 = pio.to_html(fig2, full_html=False)
    
    return render_template("advance.html", chart1=chart1, chart2=chart2, chart3=chart3)

@views.route('/update_chart', methods=['GET'])
def update_chart():
    chart_id = request.args.get('chart_id')
    movie_title = request.args.get('movie_title')
    width = request.args.get('width', 650)
    height = request.args.get('height', 470)

    df = get_movie_data()
    if df is None:
        return jsonify(error="Error fetching movie data"), 500

    df2 = feature_extraction(df)
    df2_long = df2.melt(id_vars=['title'], value_vars=['vote_average', 'popularity', 'vote_count', 'runtime', 'trend_score'], var_name='metric', value_name='value')

    fig = go.Figure()
    subset = df2_long[df2_long['title'].str.contains(movie_title, case=False, na=False)]
    fig.add_trace(go.Scatterpolar(
        r=subset['value'],
        theta=subset['metric'],
        name=movie_title,
        mode='lines',
        line=dict(dash='solid')  # Valid properties
    ))

    fig.update_layout(
        polar=dict(angularaxis=dict(rotation=90)),
        title=f"Details for {movie_title}",
        width=int(width),
        height=int(height)
    )

    chart_html = pio.to_html(fig, full_html=False)
    return jsonify(chart_html=chart_html)

# search
@views.route('/search_results.html')
def search_results_page():
    return render_template("search_results.html")

@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        # Implement your search logic here
        results = search_movies(query)
        return render_template('search_results.html', query=query, results=results)
    else:
        flash('Please enter a search term', category='error')
        return redirect(url_for('views.homepage'))

def search_movies(query):
    results = Movie.query.filter(
        (Movie.title.ilike(f'%{query}%')) |
        (Movie.overview.ilike(f'%{query}%')) |
        (Movie.actors.any(Actor.name.ilike(f'%{query}%'))) |
        (Movie.genres.any(Genre.name.ilike(f'%{query}%')))
    ).all()
    return results

#in search bar, top searches
@views.route('/top_searches', methods=['GET'])
def top_searches():
    query = request.args.get('query', '')
    if query:
        results = Movie.query.filter(Movie.title.ilike(f'%{query}%')).limit(10).all()
    else:
        results = Movie.query.order_by(Movie.popularity.desc()).limit(10).all()
    
    top_searches = [{'title': movie.title} for movie in results]
    return jsonify(top_searches)

#search bar, alphabetically
@views.route('/alphabetical_searches', methods=['GET'])
def alphabetical_searches():
    query = request.args.get('query', '')
    if query:
        results = Movie.query.filter(Movie.title.ilike(f'{query}%')).order_by(Movie.title).limit(10).all()
    else:
        results = Movie.query.order_by(Movie.title).limit(10).all()
    
    alphabetical_searches = [{'title': movie.title} for movie in results]
    return jsonify(alphabetical_searches)

@views.route('/movie_details/<int:movie_id>')
def movie_details_page(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('movie_details.html', movie=movie)

#movie favourite handling
@views.route('/add_to_favourites', methods=['POST'])
@login_required
def add_to_favourites():
    movie_id = request.args.get('movie_id')
    movie = Movie.query.get(movie_id)
    if movie and movie not in current_user.user_favourites:
        current_user.user_favourites.append(movie)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@views.route('/remove_from_favourites', methods=['POST'])
@login_required
def remove_from_favourites():
    movie_id = request.args.get('movie_id')
    movie = Movie.query.get(movie_id)
    if movie and movie in current_user.user_favourites:
        current_user.user_favourites.remove(movie)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@views.route('/user_favourites.html')
@login_required
def user_favourites():
    favourites = current_user.user_favourites
    return render_template('user_favourites.html', favourites=favourites)

@views.route('/settings.html')
def settings_page():
    return render_template("settings.html")




