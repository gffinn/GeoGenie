import { Link } from 'react-router-dom';
import './HowItWorks.css';

const STEPS = [
  {
    number: '01',
    title: 'Submit a URL',
    description:
      'Paste any publicly accessible web page URL into the analyzer. GEO Genie fetches the live page using a headless browser, so JavaScript-rendered content is captured accurately.',
  },
  {
    number: '02',
    title: 'Content Analysis',
    description:
      'Our engine runs fifteen independent analyzers in parallel — evaluating GEO content signals, technical infrastructure, content structure, and AI access controls.',
  },
  {
    number: '03',
    title: 'Weighted Scoring',
    description:
      'Each signal is weighted according to its empirical impact on AI citation likelihood, drawn from peer-reviewed GEO research and the technical infrastructure rubric. The result is a single score from 0–100 with a letter grade.',
  },
  {
    number: '04',
    title: 'Critical Failure Checks',
    description:
      'Before assigning a grade, GEO Genie checks for critical failures: a page that won\'t load or blocks all AI crawlers is an automatic F. A page served over HTTP is capped at D regardless of its content score.',
  },
  {
    number: '05',
    title: 'Actionable Recommendations',
    description:
      'GEO Genie surfaces prioritized improvements ranked by impact — high, medium, or low — so you know exactly what to fix first.',
  },
];

const SIGNAL_GROUPS = [
  {
    category: 'GEO Content Signals',
    note: 'Research-backed — Aggarwal et al., KDD 2024',
    signals: [
      { label: 'Statistics & Data',  weight: '13%', desc: 'Numbers, percentages, and quantitative evidence in content' },
      { label: 'Expert Quotations',  weight: '11%', desc: 'Cited statements attributed to named authorities' },
      { label: 'Citations & Sources', weight: '10%', desc: 'Inline references to authors and publications' },
      { label: 'Content Freshness',  weight: '9%',  desc: 'Publication and last-updated date signals (3.2× citation multiplier within 30 days)' },
    ],
  },
  {
    category: 'Technical Infrastructure',
    note: 'Infrastructure rubric v2',
    signals: [
      { label: 'HTTPS',             weight: '9%',  desc: 'Page served over a secure connection — critical failure if absent (caps grade at D)' },
      { label: 'Title & Meta Tags', weight: '7%',  desc: '<title> tag and <meta name="description"> presence' },
      { label: 'Mobile Responsive', weight: '5%',  desc: 'Viewport meta tag with width=device-width' },
    ],
  },
  {
    category: 'Content & Structure',
    note: 'SE Ranking 400K URL study, 2025',
    signals: [
      { label: 'Content Structure', weight: '8%',  desc: 'Heading hierarchy (H1→H2→H3) and semantic HTML elements (<main>, <article>, <nav>, etc.)' },
      { label: 'Schema Markup',     weight: '6%',  desc: 'JSON-LD structured data (Article, FAQ, HowTo)' },
      { label: 'FAQ Formatting',    weight: '4%',  desc: 'Question-phrased headings with extractable answer blocks' },
      { label: 'Authoritative Tone', weight: '4%', desc: 'Confident, expert language — minimal hedging' },
      { label: 'Readability',       weight: '2%',  desc: 'Flesch-Kincaid grade level analysis' },
    ],
  },
  {
    category: 'AI Access',
    note: 'Liu et al., IMC 2025 · llmstxt.org',
    signals: [
      { label: 'Crawlability',  weight: '5%', desc: 'Server-side rendered content accessible without JavaScript — critical failure if page is blank' },
      { label: 'AI Crawlers',   weight: '4%', desc: 'robots.txt allows key AI search and retrieval crawlers (GPTBot, ClaudeBot, PerplexityBot, etc.) — critical failure if all are blocked' },
      { label: 'llms.txt',      weight: '3%', desc: 'Presence of /llms.txt — the emerging standard for declaring content usage preferences to LLM assistants' },
    ],
  },
];

const GRADE_SCALE = [
  { grade: 'A', range: '90–100', label: 'Excellent AI visibility', color: 'var(--grade-a)' },
  { grade: 'B', range: '80–89',  label: 'Good — minor improvements needed', color: 'var(--grade-b)' },
  { grade: 'C', range: '70–79',  label: 'Moderate — improvements recommended', color: 'var(--grade-c)' },
  { grade: 'D', range: '60–69',  label: 'Poor — significant issues present', color: 'var(--grade-d)' },
  { grade: 'F', range: 'Below 60', label: 'Critical issues blocking AI discoverability', color: 'var(--grade-f)' },
];

export default function HowItWorks() {
  const totalSignals = SIGNAL_GROUPS.reduce((sum, g) => sum + g.signals.length, 0);

  return (
    <div className="hiw-page">
      <div className="hiw-container">
        <header className="hiw-header">
          <h1 className="hiw-title">How It Works</h1>
          <p className="hiw-subtitle">
            GEO Genie scores your content against the signals that AI language models
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
          <h2 className="signals-heading">The {totalSignals} Scoring Signals</h2>
          <p className="signals-intro">
            Signals are grouped by category. Each weight reflects its empirically measured
            contribution to AI citation rates or technical discoverability.
          </p>
          <div className="signals-groups">
            {SIGNAL_GROUPS.map((group) => (
              <div key={group.category} className="signal-group">
                <div className="signal-group-header">
                  <span className="signal-group-name">{group.category}</span>
                  <span className="signal-group-note">{group.note}</span>
                </div>
                <div className="signals-grid">
                  {group.signals.map((s) => (
                    <div key={s.label} className="signal-card">
                      <div className="signal-top">
                        <span className="signal-label">{s.label}</span>
                        <span className="signal-weight">{s.weight}</span>
                      </div>
                      <p className="signal-desc">{s.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="hiw-grades">
          <h2 className="signals-heading">Grading Scale</h2>
          <div className="grade-scale">
            {GRADE_SCALE.map(({ grade, range, label, color }) => (
              <div key={grade} className="grade-row">
                <span className="grade-letter" style={{ color }}>{grade}</span>
                <span className="grade-range">{range}</span>
                <span className="grade-label">{label}</span>
              </div>
            ))}
          </div>
          <p className="grade-note">
            Critical failures override the numeric grade: a page that fails to load or
            blocks all AI crawlers receives an automatic F. A page without HTTPS is capped
            at D regardless of its content score.
          </p>
        </section>

        <div className="hiw-cta">
          <Link to="/" className="cta-button">Analyze Your Page</Link>
          <Link to="/about" className="cta-link">Learn about the research →</Link>
        </div>
      </div>
    </div>
  );
}
