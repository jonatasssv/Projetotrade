import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Análise de Ações", layout="wide")

st.title("🔍 Comparativo de Ações")
st.write("---")

st.header("Tabela de Comparação de Ações")

# Lista de tickers para a tabela (você pode personalizar esta lista)
tickers_list = ['PETR4.SA', 'ITUB3.SA', 'VALE3.SA', 'WEGE3.SA', 'BBAS3.SA']

@st.cache_data
def get_screener_data(tickers):
    screener_df = pd.DataFrame(columns=['Ticker', 'Preço', 'P/L', 'Div. Yield (%)', 'Volume', 'Valor de Mercado', 'Setor'])
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            price = info.get('currentPrice')
            pe_ratio = info.get('trailingPE')
            div_yield = info.get('dividendYield') * 100 if info.get('dividendYield') else None
            volume = info.get('volume')
            market_cap = info.get('marketCap')
            sector = info.get('sector')
            
            new_row = pd.DataFrame([{
                'Ticker': ticker,
                'Preço': price,
                'P/L': pe_ratio,
                'Div. Yield (%)': div_yield,
                'Volume': volume,
                'Valor de Mercado': market_cap,
                'Setor': sector
            }])
            screener_df = pd.concat([screener_df, new_row], ignore_index=True)
        except Exception as e:
            st.warning(f"Não foi possível buscar dados para {ticker}.")

    return screener_df

screener_df = get_screener_data(tickers_list)

# Exibir a tabela no Streamlit
screener_df = screener_df.round(2)
st.dataframe(screener_df)