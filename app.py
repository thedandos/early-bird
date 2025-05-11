import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import pandas as pd

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

st.set_page_config(page_title="Early Surge Scanner", layout="wide")
st.title("🚀 Oracle+ Early Surge Scanner")

# Calculate last Friday's date
today = datetime.now()
offset = (today.weekday() - 4) % 7  # 4 = Friday
last_friday = today - timedelta(days=offset)
last_friday_str = last_friday.strftime("%Y-%m-%d")

# Function to fetch previous movers
def fetch_friday_movers():
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{last_friday_str}?adjusted=true&apiKey={POLYGON_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        st.warning("Polygon API error: Unable to fetch previous movers.")
        return pd.DataFrame()

    data = response.json().get("results", [])
    movers = []
    for stock in data:
        try:
            change_pct = ((stock["c"] - stock["o"]) / stock["o"]) * 100
            if change_pct >= 5 and stock["v"] >= 500_000:
                movers.append({
                    "Ticker": stock["T"],
                    "% Gain": round(change_pct, 2),
                    "Volume": stock["v"]
                })
        except (TypeError, ZeroDivisionError):
            continue

    movers_df = pd.DataFrame(movers).sort_values("% Gain", ascending=False).head(5)
    return movers_df

# Display Friday movers
st.subheader("📈 Top 5 Early Movers from Last Friday")
friday_movers = fetch_friday_movers()
if not friday_movers.empty:
    st.dataframe(friday_movers, use_container_width=True)
else:
    st.info("No qualifying movers found or market data unavailable.")
