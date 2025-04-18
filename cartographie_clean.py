import streamlit as st
import pandas as pd
import plotly.express as px

# Données simulées
data = {
    "Région / Commune": ["Verviers", "Liège", "Charleroi", "Namur", "Mons"],
    "Non-recours au revenu d'intégration (%)": [28, 25, 30, 22, 27],
    "Délai d'attente logement public (mois)": [72, 65, 80, 60, 70],
    "Non-recours à l'aide juridique (%)": [35, 33, 40, 30, 38],
    "Confiance institutionnelle basse (%)": [52, 48, 60, 45, 55]
}

df = pd.DataFrame(data)

st.title("Cartographie des Effacements Civiques")
st.write("""
Cet outil interactif permet de visualiser des données clés sur le non-recours, 
la confiance civique et l'accès aux droits dans plusieurs villes wallonnes.
""")

# Choix de l'indicateur
indicator = st.selectbox("Choisissez un indicateur à visualiser :", df.columns[1:])

# Graphique
fig = px.bar(df, x="Région / Commune", y=indicator, color="Région / Commune", 
             title=f"{indicator} par commune", labels={indicator: indicator})

st.plotly_chart(fig, use_container_width=True)

# Tableau brut
if st.checkbox("Afficher les données brutes"):
    st.dataframe(df)

st.caption("Sources : ULiège, IWEPS, Unia, KCE, Solidaris, Observatoire de la Santé du Hainaut")
