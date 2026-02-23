import './Results.css';

const SCORE_LABELS = {
  statistic_score: 'Statistics & Data',
  citation_score: 'Citations',
  structure_score: 'Content Structure',
  quotation_score: 'Quotations',
  schema_score: 'Schema Markup',
  freshness_score: 'Content Freshness',
  faq_score: 'FAQ Coverage',
  readability_score: 'Readability',
  tone_score: 'Authoritative Tone',
  robots_score: 'Robots / Meta',
  crawlability_score: 'Crawlability',
};

const REC_EXAMPLES = {
  statistic_score: {
    before: '"Our product significantly improved performance."',
    after: '"Our product improved performance by 73% across 1,200 test cases (Smith et al., 2024)."',
  },
  quotation_score: {
    before: 'Experts say this approach works well.',
    after: '"This approach reduces latency by half," said Dr. Jane Lee, Director of Engineering at Cloudflare.',
  },
  citation_score: {
    before: 'Studies show that citations help visibility.',
    after: 'According to Aggarwal et al. (KDD 2024), inline citations improve AI visibility by 30\u201340%.',
  },
  freshness_score: {
    before: 'No date visible on the page.',
    after: 'Last updated: January 15, 2025 \u00b7 dateModified set in JSON-LD schema.',
  },
  structure_score: {
    before: 'Large wall of text with no headings or lists.',
    after: 'Clear H1 \u2192 H2 \u2192 H3 hierarchy, bullet-point lists, and logical sections.',
  },
  schema_score: {
    before: 'No structured data on the page.',
    after: 'JSON-LD Article schema with headline, author, datePublished, and dateModified.',
  },
  tone_score: {
    before: '"This might possibly help improve your results."',
    after: '"This strategy improves visibility by 40% across all tested domains."',
  },
  faq_score: {
    before: 'Content written in paragraph form only.',
    after: 'Question-phrased headings ("What is GEO?") with 40\u201360 word answer blocks and FAQ schema.',
  },
  crawlability_score: {
    before: 'Client-side rendered SPA \u2014 blank page for AI crawlers.',
    after: 'Server-side rendered with Next.js/Astro \u2014 full HTML available on first request.',
  },
  robots_score: {
    before: 'User-agent: * \u00b7 Disallow: /',
    after: 'User-agent: GPTBot \u00b7 Allow: / \u00b7 User-agent: ClaudeBot \u00b7 Allow: /',
  },
  readability_score: {
    before: '"The implementation of the aforementioned methodology facilitates optimization."',
    after: '"This method makes your content easier for AI to find and cite."',
  },
};

function parseRec(message) {
  const sentences = message.split(/(?<=\.)\s+/);
  const title = sentences[0]?.replace(/\.$/, '') || '';
  const citationRegex = /\((?:[A-Z][a-z]+(?:\s+et\s+al\.)?.*?\d{4}.*?|.*?(?:KDD|NeurIPS|WSDM|IMC).*?)\)$/;
  const descSentences = sentences.slice(1).filter((s) => !citationRegex.test(s.trim()));
  const description = descSentences.join(' ');
  return { title, description };
}

function gradeColor(grade) {
  if (grade === 'A') return 'var(--grade-a)';
  if (grade === 'B') return 'var(--grade-b)';
  if (grade === 'C') return 'var(--grade-c)';
  if (grade === 'D') return 'var(--grade-d)';
  return 'var(--grade-f)';
}

function scoreColor(score) {
  if (score >= 70) return 'var(--grade-a)';
  if (score >= 50) return 'var(--grade-b)';
  if (score >= 30) return 'var(--grade-c)';
  return 'var(--grade-f)';
}

export default function Results({ data, onReset }) {
  const { url, total_score, grade, scores, recommendations } = data;

  return (
    <div className="results">
      {/* Header: score + grade */}
      <div className="results-header">
        <div className="results-score-ring" style={{ '--ring-color': gradeColor(grade) }}>
          <span className="results-score-value">{Math.round(total_score)}</span>
          <span className="results-score-label">/ 100</span>
        </div>
        <div className="results-grade-info">
          <span className="results-grade" style={{ color: gradeColor(grade) }}>{grade}</span>
          <span className="results-url">{url}</span>
        </div>
      </div>

      {/* Individual scores */}
      <div className="results-scores">
        <h3 className="results-section-title">Score Breakdown</h3>
        <div className="results-score-grid">
          {scores && Object.entries(scores)
            .filter(([key]) => SCORE_LABELS[key])
            .map(([key, value]) => (
            <div key={key} className="score-bar-item">
              <div className="score-bar-header">
                <span className="score-bar-label">{SCORE_LABELS[key] || key}</span>
                <span className="score-bar-value" style={{ color: scoreColor(value) }}>{Math.round(value)}</span>
              </div>
              <div className="score-bar-track">
                <div
                  className="score-bar-fill"
                  style={{
                    width: `${value}%`,
                    backgroundColor: scoreColor(value),
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {recommendations && recommendations.length > 0 && (
        <div className="results-recommendations">
          <h3 className="results-section-title">Recommendations</h3>
          <ul className="rec-list">
            {recommendations.map((rec, i) => {
              const { title, description } = parseRec(rec.message);
              const examples = REC_EXAMPLES[rec.category];
              return (
                <li key={`${rec.category}-${i}`} className={`rec-card rec-${rec.impact}`}>
                  <div className="rec-card-header">
                    <span className="rec-priority">{rec.impact}</span>
                    <h4 className="rec-title">{title}</h4>
                  </div>
                  {description && <p className="rec-description">{description}</p>}
                  {examples && (
                    <div className="rec-examples">
                      <div className="rec-example rec-example-before">
                        <span className="rec-example-label">Before</span>
                        <span className="rec-example-text">{examples.before}</span>
                      </div>
                      <div className="rec-example rec-example-after">
                        <span className="rec-example-label">After</span>
                        <span className="rec-example-text">{examples.after}</span>
                      </div>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      <button className="results-reset-btn" onClick={onReset}>
        Analyze Another URL
      </button>
    </div>
  );
}
