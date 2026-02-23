from ..config import settings


def calculate_total_score(scores: dict[str, float]) -> float:
    """Calculate weighted total score from individual analyzer scores."""
    total = 0.0
    for metric, weight in settings.WEIGHTS.items():
        total += scores.get(metric, 0.0) * weight
    return round(total, 1)


def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"
