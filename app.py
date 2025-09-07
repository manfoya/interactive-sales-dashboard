import streamlit as st
import pandas as pd
import plotly.express as px

 # Configuration de la Page
st.set_page_config(
    page_title="Sales Performance Dashboard",
    layout="wide"
)

 # Chargement des Données
@st.cache_data # Cache les données pour de meilleures performances
def load_data(file_path):
    df = pd.read_excel(file_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data('data/global_superstore_2016.xlsx')

 # Barre Latérale (Sidebar) pour les Filtres
st.sidebar.header("Filtres")

region = st.sidebar.multiselect(
    "Sélectionnez la Région :",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

country = st.sidebar.multiselect(
    "Sélectionnez le Pays :",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

category = st.sidebar.multiselect(
    "Sélectionnez la Catégorie :",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

 # Application des Filtres
 # On utilise try-except pour éviter les erreurs si l'utilisateur désélectionne tout
try:
    df_selection = df.query(
        "Region == @region & Country == @country & Category == @category"
    )
except Exception as e:
    st.error("Veuillez sélectionner au moins une option pour chaque filtre.")
    st.stop() # Arrête l'exécution du script si les filtres sont vides

 # Page Principale
st.title("Sales Performance Dashboard")
st.markdown("")

 # Indicateurs Clés de Performance (KPIs)
total_sales = int(df_selection["Sales"].sum())
total_profit = int(df_selection["Profit"].sum())

left_kpi, middle_kpi, right_kpi = st.columns(3)
with left_kpi:
    st.subheader("Ventes Totales :")
    st.subheader(f"US $ {total_sales:,}")
with middle_kpi:
    st.subheader("Profit Total :")
    st.subheader(f"US $ {total_profit:,}")
with right_kpi:
    st.subheader("Marge de Profit Moyenne :")
    if total_sales > 0:
        profit_margin = (total_profit / total_sales) * 100
        st.subheader(f"{profit_margin:.2f} %")
    else:
        st.subheader("N/A")

st.markdown("")

 # Organisation des Graphiques en Colonnes
left_chart, right_chart = st.columns(2)

 # Graphique 1 : Évolution des Ventes dans le Temps
with left_chart:
    # On regroupe par mois pour un graphique plus lisible
    df_selection['Month'] = df_selection['Order Date'].dt.to_period('M').astype(str)
    sales_by_month = df_selection.groupby('Month')['Sales'].sum().reset_index()
    
    fig_sales_by_date = px.line(
        sales_by_month,
        x="Month",
        y="Sales",
        title="<b>Évolution des Ventes par Mois</b>",
        template="plotly_white"
    )
    fig_sales_by_date.update_xaxes(tickangle=45)
    st.plotly_chart(fig_sales_by_date, use_container_width=True)

 # Graphique 2 : Ventes par Sous-Catégorie de Produit
with right_chart:
    # On utilise la sous-catégorie pour plus de détails
    sales_by_subcategory = df_selection.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=True)
    fig_sales_by_subcategory = px.bar(
        sales_by_subcategory,
        x=sales_by_subcategory.values,
        y=sales_by_subcategory.index,
        orientation='h',
        title="<b>Ventes par Sous-Catégorie</b>",
        template="plotly_white",
        labels={'x': 'Ventes', 'y': 'Sous-Catégorie'}
    )
    st.plotly_chart(fig_sales_by_subcategory, use_container_width=True)

 # Affichage des données filtrées dans un expander
with st.expander("Voir les Données Détaillées"):
    st.dataframe(df_selection)