import { useState } from 'react';
import './SearchBar.css';

export default function SearchBar({ onFocus, onType, onSubmit, disabled }) {
  const [url, setUrl] = useState('');

  const handleChange = (e) => {
    const value = e.target.value;
    setUrl(value);
    if (value.length === 1) {
      onType?.();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;

    const withProtocol = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    try {
      const parsed = new URL(withProtocol);
      if (!['http:', 'https:'].includes(parsed.protocol)) return;
      onSubmit?.(parsed.href);
    } catch {
      // Invalid URL — ignore
    }
  };

  return (
    <form className="search-bar-form" onSubmit={handleSubmit}>
      <div className="search-input-wrapper">
        <input
          type="text"
          className="search-input"
          placeholder="Enter a URL to analyze..."
          value={url}
          onChange={handleChange}
          onFocus={onFocus}
          disabled={disabled}
          autoComplete="off"
          spellCheck="false"
        />
        <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </div>
      <button
        type="submit"
        className="analyze-btn"
        disabled={disabled || !url.trim()}
      >
        Analyze
      </button>
    </form>
  );
}
