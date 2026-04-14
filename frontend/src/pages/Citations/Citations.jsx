import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Citations.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Citations() {
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/citations`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load citations (${res.status})`);
        return res.json();
      })
      .then((data) => {
        setCitations(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="citations-page">
      <nav className="citations-nav">
        <Link to="/" className="citations-back">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          Back to GEO Genie
        </Link>
      </nav>

      <header className="citations-header">
        <h1 className="citations-title">Citations & References</h1>
        <p className="citations-subtitle">
          The academic publications and resources that inform GEO Genie's scoring methodology.
        </p>
      </header>

      {loading && <p className="citations-loading">Loading citations...</p>}
      {error && <p className="citations-error">{error}</p>}

      {!loading && !error && (
        <ol className="citations-list">
          {citations.map((cite, i) => (
            <li key={cite.doi || i} className="citation-card">
              <span className="citation-year">{cite.year}</span>
              <div className="citation-body">
                <p className="citation-authors">{cite.authors}</p>
                <h2 className="citation-title">{cite.title}</h2>
                <p className="citation-venue">{cite.venue}</p>
                {cite.note && <p className="citation-note">{cite.note}</p>}
                <a
                  href={cite.doi}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="citation-link"
                >
                  {cite.doi}
                </a>
              </div>
            </li>
          ))}
        </ol>
      )}

      <footer className="footer">
        A Masters AI Project — Generative Engine Optimization
        <span className="footer-sep">·</span>
        <Link to="/" className="footer-link">Home</Link>
      </footer>
    </div>
  );
}
