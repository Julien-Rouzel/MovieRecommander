import { useState } from 'react';
import axios from 'axios';
import './index.css';

function App() {
  const [movie, setMovie] = useState('');
  const [results, setResults] = useState([]);

  const searchMovies = async () => {
    try {
      const response = await axios.get(`https://movierecommander-3xfc.onrender.com/recommendations/${movie}`);
      setResults(response.data);
    } catch (error) {
      alert('Film introuvable ou erreur serveur.');
    }
  };

  const reset = () => {
    setMovie('');
    setResults([]);
  };

  return (
    <div className="app">
      <h1 className="title" onClick={reset}>🍿 MovieFinder AI</h1>
      <input
        type="text"
        className="search-bar"
        placeholder="Nom d'un film que tu as aimé..."
        value={movie}
        onChange={(e) => setMovie(e.target.value)}
      />
      <button onClick={searchMovies}>Chercher des films similaires</button>

      <div className="movies">
        {results.map((film) => (
          <div className="movie" key={film.title}>
            <h2>{film.title}</h2>
            {film.poster && (
              <a href={`https://www.themoviedb.org/search?query=${encodeURIComponent(film.title)}`} target="_blank" rel="noopener noreferrer">
                <img src={film.poster} alt={film.title} />
              </a>
            )}
            <p>{film.overview}</p>
            <p className="reason-box">🎯 {film.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
