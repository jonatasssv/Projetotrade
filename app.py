import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Análise de Dividendos", layout="wide")

st.title("📊 Análise de Dividendos e Desempenho de Ações")
st.write("---")

# --- Barra Lateral para Interatividade ---
st.sidebar.header("⚙️ Configurações")
ticker = st.sidebar.text_input("Insira o Ticker da Ação (ex: PINE4.SA)", "PINE4.SA")
start_date = st.sidebar.date_input("Data de Início", datetime(2020, 1, 1))
end_date = st.sidebar.date_input("Data de Fim", datetime.now().date())
st.sidebar.write("---")

if ticker:
    st.header(f"Resultados para {ticker}")

    @st.cache_data
    def get_data(ticker, start, end):
        # Baixar os dados de preço da ação
        df_data = yf.download(ticker, start=start, end=end)
        return df_data

    # Carregar os dados
    df_pine4 = get_data(ticker, start_date, end_date)

    if df_pine4.empty:
        st.error("Não foi possível carregar os dados para este ticker. Verifique se o nome está correto.")
    else:
        try:
            # --- CORREÇÃO: Nivelar o índice de colunas ---
            df_pine4.columns = [col[0] for col in df_pine4.columns]

            # Baixar o histórico de dividendos
            acoes_corporativas = yf.Ticker(ticker).actions
            dividendos = acoes_corporativas[acoes_corporativas['Dividends'] > 0].copy()
            dividendos = dividendos.rename(columns={'Dividends': 'Valor do Dividendo'})
            dividendos.index.name = 'Data Ex-Dividendo'
            dividendos = dividendos[['Valor do Dividendo']]

            # Garantir que ambos os índices sejam 'tz-naive' antes de fazer a união
            df_pine4.index = df_pine4.index.tz_localize(None)
            dividendos.index = dividendos.index.tz_localize(None)

            # Usar pd.merge para unir os DataFrames
            tabela_dividendos = pd.merge(dividendos, df_pine4[['Close']], 
                                        left_index=True, right_index=True, how='left')

            tabela_dividendos = tabela_dividendos.rename(columns={'Close': 'Preço na Data Ex-Dividendo'})
            tabela_dividendos['Dividend Yield (%)'] = (tabela_dividendos['Valor do Dividendo'] / tabela_dividendos['Preço na Data Ex-Dividendo']) * 100
            tabela_dividendos['Crescimento do Dividendo (%)'] = tabela_dividendos['Valor do Dividendo'].pct_change() * 100
            tabela_dividendos = tabela_dividendos.dropna().round(2)
            tabela_dividendos.index.name = 'Data Ex-Dividendo'

            # --- Exibir a Tabela no Streamlit ---
            st.subheader("Tabela de Dividendos")
            st.dataframe(tabela_dividendos)

            # --- Exibir Gráfico de Dividend Yield no Streamlit ---
            st.subheader("Gráfico de Dividend Yield")
            fig_yield, ax_yield = plt.subplots(figsize=(12, 7))
            sns.lineplot(x=tabela_dividendos.index, y='Dividend Yield (%)', data=tabela_dividendos, marker='o', color='b', ax=ax_yield)
            ax_yield.set_title(f'Dividend Yield (%) de {ticker} por Data Ex-Dividendo', fontsize=16)
            ax_yield.set_xlabel('Data Ex-Dividendo', fontsize=12)
            ax_yield.set_ylabel('Dividend Yield (%)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig_yield)

            # --- Exibir Gráfico de Comparação com Ibovespa ---
            st.subheader("Comparação com o Ibovespa")
            df_ibovespa = get_data('^BVSP', start_date, end_date)
            
            if not df_ibovespa.empty:
                df_pine4['Normalized_Close'] = df_pine4['Close'] / df_pine4['Close'].iloc[0] * 100
                df_ibovespa['Normalized_Close'] = df_ibovespa['Close'] / df_ibovespa['Close'].iloc[0] * 100

                fig_comp, ax_comp = plt.subplots(figsize=(12, 7))
                ax_comp.plot(df_pine4.index, df_pine4['Normalized_Close'], label=f'{ticker} (Performance)', color='blue')
                ax_comp.plot(df_ibovespa.index, df_ibovespa['Normalized_Close'], label='Ibovespa (^BVSP)', color='red', linestyle='--')
                ax_comp.set_title(f'Comparação de Desempenho: {ticker} vs. Ibovespa', fontsize=16)
                ax_comp.set_xlabel('Data', fontsize=12)
                ax_comp.set_ylabel('Retorno Normalizado (%)', fontsize=12)
                ax_comp.legend()
                ax_comp.grid(True)
                st.pyplot(fig_comp)
            else:
                st.warning("Não foi possível carregar os dados do Ibovespa para a comparação.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar os dados: {e}")