from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_caching import Cache
from flask_login import current_user, login_required
from Website.models import Movie, Genre, Actor, Director, MovieGenre, MovieActor, MovieDirector, User
from Website.movie_api import fetch_api_data, process_movie_data, feature_extraction
from Website.auth import validate_user_details
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from Website import db, cache
import plotly.express as px
import plotly.io as pio
import pandas as pd
from wordcloud import WordCloud
import numpy as np
from datetime import datetime
from sqlalchemy.orm import joinedload, selectinload
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import networkx as nx

# Define blueprint
views = Blueprint('views', __name__) 

# Define the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Website', 'static', 'profile_pics')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to get movie data
def get_movie_data():
    # Retrieve necessary columns for the intermediate page using joinedload
    query = db.session.query(Movie).options(
        selectinload(Movie.directors),   # Load directors eagerly
        selectinload(Movie.genres),      # Load genres eagerly
    ).join(MovieDirector, Movie.movie_id == MovieDirector.c.movie_id)\
    .join(Director, Director.director_id == MovieDirector.c.director_id)\
    .join(MovieGenre, Movie.movie_id == MovieGenre.c.movie_id)\
    .join(Genre, Genre.genre_id == MovieGenre.c.genre_id)\
    .all()

    # Prepare the data for the response
    data = [{
        'title': row.title,  # Directly get the movie title
        'vote_count': row.vote_count,  # Directly get vote count
        'popularity': row.popularity,  # Directly get popularity
        'runtime': row.runtime,  # Directly get runtime
        'director': ', '.join([director.name for director in row.directors]),  # Join directors' names if there are multiple
        'genre': ', '.join([genre.name for genre in row.genres]),  # Join genres if there are multiple
        'release_year': row.release_year,  # Directly get release year
        'overview_sentiment': row.overview_sentiment,  # Directly get overview sentiment
        'Star1': row.Star1,  # Directly get Star1
    } for row in query]

    df = pd.DataFrame(data)
    
    # Split the 'genre' column into individual genres and explode the DataFrame
    df['genre'] = df['genre'].str.split(', ')
    df = df.explode('genre')
    
    return df

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

@views.route('/testing.html', methods=['GET', 'POST'])
def testing():
    # Retrieve necessary columns for the basic page using joinedload
    query = db.session.query(Movie).options(
        selectinload(Movie.directors),   # Load directors eagerly
        selectinload(Movie.genres),      # Load genres eagerly
    ).join(MovieDirector, Movie.movie_id == MovieDirector.c.movie_id)\
    .join(Director, Director.director_id == MovieDirector.c.director_id)\
    .join(MovieGenre, Movie.movie_id == MovieGenre.c.movie_id)\
    .join(Genre, Genre.genre_id == MovieGenre.c.genre_id)\
    .all()

    # Prepare the data for the response
    data = [{
        'title': row.title,  # Directly get the movie title
        'vote_count': row.vote_count,  # Directly get vote count
        'popularity': row.popularity,  # Directly get popularity
        'director': ', '.join([director.name for director in row.directors]),  # Join directors' names if there are multiple
        'genre': ', '.join([genre.name for genre in row.genres]),  # Join genres if there are multiple
        'release_year': row.release_year,  # Directly get release year
        'adult': row.adult,  # Directly get adult status
        'Star1': row.Star1,  # Directly get Star1
        'Star2': row.Star2,  # Directly get Star2
        'Star3': row.Star3,  # Directly get Star3
        'Star4': row.Star4   # Directly get Star4
    } for row in query]

    return render_template("testing.html", data=data)

