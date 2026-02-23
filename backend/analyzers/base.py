from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """Base class for all GEO analyzers."""

    name: str = "base"
    score_field: str = "base_score"

    @abstractmethod
    def analyze(self, html: str, url: str) -> dict:
        """Analyze HTML content and return metrics dict.

        Must include a 'score' key (0-100) and any additional metrics.
        """
        ...
