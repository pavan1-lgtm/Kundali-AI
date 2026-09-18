"""
app.py
Kundli AI -- Streamlit demo app.

Run with:  streamlit run app.py

Flow: user enters birth date, time and place -> kundli_calc.py computes
an accurate sidereal chart via Swiss Ephemeris -> chart_renderer.py
draws it as a North Indian diamond chart -> interpretation.py asks
Claude to write a grounded reading on top of the *calculated* data ->
ml_component.py adds a small clustering "archetype" as a bonus
data-science touch.
"""

import streamlit as st
from datetime import date, time

from kundli_calc import calculate_chart
from chart_renderer import render_north_indian_chart
from interpretation import generate_interpretation
from ml_component import which_archetype

st.set_page_config(page_title="Kundli AI", page_icon="🔯", layout="centered")

st.title("🔯 Kundli AI")
st.caption(
    "Enter birth details for an accurate Vedic (sidereal) chart, "
    "computed with the Swiss Ephemeris and interpreted with Claude."
)

with st.form("birth_form"):
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Date of birth", value=date(2000, 1, 1),
                                    min_value=date(1900, 1, 1), max_value=date.today())
    with col2:
        birth_time = st.time_input("Time of birth", value=time(12, 0))

    place = st.text_input("Place of birth", placeholder="e.g. Panipat, Haryana, India")
    language = st.selectbox("Interpretation language", ["English", "Hindi"])
    submitted = st.form_submit_button("Generate Kundli")

if submitted:
    if not place.strip():
        st.error("Please enter a place of birth.")
    else:
        with st.spinner("Calculating planetary positions..."):
            try:
                chart = calculate_chart(birth_date, birth_time, place)
            except Exception as e:
                st.error(f"Couldn't calculate chart: {e}")
                st.stop()

        st.subheader("Your Kundli")
        fig = render_north_indian_chart(chart)
        st.pyplot(fig)

        asc = chart["ascendant"]
        st.markdown(
            f"**Ascendant (Lagna):** {asc['sign']} {asc['degree']}° "
            f"&nbsp;|&nbsp; **Nakshatra:** {asc['nakshatra']} (pada {asc['pada']})"
        )

        with st.expander("Full planetary positions"):
            rows = []
            for name, info in chart["planets"].items():
                rows.append({
                    "Planet": name, "Sign": info["sign"], "Degree": info["degree"],
                    "House": info["house"], "Nakshatra": info["nakshatra"], "Pada": info["pada"]
                })
            st.table(rows)

        st.subheader("AI Interpretation")
        with st.spinner("Writing your reading..."):
            try:
                reading = generate_interpretation(chart, language)
                st.write(reading)
            except Exception as e:
                st.warning(
                    "Interpretation unavailable (set ANTHROPIC_API_KEY to enable this). "
                    f"Details: {e}"
                )

        with st.expander("Bonus: ML archetype cluster"):
            st.caption(
                "Demonstration only: encodes the chart as a 12-house sign vector and "
                "clusters it against a synthetic sample population with KMeans -- "
                "swap in a real user database to make this meaningful."
            )
            archetype = which_archetype(chart)
            st.write(f"This chart falls into archetype cluster **#{archetype}**.")
