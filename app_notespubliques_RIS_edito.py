
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Notes Publiques – RIS", layout="wide")

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("ris_communes.csv")

df = load_data()

# Interface avec onglet édito inclus
tab0, tab1, tab2, tab3, tab4 = st.tabs(["Édito", "Veille", "Carte", "Graphique", "Brief"])

# Onglet 0 – Édito
with tab0:
    st.header("🪧 Pourquoi cette carte civique ?")
    with open("edito.md", "r") as f:
        st.markdown(f.read())

# Onglet 1 – Veille
with tab1:
    st.header("📚 Veille publique")
    veille = pd.read_csv("veille_publique_liens_corriges.csv")
    for i, row in veille.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.write(row["Résumé"])

# Onglet 2 – Carte
with tab2:
    st.header("🗺️ Carte du taux de RIS par commune")
    fig = px.choropleth(df,
                        locations="Code NIS",
                        geojson="https://raw.githubusercontent.com/BelgianOpenData/belgian-municipalities-geojson/main/geojson/municipalities.geojson",
                        color="Taux RIS",
                        hover_name="Commune",
                        color_continuous_scale="Reds",
                        featureidkey="properties.NISCODE")
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

# Onglet 3 – Graphique
with tab3:
    st.header("📊 Visualisation comparative")
    bar = px.bar(df.sort_values("Taux RIS", ascending=False),
                 x="Commune", y="Taux RIS",
                 color="Taux RIS", color_continuous_scale="Reds")
    bar.update_layout(xaxis_title=None, yaxis_title="Taux RIS (%)")
    st.plotly_chart(bar, use_container_width=True)

# Onglet 4 – Brief
with tab4:
    st.header("📝 Brief hebdomadaire")
    with open("brief_2024-04-21_RIS.md", "r") as f:
        st.markdown(f.read())
