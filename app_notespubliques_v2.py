
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="Notes Publiques", layout="wide")

st.title("🧠 Veille civique & cartographie structurante")

@st.cache_data
def load_data():
    return pd.read_csv("veille_publique.csv")

@st.cache_data
def load_brief():
    try:
        with open("brief.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Brief non disponible."

df = load_data()
brief_text = load_brief()

# Thème actif détecté automatiquement
def get_theme_actif(data):
    filtres = data[data["Afficher dans l’app ?"] == "Oui"]
    if not filtres.empty:
        return filtres.iloc[0]["Thème"]
    return None

theme_actif = get_theme_actif(df)

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["📄 Veille", "🗺️ Carte", "📊 Visualisation", "📝 Brief"])

with tab1:
    st.subheader("Filtrer par thème")
    all_themes = sorted(df["Thème"].dropna().unique())
    selected_theme = st.selectbox("Choisir un thème :", all_themes, index=all_themes.index(theme_actif) if theme_actif in all_themes else 0)

    filtered_df = df[(df["Afficher dans l’app ?"] == "Oui") & (df["Thème"] == selected_theme)]

    for _, row in filtered_df.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.markdown(f"**Source :** {row['Source']} | **Type :** {row['Type']} | **Date :** {row['Date']}")
        st.markdown(f"**Thème :** {row['Thème']} | **Priorité :** {row['Priorité']} | **Statut :** {row['Statut']}")
        st.markdown(f"_{row['Résumé']}_")
        st.markdown("---")

with tab2:
    st.subheader(f"🗺️ Carte des signaux – Thème : {selected_theme}")
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
                    get_color='[0, 100, 200, 160]',
                    get_radius=8000,
                    pickable=True,
                ),
            ],
            tooltip={"text": "{Titre}\n{Thème}"}
        ))
    else:
        st.info("Aucun point géographique pour ce thème.")

with tab3:
    st.subheader("📊 Nombre de ressources par thème")
    chart_df = df[df["Afficher dans l’app ?"] == "Oui"]
    if not chart_df.empty:
        fig = px.bar(
            chart_df.groupby("Thème").size().reset_index(name="Nombre de ressources"),
            x="Thème", y="Nombre de ressources",
            color="Thème", text="Nombre de ressources",
            title="Répartition des publications par thème"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("📝 Analyse – Brief hebdomadaire")
    st.markdown(brief_text)
