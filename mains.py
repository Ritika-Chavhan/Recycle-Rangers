import pandas as pd
import streamlit as st
import preprocessor
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import geopandas as gpd

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
    <div class='custom-subheader'>🔍 Crime Prediction Analysis Dashboard</div>
    """, unsafe_allow_html=True)


st.markdown(
    """
    <p style='color: #f1f1f1; font-size:20px;'>
       This project is about creating an interactive dashboard that shows crime data for different districts across Indian states. The main aim is to find patterns, trends, and connections between different types of crimes over the years. This can help the police, government, and decision-makers take better actions to prevent crimes and keep people safe.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")


# Load the logo image
logo = Image.open("crime logo.png")  # Replace with the path to your logo file

# Display the logo at the top of the sidebar
st.sidebar.image (logo, use_container_width=True)  # Updated parameter
st.sidebar.header("Filter Options")



# District Filter
# Sidebar Filters

# District Filter
if st.sidebar.checkbox("Select All Districts", value=True):
    district_filter = df["DISTRICT"].unique()
else:
    district_filter = st.sidebar.multiselect(
        "Select District",
        options=df["DISTRICT"].unique(),
        default=[]
    )

# State Filter
if st.sidebar.checkbox("Select All States", value=True):
    state_filter = df["STATE/UT"].unique()
else:
    state_filter = st.sidebar.multiselect(
        "Select State",
        options=df["STATE/UT"].unique(),
        default=[]
    )

# Year Range Filter
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(int(df["Year"].min()), int(df["Year"].max()))
)

# Apply Filters
filtered_df = df[
    (df["DISTRICT"].isin(district_filter)) &
    (df["STATE/UT"].isin(state_filter)) &
    (df["Year"].between(year_range[0], year_range[1]))
]


# Create a single row for KPIs
col1, col2, col3 = st.columns(3)
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
# Inject KPI styling with increased size
st.markdown("""
    <style>
    .kpi-container {
        font-size: 20px;
        font-weight: bold;
        color: #f1f1f1;
        padding: 10px 10px;
        border-radius: 20px;
        background-color:#DAA520;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
        margin-top: 30px;
    }
    .kpi-value {
        font-size: 28px;
        color: #e74c3c;
        font-weight: 700;
        display: block;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# Show KPIs
col1, col2, col3 = st.columns(3)

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
# Section Heading
st.markdown("<h3 style='color:#FFBF00;'>Top 10 Districts by Murder Count</h3>", unsafe_allow_html=True)

top_murder_df = (
    filtered_df.groupby("DISTRICT")["Murder"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .head(10)
)
# Plotly Bar Chart
fig = px.bar(
    top_murder_df,
    x="Murder",
    y="DISTRICT",
    orientation="h",
    color="Murder",
    color_continuous_scale="Reds",
    labels={"Murder": "Total Murders", "DISTRICT": "District"},
    height=500
)

# Styled Layout with axis color customization
fig.update_layout(
   yaxis=dict(
    autorange="reversed",
    tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
    titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
),
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgrey',
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#2c3e50",family="Arial Bold", size=14)  # General font (used if specific not defined)
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    <div style='font-size:20px;'>
        Summary:
       The visualization displays the top 10 districts ranked by the number of murder cases reported, allowing for quick identification of regions with the highest incidence of this crime.  </div>
    """,
    unsafe_allow_html=True
)

st.write("---")





############################2
# Section Heading instead of using chart title
st.markdown("<h3 style='color:#FFBF00;'>📊 Total Crimes by State/UT</h3>", unsafe_allow_html=True)

# Correct: filter only on selected states and year range
state_crime_totals = (
    df[df["STATE/UT"].isin(state_filter) & df["Year"].between(year_range[0], year_range[1])]
    .groupby("STATE/UT")["Total Crimes"]
    .sum()
    .sort_values(ascending=True)
    .reset_index()
)

# Plotly Bar Chart
if state_crime_totals.empty:
    st.warning("No data available for the selected filters.")