@views.route('/basic.html', methods=['GET', 'POST'])
@cache.cached(timeout=300)
@login_required
def basic():
    # Retrieve necessary columns for the basic page using joinedload
    query = db.session.query(Movie).options(
        selectinload(Movie.directors),   # Load directors eagerly
        selectinload(Movie.genres),      # Load genres eagerly
    ).join(MovieDirector, Movie.movie_id == MovieDirector.c.movie_id)\
    .join(Director, Director.director_id == MovieDirector.c.director_id)\
    .join(MovieGenre, Movie.movie_id == MovieGenre.c.movie_id)\
    .join(Genre, Genre.genre_id == MovieGenre.c.genre_id)\
    .all()

    # Prepare the data for the response
    data = [{
        'title': row.title,  # Directly get the movie title
        'vote_count': row.vote_count,  # Directly get vote count
        'director': ', '.join([director.name for director in row.directors]),  # Join directors' names if there are multiple
        'genre': ', '.join([genre.name for genre in row.genres]),  # Join genres if there are multiple
        'release_year': row.release_year,  # Directly get release year
        'adult': row.adult,  # Directly get adult status
        'Star1': row.Star1,  # Directly get Star1
        'Star2': row.Star2,  # Directly get Star2
        'Star3': row.Star3,  # Directly get Star3
        'Star4': row.Star4   # Directly get Star4
    } for row in query]

    df = pd.DataFrame(data)
    
    ##CHART 1: Top 10 Most Popular Movies (By vote_count and Popularity)
    df1 = df.groupby('title').agg({'vote_count': 'sum'}).sort_values(by=['vote_count'], ascending=False).head(10)
    fig1 = px.bar(df1, x='vote_count', y=df1.index, orientation='h', width=600, height=400)
    chart1 = pio.to_html(fig1, full_html=False)

    ##CHART 2: Top 10 Most Prolific Directors (By vote_count)
    df2 = df.groupby('director').agg({'vote_count': 'sum'}).sort_values(by=['vote_count'], ascending=False).head(10).reset_index()
    fig2 = px.treemap(df2, path=['director'], values='vote_count', color='vote_count', width=640, height=300,
                      hover_data={'director': True, 'vote_count': True})
    chart2 = pio.to_html(fig2, full_html=False)

    ##CHART 3: Genre Distribution
    df3 = df['genre'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).to_frame('genre')
    df3 = df3.groupby('genre').size().reset_index(name="count")
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

###INTERMEDIATE SECTION
# Layout for Dash app
def create_dash_app(flask_app):
    # Initialize Dash app
    dash_app = dash.Dash(__name__, server=flask_app, url_base_pathname='/dash/')

    #dash font 
    dash_app.css.append_css({"external_url": "/static/intermediate.css"})

    # Calculate the top 10 directors based on vote count within the Flask application context
    with flask_app.app_context():
        df_director = get_movie_data()
        top_directors = df_director.groupby('director').agg({'vote_count': 'sum'}).sort_values(by=['vote_count'], ascending=False).head(10).index.tolist()
    
    # Define a variable to indicate the current mode (light or dark)
    mode = 'dark'  # Change this to 'light' for light mode

    # Define styles for light and dark modes
    light_mode_styles = {
        'backgroundColor': '#FFF',
        'textColor': '#000',
        'dropdownBackgroundColor': '#FFF',
        'dropdownTextColor': '#000',
        'chartContainerBackgroundColor': '#FFF',
        'descriptionContainerBackgroundColor': '#FFF',
        'descriptionTextColor': '#000'
    }
    
    dark_mode_styles = {
    'backgroundColor': '#111',
    'textColor': '#FFF',
    'dropdownBackgroundColor': '#333',
    'dropdownTextColor': '#FFF',
    'chartContainerBackgroundColor': '#222',
    'descriptionContainerBackgroundColor': '#222',
    'descriptionTextColor': '#AAA'
    }

