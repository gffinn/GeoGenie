from ..config import settings


def calculate_total_score(scores: dict[str, float]) -> float:
    """Calculate weighted total score from individual analyzer scores."""
    total = 0.0
    for metric, weight in settings.WEIGHTS.items():
        total += scores.get(metric, 0.0) * weight
    return round(total, 1)


def score_to_grade(score: float, scores: dict[str, float] | None = None) -> str:
    """Convert numeric score to letter grade, applying critical failure overrides.

    Critical failures (evaluated before numeric thresholds):
      - crawlability_score == 0  → F  (page did not load)
      - robots_score == 0        → F  (all AI crawlers explicitly blocked)
      - https_score == 0         → D  (no HTTPS; caps grade regardless of total)

    Thresholds (stricter rubric v2):
      90–100 → A, 80–89 → B, 70–79 → C, 60–69 → D, <60 → F
    """
    if scores:
        # Hard failures — page unreadable or fully AI-blocked
        if scores.get("crawlability_score", 100.0) == 0.0:
            return "F"
        if scores.get("robots_score", 100.0) == 0.0:
            return "F"
        # HTTPS failure — cap at D even if numeric score would be higher
        if scores.get("https_score", 100.0) == 0.0 and score >= 70.0:
            return "D"

    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
