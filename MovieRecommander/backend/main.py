import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recommendations/{movie_name}")
def get_recommendations(movie_name: str):
    search_url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}
    search_response = requests.get(search_url, params=params).json()

    if not search_response['results']:
        raise HTTPException(status_code=404, detail="Film introuvable.")

    movie_id = search_response['results'][0]['id']

    recommendations_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
    rec_params = {"api_key": TMDB_API_KEY}
    recommendations_response = requests.get(recommendations_url, params=rec_params).json()

    recommendations = recommendations_response.get('results', [])[:3]

    return [
        {
            "title": movie["title"],
            "overview": movie["overview"],
            "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None
        }
        for movie in recommendations
    ]
