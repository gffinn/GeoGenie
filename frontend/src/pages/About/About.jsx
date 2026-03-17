import { Link } from 'react-router-dom';
import './About.css';

export default function About() {
  return (
    <div className="about-page">
      <div className="about-container">
        <header className="about-header">
          <h1 className="about-title">
            About <span className="about-geo">GEO</span><span className="about-genie">Genie</span>
          </h1>
          <p className="about-subtitle">
            A Masters AI research project built to help content creators understand
            and improve their visibility in AI-powered search engines.
          </p>
        </header>

        <section className="about-section">
          <h2>What is GEO?</h2>
          <p>
            Generative Engine Optimization (GEO) is the emerging practice of optimizing web content
            so it is cited, quoted, and recommended by AI language models — systems like ChatGPT,
            Perplexity, and Google's AI Overviews. As search behavior shifts from blue links to
            generated answers, traditional SEO is no longer enough.
          </p>
          <p>
            GEOGenie analyzes your content against the signals that large language models actually
            use when deciding which sources to surface in their responses: statistical evidence,
            expert citations, authoritative tone, structured data, and more.
          </p>
        </section>

        <section className="about-section">
          <h2>The Research</h2>
          <p>
            GEOGenie was built on peer-reviewed research published in venues including ACM, arXiv,
            and leading AI conferences. Our scoring methodology is grounded in empirical findings
            about what makes content more likely to be cited by generative AI systems.
          </p>
          <p>
            The tool evaluates eleven distinct signals — from statistical richness and quotation
            density to crawlability and schema markup — each weighted according to their relative
            impact found in the literature.
          </p>
        </section>

        <section className="about-section">
          <h2>Who Built This?</h2>
          <p>
            GEOGenie is a capstone project developed as part of a Masters in Artificial Intelligence
            program. It was designed to bridge the gap between cutting-edge NLP research and
            practical tools that everyday content creators and marketers can use.
          </p>
        </section>

        <div className="about-cta">
          <Link to="/" className="cta-button">Try the Analyzer</Link>
          <Link to="/how-it-works" className="cta-link">See how it works →</Link>
        </div>
      </div>
    </div>
  );
}
