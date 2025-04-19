import streamlit as st
st.set_page_config(page_title="Notes Publiques", layout="wide")

import pandas as pd
import geopandas as gpd
import plotly.express as px
import os

# --- Chargement robuste des fichiers ---
def charger_csv(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.warning(f"Fichier manquant : {path}")
        return pd.DataFrame()

def charger_md(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Fichier introuvable : {path}"

def charger_geojson(path):
    try:
        return gpd.read_file(path)
    except Exception as e:
        st.error(f"Erreur de chargement GeoJSON : {e}")
        return gpd.GeoDataFrame()

# --- Données ---
ris_df = charger_csv("ris_communes.csv")
aj_df = charger_csv("aj_ris_communes.csv")
neet_df = charger_csv("ris_communes_neet_updated.csv")
veille_publique = charger_csv("veille_publique_liens_corriges.csv")
veille_aj = charger_csv("veille_aj.csv")
geo_df = charger_geojson("communes_wallonie.geojson")

# --- Textes ---
edito = charger_md("edito.md")
bio = charger_md("bio.md")
faq = charger_md("faq.md")
brief_ris = charger_md("brief_2024-04-21_RIS.md")
brief_aj = charger_md("brief_aj_ris.md")

# --- Interface ---
st.title("Notes Publiques")

modules = {
    "RIS seul": {
        "veille": veille_publique,
        "brief": brief_ris,
        "df": ris_df,
        "carte": neet_df,
        "geo": geo_df,
        "graph": "Taux RIS",
    },
    "Aide juridique": {
        "veille": veille_aj,
        "brief": brief_aj,
        "df": aj_df,
        "carte": aj_df,
        "geo": geo_df,
        "graph": "Ratio AJ/RIS",
    },
}

module_selection = st.sidebar.selectbox("\ud83d\udccc Sélectionne un module", list(modules.keys()))
st.markdown(f"### \ud83d\udd39 Module actif : {module_selection}")

mod = modules[module_selection]

# --- Edito ---
with st.expander("\ud83d\udcd6 Lire l’édito", expanded=True):
    st.markdown(edito)

# --- Carte ---
st.subheader("\ud83d\udcca Carte thématique")
if not mod["carte"].empty and not mod["geo"].empty:
    carte = mod["carte"].merge(mod["geo"], on="Code NIS", how="left")
    gdf = gpd.GeoDataFrame(carte)
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=mod["graph"],
        mapbox_style="carto-positron",
        zoom=7, center={"lat": 50.5, "lon": 4.7},
        opacity=0.6,
        hover_name="Commune",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Carte non disponible.")

# --- Graphique ---
st.subheader("\ud83d\udcca Graphique comparatif")
if mod["df"].empty is False:
    df_sorted = mod["df"].sort_values(mod["graph"], ascending=False)
    top_bottom = pd.concat([df_sorted.head(5), df_sorted.tail(5)])
    fig_bar = px.bar(top_bottom, x="Commune", y=mod["graph"], color="Commune")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Veille ---
st.subheader("\ud83d\udd0d Veille publique")
if not mod["veille"].empty:
    for _, row in mod["veille"].iterrows():
        st.markdown(f"- **[{row['Titre']}]({row['Lien']})**\n    > {row['Résumé']}")
else:
    st.info("Aucune veille disponible.")

# --- Brief ---
st.subheader("\ud83d\udcd1 Brief analytique")
st.markdown(mod["brief"])

# --- Bas de page ---
st.divider()
st.markdown("### \ud83d\udc64 Bio publique")
st.markdown(bio)

st.markdown("### \ud83d\udcc4 FAQ")
st.markdown(faq)

# --- Diagnostic ---
st.sidebar.markdown("### \ud83d\udd27 Diagnostic modules")
for nom, infos in modules.items():
    st.sidebar.markdown(f"- **{nom}** : ")
    if infos["df"].empty:
        st.sidebar.markdown(f"  - ❌ Données principales manquantes")
    else:
        st.sidebar.markdown(f"  - ✅ Données principales OK")
    if infos["carte"].empty:
        st.sidebar.markdown(f"  - ❌ Données carte manquantes")
    else:
        st.sidebar.markdown(f"  - ✅ Données carte OK")
    if infos["veille"].empty:
        st.sidebar.markdown(f"  - ❌ Veille vide")
    else:
        st.sidebar.markdown(f"  - ✅ Veille OK")
    st.sidebar.markdown("---")
