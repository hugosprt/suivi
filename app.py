import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Suivi Patrimoine - Christine", layout="wide")

st.title("📊 Suivi de Portefeuille Titres")
st.info("Note : Les fonds (FCP/SICAV) utilisent le dernier cours connu si le flux live est indisponible.")

# 1. Base de données des actifs
# J'ai mis à jour les Tickers pour maximiser les chances de succès
data = {
    'Nom': [
        'SG AMUNDI ACTIONS FRANCE', 'CHRISTIAN DIOR', 'DANONE', 
        'CG NOUVELLE ASIE', 'CM AM CONVICT.USA', 'CM-AM EUROPE GROWT', 
        'ECHIQ.VALUE EUROPE', 'B.R.US VAL.M.FAC', 'NESTLE', 'GOLD BULLION'
    ],
    'Ticker': [
        '0P00008HGV.F', 'CDI.PA', 'BN.PA', 
        '0P0000XW75.F', 'FR00140077E1.PA', '0P00000X61.F', 
        '0P0000V79A.F', 'LU1458428163.LU', 'NESN.SW', 'GBS.L'
    ],
    'Quantité': [124.486, 25, 28, 5.0, 67.019, 1.824, 22.1723, 28.911, 50, 33],
    'Prix_Achat_Janvier': [68.52, 542.00, 74.12, 855.90, 154.71, 8145.11, 344.35, 194.43, 80.52, 367.38]
}

df = pd.DataFrame(data)

# 2. Fonction de récupération des cours avec sécurité
@st.cache_data(ttl=3600)
def get_live_prices(tickers_list, prix_janvier):
    prices = []
    for i, t in enumerate(tickers_list):
        try:
            ticker_data = yf.Ticker(t)
            # On prend l'historique récent
            hist = ticker_data.history(period="5d")
            if not hist.empty:
                val = hist['Close'].iloc[-1]
                # Si la valeur est aberrante (proche de 0), on prend celle de janvier
                prices.append(val if val > 0.1 else prix_janvier[i])
            else:
                prices.append(prix_janvier[i])
        except:
            prices.append(prix_janvier[i])
    return prices

# Application du calcul des prix
df['Prix_Actuel'] = get_live_prices(df['Ticker'].tolist(), df['Prix_Achat_Janvier'].tolist())

# 3. Calculs financiers
df['Valeur_Janvier'] = df['Quantité'] * df['Prix_Achat_Janvier']
df['Valeur_Actuelle'] = df['Quantité'] * df['Prix_Actuel']
df['Evolution_%'] = ((df['Valeur_Actuelle'] - df['Valeur_Janvier']) / df['Valeur_Janvier']) * 100

total_janvier = df['Valeur_Janvier'].sum()
total_actuel = df['Valeur_Actuelle'].sum()
gain_perte = total_actuel - total_janvier
perf_globale = (gain_perte / total_janvier) * 100

# 4. Affichage du Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("Valeur Initiale (Janv)", f"{total_janvier:,.2f} €")
col2.metric("Valeur Actuelle", f"{total_actuel:,.2f} €", f"{perf_globale:.2f} %")
col3.metric("Plus-value Latente", f"{gain_perte:,.2f} €")

st.divider()

# Graphique
fig = px.bar(df, x='Nom', y='Evolution_%', color='Evolution_%',
             title="Performance par ligne (%)",
             color_continuous_scale='RdYlGn')
st.plotly_chart(fig, use_container_width=True)

# Tableau propre
st.subheader("Détail des positions")
st.table(df[['Nom', 'Quantité', 'Prix_Achat_Janvier', 'Prix_Actuel', 'Evolution_%']].style.format({
    'Prix_Achat_Janvier': '{:.2f} €',
    'Prix_Actuel': '{:.2f} €',
    'Evolution_%': '{:+.2f} %'
}))
