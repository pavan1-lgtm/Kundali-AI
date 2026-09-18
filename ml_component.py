"""
ml_component.py
BONUS / interview talking point: a small, honest ML layer on top of the
astrology data, so the project isn't "just an LLM wrapper."

Idea: represent each chart as a 12-dim vector = which sign occupies
each house (whole-sign system). Cluster a batch of charts with KMeans
to find "archetypes" -- e.g. users whose charts cluster together tend
to ask similar follow-up questions. Here we demonstrate it on
synthetic sample charts so it runs standalone without a real user
database; swap `sample_dataset()` for real stored charts once you
have users.
"""

import numpy as np
from sklearn.cluster import KMeans

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def chart_to_vector(chart: dict) -> np.ndarray:
    """Encode a chart as a 12-length vector of sign indices, one per house."""
    return np.array([ZODIAC_SIGNS.index(chart["houses"][h]) for h in range(1, 13)])


def sample_dataset(n: int = 40, seed: int = 42) -> np.ndarray:
    """Synthetic stand-in for a real database of past user charts."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 12, size=(n, 12))


def cluster_archetypes(vectors: np.ndarray, n_clusters: int = 4):
    """Fit KMeans and return (labels, cluster_centers)."""
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = km.fit_predict(vectors)
    return labels, km.cluster_centers_


def which_archetype(chart: dict, dataset: np.ndarray = None, n_clusters: int = 4) -> int:
    """Fit clusters on the dataset (or a synthetic one) and classify this chart."""
    if dataset is None:
        dataset = sample_dataset()
    labels, centers = cluster_archetypes(dataset, n_clusters)
    vec = chart_to_vector(chart)
    distances = np.linalg.norm(centers - vec, axis=1)
    return int(np.argmin(distances))
