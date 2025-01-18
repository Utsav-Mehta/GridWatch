# import streamlit as st
# import pandas as pd
# import sqlite3
# import plotly.express as px
# import folium
# from folium.plugins import MarkerCluster, HeatMap  # Import HeatMap here
# from streamlit_folium import st_folium
# import time


# # Page configuration
# st.set_page_config(page_title="GridWatch", layout="wide")

# # Load data with caching
# @st.cache_data
# def load_data(db_path):
#     start_time = time.time()
#     conn = sqlite3.connect(db_path)
#     df = pd.read_sql_query("SELECT * FROM vehicle_counts_with_streets;", conn)
#     conn.close()
#     df["time"] = pd.to_datetime(df["timestamp"]).dt.time
#     df["date"] = pd.to_datetime(df["timestamp"]).dt.date
#     df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
#     df["weekday"] = pd.to_datetime(df["timestamp"]).dt.weekday
#     st.write(f"Data loaded in {time.time() - start_time:.2f} seconds")
#     return df

# # Load dataset
# db_path = "vehicle_counts_with_streets.db"
# data = load_data(db_path)

# # Sidebar configuration
# st.sidebar.header("Dashboard Options")
# dashboard_mode = st.sidebar.selectbox("Choose Dashboard", options=["General Overview", "Detailed Analysis"])

# if dashboard_mode == "General Overview":
#     # General Insights Dashboard
#     st.title("GridWatch: General Insights Dashboard")

#     # Create two columns
#     col1, col2 = st.columns(2)

#     with col1:
#         # Total vehicle counts by top streets
#         st.subheader("Top 10 Streets by Total Vehicle Counts")
#         top_streets = data.groupby("street_name")["count"].sum().nlargest(10).reset_index()
#         fig_top_streets = px.bar(
#             top_streets,
#             x="street_name",
#             y="count",
#             title="Top 10 Streets by Total Vehicle Counts",
#             labels={"street_name": "Street Name", "count": "Total Vehicle Count"},
#         )
#         st.plotly_chart(fig_top_streets, use_container_width=True)

#     with col2:
#         # Average traffic trends by hour
#         st.subheader("Average Traffic Trends by Hour")
#         avg_traffic_by_hour = data.groupby("hour")["count"].mean().reset_index()
#         fig_avg_traffic = px.line(
#             avg_traffic_by_hour,
#             x="hour",
#             y="count",
#             title="Average Traffic Trends by Hour",
#             labels={"hour": "Hour of Day", "count": "Average Vehicle Count"},
#         )
#         st.plotly_chart(fig_avg_traffic, use_container_width=True)

#     # New Insights: Marker Map
#     st.subheader("Traffic Hotspots (Marker Map)")
#     map_center = [data["latitude"].mean(), data["longitude"].mean()]
#     marker_map = folium.Map(location=map_center, zoom_start=12)
#     marker_cluster = MarkerCluster().add_to(marker_map)

#     for _, row in data.iterrows():
#         folium.Marker(
#             location=[row["latitude"], row["longitude"]],
#             popup=f"Street: {row['street_name']}<br>Count: {row['count']}",
#         ).add_to(marker_cluster)

#     st_folium(marker_map, width=800, height=500)

#     # Additional insight: Hourly traffic distribution for top streets
#     st.subheader("Hourly Traffic Distribution for Top Streets")
#     top_streets_list = top_streets["street_name"].tolist()
#     hourly_distribution = data[data["street_name"].isin(top_streets_list)]
#     hourly_distribution = hourly_distribution.groupby(["street_name", "hour"])["count"].mean().reset_index()

#     fig_hourly_distribution = px.line(
#         hourly_distribution,
#         x="hour",
#         y="count",
#         color="street_name",
#         title="Hourly Traffic Distribution for Top Streets",
#         labels={"hour": "Hour of Day", "count": "Average Vehicle Count", "street_name": "Street Name"},
#     )
#     st.plotly_chart(fig_hourly_distribution, use_container_width=True)

# else:
#     # Detailed Analysis Dashboard
#     st.title("GridWatch: Detailed Analysis Dashboard")

#     # Sidebar filters
#     st.sidebar.subheader("Street Name")
#     unique_streets = data["street_name"].unique()
#     selected_street = st.sidebar.selectbox("Select a street", options=unique_streets)

#     filtered_data_by_street = data[data["street_name"] == selected_street]

#     st.sidebar.subheader("Time Range")
#     start_time_filter = st.sidebar.time_input("Start Time", value=pd.to_datetime("00:00").time())
#     end_time_filter = st.sidebar.time_input("End Time", value=pd.to_datetime("23:59").time())

#     filtered_data_by_time = filtered_data_by_street[
#         (filtered_data_by_street["time"] >= start_time_filter) &
#         (filtered_data_by_street["time"] <= end_time_filter)
#     ]

#     st.sidebar.subheader("Latitude Range")
#     min_lat = st.sidebar.number_input("Min Latitude", value=float(filtered_data_by_time["latitude"].min()))
#     max_lat = st.sidebar.number_input("Max Latitude", value=float(filtered_data_by_time["latitude"].max()))

#     st.sidebar.subheader("Longitude Range")
#     min_lon = st.sidebar.number_input("Min Longitude", value=float(filtered_data_by_time["longitude"].min()))
#     max_lon = st.sidebar.number_input("Max Longitude", value=float(filtered_data_by_time["longitude"].max()))

#     filtered_data = filtered_data_by_time[
#         (filtered_data_by_time["latitude"] >= min_lat) & 
#         (filtered_data_by_time["latitude"] <= max_lat) &
#         (filtered_data_by_time["longitude"] >= min_lon) & 
#         (filtered_data_by_time["longitude"] <= max_lon)
#     ]

#     # Detailed Timeseries Plot
#     st.subheader("Vehicle Counts Over Time")
#     if not filtered_data.empty:
#         fig = px.line(
#             filtered_data,
#             x="timestamp",
#             y="count",
#             title=f"Vehicle Counts Over Time for {selected_street}",
#             labels={"timestamp": "Time", "count": "Vehicle Count"},
#         )
#         fig.update_layout(xaxis_title="Time", yaxis_title="Vehicle Count", xaxis_tickangle=45)
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.warning("No data available for the selected filters.")

#     # Heatmap for selected street and filters
#     st.subheader("Vehicle Count Heatmap")
#     if not filtered_data.empty:
#         map_center = [filtered_data["latitude"].mean(), filtered_data["longitude"].mean()]
#         m = folium.Map(location=map_center, zoom_start=15)
#         HeatMap(data=filtered_data[["latitude", "longitude", "count"]].values).add_to(m)
#         st_folium(m, width=700, height=500)
#     else:
#         st.warning("No data available to generate the heatmap.")

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
        st.subheader("Hourly Traffic Distribution for Top Streets")
        top_streets_list = top_streets["street_name"].tolist()
        hourly_distribution = data[data["street_name"].isin(top_streets_list)]
        hourly_distribution = hourly_distribution.groupby(["street_name", "hour"])["count"].mean().reset_index()

        fig_hourly_distribution = px.line(
            hourly_distribution,
            x="hour",
            y="count",
            color="street_name",
            title="Hourly Traffic Distribution for Top Streets",
            labels={"hour": "Hour of Day", "count": "Average Vehicle Count", "street_name": "Street Name"},
        )
        st.plotly_chart(fig_hourly_distribution, use_container_width=True)

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
