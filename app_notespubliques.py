
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Notes Publiques – Veille & Carto", layout="wide")

st.title("🧠 Veille civique & 🗺️ Cartographie publique")
st.markdown("## Thème en une : Pauvreté, Climat et Inégalités structurelles")

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("veille_publique.csv")

df = load_data()

# Onglets
tab1, tab2 = st.tabs(["📄 Veille publique", "🗺️ Cartographie civique"])

with tab1:
    st.subheader("📌 Ressources publiques filtrées")
    filtres = st.multiselect("Filtrer par thème :", sorted(df["Thème"].dropna().unique()), default=None)
    statut = st.multiselect("Filtrer par statut :", sorted(df["Statut"].dropna().unique()), default=None)
    priorité = st.multiselect("Filtrer par priorité :", sorted(df["Priorité"].dropna().unique()), default=None)

    filtered_df = df[df["Afficher dans l’app ?"] == "Oui"]

    if filtres:
        filtered_df = filtered_df[filtered_df["Thème"].isin(filtres)]
    if statut:
        filtered_df = filtered_df[filtered_df["Statut"].isin(statut)]
    if priorité:
        filtered_df = filtered_df[filtered_df["Priorité"].isin(priorité)]

    for _, row in filtered_df.iterrows():
        st.markdown(f"### [{row['Titre']}]({row['Lien']})")
        st.markdown(f"**Source :** {row['Source']} | **Type :** {row['Type']} | **Date :** {row['Date']}")
        st.markdown(f"**Thème :** {row['Thème']} | **Priorité :** {row['Priorité']} | **Statut :** {row['Statut']}")
        st.markdown(f"_{row['Résumé']}_")
        st.markdown("---")

with tab2:
    st.subheader("🗺️ Cartographie des tensions identifiées")
    carto_df = df[(df["Afficher dans la carto ?"] == "Oui") & (df["Latitude"].notna()) & (df["Longitude"].notna())]
    
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
        st.info("Aucun point cartographique affiché pour le moment.")
