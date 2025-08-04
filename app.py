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
ticker = st.sidebar.text_input("Insira o Ticker da Ação Principal (ex: PINE4.SA)", "PINE4.SA")
start_date = st.sidebar.date_input("Data de Início", datetime(2020, 1, 1))
end_date = st.sidebar.date_input("Data de Fim", datetime.now().date())

# --- CAMPO DE COMPARAÇÃO DINÂMICO ---
comparar_ticker = st.sidebar.text_input("Comparar com (padrão: Ibovespa)", "^BVSP")
st.sidebar.write("---")

if ticker:
    st.header(f"Resultados para {ticker}")


    @st.cache_data
    def get_data(ticker, start, end):
        df_data = yf.download(ticker, start=start, end=end)
        return df_data


    # Carregar os dados
    df_principal = get_data(ticker, start_date, end_date)

    if df_principal.empty:
        st.error(
            f"Não foi possível carregar os dados para o ticker principal: {ticker}. Verifique se o nome está correto.")
    else:
        try:
            # --- CORREÇÃO: Nivelar o índice de colunas ---
            df_principal.columns = [col[0] for col in df_principal.columns]

            # Baixar o histórico de dividendos
            acoes_corporativas = yf.Ticker(ticker).actions
            dividendos = acoes_corporativas[acoes_corporativas['Dividends'] > 0].copy()
            dividendos = dividendos.rename(columns={'Dividends': 'Valor do Dividendo'})
            dividendos.index.name = 'Data Ex-Dividendo'
            dividendos = dividendos[['Valor do Dividendo']]

            # Garantir que ambos os índices sejam 'tz-naive' antes de fazer a união
            df_principal.index = df_principal.index.tz_localize(None)
            dividendos.index = dividendos.index.tz_localize(None)

            tabela_dividendos = pd.merge(dividendos, df_principal[['Close']],
                                         left_index=True, right_index=True, how='left')

            tabela_dividendos = tabela_dividendos.rename(columns={'Close': 'Preço na Data Ex-Dividendo'})
            tabela_dividendos['Dividend Yield (%)'] = (tabela_dividendos['Valor do Dividendo'] / tabela_dividendos[
                'Preço na Data Ex-Dividendo']) * 100
            tabela_dividendos['Crescimento do Dividendo (%)'] = tabela_dividendos[
                                                                    'Valor do Dividendo'].pct_change() * 100
            tabela_dividendos = tabela_dividendos.dropna().round(2)
            tabela_dividendos.index.name = 'Data Ex-Dividendo'

            # --- Exibir a Tabela Colorida no Streamlit ---
            st.subheader("Tabela de Dividendos")


            def color_growth(val):
                color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f'color: {color}'


            styled_table = tabela_dividendos.style.applymap(color_growth, subset=['Crescimento do Dividendo (%)'])
            st.dataframe(styled_table)

            # --- Exibir Gráfico de Dividend Yield no Streamlit ---
            st.subheader("Gráfico de Dividend Yield")
            fig_yield, ax_yield = plt.subplots(figsize=(12, 7))
            sns.lineplot(x=tabela_dividendos.index, y='Dividend Yield (%)', data=tabela_dividendos, marker='o',
                         color='b', ax=ax_yield)
            ax_yield.set_title(f'Dividend Yield (%) de {ticker} por Data Ex-Dividendo', fontsize=16)
            ax_yield.set_xlabel('Data Ex-Dividendo', fontsize=12)
            ax_yield.set_ylabel('Dividend Yield (%)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig_yield)

            # --- Exibir Gráfico de Comparação Dinâmica ---
            st.subheader(f"Comparação de Desempenho")
            df_comparacao = get_data(comparar_ticker, start_date, end_date)

            if not df_comparacao.empty:
                df_principal['Normalized_Close'] = df_principal['Close'] / df_principal['Close'].iloc[0] * 100
                df_comparacao['Normalized_Close'] = df_comparacao['Close'] / df_comparacao['Close'].iloc[0] * 100

                fig_comp, ax_comp = plt.subplots(figsize=(12, 7))
                ax_comp.plot(df_principal.index, df_principal['Normalized_Close'], label=f'{ticker} (Performance)',
                             color='blue')
                ax_comp.plot(df_comparacao.index, df_comparacao['Normalized_Close'], label=f'{comparar_ticker}',
                             color='red', linestyle='--')
                ax_comp.set_title(f'Comparação de Desempenho: {ticker} vs. {comparar_ticker}', fontsize=16)
                ax_comp.set_xlabel('Data', fontsize=12)
                ax_comp.set_ylabel('Retorno Normalizado (%)', fontsize=12)
                ax_comp.legend()
                ax_comp.grid(True)
                st.pyplot(fig_comp)
            else:
                st.warning(
                    f"Não foi possível carregar os dados para o ticker de comparação: {comparar_ticker}. Verifique o nome.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar os dados. Tente novamente com um ticker diferente. Erro: {e}")