# Select styles based on the current mode
    styles = dark_mode_styles if mode == 'dark' else light_mode_styles

    dash_app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label='Year Filtering', children=[
                html.Div([
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': str(year), 'value': year} for year in range(2019, datetime.now().year)],
                        multi=True,
                        placeholder='Select Year(s)',
                    ),
                    html.Div([
                        html.Div([
                        html.H2("Number of Movie Releases by Genre Over Time", style={'color': styles['textColor'], 'textAlign': 'center'}),
                        dcc.Graph(id='chart1')
                    ], className='chart-container', style={'backgroundColor': styles['chartContainerBackgroundColor']}),
                        html.Div([
                            html.P("2020-2022 has seen a trend in increase of movies across majority of genres. Drama and Documentary are genres that are frequently released throughout the years, with comedy coming at a close second. The least released genres are War, Western and history due to lack of demand and interest from audience.", style={'color': styles['descriptionTextColor']})
                    ], className='description-container', style={'backgroundColor': styles['descriptionContainerBackgroundColor']})
                    ], className='chart-description-wrapper'),
                    html.Div([
                        html.Div([
                            html.H2("Average Movie Runtime by Year", style={'color': styles['textColor'], 'textAlign': 'center'}),
                            dcc.Graph(id='chart2')
                    ], className='chart-container', style={'backgroundColor': styles['chartContainerBackgroundColor']}),
                        html.Div([
                        html.P("Across all of the years, the average movie runtime are closely knitted together with 2019 showing the highest average runtime. Then, from there forth, the average runtime has been decreasing with the year 2023 ending up with only 20 minutes. This could be due to the fact that movies are becoming more fast-paced and concise to adapt to audience's decreasing attention span in modern times due to the influence of social media", style={'color': styles['descriptionTextColor']})
                        ], className='description-container')
                    ], className='chart-description-wrapper')
                ])
            ]),
            dcc.Tab(label='Genre Filtering', children=[
                html.Div([
                    dcc.Dropdown(
                        id='genre-dropdown',
                        options=[{'label': genre.name, 'value': genre.name} for genre in Genre.query.all()],
                        multi=True,
                        placeholder='Select Genre(s)'
                    ),
                    html.Div([
                        html.Div([
                            html.H2("Top 10 Starred Actors/Actresses Across Genres", style={'color': styles['textColor'], 'textAlign': 'center'}),
                            dcc.Graph(id='chart3')
                        ], className='chart-container', style={'backgroundColor': styles['chartContainerBackgroundColor']}),
                        html.Div([
                            html.P("""The chart shows the top 10 actors/actresses have all starred in a decent amount of comedy movies. Moreover, talented actors/actresses are more likely to be casted in comedy movies due to their ability to deliver great punchlines and comedic timing. 
                                   Action, Thriller, Drama and Horror are the next most popular genres that actors/actresses have starred in which indicates them having a different set of acting skills to deliver a convincing performance. 
                                   War is the least popular genre for actors/actresses to star in due to the lack of demand and interest from the audience. It is also a challenging genre to act in as it requires actors/actresses to portray the harsh realities of war. 
                                   Ultimately, the chart shows that actors/actresses have starred in a variety of genres which showcases their versatility and acting skills.""")
                        ], className='description-container', style={'color': styles['descriptionTextColor'], 'padding-left': '10px'})
                    ], className='chart-description-wrapper', style={'display': 'flex', 'align-items': 'center'}),
                    html.Div([
                        html.Div([
                            html.H2("Average Popularity and Sentiment of Movies by Genre", style={'color': styles['textColor'], 'textAlign': 'center'}),
                            dcc.Graph(id='chart4')
                        ], className='chart-container', style={'backgroundColor': styles['chartContainerBackgroundColor']}),
                        html.Div([
                            html.P("Family and adventure movies have the highest average popularity and sentiment score. This is due to the fact that family movies are generally heartwarming and have a positive message that resonates with the audience. Adventure movies are also popular as they provide an escape from reality and take the audience on an exciting journey. Western and horror movies have the lowest average popularity and sentiment score. Western movies are a niche genre that appeals to a specific audience, while horror movies are known for their dark and unsettling themes.")
                        ], className='description-container', style={'color': styles['descriptionTextColor']})
                    ], className='chart-description-wrapper')
                ])
            ]),
            dcc.Tab(label='Director Filtering', children=[
                html.Div([
                    dcc.Dropdown(
                        id='director-dropdown',
                        options=[{'label': director, 'value': director} for director in top_directors],
                        multi=True,
                        placeholder='Select Director(s)'
                    ),
                    html.Div([
                        html.Div([
                            html.H2("Popularity Success of Genres by Top 10 Directors", style={'color': styles['textColor'], 'textAlign': 'center'}),
                            dcc.Graph(id='chart5')
                        ], className='chart-container', style={'backgroundColor': styles['chartContainerBackgroundColor']}),
                        html.Div([
                            html.P("James Mangold has the highest average popularity across all genres, working on box-office movies such as Logan, Ford v Ferrari and Walk the Line. Followed by Francis Lawrence and Robert Schwentke, which shows their ability to direct movies of different themes that resonate with the audience.", style={'color': styles['descriptionTextColor']})
                        ], className='description-container', style={'backgroundColor': styles['descriptionContainerBackgroundColor']})
                    ], className='chart-description-wrapper')
                ])
            ])
        ])
    ], style={'fontFamily': 'Nunito'})

    # Add the CSS link to the Google Fonts API
    dash_app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    df = get_movie_data()
    # Callbacks for updating charts based on filters
    @dash_app.callback(
        Output('chart1', 'figure'),
        [Input('year-dropdown', 'value')]
    )
    def update_chart1(selected_years):
        df1 = df.copy()
        if selected_years:
            df1 = df1[df1['release_year'].isin(selected_years)]
            
        ##CHART 1: Number of Movie Releases by Genre Over Time
        df1 = df1.groupby(['release_year', 'genre']).size().reset_index(name='count')
        df1 = df1.sort_values(by=['release_year', 'count'], ascending=[False, True])
        fig1 = px.area(df1, x="release_year", y="count", color="genre", line_group="genre")
        fig1.update_xaxes(dtick=1)  # Update x-axis to set the interval to one year
        return fig1

    @dash_app.callback(
        Output('chart2', 'figure'),
        [Input('year-dropdown', 'value')]
    )
    def update_chart2(selected_years):
        df2 = df.copy()
        if selected_years:
            df2 = df2[df2['release_year'].isin(selected_years)]
        
                        # Print the data to verify
        print("Chart 2 Data:")
        print(df2.head())
        
        ##CHART 2: Average Movie Runtime by year
        fig2 = px.box(df2, x="release_year", y="runtime", hover_data=["release_year", "runtime"])
        fig2.update_xaxes(dtick=1)
        return fig2

    @dash_app.callback(
        Output('chart3', 'figure'),
        [Input('genre-dropdown', 'value')]
    )
    def update_chart3(selected_genres):
        df3 = df.copy()
        if selected_genres:
            df3 = df3[df3['genre'].isin(selected_genres)]
            
        #CHART 3: Top 10 Starred Actors/Actresses Across Genres
        # Concatenate the Star columns into a single Series\       
        stars = pd.concat([
            df3[['Star1', 'genre']].rename(columns={'Star1': 'actor'}),
        ])
        
        # Group by actor and genre, and count the occurrences
        df3 = stars.groupby(['actor', 'genre']).size().reset_index(name='count')
        # Step 4: Calculate the total count of appearances for each actor
        actor_counts = df3.groupby('actor')['count'].sum().reset_index()
        # Step 5: Select the top 10 actors based on the total count
        top_10_actors = actor_counts.nlargest(10, 'count')['actor']
        # Step 6: Filter the original DataFrame to include only the top 10 actors
        df3 = df3[df3['actor'].isin(top_10_actors)]
        
        # Pivot the DataFrame to create matrix of actors and genres
        df3 = df3.pivot(index="actor", columns="genre", values="count").fillna(0)
        
        #Heatmap
        fig3 = px.imshow(df3, x=df3.columns, y=df3.index)
        fig3.update_layout(width=500, height=500)
        return fig3

    @dash_app.callback(
        Output('chart4', 'figure'),
        [Input('genre-dropdown', 'value')]
    )
    def update_chart4(selected_genres):
        df4 = df.copy()
        if selected_genres:
            df4 = df4[df4['genre'].isin(selected_genres)]
        
                # Print the data to verify
        print("Chart 4 Data:")
        print(df4.head())
        
        ##CHART 4: Average Popularity and Sentiment of Movies by Genre
        sentiment_df = df4.groupby('genre').agg({'popularity': 'mean', 'overview_sentiment': 'mean'}).reset_index()
        fig4 = px.scatter(sentiment_df, x='popularity', y='overview_sentiment', color = 'genre', hover_data = ['genre'])

        return fig4

    @dash_app.callback(
        Output('chart5', 'figure'),
        [Input('director-dropdown', 'value')]
    )
    def update_chart5(selected_directors):
        df5 = df.copy()
        if selected_directors:
            df5 = df[df['director'].isin(selected_directors)]
            
        #CHART 5: Popularity Success of Genres by Top 10 Directors
        top_directors = df5.groupby('director').agg({'vote_count': 'sum'}).sort_values(by=['vote_count'], ascending=False).head(10).reset_index()
        df5 = df[df['director'].isin(top_directors['director'])]
        df5 = df5.groupby(['director', 'genre']).agg({'popularity': "mean"}).sort_values(by=['popularity'], ascending=False).reset_index()
        
        fig5 = px.bar(df5, x='director', y='popularity', color='genre', barmode='stack')
        return fig5
    
    return dash_app

