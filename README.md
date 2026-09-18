# Kundli AI

A Vedic (sidereal) kundli generator with an AI-written interpretation on top —
built for a live demo, not just a notebook.

**Pipeline:** birth date/time/place → Swiss Ephemeris calculates accurate
planetary positions (`kundli_calc.py`) → North Indian diamond chart is drawn
(`chart_renderer.py`) → Claude turns the calculated data into a readable
interpretation (`interpretation.py`) → a small KMeans layer clusters the
chart into an "archetype" as a bonus ML touch (`ml_component.py`) → all tied
together in a one-page Streamlit app (`app.py`).

## Setup

```bash
pip install -r requirements.txt
```

You'll also need Swiss Ephemeris data files for full historical accuracy
(pyswisseph ships a reduced built-in set that works for most modern dates
without any extra download). If you hit accuracy issues for older dates,
download the ephemeris files from https://www.astro.com/ftp/swisseph/ephe/
and point to them with `swe.set_ephe_path("/path/to/ephe")` at the top of
`kundli_calc.py`.

Set your Anthropic API key so the interpretation step works:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Run

```bash
streamlit run app.py
```

Enter a birth date, time, and place — the app geocodes the place automatically
(no manual lat/long needed), computes the chart, draws it, and generates the
reading.

## Files

| File | Purpose |
|---|---|
| `kundli_calc.py` | Core astronomy: Julian day conversion, ayanamsa, planetary longitudes, houses, nakshatra — all deterministic, no LLM involved |
| `chart_renderer.py` | Draws the North Indian diamond chart with matplotlib |
| `interpretation.py` | Builds the prompt from calculated chart data and calls Claude for the reading |
| `ml_component.py` | Bonus: encodes charts as vectors and clusters them with KMeans |
| `app.py` | Streamlit UI tying it all together |

## Why this is a good interview project

- **It's a real pipeline, not an API wrapper.** The astronomy (Swiss Ephemeris)
  is deterministic and separate from the LLM step — you can explain exactly
  where the "AI" part starts and stops, which shows judgment interviewers
  respect.
- **It's visual and live.** A chart renders and a reading appears in seconds —
  no need to explain metrics, they just watch it work.
- **It has a genuine ML component**, not just prompting — the KMeans
  archetype layer gives you something to discuss beyond "I called an API":
  feature engineering (chart → vector), unsupervised learning, and how you'd
  extend it with a real user dataset.
- **It's personal and memorable.** Tying it to Vedic astrology makes it stand
  out from generic classifier/chatbot projects and gives you an authentic
  story about why you built it.

## Possible extensions (good "what would you add next" answers)

- Add Dasha (planetary period) calculations for timing-based predictions
- Compatibility (Guna Milan) scoring between two charts
- Cache geocoding results and add a small SQLite store of past queries so
  the ML clustering becomes meaningful on real data
- Deploy on Streamlit Community Cloud for a shareable live link