else:
    fig = px.bar(
        state_crime_totals,
        x='STATE/UT',
        y='Total Crimes',
        color='Total Crimes',
        color_continuous_scale='Viridis',
        labels={'STATE/UT': 'State/UT', 'Total Crimes': 'Total Crimes'},
        height=500
    )

    # Update layout with axis styling and other customizations
    fig.update_layout(
        xaxis=dict(
            tickangle=-45,
            showgrid=True,
            gridcolor='lightgrey',
            tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
            titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
        ),
        yaxis=dict(
            tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
            titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2c3e50", family="Arial Bold", size=14)
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


st.markdown(
    """
    <div style='font-size:20px;'>
        Summary:This  bar chart presents the total number of crimes reported across various States and Union Territories. The data is sorted in ascending order to clearly highlight regions with comparatively lower to higher crime volumes. Each bar represents a state/UT, with exact crime counts labeled for clarity, enabling quick visual comparison across regions
         </div>
    """,
    unsafe_allow_html=True
)
st.write("---")






############################3

st.markdown(
    f"<h3 style='color:#FFBF00;'>📈Cases Over the Years</h3>",
    unsafe_allow_html=True
)
# Crime types for dropdown
crime_types = ['Murder', 'Assault on women', 'Kidnapping and Abduction', 'Robbery', 'Hurt']

# Ensure numeric values
filtered_df[crime_types] = filtered_df[crime_types].apply(pd.to_numeric, errors='coerce')


# Styled Dropdown Heading
st.markdown("<h4 style='font-size:20px; font-weight:bold; font-family:Arial;'>🔍 Select a Crime Type</h4>", unsafe_allow_html=True)

# Dropdown for crime type selection
selected_crime = st.selectbox("", crime_types)

# Group by Year and sum for selected crime
trend_df = filtered_df.groupby("Year")[[selected_crime]].sum().reset_index()

# Line chart
fig = px.line(
    trend_df,
    x="Year",
    y=selected_crime,
    title=None,
    markers=True,
    labels={"Year": "Year", selected_crime: "Cases"},
    template="simple_white",
    color_discrete_sequence=["#FF6347"]  # Optional line color
)
# Update layout with axis styling and other customizations
fig.update_layout(
    xaxis=dict(
        tickangle=-45,
        showgrid=True,
        gridcolor='lightgrey',
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    yaxis=dict(
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#2c3e50", family="Arial Bold", size=14)
)
# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    <div style='font-size:20px;'>
        Summary:This line chart visualizes the trend of selected crime types over the years. Users can choose a specific crime (e.g., Murder, Robbery, etc.) from the dropdown, and the graph dynamically updates to display how the number of reported cases has changed annually. This helps identify rising or declining patterns in criminal activity over time.
         </div>
    """,
    unsafe_allow_html=True
)
st.write("---")








##############################4

# Acts to analyze
acts = ['Prevention of atrocities (POA) Act', 'Protection of Civil Rights (PCR) Act']
filtered_df[acts] = filtered_df[acts].apply(pd.to_numeric, errors='coerce')

# Prepare filtered data
act_trend = (
    filtered_df.groupby('Year')[acts]
    .sum()
    .reset_index()
    .melt(id_vars='Year', var_name='Crime Type', value_name='Number of Cases')
)

# Group by Crime Type for total across selected years
act_summary = act_trend.groupby('Crime Type')['Number of Cases'].sum().reset_index()

# Section Title
st.markdown(
    "<h3 style='color:#FFBF00; font-size:26px;'>📊 POA & PCR Bar Chart by Year Range</h3>",
    unsafe_allow_html=True
)

# Plot
fig = px.bar(
    act_summary,
    x='Crime Type',
    y='Number of Cases',
    color='Crime Type',
    labels={'Number of Cases': 'Number of Cases', 'Crime Type': 'Crime Type'},
    color_discrete_map={
        'Prevention of atrocities (POA) Act': '#000080',
        'Protection of Civil Rights (PCR) Act': '#FF7F50'
    },
    height=500
)
# Update layout with axis styling and other customizations
fig.update_layout(
    xaxis=dict(
        gridcolor='lightgrey',
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    yaxis=dict(
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#2c3e50", family="Arial Bold", size=14)
)
# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)



st.markdown(
    """
    <div style='font-size:20px;'>
        This bar chart compares the total number of cases reported under the Prevention of Atrocities (POA) Act and the Protection of Civil Rights (PCR) Act across all years. It provides a clear visual summary of how frequently each act has been invoked, offering insights into trends related to caste-based discrimination and civil rights violations.
         </div>
    """,
    unsafe_allow_html=True
)
st.write("---")





##################5

# Group by state and sum murders
state_murder_df = df.groupby('STATE/UT')['Murder'].sum().sort_values(ascending=False).head(10).reset_index()

# Section title
st.markdown(
    "<h3 style='color:#FFBF00;'>🩸 Top 10 States/UTs with Highest Murders</h3>",
    unsafe_allow_html=True
)

# Plotly pie chart
fig = px.pie(
    state_murder_df,
    values='Murder',
    names='STATE/UT',
    title='',
    color_discrete_sequence=px.colors.qualitative.Set3,
    hole=0.3  # Makes it a donut-style chart (optional)
)


# Update layout with axis styling and other customizations
fig.update_layout(
    xaxis=dict(
        gridcolor='lightgrey',
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    yaxis=dict(
        tickfont=dict(color="#f1f1f1", family="Arial Bold", size=14),
        titlefont=dict(color="#f1f1f1", family="Arial Bold", size=14)
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#2c3e50", family="Arial Bold", size=14)
)
# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)


st.markdown(
    """
    <div style='font-size:20px;'>
        This donut chart illustrates the top 10 States and Union Territories with the highest number of murder cases reported. It provides a quick visual comparison of murder distribution across regions, helping to identify the most affected states in terms of homicide incidents.
         </div>
    """,
    unsafe_allow_html=True
)
st.write("---")

















############################6
st.markdown(
    "<h3 style='color:#FFBF00;'>🩸 Top 10 States/UTs with Highest Murders</h3>",
    unsafe_allow_html=True
)


# GeoJSON path
geojson_url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'

# Read GeoJSON
gdf = gpd.read_file(geojson_url)
gdf = gdf.rename(columns={"ST_NM": "STATE/UT"})

# Ensure correct types for merging
df['STATE/UT'] = df['STATE/UT'].astype(str)
gdf['STATE/UT'] = gdf['STATE/UT'].astype(str)

years = sorted(df['Year'].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)


# Optional: Add filter by crime category (e.g., Murder, Kidnapping, etc.)
crime_columns = [col for col in df.columns if col not in ['STATE/UT', 'DISTRICT', 'Year']]
selected_crime = st.sidebar.selectbox("Select Crime Type", ['Total Crimes'] + crime_columns)

# Aggregate
state_crimes = filtered_df.groupby('STATE/UT')[selected_crime].sum().reset_index()
state_crimes.rename(columns={selected_crime: 'Crime Value'}, inplace=True)





# Merge with GeoDataFrame
merged = gdf.merge(state_crimes, on='STATE/UT', how='left')
merged['Crime Value'] = merged['Crime Value'].fillna(0)
merged = merged.reset_index()

# Choropleth map
fig = px.choropleth(
    merged,
    geojson=merged.geometry.__geo_interface__,
    locations='index',
    color='Crime Value',
    hover_name='STATE/UT',
    hover_data={'Crime Value': True, 'index': False},
    color_continuous_scale='OrRd',
    range_color=(0, merged['Crime Value'].max()),
    title=f"🗺️ India: {selected_crime} ({selected_year})"
)

fig.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Crimes", thickness=15, len=0.75)
)

# Display map
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# KPI Metrics
col1, col2, col3 = st.columns(3)
with col1:
    max_val = merged['Crime Value'].max()
    st.metric("Highest Crime State",
              value=merged.loc[merged['Crime Value'].idxmax(), 'STATE/UT'],
              delta=f"{int(max_val):,} cases")
with col2:
    non_zero = merged[merged['Crime Value'] > 0]
    if not non_zero.empty:
        min_val = non_zero['Crime Value'].min()
        st.metric("Lowest Crime State",
                  value=non_zero.loc[non_zero['Crime Value'].idxmin(), 'STATE/UT'],
                  delta=f"{int(min_val):,} cases")
with col3:
    st.metric("National Total",
              value=f"{int(merged['Crime Value'].sum()):,}",
              delta=f"{merged['Crime Value'].astype(bool).sum()} states reported crimes")




st.markdown(
    """
    <div style='font-size:20px;'>
       This interactive choropleth map visualizes the distribution of a selected crime type across Indian States and Union Territories for a chosen year. Users can filter by both year and specific crime categories (e.g., Murder, Kidnapping, etc.) via the sidebar. The darker shades indicate higher reported cases, allowing for a quick comparison of crime intensity across regions.
         </div>
    """,
    unsafe_allow_html=True
)
st.write("---")