# @views.route('/testing.html')
# def testing():
#     return render_template("testing.html", text="Hi, my name is", user="ALi", boolean=True)

@views.route('/intermediate.html', methods=['GET', 'POST'])
@cache.cached(timeout=300)
def intermediate():
    return render_template('intermediate.html')
    
@views.route('/advanced.html', methods=['GET', 'POST'])
def advanced():    
    ##CHART 1: Map visualization of movie production countries
    query = db.session.query(Movie.production_countries).all()
    
    data = [{'production_countries': row.production_countries} for row in query]
    
    df = pd.DataFrame(data)
    
    # Split the 'production_countries' column into individual countries and explode the DataFrame
    df['production_countries'] = df['production_countries'].str.split(', ')
    df = df.explode('production_countries')
    
    df1 = df.groupby('production_countries').size().reset_index(name='No_of_Movies')
    fig1 = px.choropleth(df1, 
                         locations='production_countries', 
                         locationmode='country names', 
                         color='No_of_Movies', 
                         hover_name='production_countries'
                         )
    fig1.update_layout(width=880)  # Set the width for Chart 1
    chart1 = pio.to_html(fig1, full_html=False)
    
    all_movies = []
    for page in range(1, 10):
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

    df2_long = df2.melt(id_vars=['title'], value_vars=['vote_average', 'popularity', 'vote_count', 'weighted_rating', 'trend_score'], var_name='metric', value_name='value')
    
    fig1 = go.Figure()
    
    # Add all movies to the legend without displaying them in the charts
    for title in df2_long['title'].unique():
        subset = df2_long[df2_long['title'] == title]
        fig1.add_trace(go.Scatterpolar(
            r=subset['value'],
            theta=subset['metric'],
            name=title,
            mode='lines',
            line=dict(dash='solid'),  # Valid properties
            visible='legendonly'  # Only show in legend
        ))

    title1 = request.args.get('title1')
    title2 = request.args.get('title2')
    chart_title = f"{title1} VS. {title2}" if title1 and title2 else "Select 2 movies to compare"

    if title1:
        print(f"Title1: {title1}")
        subset = df2_long[df2_long['title'] == title1]
        print(f"Subset for title1: {subset}")
        if not subset.empty:
            fig1.add_trace(go.Scatterpolar(
                r=subset['value'],
                theta=subset['metric'],
                name=title1,
                mode='lines',
                line=dict(color='blue', dash='solid')  # Valid properties
            ))
        else:
            print(f"No data found for title1: {title1}")

    if title2:
        print(f"Title2: {title2}")
        subset = df2_long[df2_long['title'] == title2]
        print(f"Subset for title2: {subset}")
        if not subset.empty:
            fig1.add_trace(go.Scatterpolar(
                r=subset['value'],
                theta=subset['metric'],
                name=title2,
                mode='lines',
                line=dict(color='red', dash='solid')  # Valid properties
            ))
        else:
            print(f"No data found for title2: {title2}")

    # Set the size of the charts and legends
    fig1.update_layout(
        showlegend=True,
        title=dict(
            text=chart_title,
            x=0.5,  # Center the title
            xanchor='center',
            yanchor='top'
        ),
        legend=dict(
            x=1,
            y=1,
            traceorder='normal',
            font=dict(
                size=10,  # Adjust the font size of the legend
            ),
        ),
        width=1170,  # Set the width of the chart
        height=450  # Set the height of the chart
    )

    chart2 = pio.to_html(fig1, full_html=False)
    
    return render_template("advanced.html", chart1=chart1, chart2=chart2, title1=title1, title2=title2)



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
    
    # Ensure directors, writers, and actors are loaded as names
    directors = [director.name for director in movie.directors]
    actors = [actor.name for actor in movie.actors]
    genres = [genre.name for genre in movie.genres]
    
    if request.method == 'POST':
        redirect(url_for('views.searched_movieDashboard', movie=movie))
    
    return render_template('movie_details.html', movie=movie, directors=directors, actors=actors, genres=genres)

