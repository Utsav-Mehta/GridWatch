import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="GridWatch", layout="wide")

# Function to query data
def query_data(db_path, query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = None

if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = None

if "unique_streets" not in st.session_state:
    st.session_state.unique_streets = None

# Sidebar configuration
st.sidebar.header("Dashboard Options")
dashboard_mode = st.sidebar.selectbox("Choose Dashboard", options=["General Overview", "Detailed Analysis"])

db_path = "vehicle_counts_with_streets.db"

if dashboard_mode == "General Overview":
    st.title("GridWatch: General Insights Dashboard")

    if st.sidebar.button("Load Data"):
        query = "SELECT * FROM vehicle_counts_with_streets;"
        st.session_state.data = query_data(db_path, query)
        st.session_state.data["time"] = pd.to_datetime(st.session_state.data["timestamp"]).dt.time
        st.session_state.data["date"] = pd.to_datetime(st.session_state.data["timestamp"]).dt.date
        st.session_state.data["hour"] = pd.to_datetime(st.session_state.data["timestamp"]).dt.hour

    if st.session_state.data is not None:
        data = st.session_state.data

        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            # Total vehicle counts by top streets
            st.subheader("Top 10 Streets by Total Vehicle Counts")
            top_streets = data.groupby("street_name")["count"].sum().nlargest(10).reset_index()
            fig_top_streets = px.bar(
                top_streets,
                x="street_name",
                y="count",
                title="Top 10 Streets by Total Vehicle Counts",
                labels={"street_name": "Street Name", "count": "Total Vehicle Count"},
            )
            st.plotly_chart(fig_top_streets, use_container_width=True)

        with col2:
            # Average traffic trends by hour
            st.subheader("Average Traffic Trends by Hour")
            avg_traffic_by_hour = data.groupby("hour")["count"].mean().reset_index()
            fig_avg_traffic = px.line(
                avg_traffic_by_hour,
                x="hour",
                y="count",
                title="Average Traffic Trends by Hour",
                labels={"hour": "Hour of Day", "count": "Average Vehicle Count"},
            )
            st.plotly_chart(fig_avg_traffic, use_container_width=True)

        # Traffic Hotspots Marker Map
        st.subheader("Traffic Hotspots (Marker Map)")
        map_center = [data["latitude"].mean(), data["longitude"].mean()]
        marker_map = folium.Map(location=map_center, zoom_start=12)
        marker_cluster = MarkerCluster().add_to(marker_map)

        for _, row in data.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"Street: {row['street_name']}<br>Count: {row['count']}",
            ).add_to(marker_cluster)

        st_folium(marker_map, width=800, height=500)

        # Hourly Traffic Distribution
        # st.subheader("Hourly Traffic Distribution for Top Streets")
        # top_streets_list = top_streets["street_name"].tolist()
        # hourly_distribution = data[data["street_name"].isin(top_streets_list)]
        # hourly_distribution = hourly_distribution.groupby(["street_name", "hour"])["count"].mean().reset_index()

        # fig_hourly_distribution = px.line(
        #     hourly_distribution,
        #     x="hour",
        #     y="count",
        #     color="street_name",
        #     title="Hourly Traffic Distribution for Top Streets",
        #     labels={"hour": "Hour of Day", "count": "Average Vehicle Count", "street_name": "Street Name"},
        # )
        # st.plotly_chart(fig_hourly_distribution, use_container_width=True)

        st.subheader("Vehicle Count Distribution for Top Streets")
        top_streets_list = top_streets["street_name"].tolist()
        distribution_data = data[data["street_name"].isin(top_streets_list)]

        fig_box_plot = px.box(
            distribution_data,
            x="street_name",
            y="count",
            title="Vehicle Count Distribution for Top Streets",
            labels={"street_name": "Street Name", "count": "Vehicle Count"},
            points=False,  # Adds individual data points to the box plot
        )

        st.plotly_chart(fig_box_plot, use_container_width=True)
elif dashboard_mode == "Detailed Analysis":
    st.title("GridWatch: Detailed Analysis Dashboard")

    if st.session_state.unique_streets is None:
        street_query = "SELECT DISTINCT street_name FROM vehicle_counts_with_streets;"
        unique_streets = query_data(db_path, street_query)["street_name"].tolist()
        unique_streets.insert(0, "All")
        st.session_state.unique_streets = unique_streets

    unique_streets = st.session_state.unique_streets

    selected_street = st.sidebar.selectbox("Select Street Name", unique_streets)
    start_time_filter = st.sidebar.selectbox(
        "Start Time", options=[f"{hour:02d}:00:00" for hour in range(24)], index=0
    )
    end_time_filter = st.sidebar.selectbox(
        "End Time", options=[f"{hour:02d}:00:00" for hour in range(24)], index=23
    )

    if st.sidebar.button("Submit Query"):
        query = "SELECT * FROM vehicle_counts_with_streets WHERE 1=1"
        if selected_street != "All":
            query += f" AND street_name = '{selected_street}'"
        query += f" AND time(timestamp) >= '{start_time_filter}'"
        query += f" AND time(timestamp) <= '{end_time_filter}'"

        st.session_state.filtered_data = query_data(db_path, query)

    if st.session_state.filtered_data is not None:
        filtered_data = st.session_state.filtered_data

        if not filtered_data.empty:
            st.subheader("Vehicle Counts Over Time")
            fig = px.line(
                filtered_data,
                x="timestamp",
                y="count",
                title="Vehicle Counts Over Time",
                labels={"timestamp": "Time", "count": "Vehicle Count"},
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Vehicle Count Heatmap")
            map_center = [filtered_data["latitude"].mean(), filtered_data["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=15)
            HeatMap(data=filtered_data[["latitude", "longitude", "count"]].values).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.warning("No data found for the specified query.")
    else:
        st.warning("No query submitted. Use the filters and click 'Submit Query'.")
