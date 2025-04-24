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

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def get_movie_data(movie_id, data_type):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/{data_type}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else {}


@app.get("/recommendations/{movie_name}")
def get_recommendations(movie_name: str):
    # Search the original movie
    search_url = f"{TMDB_BASE_URL}/search/movie"
    search_params = {"api_key": TMDB_API_KEY, "query": movie_name}
    search_response = requests.get(search_url, params=search_params).json()

    if not search_response['results']:
        raise HTTPException(status_code=404, detail="Film introuvable.")

    original_movie = search_response['results'][0]
    movie_id = original_movie['id']

    # Get original movie details
    original_details = get_movie_data(movie_id, "")
    original_genres = {g['name'] for g in original_details.get('genres', [])}
    original_credits = get_movie_data(movie_id, "credits")
    original_cast = {a['name'] for a in original_credits.get('cast', [])[:5]}
    original_crew = {d['name'] for d in original_credits.get('crew', []) if d['job'] == 'Director'}

    # Get recommendations
    recommendations_url = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations"
    rec_params = {"api_key": TMDB_API_KEY}
    recommendations_response = requests.get(recommendations_url, params=rec_params).json()
    recommendations = recommendations_response.get('results', [])[:3]

    enriched = []
    for rec in recommendations:
        rec_id = rec['id']
        details = get_movie_data(rec_id, "")
        credits = get_movie_data(rec_id, "credits")

        rec_genres = {g['name'] for g in details.get('genres', [])}
        rec_cast = {a['name'] for a in credits.get('cast', [])[:5]}
        rec_directors = {d['name'] for d in credits.get('crew', []) if d['job'] == 'Director'}

        shared_genres = original_genres & rec_genres
        shared_cast = original_cast & rec_cast
        shared_director = original_crew & rec_directors

        reasons = []
        if shared_genres:
            reasons.append(f"genre(s) commun(s) : {', '.join(shared_genres)}")
        if shared_director:
            reasons.append(f"réalisé par {', '.join(shared_director)}")
        if shared_cast:
            reasons.append(f"acteur(s) en commun : {', '.join(shared_cast)}")

        enriched.append({
            "title": rec["title"],
            "overview": rec["overview"],
            "poster": f"https://image.tmdb.org/t/p/w500{rec['poster_path']}" if rec.get('poster_path') else None,
            "reason": "Recommandé car " + ", et ".join(reasons) if reasons else "Recommandation basée sur la similarité globale."
        })

    return enriched

