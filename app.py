
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Notes Civiques", layout="wide")

@st.cache_data
def charger_md(nom_fichier):
    try:
        with open(nom_fichier, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

@st.cache_data
def charger_donnees():
    try:
        ris = pd.read_csv("data/ris_communes.csv")
        logement = pd.read_csv("data/logements_inoccupes.csv")
        sante = pd.read_csv("data/medecins_par_commune.csv")
        geo = gpd.read_file("data/communes_wallonie.geojson")
        return ris, logement, sante, geo
    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return None, None, None, None

ris_df, logement_df, sante_df, geo_df = charger_donnees()

st.title("Notes Civiques")
st.markdown("Une application civique modulaire pour révéler les tensions invisibles")
modules = ["Module 1 : RIS x Logement", "Module 2 : RIS x Santé"]
choix = st.selectbox("Choisis un module", modules)

if choix == modules[0] and ris_df is not None:
    st.header("Carte : Score RIS x Logements publics inoccupés")
    data = pd.merge(ris_df, logement_df, on="Commune")
    data["Score croisé"] = data["Taux RIS"] * data["Taux logements vides"]
    geo = geo_df.merge(data, left_on="NOM_COMM", right_on="Commune")
    fig = px.choropleth(geo,
                        geojson=geo.geometry,
                        locations=geo.index,
                        color="Score croisé",
                        hover_name="Commune",
                        projection="mercator")
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Graphique comparatif")
    fig_bar = px.bar(data.sort_values("Score croisé", ascending=False).head(10),
                     x="Commune", y="Score croisé", color="Score croisé",
                     color_continuous_scale="Reds")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Brief analytique")
    st.markdown(charger_md("brief_2024-04-21_RIS.md"))

elif choix == modules[1] and ris_df is not None:
    st.header("Carte : Score RIS x Densité médicale inverse")
    data = pd.merge(ris_df, sante_df, on="Commune")
    data["Score croisé"] = data["Taux RIS"] * (1 / data["Densité médecins"])
    geo = geo_df.merge(data, left_on="NOM_COMM", right_on="Commune")
    fig = px.choropleth(geo,
                        geojson=geo.geometry,
                        locations=geo.index,
                        color="Score croisé",
                        hover_name="Commune",
                        projection="mercator")
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Graphique comparatif")
    fig_bar = px.bar(data.sort_values("Score croisé", ascending=False).head(10),
                     x="Commune", y="Score croisé", color="Score croisé",
                     color_continuous_scale="Reds")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Brief analytique")
    st.markdown(charger_md("brief_sante.md"))

st.sidebar.markdown("## À propos")
st.sidebar.markdown(charger_md("bio.md"))

st.markdown("---")
st.markdown("## Questions fréquentes")
st.markdown(charger_md("faq.md"))
