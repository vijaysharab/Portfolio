import streamlit as st 
import yfinance as yf
from curl_cffi import requests
import pandas as pd

session = requests.Session(impersonate="chrome", verify=False)
#ticker = yf.Ticker("AAPL", session=session)

st.set_page_config(
    page_title="My Portfolio",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",

)
st.title("📈 Stock Search (Yahoo Finance)")
with st.sidebar:
    st.title("Menu")
    #st.radio("Go to", ["Home", "Portfolio"])

# Step 1: User types partial name or ticker
query = st.text_input(
    "Type part of a stock name or ticker (e.g. apple, tesla, micro):",
    placeholder="Start typing..."
)
@st.cache_data(show_spinner=False)
def search_ticker_by_name(partial_name):
    """
    Searches for stock tickers using a partial company name.
    
    Args:
        partial_name (str): The partial name of the company to search for.

    Returns:
        list: A list of dictionaries containing symbol, name, and exchange for potential matches.
    """
    try:
        # Use yf.Search to find quotes (tickers) based on the query
        search_results = yf.Search(partial_name, max_results=10) # Limit the results for brevity
        
        quotes = search_results.quotes
        
        if not quotes:
            st.write(f"No results found for '{partial_name}'")
            return []

        found_tickers = []
        st.write(f"Found potential matches for '{partial_name}':")
        for quote in quotes:
            # Extract relevant information from each quote result
            ticker_info = {
                "symbol": quote['symbol'],
                "shortName": quote.get('shortName', 'N/A'),
                "exchange": quote.get('exchange', 'N/A'),
                "quoteType": quote.get('quoteType', 'N/A')
            }
            found_tickers.append(ticker_info)
            #st.write(f"* **{ticker_info['symbol']}**: {ticker_info['shortName']} ({ticker_info['exchange']}) - Type: {ticker_info['quoteType']}")
        
        return found_tickers

    except Exception as e:
        st.write(f"An error occurred during the search: {e}")
        return []

# Step 2: Search and show selectable options
stocks = search_ticker_by_name(query)


if stocks:
    st.success("Stock Confirmed")
    selection = st.pills("Stocks found", stocks,
        format_func=lambda x: x["symbol"], selection_mode="single")
    #st.markdown(f"Your selected options: {selection}.") 
    
    if selection is not None:
        st.write("**Ticker Symbol:**", selection["symbol"])
        # Optional: Fetch basic info
        ticker = yf.Ticker(selection["symbol"])
        info = ticker.info
        st.write(info)
        st.subheader("Basic Info")
        st.write("**Company Name:**",  info.get("shortName", "N/A"))
        st.write("**Sector:**", info.get("sector", "N/A"))
        st.write("**Industry:**", info.get("industry", "N/A"))
        st.write("**Market Cap:**", info.get("marketCap", "N/A"))
        confusion_matrix = pd.DataFrame(
        {
            "Previous Close": info.get("previousClose", "N/A"),
            "Open": info.get("open", "N/A"),
            "Bid": info.get("bid", "N/A"),
            "Ask": info.get("ask", "N/A"),
            "Days Range": info.get("regularMarketDayRange", "N/A"),
            "52 Week Range": info.get("fiftyTwoWeekRange", "N/A"),
            "Volume": info.get("Volume", "N/A"),
            "averageVolume": info.get("averageVolume", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "PEG Ratio": info.get("trailingPegRatio", "N/A"),
        },
        index=[""]
        )
        st.table(confusion_matrix)
    else:
        st.write("Selection is None")

elif query:
    st.warning("No matching stocks found.")