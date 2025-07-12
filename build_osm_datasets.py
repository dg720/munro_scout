import overpy
import pandas as pd
from geopy.distance import geodesic
from rag_retriever import answer_hiking_query

# Initialize Overpass API
api = overpy.Overpass()

# Munro (peaks over 914.4m / 3000ft)
munro_query = """
[out:json][timeout:60];
(
  node["natural"="peak"](55.0,-8.0,58.7,-3.0);
);
out body;
"""

# Railway stations
station_query = """
[out:json][timeout:60];
(
  node["railway"="station"](55.0,-8.0,58.7,-3.0);
);
out body;
"""

# Run queries
munro_result = api.query(munro_query)
station_result = api.query(station_query)

# Process Munros
munros = []
for node in munro_result.nodes:
    ele = node.tags.get("ele")
    try:
        ele = float(ele)
        if ele >= 914.4:
            munros.append(
                {
                    "name": node.tags.get("name", "Unnamed"),
                    "lat": node.lat,
                    "lon": node.lon,
                    "height": ele,
                }
            )
    except (TypeError, ValueError):
        continue

# Process Stations
stations = []
for node in station_result.nodes:
    stations.append(
        {"name": node.tags.get("name", "Unnamed"), "lat": node.lat, "lon": node.lon}
    )

# Convert to DataFrames
munros_df = pd.DataFrame(munros)
stations_df = pd.DataFrame(stations)

# Save
munros_df.to_csv("data/munros_osm.csv", index=False)
stations_df.to_csv("data/train_stations_osm.csv", index=False)

print("Saved: data/munros_osm.csv and data/train_stations_osm.csv")

edges = []

for _, station in stations_df.iterrows():
    for _, munro in munros_df.iterrows():
        distance = geodesic(
            (station["lat"], station["lon"]), (munro["lat"], munro["lon"])
        ).km
        if distance <= 30:  # Filter for practical hiking proximity
            edges.append(
                {
                    "station_name": station["name"],
                    "station_lat": station["lat"],
                    "station_lon": station["lon"],
                    "munro_name": munro["name"],
                    "munro_lat": munro["lat"],
                    "munro_lon": munro["lon"],
                    "distance_km": round(distance, 2),
                }
            )

# Save results
edges_df = pd.DataFrame(edges)
edges_df.to_csv("data/station_to_munro_edges.csv", index=False)

print("Saved: data/station_to_munro_edges.csv")
