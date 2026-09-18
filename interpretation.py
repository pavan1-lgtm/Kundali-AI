"""
interpretation.py
Turns calculated planetary/house data into a natural-language reading
using Claude. The chart math (kundli_calc.py) stays deterministic and
accurate; the LLM is only used for the readable interpretation on top
of it -- this separation is worth mentioning in an interview, since it
shows you know not to let an LLM "hallucinate" astronomy.
"""

import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def build_prompt(chart: dict, language: str = "English") -> str:
    asc = chart["ascendant"]
    lines = [
        f"Ascendant (Lagna): {asc['sign']} ({asc['degree']}°), "
        f"Nakshatra: {asc['nakshatra']} pada {asc['pada']}"
    ]
    for name, info in chart["planets"].items():
        lines.append(
            f"{name}: {info['sign']} ({info['degree']}°), house {info['house']}, "
            f"Nakshatra {info['nakshatra']} pada {info['pada']}"
        )
    chart_summary = "\n".join(lines)

    prompt = f"""You are a knowledgeable Vedic astrology interpreter. Based ONLY on the
calculated chart data below, write a warm, grounded reading in {language}.
Cover: personality (from Ascendant/Moon), career tendencies (10th house
influences), relationships (7th house / Venus), and one general life theme.
Keep it to about 200-250 words. Avoid superstition-heavy or fatalistic
language -- frame everything as tendencies, not certainties.

Chart data:
{chart_summary}
"""
    return prompt


def generate_interpretation(chart: dict, language: str = "English") -> str:
    prompt = build_prompt(chart, language)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
