
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import pydeck as pdk

st.set_page_config(page_title="Notes Publiques – RIS", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("veille_RIS.csv")

@st.cache_data
def load_ris_indicateur():
    return pd.read_csv("ris_communes.csv")

@st.cache_data
def load_edito():
    with open("edito.md", "r", encoding="utf-8") as f:
        return f.read()

@st.cache_data
def load_briefs():
    briefs = []
    for filename in sorted(os.listdir("briefs"), reverse=True):
        if filename.endswith(".md"):
            with open(os.path.join("briefs", filename), "r", encoding="utf-8") as f:
                content = f.read()
            date_str = filename.split("_")[1]
            theme = filename.split("_")[2].replace(".md", "")
            briefs.append({
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
                "theme": theme,
                "content": content
            })
    return briefs

df = load_data()
df_ris = load_ris_indicateur()
edito = load_edito()
briefs = load_briefs()

tabs = st.tabs(["🗣️ Édito", "📄 Veille", "🗺️ Carte", "📊 Graphique", "📝 Brief"])

# Édito
with tabs[0]:
    st.markdown(edito)

# Veille
with tabs[1]:
    st.subheader("🧠 Rapport public de référence")
    for _, row in df.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.markdown(f"**Source :** {row['Source']} | **Type :** {row['Type']} | **Date :** {row['Date']}")
        st.markdown(f"**Résumé :** _{row['Résumé']}_")
        st.markdown("---")

# Carte
with tabs[2]:
    st.subheader("🗺️ Carte des taux RIS par commune (extrait)")
    # Emplacement simulé pour chaque commune (coords approximatives)
    coords = {
        "Verviers": (50.59, 5.85),
        "Charleroi": (50.41, 4.44),
        "Liège": (50.64, 5.57),
        "Namur": (50.46, 4.87),
        "Mons": (50.45, 3.95),
        "Tournai": (50.61, 3.39)
    }
    df_ris["Latitude"] = df_ris["Commune"].map(lambda x: coords[x][0])
    df_ris["Longitude"] = df_ris["Commune"].map(lambda x: coords[x][1])
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=50.5,
            longitude=4.9,
            zoom=7,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df_ris,
                get_position='[Longitude, Latitude]',
                get_color='[255, 0, 0, 160]',
                get_radius=8000,
                pickable=True,
            ),
        ],
        tooltip={"text": "{Commune} : {Taux RIS pour 1000 habitants} / 1000 hab"}
    ))

# Graphique
with tabs[3]:
    st.subheader("📊 Comparaison entre communes")
    fig = px.bar(
        df_ris,
        x="Commune",
        y="Taux RIS pour 1000 habitants",
        text="Taux RIS pour 1000 habitants",
        color="Commune",
        color_discrete_sequence=["#F94144", "#F3722C", "#F9C74F", "#43AA8B", "#577590", "#6A4C93"],
        title="Taux de bénéficiaires du RIS par commune"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Brief
with tabs[4]:
    st.subheader("📝 Brèche hebdo")
    for b in briefs:
        st.markdown(f"### 📌 {b['date'].strftime('%d %B %Y')} – {b['theme'].upper()}")
        st.markdown(b["content"])
        st.markdown("---")
