import requests
from dotenv import load_dotenv
from os import environ

load_dotenv()

TOKEN = environ.get("API_TOKEN")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}
url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"
response = requests.get(url, headers=headers)
print(response.text)

# Create weighted rating (vote_count and vote_average), Trend score (release year...)