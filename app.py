import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("📊 Notes Publiques")

# --- Fonctions robustes de chargement ---
def charger_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        st.warning(f"⚠️ Fichier manquant : {path}")
        return pd.DataFrame()

def charger_md(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    else:
        st.warning(f"⚠️ Fichier manquant : {path}")
        return ""

def charger_geojson(path):
    if os.path.exists(path):
        return gpd.read_file(path)
    else:
        st.warning(f"⚠️ Fichier GeoJSON manquant : {path}")
        return gpd.GeoDataFrame()

# --- Chargement des données ---
ris_df = charger_csv("ris_communes.csv")
aj_ris_df = charger_csv("aj_ris_communes.csv")
neet_df = charger_csv("ris_communes_neet.csv")
veille_publique = charger_csv("veille_publique_liens_corriges.csv")
veille_aj = charger_csv("veille_aj.csv")
geo_df = charger_geojson("communes_wallonie.geojson")

edito = charger_md("edito.md")
bio = charger_md("bio.md")
faq = charger_md("faq.md")
brief_ris = charger_md("brief_2024-04-21_RIS.md")
brief_aj = charger_md("brief_aj_ris.md")

# --- Fonctions d'affichage ---
def afficher_veille(df):
    if df.empty:
        st.info("Aucune veille disponible.")
        return
    for _, row in df.iterrows():
        st.markdown(f"**{row.get('Titre', '')}**\n\n{row.get('Résumé', '')}\n\n[Lire le rapport]({row.get('Lien', '')})")

def afficher_carte(df, indicateur, titre):
    if geo_df.empty or df.empty:
        st.info("Carte non disponible.")
        return
    merged = geo_df.merge(df, left_on="NIS5", right_on="Code NIS", how="inner")
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
    if df.empty:
        st.info("Données insuffisantes pour le graphique.")
        return
    top5 = df.sort_values(by=indicateur, ascending=False).head(5)
    bottom5 = df.sort_values(by=indicateur, ascending=True).head(5)
    combined = pd.concat([top5, bottom5])
    fig = px.bar(combined, x="Commune", y=indicateur, color="Commune", title=f"Top & Flop : {indicateur}")
    st.plotly_chart(fig)

# --- Interface ---
menu = st.sidebar.selectbox("📌 Sélectionne un module", ["RIS seul", "Aide juridique"])

st.markdown(edito)

if menu == "RIS seul":
    st.header("Carte : Taux RIS x NEET")
    if not neet_df.empty:
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
