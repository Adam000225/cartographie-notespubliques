import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# --- Chargement des données ---
ris_df = pd.read_csv("ris_communes.csv")
aj_ris_df = pd.read_csv("aj_ris_communes.csv")
neet_df = pd.read_csv("ris_communes_neet.csv")
veille_publique = pd.read_csv("veille_publique_liens_corriges.csv")
veille_aj = pd.read_csv("veille_AJ.csv")
geo_df = gpd.read_file("communes_wallonie.geojson")

with open("edito.md", "r") as f:
    edito = f.read()
with open("bio.md", "r") as f:
    bio = f.read()
with open("faq.md", "r") as f:
    faq = f.read()
with open("brief_2024-04-21_RIS.md", "r") as f:
    brief_ris = f.read()
with open("brief_aj_ris.md", "r") as f:
    brief_aj = f.read()

# --- Fonctions utiles ---
def afficher_veille(df):
    for _, row in df.iterrows():
        st.markdown(f"**{row['Titre']}**\n\n{row['Résumé']}\n\n[Lire le rapport]({row['Lien']})")

def afficher_carte(df, indicateur, titre):
    merged = geo_df.merge(df, left_on="NIS5", right_on="Code NIS")
    fig = px.choropleth_mapbox(
        merged,
        geojson=merged.geometry,
        locations=merged.index,
        color=indicateur,
        mapbox_style="open-street-map",
        zoom=7,
        center={"lat": 50.5, "lon": 4.7},
        opacity=0.5,
        title=titre
    )
    st.plotly_chart(fig)

def graphique_top_bottom(df, indicateur):
    top5 = df.sort_values(by=indicateur, ascending=False).head(5)
    bottom5 = df.sort_values(by=indicateur, ascending=True).head(5)
    combined = pd.concat([top5, bottom5])
    fig = px.bar(combined, x="Commune", y=indicateur, color="Commune", title=f"Top & Flop : {indicateur}")
    st.plotly_chart(fig)

# --- App Streamlit ---
st.set_page_config(layout="wide")
st.title("📊 Notes Publiques")

menu = st.sidebar.selectbox("Choisir un module", ["RIS", "Aide juridique"])

st.markdown(edito)

if menu == "RIS":
    st.header("Carte : Taux de RIS croisé NEET")
    neet_df["Taux croisé"] = neet_df["Taux RIS"] * neet_df["Taux NEET"]
    afficher_carte(neet_df, "Taux croisé", "Communes : Taux RIS x Taux NEET")

    st.header("Graphique comparatif : RIS")
    graphique_top_bottom(ris_df, "Taux RIS")

    st.header("Veille publique : RIS")
    afficher_veille(veille_publique)

    st.header("Brief analytique : RIS")
    st.markdown(brief_ris)

elif menu == "Aide juridique":
    st.header("Carte : Ratio AJ/RIS")
    afficher_carte(aj_ris_df, "Ratio AJ/RIS", "Ratio Aide Juridique / RIS par commune")

    st.header("Graphique comparatif : AJ/RIS")
    graphique_top_bottom(aj_ris_df, "Ratio AJ/RIS")

    st.header("Veille publique : Aide juridique")
    afficher_veille(veille_aj)

    st.header("Brief analytique : Aide juridique")
    st.markdown(brief_aj)

# --- Bio et FAQ ---
st.header("Bio publique")
st.markdown(bio)

st.header("Questions fréquentes")
st.markdown(faq)
