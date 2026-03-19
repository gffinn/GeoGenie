import './Results.css';

// Grouped score display — order and category labels preserved from config.py
const SCORE_GROUPS = [
  {
    category: 'GEO Content Signals',
    keys: ['statistic_score', 'quotation_score', 'citation_score', 'freshness_score'],
  },
  {
    category: 'Technical Infrastructure',
    keys: ['https_score', 'meta_tags_score', 'mobile_score'],
  },
  {
    category: 'Content & Structure',
    keys: ['structure_score', 'schema_score', 'faq_score', 'tone_score', 'readability_score'],
  },
  {
    category: 'AI Access',
    keys: ['crawlability_score', 'robots_score', 'llms_txt_score'],
  },
];

const SCORE_LABELS = {
  statistic_score:   'Statistics & Data',
  quotation_score:   'Quotations',
  citation_score:    'Citations',
  freshness_score:   'Content Freshness',
  https_score:       'HTTPS',
  meta_tags_score:   'Title & Meta Tags',
  mobile_score:      'Mobile Responsive',
  structure_score:   'Content Structure',
  schema_score:      'Schema Markup',
  faq_score:         'FAQ Coverage',
  tone_score:        'Authoritative Tone',
  readability_score: 'Readability',
  crawlability_score: 'Crawlability',
  robots_score:      'AI Crawlers',
  llms_txt_score:    'llms.txt',
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
  https: {
    before: 'http://example.com — served over plain HTTP.',
    after: 'https://example.com — TLS certificate via Let\'s Encrypt, all HTTP redirected to HTTPS.',
  },
  meta_tags: {
    before: 'No <title> or <meta name="description"> on the page.',
    after: '<title>GEO Guide 2025</title> · <meta name="description" content="Learn how to optimize your content for AI visibility in 2025.">',
  },
  mobile: {
    before: 'No viewport meta tag — page renders at desktop width on mobile.',
    after: '<meta name="viewport" content="width=device-width, initial-scale=1"> added to <head>.',
  },
  llms_txt: {
    before: 'No /llms.txt file at the domain root.',
    after: 'https://example.com/llms.txt created with site description, key pages, and usage preferences.',
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

      {/* Individual scores grouped by category */}
      <div className="results-scores">
        <h3 className="results-section-title">Score Breakdown</h3>
        {scores && SCORE_GROUPS.map((group) => (
          <div key={group.category} className="score-group">
            <span className="score-group-label">{group.category}</span>
            <div className="results-score-grid">
              {group.keys.map((key) => {
                const value = scores[key] ?? 0;
                return (
                  <div key={key} className="score-bar-item">
                    <div className="score-bar-header">
                      <span className="score-bar-label">{SCORE_LABELS[key]}</span>
                      <span className="score-bar-value" style={{ color: scoreColor(value) }}>{Math.round(value)}</span>
                    </div>
                    <div className="score-bar-track">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${value}%`, backgroundColor: scoreColor(value) }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
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
