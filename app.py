import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="GridWatch", layout="wide")  

@st.cache_data
def load_data(db_path):
    start_time = time.time()  
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM vehicle_counts_with_streets;", conn)  # Load the entire dataset
    conn.close()
    df["time"] = pd.to_datetime(df["timestamp"]).dt.time
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    st.write(f"Data loaded in {time.time() - start_time:.2f} seconds")
    return df

db_path = "vehicle_counts_with_streets.db"  
data = load_data(db_path)

st.title("GridWatch: NYC Congestion Pricing Impact Dashboard")

st.sidebar.header("Filters")

st.sidebar.subheader("Street Name")
unique_streets = data["street_name"].unique()
selected_street = st.sidebar.selectbox("Select a street", options=unique_streets)

start_time = time.time()
filtered_data_by_street = data[data["street_name"] == selected_street]
st.write(f"Street filtering completed in {time.time() - start_time:.2f} seconds")

st.sidebar.subheader("Time Range")
start_time_filter = st.sidebar.time_input("Start Time", value=pd.to_datetime("00:00").time())
end_time_filter = st.sidebar.time_input("End Time", value=pd.to_datetime("23:59").time())

start_time = time.time()
filtered_data_by_time = filtered_data_by_street[
    (filtered_data_by_street["time"] >= start_time_filter) &
    (filtered_data_by_street["time"] <= end_time_filter)
]
st.write(f"Time filtering completed in {time.time() - start_time:.2f} seconds")

st.sidebar.subheader("Latitude Range")
min_lat = st.sidebar.number_input("Min Latitude", value=float(filtered_data_by_time["latitude"].min()))
max_lat = st.sidebar.number_input("Max Latitude", value=float(filtered_data_by_time["latitude"].max()))

st.sidebar.subheader("Longitude Range")
min_lon = st.sidebar.number_input("Min Longitude", value=float(filtered_data_by_time["longitude"].min()))
max_lon = st.sidebar.number_input("Max Longitude", value=float(filtered_data_by_time["longitude"].max()))

filtered_data = filtered_data_by_time[
    (filtered_data_by_time["latitude"] >= min_lat) &
    (filtered_data_by_time["latitude"] <= max_lat) &
    (filtered_data_by_time["longitude"] >= min_lon) &
    (filtered_data_by_time["longitude"] <= max_lon)
]

st.subheader("Vehicle Counts Over Time")
if not filtered_data.empty:
    start_time = time.time()
    fig = px.line(
        filtered_data,
        x="timestamp",
        y="count",
        title=f"Vehicle Counts Over Time for {selected_street}",
        labels={"timestamp": "Time", "count": "Vehicle Count"},
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Vehicle Count",
        xaxis_tickangle=45,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Timeseries plot rendered in {time.time() - start_time:.2f} seconds")
else:
    st.warning("No data available for the selected filters.")

st.subheader("Vehicle Count Heatmap")
if not filtered_data.empty:
    start_time = time.time()
    map_center = [filtered_data["latitude"].mean(), filtered_data["longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=15)  # Zoomed-in view

    HeatMap(data=filtered_data[["latitude", "longitude", "count"]].values).add_to(m)

    st_data = st_folium(m, width=700, height=500)
    st.write(f"Heatmap rendered in {time.time() - start_time:.2f} seconds")
else:
    st.warning("No data available to generate the heatmap.")