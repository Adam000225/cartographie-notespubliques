
import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

st.set_page_config(page_title="Notes Publiques – Veille & Carto", layout="wide")

st.title("🧠 Veille civique & 🗺️ Cartographie publique")

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("veille_publique.csv")

df = load_data()

# Détection du thème actif automatiquement
def get_theme_actif(df):
    filtres = df[df["Afficher dans l’app ?"] == "Oui"]
    if not filtres.empty:
        return filtres.iloc[0]["Thème"]
    return None

theme_actif = get_theme_actif(df)

if theme_actif:
    st.markdown(f"## 🎯 Thème en une : {theme_actif}")
else:
    st.markdown("## Aucun thème actif cette semaine")

# Onglets
tab1, tab2 = st.tabs(["📄 Veille publique", "🗺️ Cartographie civique"])

with tab1:
    st.subheader("📊 Répartition des ressources par thème")
    chart_data = df[df["Afficher dans l’app ?"] == "Oui"]
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("Thème:N", sort="-y"),
            y="count():Q",
            color="Thème:N",
            tooltip=["Thème:N", "count():Q"]
        )
        .properties(width=600, height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("📌 Ressources publiques")
    for _, row in chart_data.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.markdown(f"**Source :** {row['Source']} | **Type :** {row['Type']} | **Date :** {row['Date']}")
        st.markdown(f"**Thème :** {row['Thème']} | **Priorité :** {row['Priorité']} | **Statut :** {row['Statut']}")
        st.markdown(f"_{row['Résumé']}_")
        st.markdown("---")

with tab2:
    st.subheader(f"🗺️ Carte des signaux pour le thème : {theme_actif}")
    carto_df = df[
        (df["Afficher dans la carto ?"] == "Oui") &
        (df["Latitude"].notna()) &
        (df["Thème"] == theme_actif)
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
                    get_color='[200, 30, 0, 160]',
                    get_radius=10000,
                    pickable=True,
                ),
            ],
            tooltip={"text": "{Titre}\n{Thème}"}
        ))
    else:
        st.info("Aucun point géographique pour ce thème.")
