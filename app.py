import streamlit as st
import ee
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time

# Function to authenticate and initialize Earth Engine
def initialize_earth_engine():
    try:
        # If deploying, you may need to authenticate using a service account or environment variables
        service_account = 'your-service-account@your-project.iam.gserviceaccount.com'
        credentials = ee.ServiceAccountCredentials(service_account, 'path/to/privatekey.json')
        ee.Initialize(credentials)
    except ee.EEException:
        st.error("Failed to initialize Google Earth Engine")

# Initialize Earth Engine
initialize_earth_engine()

# Title of the application
st.title("Mapa de NDVI no Brasil - Linha do Tempo")

# Map configuration
latitude = -22.81
longitude = -50.48
zoom = 9

# Create the base map with folium
m = folium.Map(location=[latitude, longitude], zoom_start=zoom)

# Select dates
start_date = st.date_input("Selecione a data de início", datetime(2019, 1, 1))
end_date = st.date_input("Selecione a data de fim", datetime(2019, 12, 31))

# "Play" button for animation
play = st.button("Play NDVI Animation")

# Function to calculate and add NDVI to the map
def add_ndvi_to_map(start_date, end_date):
    point = ee.Geometry.Point(longitude, latitude)
    data = ee.ImageCollection("COPERNICUS/S2").filterBounds(point).filterDate(start_date, end_date)

    if data.size().getInfo() > 0:
        image = ee.Image(data.sort("CLOUD_COVERAGE_ASSESSMENT").first())
        ndvi = image.expression(
            "(NIR - RED) / (NIR + RED)",
            {
                "NIR": image.select("B8"),
                "RED": image.select("B4")
            }
        )

        ndvi_params = {
            "min": 0,
            "max": 1,
            "palette": ['red', 'orange', 'yellow', 'yellowgreen', 'green', 'black']
        }

        map_id_dict = ee.Image(ndvi).getMapId(ndvi_params)
        folium.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Google Earth Engine',
            overlay=True,
            name=f"NDVI {start_date} to {end_date}",
        ).add_to(m)
    else:
        st.warning(f"Nenhuma imagem disponível entre {start_date} e {end_date}.")

# Add NDVI to the map for the selected period
if start_date and end_date and not play:
    add_ndvi_to_map(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

# Animation when clicking "Play"
if play:
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=30)
        if next_date > end_date:
            next_date = end_date
        st.write(f"Exibindo NDVI de {current_date.strftime('%Y-%m-%d')} até {next_date.strftime('%Y-%m-%d')}")
        add_ndvi_to_map(current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'))
        st_folium(m, width=800, height=600)
        time.sleep(1)  # Pause of 1 second to simulate the animation
        current_date = next_date

# Display the map in the Streamlit application
st_folium(m, width=800, height=600)
