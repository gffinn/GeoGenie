import { Link } from 'react-router-dom';
import './HowItWorks.css';

const STEPS = [
  {
    number: '01',
    title: 'Submit a URL',
    description:
      'Paste any publicly accessible web page URL into the analyzer. GEOGenie fetches the live page using a headless browser, so JavaScript-rendered content is captured accurately.',
  },
  {
    number: '02',
    title: 'Content Analysis',
    description:
      'Our engine runs eleven independent analyzers in parallel — evaluating statistical richness, expert quotations, citation density, structural markup, freshness signals, and more.',
  },
  {
    number: '03',
    title: 'Weighted Scoring',
    description:
      'Each signal is weighted according to its empirical impact on AI citation likelihood, drawn from peer-reviewed GEO research. The result is a single score from 0–100 with a letter grade.',
  },
  {
    number: '04',
    title: 'Actionable Recommendations',
    description:
      'GEOGenie surfaces prioritized improvements ranked by impact — high, medium, or low — with concrete before/after examples so you know exactly what to change.',
  },
];

const SIGNALS = [
  { label: 'Statistics & Data', weight: '17%', desc: 'Numbers, percentages, and quantitative evidence' },
  { label: 'Expert Quotations', weight: '15%', desc: 'Cited statements from named authorities' },
  { label: 'Citations & Sources', weight: '14%', desc: 'Author and publication references' },
  { label: 'Content Freshness', weight: '12%', desc: 'Publication and update date signals' },
  { label: 'Content Structure', weight: '10%', desc: 'Heading hierarchy and semantic HTML' },
  { label: 'Crawlability', weight: '7%', desc: 'Server-side rendering and bot accessibility' },
  { label: 'Schema Markup', weight: '8%', desc: 'JSON-LD structured data' },
  { label: 'Authoritative Tone', weight: '5%', desc: 'Confident, expert language patterns' },
  { label: 'FAQ Formatting', weight: '5%', desc: 'Question-and-answer structure' },
  { label: 'Robots & Meta', weight: '5%', desc: 'robots.txt and indexability signals' },
  { label: 'Readability', weight: '2%', desc: 'Flesch-Kincaid grade level analysis' },
];

export default function HowItWorks() {
  return (
    <div className="hiw-page">
      <div className="hiw-container">
        <header className="hiw-header">
          <h1 className="hiw-title">How It Works</h1>
          <p className="hiw-subtitle">
            GEOGenie scores your content against the signals that AI language models
            actually use when deciding which sources to cite in their answers.
          </p>
        </header>

        <section className="hiw-steps">
          {STEPS.map((step) => (
            <div key={step.number} className="hiw-step">
              <div className="step-number">{step.number}</div>
              <div className="step-body">
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.description}</p>
              </div>
            </div>
          ))}
        </section>

        <section className="hiw-signals">
          <h2 className="signals-heading">The 11 Scoring Signals</h2>
          <p className="signals-intro">
            Each signal is weighted based on its empirically measured contribution
            to AI citation rates.
          </p>
          <div className="signals-grid">
            {SIGNALS.map((s) => (
              <div key={s.label} className="signal-card">
                <div className="signal-top">
                  <span className="signal-label">{s.label}</span>
                  <span className="signal-weight">{s.weight}</span>
                </div>
                <p className="signal-desc">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <div className="hiw-cta">
          <Link to="/" className="cta-button">Analyze Your Page</Link>
          <Link to="/about" className="cta-link">Learn about the research →</Link>
        </div>
      </div>
    </div>
  );
}
