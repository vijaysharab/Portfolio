import streamlit as st 
import yfinance as yf
from curl_cffi import requests
import pandas as pd
import datetime
import plotly.express as px

session = requests.Session(impersonate="chrome", verify=False)
#ticker = yf.Ticker("AAPL", session=session)
st.set_page_config(
    page_title="My Portfolio",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
########################################### Definations ##########################################
def update_df():
    df = pd.read_parquet("data.parquet")
    for index, row in df.iterrows():
        ticker = yf.Ticker(row["Ticker"], session=session)
        pair = yf.Ticker("DKK=X", session=session)
        data = pair.history(period="1d")
        if not data.empty:
            USDDKK = data["Close"].iloc[-1]
        #ticker = yf.Ticker(selection[symbol])
        info = ticker.info
        if  info["currency"] =="USD":
            row["Current price"]=info["currentPrice"]
            row["Current price in DKK"]=round(info["currentPrice"]*float(USDDKK)*float(row["Quantity"]),2)
            row["Profit/Loss"]=round((float(info["currentPrice"])-float(row["Purchase Value"]))*float(row["Quantity"])*float(USDDKK),2)
            row["Change in %"]=round((float(info["currentPrice"])-float(row["Purchase Value"])/float(row["Purchase Value"]))*100,2)
        if  info["currency"] =="DKK":
            row["Current price"]=info["currentPrice"]
            row["Current price in DKK"]=round(info["currentPrice"]*1*float(row["Quantity"]),2)
            row["Profit/Loss"]=round((float(info["currentPrice"])-float(row["Purchase Value"]))*float(row["Quantity"])*1,2)
            row["Change in %"]=round((float(info["currentPrice"])-float(row["Purchase Value"])/float(row["Purchase Value"]))*100,2)    
    df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")

def style_row(row):   # 👈 row IS defined here
    if row["Change in %"] > 0:
        return ["background-color: #d4f7d4; color: green"] * len(row)
    elif row["Change in %"] < 0:
        return ["background-color: #f7d4d4; color: red"] * len(row)
    else:
        return [""] * len(row)

@st.dialog("Add Stock to Portfolio")
def add_stock_dialog():
    symbol = st.text_input("Stock Symbol", placeholder="AAPL")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    buy_price = st.number_input("Buy Price", min_value=0.0, step=0.01)
    buy_date = st.date_input("Purchase Date", datetime.datetime.now())

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Add"):
            if symbol:
                ticker = yf.Ticker(symbol, session=session)
                pair = yf.Ticker("DKK=X", session=session)
                data = pair.history(period="1d")
                if not data.empty:
                    USDDKK = data["Close"].iloc[-1]
                #ticker = yf.Ticker(selection[symbol])
                info = ticker.info
                df = pd.read_parquet("data.parquet")
                if  info["currency"] =="USD":
                    df.loc[len(df)] = [symbol, info["longName"], info["currency"],buy_price,
                    round(float(buy_price)*float(quantity)*float(USDDKK),2),
                    quantity,
                    buy_date,
                    info["currentPrice"],
                    round(info["currentPrice"]*float(USDDKK)*quantity,2),
                    round((float(info["currentPrice"])-float(buy_price))*float(quantity)*float(USDDKK),2),
                    round(((float(info["currentPrice"])-float(buy_price))/float(buy_price))*100,2)]
                if  info["currency"] =="DKK":
                    df.loc[len(df)] = [symbol, info["longName"], 
                    info["currency"],
                    buy_price,round(float(buy_price)*float(quantity),2),
                    quantity,buy_date,info["currentPrice"],
                    round(info["currentPrice"]*1*quantity,2),
                    round((float(info["currentPrice"])-float(buy_price))*float(quantity),2),
                    round(((float(info["currentPrice"])-float(buy_price))/float(buy_price))*100,2)]
                df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
                st.success(f"{symbol.upper()} added!")
                st.rerun()
            else:
                st.error("Stock symbol required")

    with col2:
        if st.button("Cancel"):
            st.rerun()
#---------------------------------------------------------------------------------------------#
# Main Program
st.title("📈 Your Portfolio")
# check for database
try:
    df = pd.read_parquet("data.parquet")
except:
    st.write("Database not available and Creating new database.")
    df = pd.DataFrame(columns=['Ticker', 'Stock Name','Currency','Purchase Value','Total Purchase Value','Quantity','Purchase date','Current Price','Current Price in DKK','Profit/Loss','Change in %'])
    df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
    #st.dataframe(df)
options = ["View", "Edit"]
selection = st.segmented_control(
    "Directions", options, selection_mode="single"
)
st.markdown(f"Your selected options: {selection}.")
if selection == "View":
    update_df()
    styled_df = df.style.apply(style_row, axis=1) 
    styled_df = styled_df.format({
    "Profit/Loss": "{:.2f}",
    "Current Price in DKK": "{:.2f}",
    "Current Price": "{:.2f}",
    "Total Purchase Value": "{:.2f}",
    "Purchase Value": "{:.2f}",
    "Change in %": "{:.2f}"
        })
    with st.expander("dataframe"):
        st.dataframe(styled_df,use_container_width=True)
if selection == "Edit":
    df=st.data_editor(df,num_rows= "dynamic")
    if st.button("Save"):
        df.to_parquet("data.parquet", engine="pyarrow", compression="snappy")
        
############# Add ticker  #####################################
if st.button("➕ Add Stock"):
    add_stock_dialog()
if not df.empty:
    col1, col2,col3 = st.columns(3)
    with col1:
        bar_df = df.set_index("Ticker")[["Total Purchase Value","Current Price in DKK"]]
        fig = px.bar(bar_df,barmode='group',text_auto='.2s')
        st.plotly_chart(fig)
    with col2:
        bar_df = df.set_index("Ticker")[["Profit/Loss"]]
        fig = px.bar(bar_df,barmode='group',text_auto='.2s')
        st.plotly_chart(fig)
    with col3:
        bar_df = df.set_index("Ticker")[["Change in %"]]
        fig = px.bar(bar_df,barmode='group',text_auto='.2s')
        st.plotly_chart(fig)
    
    col1, col2,col3 = st.columns(3)
    with col1:
        fig = px.pie(df, values='Total Purchase Value',names='Ticker',
             title='Portfolio Allocation',
             )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    with col2:
        fig = px.pie(df, values='Current Price in DKK',names='Ticker',
             title='Portfolio Allocation Present',
             )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    with col3 :
        Investment = df["Total Purchase Value"].sum()
        NPV = df["Current Price in DKK"].sum()
        profit = NPV-Investment
        st.write("Investment is "+str(Investment))
        st.write("Net Present Value is "+str(round(NPV,2)))
        st.write("profit is "+str(round(profit,2)))
        st.write("Profit in % "+str(round((profit/Investment)*100,2)))
