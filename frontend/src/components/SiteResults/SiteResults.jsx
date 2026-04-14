import './SiteResults.css';

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
  statistic_score:    'Statistics & Data',
  quotation_score:    'Quotations',
  citation_score:     'Citations',
  freshness_score:    'Content Freshness',
  https_score:        'HTTPS',
  meta_tags_score:    'Title & Meta Tags',
  mobile_score:       'Mobile Responsive',
  structure_score:    'Content Structure',
  schema_score:       'Schema Markup',
  faq_score:          'FAQ Coverage',
  tone_score:         'Authoritative Tone',
  readability_score:  'Readability',
  crawlability_score: 'Crawlability',
  robots_score:       'AI Crawlers',
  llms_txt_score:     'llms.txt',
};

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

function averageScores(pages) {
  const completed = pages.filter((p) => p.status === 'completed' && p.scores);
  if (completed.length === 0) return {};

  const totals = {};
  for (const page of completed) {
    for (const [key, value] of Object.entries(page.scores)) {
      totals[key] = (totals[key] || 0) + (value ?? 0);
    }
  }

  const avg = {};
  for (const [key, sum] of Object.entries(totals)) {
    avg[key] = sum / completed.length;
  }
  return avg;
}

export default function SiteResults({ data, onReset }) {
  const { url, total_score, grade, pages = [] } = data;

  const completed = pages.filter((p) => p.status === 'completed');
  const failed = pages.filter((p) => p.status === 'failed');
  const avgScores = averageScores(pages);

  return (
    <div className="site-results">
      {/* Header: score + grade */}
      <div className="site-results-header">
        <div className="site-score-ring" style={{ '--ring-color': gradeColor(grade) }}>
          <span className="site-score-value">{Math.round(total_score)}</span>
          <span className="site-score-label">/ 100</span>
        </div>
        <div className="site-grade-info">
          <span className="site-grade" style={{ color: gradeColor(grade) }}>{grade}</span>
          <span className="site-url">{url}</span>
          <span className="site-summary">
            {completed.length} page{completed.length !== 1 ? 's' : ''} analyzed
            {failed.length > 0 && `, ${failed.length} failed`}
          </span>
        </div>
      </div>

      {/* Score breakdown — averaged across all pages */}
      <div className="site-scores">
        <h3 className="site-section-title">Score Breakdown</h3>
        {SCORE_GROUPS.map((group) => (
          <div key={group.category} className="site-score-group">
            <span className="site-score-group-label">{group.category}</span>
            <div className="site-score-grid">
              {group.keys.map((key) => {
                const value = avgScores[key] ?? 0;
                return (
                  <div key={key} className="site-score-bar-item">
                    <div className="site-score-bar-header">
                      <span className="site-score-bar-label">{SCORE_LABELS[key]}</span>
                      <span
                        className="site-score-bar-value"
                        style={{ color: scoreColor(value) }}
                      >
                        {Math.round(value)}
                      </span>
                    </div>
                    <div className="site-score-bar-track">
                      <div
                        className="site-score-bar-fill"
                        style={{
                          width: `${value}%`,
                          backgroundColor: scoreColor(value),
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <button className="results-reset-btn" onClick={onReset}>
        Analyze Another Site
      </button>
    </div>
  );
}
