import pandas as pd
import requests
from dotenv import load_dotenv
from os import environ
from datetime import datetime

load_dotenv()

TOKEN = environ.get("API_TOKEN")
API_KEY = environ.get("API_KEY")

if not TOKEN:
    raise ValueError("API_TOKEN is not set. Please set it in your .env file.")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def fetch_api_data(page=1):
    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&sort_by=popularity.desc&api_key={API_KEY}"
    response = requests.get(url, headers=headers)
    print(f"Fetching data for page {page}: Status Code {response.status_code}")  # Debugging: Print status code
    if response.status_code == 200:
        return response.json()  # Should return a dictionary with 'results'
    else:
        print(f"Failed to fetch data: {response.content}")  # Debugging: Print response content
        return None

def process_movie_data(movie):
    movie_data = {
        'title': movie.get('title'),
        'overview': movie.get('overview'),
        'release_date': movie.get('release_date'),
        'adult': movie.get('adult'),
        'vote_average': movie.get('vote_average'),
        'vote_count': movie.get('vote_count'),
        'popularity': movie.get('popularity'),
        'runtime': movie.get('runtime')  # Ensure runtime is included
    }
    return movie_data

def feature_extraction(df):
    #Weighted rating (vote_count and vote_average)- ensure movies with high number of votes are given more wieght than those with fewer votes
    C = df['vote_average'].mean() #Average rating across all movies
    m = df['vote_count'].quantile(0.9) #Minimum votes required to be listed in the chart (threshold)
    df['weighted_rating'] =  (df['vote_count'] / (df['vote_count'] + m) * df['vote_average']) + (m / (df['vote_count'] + m) * C)
    
    #Trend score (release year...)
    current_year = datetime.now().year
    df['release_year'] = pd.to_datetime(df['release_date']).dt.year
    df['trend_score'] = df['popularity'] / (current_year - df['release_year'] + 1)
    return df