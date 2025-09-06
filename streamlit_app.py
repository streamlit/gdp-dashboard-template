import streamlit as st
import ee
import geemap.foliumap as geemap
import pandas as pd
import datetime

# Inicializar Earth Engine
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

st.set_page_config(layout="wide")
st.title("🌍 Monitoramento da Qualidade do Ar - Hortolândia")

# Filtros na barra lateral
start_date = st.sidebar.date_input("Data início", value=datetime.date(2025, 9, 1))
end_date = st.sidebar.date_input("Data fim", value=datetime.date(2025, 9, 5))
sd = pd.to_datetime(start_date).strftime("%Y-%m-%d")
ed = pd.to_datetime(end_date).strftime("%Y-%m-%d")

pollutant = st.sidebar.selectbox("Selecione o poluente", ["NO2", "O3", "CO"])

# Região de Hortolândia
roi = ee.Geometry.Point([-47.2191, -22.8583]).buffer(20000)

# Coleções do Sentinel-5P
collections = {
    "NO2": "COPERNICUS/S5P/OFFL/L3_NO2",
    "O3": "COPERNICUS/S5P/OFFL/L3_O3",
    "CO": "COPERNICUS/S5P/OFFL/L3_CO"
}
band_map = {
    "NO2": "NO2_column_number_density",
    "O3": "O3_column_number_density",
    "CO": "CO_column_number_density"
}

col = ee.ImageCollection(collections[pollutant]).select(band_map[pollutant])
col = col.filterDate(sd, ed).filterBounds(roi)
image = col.mean()

# Cores no mapa
vis_params = {
    "NO2": {"min": 0, "max": 0.0002, "palette": ["white", "yellow", "red"]},
    "O3": {"min": 0.12, "max": 0.15, "palette": ["blue", "green", "red"]},
    "CO": {"min": 0, "max": 0.05, "palette": ["white", "orange", "red"]}
}

# Criar mapa
Map = geemap.Map(center=[-22.8583, -47.2191], zoom=10)
Map.addLayer(image, vis_params[pollutant], pollutant)
Map.addLayer(roi, {"color": "black"}, "Hortolândia")
Map.add_colorbar(vis_params[pollutant], label=pollutant, layer_name=pollutant)
Map.to_streamlit(height=600)

# Estatísticas
mean_dict = image.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=roi,
    scale=1000,
    bestEffort=True
).getInfo()

st.subheader("📊 Estatísticas médias na região de Hortolândia")
st.write(mean_dict)

