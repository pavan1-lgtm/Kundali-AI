"""
kundli_calc.py
Core astrology engine: converts birth date/time/place into planetary
positions, ascendant, houses and nakshatra using the Swiss Ephemeris
(pyswisseph), in the sidereal (Vedic / Lahiri) zodiac.
"""

import swisseph as swe
from datetime import datetime
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,   # North Node
}


def geocode_place(place_name: str):
    """Look up latitude, longitude and IANA timezone for a place name."""
    geolocator = Nominatim(user_agent="kundli-ai")
    location = geolocator.geocode(place_name)
    if location is None:
        raise ValueError(f"Could not find location: {place_name}")

    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=location.latitude, lng=location.longitude)
    if tz_name is None:
        raise ValueError("Could not determine timezone for this location")

    return location.latitude, location.longitude, tz_name


def to_julian_day_utc(birth_date, birth_time, tz_name: str) -> float:
    """
    birth_date: datetime.date
    birth_time: datetime.time
    tz_name: IANA timezone string, e.g. 'Asia/Kolkata'
    Returns the Julian Day (UT) that Swiss Ephemeris expects.
    """
    local_dt = datetime.combine(birth_date, birth_time)
    tz = pytz.timezone(tz_name)
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)

    jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    )
    return jd


def sign_and_nakshatra(sidereal_longitude: float):
    """Given a sidereal longitude (0-360), return (sign, degree_in_sign, nakshatra, pada)."""
    lon = sidereal_longitude % 360
    sign = ZODIAC_SIGNS[int(lon // 30)]
    degree_in_sign = lon % 30

    nak_index = int(lon // (360 / 27))
    nakshatra = NAKSHATRAS[nak_index]
    pada = int((lon % (360 / 27)) // (360 / 27 / 4)) + 1

    return sign, round(degree_in_sign, 2), nakshatra, pada


def calculate_chart(birth_date, birth_time, place_name: str) -> dict:
    """
    Main entry point. Returns a dict with:
      - ascendant: {sign, degree}
      - planets: {name: {sign, degree, nakshatra, pada, house}}
      - houses: {house_number: sign}  (whole-sign house system)
      - meta: lat, lon, tz, jd
    """
    lat, lon, tz_name = geocode_place(place_name)
    jd_ut = to_julian_day_utc(birth_date, birth_time, tz_name)

    # Use Lahiri ayanamsa - the standard for Vedic (sidereal) astrology
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # Ascendant (tropical), houses via Placidus, then convert to sidereal
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    asc_tropical = ascmc[0]
    asc_sidereal = (asc_tropical - ayanamsa) % 360
    asc_sign, asc_deg, asc_nak, asc_pada = sign_and_nakshatra(asc_sidereal)
    asc_sign_index = ZODIAC_SIGNS.index(asc_sign)

    # Whole-sign houses: house 1 = ascendant's sign, house 2 = next sign, etc.
    houses = {
        i + 1: ZODIAC_SIGNS[(asc_sign_index + i) % 12]
        for i in range(12)
    }

    planets_out = {}
    for name, code in PLANETS.items():
        pos, _ = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH)
        tropical_lon = pos[0]
        sidereal_lon = (tropical_lon - ayanamsa) % 360
        sign, deg, nak, pada = sign_and_nakshatra(sidereal_lon)
        sign_index = ZODIAC_SIGNS.index(sign)
        house_num = ((sign_index - asc_sign_index) % 12) + 1

        planets_out[name] = {
            "sign": sign, "degree": deg, "nakshatra": nak,
            "pada": pada, "house": house_num
        }

    # Ketu (South Node) is always exactly opposite Rahu
    rahu = planets_out["Rahu"]
    ketu_sidereal = (ZODIAC_SIGNS.index(rahu["sign"]) * 30 + rahu["degree"] + 180) % 360
    ketu_sign, ketu_deg, ketu_nak, ketu_pada = sign_and_nakshatra(ketu_sidereal)
    ketu_sign_index = ZODIAC_SIGNS.index(ketu_sign)
    planets_out["Ketu"] = {
        "sign": ketu_sign, "degree": ketu_deg, "nakshatra": ketu_nak,
        "pada": ketu_pada, "house": ((ketu_sign_index - asc_sign_index) % 12) + 1
    }

    return {
        "ascendant": {
            "sign": asc_sign, "degree": asc_deg,
            "nakshatra": asc_nak, "pada": asc_pada
        },
        "planets": planets_out,
        "houses": houses,
        "meta": {"lat": lat, "lon": lon, "tz": tz_name, "jd_ut": jd_ut, "ayanamsa": round(ayanamsa, 4)}
    }
