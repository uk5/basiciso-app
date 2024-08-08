import streamlit as st
import geopandas as gpd
import requests
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import contextily as ctx
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

API_KEY = '5b3ce3597851110001cf62483c9fa348736d4315a694410fd874e918'

def get_isochrones(lat, lon, minutes):
    url = 'https://api.openrouteservice.org/v2/isochrones/driving-car'
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'locations': [[lon, lat]],
        'range': [m * 60 for m in minutes]
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

def create_isochrones_gdf(isochrones_data):
    polygons = [Polygon(feature['geometry']['coordinates'][0]) for feature in isochrones_data['features']]
    return gpd.GeoDataFrame(geometry=polygons, crs='EPSG:4326')

def main():
    st.title('Isochrone Map Generator')

    lat = st.number_input("Enter the latitude:", value=25.00307729247567)
    lon = st.number_input("Enter the longitude:", value=55.167526256190804)
    user_input = st.text_input("Enter isochrone times in minutes (e.g., 5,10,15,20):")

    if user_input:
        try:
            minutes = list(map(int, user_input.split(',')))
            isochrone_data = get_isochrones(lat, lon, minutes)
            if isochrone_data:
                gdf_isochrones = create_isochrones_gdf(isochrone_data)
                gdf_location = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs='EPSG:4326')

                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_isochrones.plot(ax=ax, alpha=0.5, edgecolor='k', cmap='viridis')
                gdf_location.plot(ax=ax, color='red', markersize=100)
                ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs='EPSG:4326')

                ax.set_title('Isochrone Map')
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')

                st.pyplot(fig)

                pdf_buffer = BytesIO()
                with PdfPages(pdf_buffer) as pdf:
                    pdf.savefig(fig)
                
                st.download_button(
                    label="Download map as PDF",
                    data=pdf_buffer.getvalue(),
                    file_name="isochrone_map.pdf",
                    mime="application/pdf"
                )

        except requests.HTTPError as e:
            st.error(f"HTTP error occurred: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
  
