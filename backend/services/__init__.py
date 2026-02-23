from .recommender import generate_recommendations
from .scorer import calculate_total_score
from .scraper import fetch_page

__all__ = ["fetch_page", "calculate_total_score", "generate_recommendations"]
