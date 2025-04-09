import pandas as pd
import streamlit as st
import preprocessor
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

df=pd.read_csv("clean_crime_district.csv")


# Main Streamlit application
st.set_page_config(page_title="crime anaylsis", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .custom-subheader {
        color:#228B22 ;
        font-size: 35px;
        font-weight: 600;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .custom-subheader {
        font-size: 35px;
        font-weight: bold;
        color: #FFBF00;
        margin-bottom: 20px;
    }
    </style>
    <div class='custom-subheader'>Crime prediction analysis dashboard</div>
    """, unsafe_allow_html=True)


st.markdown(
    """
    <p style='color:#00BFFF; font-size:20px;font-weight: bold;'>
        Lung cancer prediction involves identifying individuals at risk using clinical and lifestyle data.
        Machine learning models assist in early detection, enabling timely diagnosis and intervention.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")


# Load the logo image
logo = Image.open("logo.jpg")  # Replace with the path to your logo file

# Display the logo at the top of the sidebar
st.sidebar.image (logo, use_container_width=True)  # Updated parameter
st.sidebar.header("Filter Options")

# Gender Filter
if st.sidebar.checkbox("Select state", value=True):
    state_filter = df["STATE/UT"].unique()
else:
    state_filter = st.sidebar.multiselect(
        "Select state",
        options=df["STATE/UT"].unique(),
        default=[]  # Start with no selection when "Select All" is unchecked
    )


if st.sidebar.checkbox("Select District", value=True):
    district_filter = df["DISTRICT"].unique()
else:
    district_filter = st.sidebar.multiselect(
        "Select district",
        options=df["DISTRICT"].unique(),
        default=[]  # Start with no selection when "Select All" is unchecked
    )

# Year Range Filter
Year_filter = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(int(df["Year"].min()), int(df["Year"].max()))
)


# Apply Filters
filtered_df = df[
    (df["STATE/UT"].isin(state_filter)) &
    (df["DISTRICT"].isin(district_filter)) &
    (df["Year"].isin(Year_filter))
]


# Create a single row for KPIs
col1, col2, col3 ,col4= st.columns(4)
# Apply filters
# KPI Calculations on filtered data
total_crimes = filtered_df['Total Crimes'].sum()
avg_crimes_district = filtered_df.groupby('DISTRICT')['Total Crimes'].sum().mean()
state_crime_totals = filtered_df.groupby('STATE/UT')['Total Crimes'].sum()
if not state_crime_totals.empty:
    state_max_crime = state_crime_totals.idxmax()
    state_max_value = state_crime_totals.max()
else:
    state_max_crime = 'N/A'
    state_max_value = 0

# Inject KPI styling
st.markdown("""
    <style>
    .kpi-container {
        font-size: 10px;
        font-weight: bold;
        color: #2c3e50;
        padding: 10px;
        border-radius: 10px;
        background-color: #f1f1f1;
        text-align: center;
    }
    .kpi-value {
        font-size: 20px;
        color: #e74c3c;
    }
    </style>
""", unsafe_allow_html=True)

# Show KPIs
col1, col2, col3,col4 = st.columns(4)

with col1:
    st.markdown(
        f'<div class="kpi-container">Total Crimes<br><span class="kpi-value">{total_crimes:,}</span></div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="kpi-container">Avg Crimes/District<br><span class="kpi-value">{avg_crimes_district:.0f}</span></div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'<div class="kpi-container">Top Crime State<br><span class="kpi-value">{state_max_crime} ({state_max_value:,})</span></div>',
        unsafe_allow_html=True
    )



#####################1

# Group and get top 10 districts with highest murders
murder_df = (
    df.groupby("DISTRICT")["Murder"]  # <- use df instead of filtered_df
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .head(10)
)

# Section title
st.markdown(
    "<h3 style='color:#8E44AD; font-size:28px;'>🔫 Top 10 Districts by Murder Count (Static View)</h3>",
    unsafe_allow_html=True
)

# Plotly horizontal bar chart
fig = px.bar(
    murder_df,
    x="Murder",
    y="DISTRICT",
    orientation="h",
    color="Murder",
    color_continuous_scale="Reds",
    labels={"Murder": "Total Murders", "DISTRICT": "District"},
)

# Layout styling
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor='lightgrey'),
    yaxis_title=None,
    xaxis_title="Total Murders"
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

############################2



# Group and sort total crimes per state from filtered data
state_crime_totals = (
    filtered_df.groupby('STATE/UT')['Total Crimes']
    .sum()
    .sort_values(ascending=True)
    .reset_index()
)
fig = px.bar(
    state_crime_totals,
    x='STATE/UT',
    y='Total Crimes',
    color='Total Crimes',
    color_continuous_scale='Viridis',
    title='📊 Bar Chart: Total Crimes by State/UT'
)
fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
st.plotly_chart(fig, use_container_width=True)


############################3

# Crime types to visualize
crime_types = ['Murder', 'Assault on women', 'Kidnapping and Abduction', 'Robbery', 'Hurt']

# Sidebar or Main Section Dropdown to select a specific crime
selected_crime = st.selectbox("🔍 Select a Crime Type to View Its Yearly Trend", crime_types)

# Ensure numeric conversion for consistency
filtered_df[crime_types] = filtered_df[crime_types].apply(pd.to_numeric, errors='coerce')

# Group data by year
trend_df = filtered_df.groupby("Year")[crime_types].sum().reset_index()

# Section Title
st.markdown(
    "<h3 style='color:#8E44AD; font-size:28px;'>📈 Yearly Trend of Selected Crime Type</h3>",
    unsafe_allow_html=True
)

# Plotly line chart for selected crime
fig = px.line(
    trend_df,
    x="Year",
    y=selected_crime,
    markers=True,
    title=f"📊 Yearly Trend of {selected_crime}",
    labels={"Year": "Year", selected_crime: "Number of Crimes"},
    template="plotly_white",
    line_shape="spline",
)

# Update layout for better visuals
fig.update_traces(line=dict(width=3), marker=dict(size=7))
fig.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor='lightgrey'),
    yaxis=dict(showgrid=True, gridcolor='lightgrey'),
    font=dict(family="Arial", size=12, color="#2C3E50")
)

# Show in Streamlit
st.plotly_chart(fig, use_container_width=True)


##########################4

# Group by year and sum POA and PCR crimes
act_trend = df.groupby('Year')[['Prevention of atrocities (POA) Act', 'Protection of Civil Rights (PCR) Act']].sum().reset_index()

# Melt the dataframe for Plotly
act_trend_melted = act_trend.melt(id_vars='Year', var_name='Crime Type', value_name='Number of Cases')

# Streamlit Section Title
st.markdown(
    "<h3 style='color:#8E44AD; font-size:28px;'>📊 Crimes Under POA & PCR Acts (Stacked Bar)</h3>",
    unsafe_allow_html=True
)

# Plotly stacked bar chart
fig = px.bar(
    act_trend_melted,
    x='Year',
    y='Number of Cases',
    color='Crime Type',
    title='Year-wise Trends of POA & PCR Cases',
    labels={'Number of Cases': 'Number of Cases', 'Year': 'Year'},
    color_discrete_map={
        'Prevention of atrocities (POA) Act': 'crimson',
        'Protection of Civil Rights (PCR) Act': 'darkblue'
    }
)

# Update layout
fig.update_layout(
    barmode='stack',
    title_x=0.5,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='lightgrey'),
    yaxis=dict(showgrid=True, gridcolor='lightgrey'),
    font=dict(size=12, color='#2C3E50')
)

# Show in Streamlit
st.plotly_chart(fig, use_container_width=True)

