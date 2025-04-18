
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="Notes Publiques", layout="wide")

# Charger les données principales
@st.cache_data
def load_data():
    return pd.read_csv("veille_publique_liens_corriges.csv")

@st.cache_data
def load_edito():
    with open("edito.md", "r", encoding="utf-8") as f:
        return f.read()

@st.cache_data
def load_briefs():
    briefs = []
    briefs_dir = "briefs"
    for filename in sorted(os.listdir(briefs_dir), reverse=True):
        if filename.endswith(".md"):
            with open(os.path.join(briefs_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
            date_str = filename.split("_")[1]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            theme = filename.split("_")[2].replace(".md", "")
            briefs.append({"date": date_obj, "theme": theme, "content": content})
    return briefs

df = load_data()
edito = load_edito()
briefs = load_briefs()

# Onglets
tabs = st.tabs(["🗣️ Édito", "📄 Veille", "🗺️ Carte", "📊 Visualisation", "📝 Briefs"])

# Onglet Édito
with tabs[0]:
    st.markdown(edito)

# Onglet Veille
with tabs[1]:
    st.subheader("Filtrer par thème")
    themes = sorted(df["Thème"].dropna().unique())
    selected_theme = st.selectbox("Choisir un thème :", themes)

    filtered = df[(df["Afficher dans l’app ?"] == "Oui") & (df["Thème"] == selected_theme)]

    for _, row in filtered.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.markdown(f"**Source :** {row['Source']} | **Type :** {row['Type']} | **Date :** {row['Date']}")
        st.markdown(f"**Thème :** {row['Thème']} | **Priorité :** {row['Priorité']} | **Statut :** {row['Statut']}")
        st.markdown(f"_{row['Résumé']}_")
        st.markdown("---")

# Onglet Carte (points géographiques uniquement)
with tabs[2]:
    st.subheader(f"🗺️ Carte des signaux géographiques – Thème : {selected_theme}")
    try:
        import pydeck as pdk
        carto_df = df[
            (df["Afficher dans la carto ?"] == "Oui") &
            (df["Latitude"].notna()) &
            (df["Thème"] == selected_theme)
        ]
        if not carto_df.empty:
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=carto_df["Latitude"].mean(),
                    longitude=carto_df["Longitude"].mean(),
                    zoom=7,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=carto_df,
                        get_position='[Longitude, Latitude]',
                        get_color='[255, 100, 100, 160]',
                        get_radius=8000,
                        pickable=True,
                    ),
                ],
                tooltip={"text": "{Titre}\n{Thème}"}
            ))
        else:
            st.info("Aucun point géographique pour ce thème.")
    except Exception as e:
        st.error("Erreur d'affichage de la carte : " + str(e))

# Onglet Visualisation
with tabs[3]:
    st.subheader("📊 Comparaison par commune")
    # Exemple de graphique à barres stylisé
    graph_data = {
        "Commune": ["Verviers", "Liège", "Charleroi", "Namur", "Mons"],
        "Taux RIS (pour 1000 hab.)": [38.5, 41.3, 45.2, 28.7, 40.1]
    }
    gdf = pd.DataFrame(graph_data)

    fig = px.bar(
        gdf,
        x="Commune",
        y="Taux RIS (pour 1000 hab.)",
        text="Taux RIS (pour 1000 hab.)",
        color="Commune",
        color_discrete_sequence=["#F94144", "#F3722C", "#F9C74F", "#43AA8B", "#577590"],
        title="Taux de bénéficiaires du revenu d’intégration par commune"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    st.plotly_chart(fig, use_container_width=True)

# Onglet Briefs
with tabs[4]:
    st.subheader("📝 Archives des briefs hebdomadaires")
    for b in briefs:
        st.markdown(f"### 📌 {b['date'].strftime('%d %B %Y')} – {b['theme'].capitalize()}")
        st.markdown(b["content"])
        st.markdown("---")
