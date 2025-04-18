
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Chargement des données
@st.cache_data
def load_data():
    veille = pd.read_csv("veille_AJ.csv")
    points = pd.read_csv("points_AJ.csv")
    return veille, points

# Chargement du brief
@st.cache_data
def load_brief():
    try:
        with open("briefs/brief_2024-04-22_AJ.md", "r") as f:
            return f.read()
    except:
        return "Brief non disponible."

# Chargement de l'onglet About
@st.cache_data
def load_about():
    try:
        with open("about.md", "r") as f:
            return f.read()
    except:
        return "À propos non disponible."

# Données
veille, points = load_data()

# Onglets
st.set_page_config(layout="wide")
tabs = st.tabs(["📌 Veille", "🗺 Carte", "📊 Visualisation", "📝 Brief", "ℹ️ About"])

# Onglet Veille
with tabs[0]:
    st.title("Veille - Accès à l’aide juridique")
    st.dataframe(veille[["Titre", "Source", "Date", "Résumé", "Lien"]])

# Onglet Carte
with tabs[1]:
    st.title("Carte des points d’accès à l’aide juridique")
    fig = px.scatter_mapbox(
        points,
        lat="Latitude",
        lon="Longitude",
        hover_name="Commune",
        hover_data=["Type"],
        color="Type",
        zoom=7,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

# Onglet Visualisation
with tabs[2]:
    st.title("Répartition des points par type")
    st.bar_chart(points["Type"].value_counts())

# Onglet Brief
with tabs[3]:
    st.title("Brèche hebdo – Aide juridique")
    st.markdown(load_brief())

# Onglet About
with tabs[4]:
    st.title("À propos")
    st.markdown(load_about())
