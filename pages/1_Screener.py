import streamlit as st
import yfinance as yf
import pandas as pd
import os

# =================================================================
# CONFIGURAÇÃO GERAL
# =================================================================
st.set_page_config(page_title="Análise de Ações", layout="wide")
st.title("🔍 Comparativo de Ações")
st.write("---")
st.header("Tabela de Comparação de Ações")


# =================================================================
# FUNÇÃO PARA OBTER UMA LISTA DINÂMICA DE TICKERS DA BOVESPA
# =================================================================
# Esta função faz web scraping para obter a lista de tickers da Bovespa.
@st.cache_data
def obter_tickers_b3_novos():
    try:
        url = "https://www.dadosdemercado.com.br/acoes"
        tabelas = pd.read_html(url, header=0)
        df = tabelas[0]

        # O ticker está na coluna 'Ticker'
        tickers = df['Ticker'].tolist()

        # Filtra os tickers para garantir que são válidos (ex: remove NaNs)
        tickers_validos = [t for t in tickers if isinstance(t, str) and len(t) > 3]

        # Adiciona o sufixo '.SA' para o yfinance
        tickers_sa = [ticker + '.SA' for ticker in tickers_validos]

        return tickers_sa
    except Exception as e:
        st.error(f"Erro ao obter a lista de tickers. Retornando uma lista padrão. Erro: {e}")
        return [
            'ABEV3.SA', 'AZUL4.SA', 'B3SA3.SA', 'BBAS3.SA', 'BBDC4.SA',
            'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'WEGE3.SA', 'LREN3.SA'
        ]


# =================================================================
# FUNÇÃO PARA OBTER DADOS DO SCREENER (USANDO YFINANCE)
# =================================================================
@st.cache_data
def get_screener_data(tickers):
    screener_df = pd.DataFrame(
        columns=['Ticker', 'Preço', 'P/L', 'Div. Yield (%)', 'Volume', 'Valor de Mercado', 'Setor'])

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
            st.warning(f"Não foi possível buscar dados para {ticker}. Erro: {e}")

    return screener_df


# =================================================================
# EXECUÇÃO DO PROGRAMA
# =================================================================
tickers_list = obter_tickers_b3_novos()
screener_df = get_screener_data(tickers_list)
screener_df = screener_df.round(2)

# Define o ticker como índice para melhorar a visualização (sem o emoji)
screener_df = screener_df.set_index('Ticker')

st.dataframe(screener_df)