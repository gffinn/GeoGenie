import './CrawlProgress.css';

export default function CrawlProgress({ data }) {
  const { pages_found, pages_analyzed, pages = [] } = data;
  const pct = pages_found > 0 ? Math.round((pages_analyzed / pages_found) * 100) : 0;

  return (
    <div className="crawl-progress">
      <div className="crawl-progress-header">
        <h3 className="crawl-progress-title">Crawling Site</h3>
        <span className="crawl-progress-count">
          {pages_analyzed} / {pages_found} pages analyzed
        </span>
      </div>

      <div className="crawl-bar-track">
        <div
          className="crawl-bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>

      <ul className="crawl-page-list">
        {pages.map((page, i) => (
          <li key={page.url || i} className="crawl-page-item">
            <span className={`crawl-status-dot crawl-status-${page.status}`} />
            <span className="crawl-page-url">{page.url}</span>
            {page.status === 'completed' && page.total_score != null && (
              <span className="crawl-page-score">{Math.round(page.total_score)}</span>
            )}
            {page.status === 'failed' && (
              <span className="crawl-page-failed">failed</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
