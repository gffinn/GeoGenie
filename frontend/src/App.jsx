import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Genie from './components/Genie/Genie';
import SearchBar from './components/SearchBar/SearchBar';
import SpeechBubble from './components/SpeechBubble/SpeechBubble';
import Results from './components/Results/Results';
import Citations from './pages/Citations/Citations';
import { DIALOGUES } from './components/Genie/expressions';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const PHASES = {
  IDLE: 'idle',
  POINTING: 'pointing',
  EXCITED: 'excited',
  THINKING: 'thinking',
  CONCERNED: 'concerned',
};

function App() {
  const [phase, setPhase] = useState(PHASES.IDLE);
  const [loaded, setLoaded] = useState(false);
  const [hasTyped, setHasTyped] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleFocus = useCallback(() => {
    if (phase === PHASES.IDLE && !results) {
      setPhase(PHASES.POINTING);
    }
  }, [phase, results]);

  const handleType = useCallback(() => {
    if (!hasTyped) {
      setHasTyped(true);
      setPhase(PHASES.EXCITED);
    }
  }, [hasTyped]);

  const handleSubmit = useCallback(async (url) => {
    setPhase(PHASES.THINKING);
    setResults(null);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Analysis failed (${response.status})`);
      }

      const data = await response.json();
      setResults(data);

      // Genie reacts to the score
      if (data.total_score >= 70) {
        setPhase(PHASES.EXCITED);
      } else if (data.total_score >= 40) {
        setPhase(PHASES.IDLE);
      } else {
        setPhase(PHASES.CONCERNED);
      }
    } catch (err) {
      setError(err.message);
      setPhase(PHASES.CONCERNED);
    }
  }, []);

  const handleReset = useCallback(() => {
    setResults(null);
    setError(null);
    setHasTyped(false);
    setPhase(PHASES.IDLE);
  }, []);

  // Build genie dialogue — override with context-aware messages when we have results
  let dialogue = DIALOGUES[phase];
  if (results) {
    if (results.total_score >= 70) {
      dialogue = `Nice! Your page scored ${results.total_score}/100 — grade ${results.grade}. Looking strong for AI visibility!`;
    } else if (results.total_score >= 40) {
      dialogue = `Your page scored ${results.total_score}/100 — grade ${results.grade}. There's room to improve. Let me show you what I found.`;
    } else {
      dialogue = `Your page scored ${results.total_score}/100 — grade ${results.grade}. We've got some work to do. Check the recommendations below.`;
    }
  } else if (error) {
    const isBlocked = /403|blocked|forbidden/i.test(error);
    dialogue = isBlocked
      ? `Hmm, that site is blocking our analysis. Some websites are aggressive about bot detection.`
      : `Oops! Something went wrong. Please check the URL and try again.`;
  }

  const homePage = (
    <div className={`app ${loaded ? 'loaded' : ''} ${results ? 'has-results' : ''}`}>
      <div className="logo">
        <h1 className="logo-text">
          <span className="logo-geo">GEO</span>
          <span className="logo-genie">Genie</span>
        </h1>
        <p className="logo-tagline">The Visibility Toggle</p>
      </div>

      <div className="genie-spirit">
        <Genie expression={phase} />
        <SpeechBubble text={dialogue} />
      </div>

      <div className="search-section">
        <SearchBar
          onFocus={handleFocus}
          onType={handleType}
          onSubmit={handleSubmit}
          disabled={phase === PHASES.THINKING}
        />
      </div>

      {error && (
        <div className="error-section">
          <div className="error-card">
            <svg className="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div className="error-content">
              <h3 className="error-title">
                {/403|blocked|forbidden/i.test(error) ? 'Site Blocked Our Analysis' : 'Analysis Failed'}
              </h3>
              <p className="error-message">
                {/403|blocked|forbidden/i.test(error)
                  ? 'The website is blocking automated access. This is common with sites that have aggressive bot detection. Try a different URL or check that the page is publicly accessible.'
                  : 'Something went wrong while analyzing this URL. Please verify the URL is correct and publicly accessible, then try again.'}
              </p>
            </div>
            <button className="error-dismiss" onClick={handleReset} aria-label="Dismiss">
              &times;
            </button>
          </div>
        </div>
      )}

      {results && (
        <div className="results-section">
          <Results data={results} onReset={handleReset} />
        </div>
      )}

      <footer className="footer">
        A Masters AI Project — Generative Engine Optimization
        <span className="footer-sep">·</span>
        <Link to="/citations" className="footer-link">Citations</Link>
      </footer>
    </div>
  );

  return (
    <Routes>
      <Route path="/" element={homePage} />
      <Route path="/citations" element={<Citations />} />
    </Routes>
  );
}

export default App;