def calculate_weighted_rating(vote_average, vote_count, C, m):
    return (vote_count / (vote_count + m) * vote_average) + (m / (vote_count + m) * C)

def calculate_combined_metric(weighted_rating, popularity, overview_sentiment):
    # Normalize the metrics (assuming max values for normalization)
    max_popularity = 2680.593
    max_overview_sentiment = 1.0

    normalized_popularity = popularity / max_popularity
    normalized_overview_sentiment = overview_sentiment / max_overview_sentiment

    # Calculate the combined metric (equal weights)
    combined_metric = (weighted_rating + normalized_popularity + normalized_overview_sentiment) / 3
    return combined_metric

@views.route('/searched_movieDashboard.html', methods=['GET'])
def searched_movieDashboard():
    movie_id = request.args.get('movie_id')
    movie = Movie.query.get_or_404(movie_id)
    
    # Prepare data for visualizations
    genres = movie.genres
    directors = movie.directors
    actors = movie.actors
    
    # CHART 1: Movie GENRE DISTRIBUTION
    genre_counts = pd.Series([genre.name for genre in genres]).value_counts()
    fig1 = px.pie(values=genre_counts, names=genre_counts.index, title='Genre Distribution')
    
    # Set the height and width for the pie chart
    fig1.update_layout(
        width=600,  # Set the width
        height=400  # Set the height
    )

    chart1 = pio.to_html(fig1, full_html=False)
    
    # CHART 2: Gauge performance based on vote_average, popularity, overview_sentiment and vote_count
    C = db.session.query(db.func.avg(Movie.vote_average)).scalar()
    m = 1000  # Minimum votes required to be listed in the chart
    
    weighted_rating = calculate_weighted_rating(movie.vote_average, movie.vote_count, C, m)
    combined_metric = calculate_combined_metric(weighted_rating, movie.popularity, movie.overview_sentiment)
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=combined_metric,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Combined Metric", 'font': {'size': 24}},
        delta={'reference': 0.5, 'increasing': {'color': "RebeccaPurple"}},
        gauge={
            'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.5], 'color': 'cyan'},
                {'range': [0.5, 1], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.75}
        }
    ))

    fig2.update_layout(paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"}, width=620, height=380)  # Set the width and height for the chart
    chart2 = pio.to_html(fig2, full_html=False)
    
    # CHART 3: OVERVIEW KEYWORDS WORDCLOUD
    keywords = movie.all_combined_keywords
    keywords = keywords.replace('[', '').replace(']', '').replace("'", '').split(', ')
    wordcloud_text = ' '.join(keywords)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_text)
    fig3 = px.imshow(wordcloud, title='')

    # Set the width and height for the word cloud chart
    fig3.update_layout(
        width=580,  # Set the width
        height=380  # Set the height
    )

    chart3 = pio.to_html(fig3, full_html=False)
    
    # CHART 4: NETWORK GRAPH for portrayal of relationship between Directors and Actors
    G = nx.Graph()
    
    # Add the current movie to the graph
    G.add_node(movie.title, type='movie')
    
    # Find similar movies based on shared genres
    similar_movies = Movie.query.join(Movie.genres).filter(Genre.name.in_([genre.name for genre in genres])).limit(10).all()    
    for similar_movie in similar_movies:
        if similar_movie.movie_id != movie.movie_id:  # Exclude the current movie
            G.add_node(similar_movie.title, type='movie')
            for genre in similar_movie.genres:
                if genre in genres:
                    G.add_edge(movie.title, similar_movie.title, genre=genre.name)
    
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        edge_text.append(edge[2]['genre'])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition='top center',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    fig4 = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                         title='',
                         titlefont_size=16,
                         showlegend=False,
                         hovermode='closest',
                         margin=dict(b=20, l=5, r=5, t=40),
                         annotations=[dict(
                             text="",
                             showarrow=False,
                             xref="paper", yref="paper"
                         )],
                         xaxis=dict(showgrid=False, zeroline=False),
                         yaxis=dict(showgrid=False, zeroline=False))
                     )
       
    # Set the width and height for the network graph
    fig4.update_layout(
        width=1250,  # Set the width
        height=400  # Set the height
    )

    chart4 = pio.to_html(fig4, full_html=False)
    return render_template('searched_movieDashboard.html', movie_name=movie.title, chart1=chart1, chart2=chart2, chart3=chart3, chart4=chart4)

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

@views.route('/remove_from_personalized', methods=['POST'])
@login_required
def remove_from_personalized():
    try:
        movie_id = request.args.get('movie_id')
        if not movie_id:
            return jsonify({'success': False, 'error': 'Movie ID is required'}), 400

        # Ensure the session is initialized
        if 'deleted_movies' not in session:
            session['deleted_movies'] = []

        deleted_movies = session['deleted_movies']
        if movie_id not in deleted_movies:
            deleted_movies.append(movie_id)
            session['deleted_movies'] = deleted_movies

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/settings.html')
def settings_page():
    return render_template("settings.html")