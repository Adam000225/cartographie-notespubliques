
import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Notes Publiques – Modules comparés", layout="wide")

@st.cache_data
def load_data_ris():
    return pd.read_csv("ris_communes_neet.csv")

@st.cache_data
def load_data_croisee():
    return pd.read_csv("aj_ris_communes.csv")

@st.cache_resource
def load_geojson():
    with open("communes_wallonie.geojson", "r") as f:
        return json.load(f)

geojson = load_geojson()

module = st.selectbox("📌 Sélectionne un module", ["RIS seul", "AJ vs RIS (croisé)"])

if module == "RIS seul":
    df = load_data_ris()
    st.title("🧭 Module RIS – Accès au Revenu d’Intégration Sociale")
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["Édito", "Veille", "Carte", "Graphique", "Brief"])

    with tab0:
        st.header("🪧 Pourquoi cette carte civique ?")
        with open("edito.md", "r") as f:
            st.markdown(f.read())

    with tab1:
        st.header("📚 Veille publique")
        veille = pd.read_csv("veille_publique_liens_corriges.csv")
        for i, row in veille.iterrows():
            st.markdown(f"### [{row['Titre']}]({row['Lien']})")
            st.write(row["Résumé"])

    with tab2:
        st.header("🗺️ Carte du taux de RIS par commune")
        fig = px.choropleth(df,
                            geojson=geojson,
                            locations="Code NIS",
                            color="Taux RIS",
                            hover_name="Commune",
                            color_continuous_scale="Reds",
                            featureidkey="properties.NISCODE")
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("📊 Visualisation comparative")
        bar = px.bar(df.sort_values("Taux RIS", ascending=False),
                     x="Commune", y="Taux RIS",
                     color="Taux RIS", color_continuous_scale="Reds")
        bar.update_layout(xaxis_title=None, yaxis_title="Taux RIS (%)")
        st.plotly_chart(bar, use_container_width=True)

    with tab4:
        st.header("📝 Brief hebdomadaire")
        with open("brief_2024-04-21_RIS.md", "r") as f:
            st.markdown(f.read())

elif module == "AJ vs RIS (croisé)":
    df = load_data_croisee()
    st.title("⚖️ Module croisé – Aide juridique et RIS")
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["Édito", "Données", "Carte", "Graphique", "Brief"])

    with tab0:
        st.header("🪧 Pourquoi ce module AJ + RIS ?")
        st.markdown("Ce module croise deux indicateurs structurels : l’accès à l’aide juridique et le taux de RIS.                     Il permet de visualiser les écarts entre vulnérabilité économique et accès effectif aux droits.")

    with tab1:
        st.header("📋 Données comparées")
        st.dataframe(df)

    with tab2:
        st.header("🗺️ Carte du ratio AJ/RIS")
        fig = px.choropleth(df,
                            geojson=geojson,
                            locations="Code NIS",
                            color="Ratio AJ/RIS",
                            hover_name="Commune",
                            color_continuous_scale="Purples",
                            featureidkey="properties.NISCODE")
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("📊 Comparaison AJ vs RIS")
        fig = px.bar(df.sort_values("Taux RIS", ascending=False),
                     x="Commune",
                     y=["Taux RIS", "Taux AJ"],
                     barmode="group")
        fig.update_layout(yaxis_title="Taux (%)")
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("📝 Brief croisé")
        with open("brief_aj_ris.md", "r") as f:
            st.markdown(f.read())
