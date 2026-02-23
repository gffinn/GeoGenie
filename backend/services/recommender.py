from ..config import settings
from ..schemas import Recommendation

# Recommendation templates with academic citations matching
# the GEO Strategies document sources.
RECOMMENDATION_TEMPLATES: dict[str, dict] = {
    "statistic_score": {
        "category": "statistics",
        "message": (
            "Add statistics and quantitative data. Replace qualitative claims "
            "like 'significantly improved' with specific numbers like "
            "'increased by 73%'. This strategy shows +40-41% visibility "
            "improvement and is especially effective for law, government, "
            "and factual queries. "
            "(Aggarwal et al., KDD 2024, Table 3)"
        ),
        "impact": "high",
    },
    "quotation_score": {
        "category": "quotations",
        "message": (
            "Include direct quotes from experts or authorities. Use attributed "
            "quotes like '\"...\" said [Expert Name], [Title]'. Quotations "
            "create distinct embeddings that AI systems prefer to cite, showing "
            "+38-40% visibility improvement. Most effective for opinion and "
            "historical content. "
            "(Aggarwal et al., KDD 2024, Table 3)"
        ),
        "impact": "high",
    },
    "citation_score": {
        "category": "citations",
        "message": (
            "Add inline citations to credible sources. Use patterns like "
            "'According to [Source]...' and link to .edu, .gov, or recognized "
            "research institutions. Citations show +30-40% visibility improvement "
            "across all domains, with the strongest effect on factual queries. "
            "(Aggarwal et al., KDD 2024, Table 3)"
        ),
        "impact": "high",
    },
    "freshness_score": {
        "category": "freshness",
        "message": (
            "Update your content with a recent modification date. Content "
            "updated within 30 days receives 3.2x more AI citations. Add a "
            "visible 'Last updated' date and ensure dateModified is set in "
            "your JSON-LD schema markup. "
            "(Search Engine Land, 2025)"
        ),
        "impact": "high",
    },
    "structure_score": {
        "category": "structure",
        "message": (
            "Improve heading structure. Use a clear H1 -> H2 -> H3 hierarchy "
            "with no skipped levels, bullet points for lists, and logical "
            "sections. Semantic HTML produces clean chunks for AI indexing. "
            "Structured formatting shows +28-40% visibility improvement. "
            "(SE Ranking 400K URL study, 2025)"
        ),
        "impact": "medium",
    },
    "schema_score": {
        "category": "schema",
        "message": (
            "Add structured data markup (JSON-LD). Implement Article, FAQ, "
            "or HowTo schema with complete properties (headline, author, "
            "datePublished, dateModified). Schema markup shows +28% visibility "
            "improvement by helping AI crawlers understand your content structure. "
            "(Industry consensus; Aggarwal et al., KDD 2024)"
        ),
        "impact": "medium",
    },
    "tone_score": {
        "category": "tone",
        "message": (
            "Strengthen your authoritative tone. Reduce hedging language "
            "(might, could, possibly, perhaps) and use more confident, "
            "persuasive language. Authoritative tone is especially effective "
            "for historical and opinion content. Avoid qualifiers that weaken "
            "your claims. "
            "(Aggarwal et al., KDD 2024, Table 3 — domain-specific results)"
        ),
        "impact": "medium",
    },
    "faq_score": {
        "category": "faq",
        "message": (
            "Add FAQ-formatted content. Use question-phrased headings "
            "(e.g., 'What is...?', 'How do you...?') and create 40-60 word "
            "answer blocks that can be directly extracted by LLMs. Implement "
            "FAQ schema markup and consider <details>/<summary> elements. "
            "FAQ format matches how users query AI systems. "
            "(Multiple industry sources)"
        ),
        "impact": "medium",
    },
    "crawlability_score": {
        "category": "crawlability",
        "message": (
            "Your page may require JavaScript to render. AI crawlers do NOT "
            "execute JavaScript — client-side rendered pages appear blank. "
            "Implement server-side rendering (Next.js, Nuxt, Astro) or "
            "pre-render pages to ensure content is accessible. "
            "(Aggarwal et al., 2024; Cloudflare crawler documentation)"
        ),
        "impact": "medium",
    },
    "robots_score": {
        "category": "robots",
        "message": (
            "Your robots.txt is blocking AI crawlers. If you want AI "
            "visibility, explicitly allow GPTBot, ChatGPT-User, and ClaudeBot. "
            "Note: 13.26% of AI bot requests ignored robots.txt in Q2 2025 "
            "(Tollbit), but major crawlers from OpenAI, Anthropic, and Google "
            "do respect it. Blocking AI crawlers can reduce total traffic by "
            "23% (Zhao & Berman, Rutgers/Wharton 2025). "
            "(Liu et al., IMC 2025; Longpre et al., NeurIPS 2024)"
        ),
        "impact": "medium",
    },
    "readability_score": {
        "category": "readability",
        "message": (
            "Optimize content readability. Aim for a Flesch Reading Ease score "
            "of 60-70 (8th-9th grade level). Tighter copy, better readability, "
            "and removing filler produces cleaner text embeddings. Fluency "
            "optimization shows +15-30% visibility improvement. "
            "(Aggarwal et al., KDD 2024)"
        ),
        "impact": "low",
    },
}

# Sort by weight descending for priority assignment
SORTED_METRICS = sorted(settings.WEIGHTS.items(), key=lambda x: x[1], reverse=True)


def generate_recommendations(
    scores: dict[str, float], threshold: float = 50.0
) -> list[Recommendation]:
    """Generate prioritized recommendations for metrics below threshold."""
    recommendations = []
    priority = 1

    for metric, _weight in SORTED_METRICS:
        score = scores.get(metric, 0.0)
        if score < threshold and metric in RECOMMENDATION_TEMPLATES:
            template = RECOMMENDATION_TEMPLATES[metric]
            recommendations.append(
                Recommendation(
                    priority=priority,
                    category=template["category"],
                    message=template["message"],
                    impact=template["impact"],
                )
            )
            priority += 1

    return recommendations
