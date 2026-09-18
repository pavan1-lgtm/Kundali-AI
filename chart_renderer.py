"""
chart_renderer.py
Draws a North-Indian style diamond kundli chart (square + diagonals + inner
diamond, 12 houses) and places each planet in its house. Returns a
matplotlib Figure that Streamlit can render directly.
"""

import matplotlib.pyplot as plt

PLANET_ABBR = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke",
}

SIGN_ABBR = {
    "Aries": "Ar", "Taurus": "Ta", "Gemini": "Ge", "Cancer": "Cn",
    "Leo": "Le", "Virgo": "Vi", "Libra": "Li", "Scorpio": "Sc",
    "Sagittarius": "Sg", "Capricorn": "Cp", "Aquarius": "Aq", "Pisces": "Pi",
}

# Approximate label position for each house number in the diamond layout.
# House 1 sits at the top center, numbering runs clockwise from there.
HOUSE_LABEL_POS = {
    1: (5, 7.7), 2: (2.3, 8.8), 3: (1.1, 6.3), 4: (2.5, 5),
    5: (1.1, 3.7), 6: (2.3, 1.2), 7: (5, 2.3), 8: (7.7, 1.2),
    9: (8.9, 3.7), 10: (7.5, 5), 11: (8.9, 6.3), 12: (7.7, 8.8),
}

HOUSE_SIGN_POS = {
    1: (5, 6.6), 2: (3.3, 8.3), 3: (2.0, 7.0), 4: (3.3, 5),
    5: (2.0, 3.0), 6: (3.3, 1.7), 7: (5, 3.4), 8: (6.7, 1.7),
    9: (8.0, 3.0), 10: (6.7, 5), 11: (8.0, 7.0), 12: (6.7, 8.3),
}


def render_north_indian_chart(chart: dict):
    """chart is the dict returned by kundli_calc.calculate_chart()."""
    fig, ax = plt.subplots(figsize=(6, 6))

    # Outer square
    ax.plot([0, 10, 10, 0, 0], [0, 0, 10, 10, 0], color="black", linewidth=1.5)
    # Diagonals
    ax.plot([0, 10], [0, 10], color="black", linewidth=1)
    ax.plot([0, 10], [10, 0], color="black", linewidth=1)
    # Inner diamond connecting side midpoints
    ax.plot([5, 10, 5, 0, 5], [10, 5, 0, 5, 10], color="black", linewidth=1)

    # Group planets by house number
    planets_by_house = {i: [] for i in range(1, 13)}
    for name, info in chart["planets"].items():
        planets_by_house[info["house"]].append(PLANET_ABBR.get(name, name[:2]))

    for house_num, sign_name in chart["houses"].items():
        sx, sy = HOUSE_SIGN_POS[house_num]
        ax.text(sx, sy, SIGN_ABBR[sign_name], fontsize=9, color="gray",
                ha="center", va="center", style="italic")

        px, py = HOUSE_LABEL_POS[house_num]
        label = " ".join(planets_by_house[house_num]) if planets_by_house[house_num] else ""
        ax.text(px, py, label, fontsize=10, fontweight="bold",
                ha="center", va="center", color="darkred")

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.axis("off")
    ax.set_aspect("equal")
    fig.tight_layout()
    return fig
