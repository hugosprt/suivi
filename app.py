import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Suivi Patrimoine - Christine", layout="wide")

st.title("📊 Suivi de Portefeuille Titres")
st.write("Base au 19/01/2026 : **83 065,57 €**")

# 1. Base de données des actifs (Mapping des ISIN vers les tickers Yahoo Finance)
# Note : Certains fonds (FCP) peuvent nécessiter une recherche de ticker spécifique
data = {
    'Nom': [
        'SG AMUNDI ACTIONS FRANCE', 'CHRISTIAN DIOR', 'DANONE', 
        'CG NOUVELLE ASIE', 'CM AM CONVICT.USA', 'CM-AM EUROPE GROWT', 
        'ECHIQ.VALUE EUROPE', 'B.R.US VAL.M.FAC', 'NESTLE', 'GOLD BULLION'
    ],
    'Ticker': [
        'FR0010431015.PA', 'CDI.PA', 'BN.PA', 
        'FR0007450002.PA', 'FR00140077E1.PA', 'FR0010037341.PA', 
        'FR0010547067.PA', 'LU1458428163.LU', 'NESN.SW', 'GBS.L'
    ],
    'Quantité': [124.486, 25, 28, 5.0, 67.019, 1.824, 22.1723, 28.911, 50, 33],
    'Prix_Achat_Janvier': [68.52, 542.00, 74.12, 855.90, 154.71, 8145.11, 344.35, 194.43, 80.52, 367.38]
}

df = pd.DataFrame(data)

# 2. Récupération des cours en temps réel
@st.cache_data(ttl=3600) # Actualise toutes les heures
def get_live_prices(tickers):
    prices = {}
    for t in tickers:
        try:
            ticker_data = yf.Ticker(t)
            prices[t] = ticker_data.history(period="1d")['Close'].iloc[-1]
        except:
            prices[t] = 0 # Valeur par défaut si erreur
    return prices

prices_dict = get_live_prices(df['Ticker'].tolist())
df['Prix_Actuel'] = df['Ticker'].map(prices_dict)

# 3. Calculs
df['Valeur_Janvier'] = df['Quantité'] * df['Prix_Achat_Janvier']
df['Valeur_Actuelle'] = df['Quantité'] * df['Prix_Actuel']
df['Evolution_%'] = ((df['Valeur_Actuelle'] - df['Valeur_Janvier']) / df['Valeur_Janvier']) * 100

total_janvier = df['Valeur_Janvier'].sum()
total_actuel = df['Valeur_Actuelle'].sum()
perf_globale = ((total_actuel - total_janvier) / total_janvier) * 100

# 4. Affichage du Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("Valeur Initiale (Janv 2026)", f"{total_janvier:,.2f} €")
col2.metric("Valeur Actuelle", f"{total_actuel:,.2f} €", f"{perf_globale:.2f} %")
col3.metric("Nombre de lignes", len(df))

st.divider()

# Graphique de répartition
fig = px.pie(df, values='Valeur_Actuelle', names='Nom', title="Répartition du Portefeuille")
st.plotly_chart(fig, use_container_width=True)

# Tableau détaillé
st.subheader("Détails par ligne")
st.dataframe(df[['Nom', 'Quantité', 'Prix_Achat_Janvier', 'Prix_Actuel', 'Evolution_%']].style.format({
    'Prix_Achat_Janvier': '{:.2f} €',
    'Prix_Actuel': '{:.2f} €',
    'Evolution_%': '{:+.2f} %'
}))
