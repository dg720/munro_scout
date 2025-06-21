import pandas as pd
from langchain.tools import tool
from geopy.distance import geodesic


def haversine_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km


# Load static data once
EDGES_PATH = "data/station_to_munro_edges.csv"
MUNROS_PATH = "data/munros_osm.csv"

edges_df = pd.read_csv(EDGES_PATH)
munros_df = pd.read_csv(MUNROS_PATH)


@tool
def get_munros_near_station(station_name: str) -> str:
    """
    Returns a list of Munros within ~30km of a given train station.
    Input: Station name (e.g. 'Aviemore')
    Output: Formatted list of Munros with distance
    """
    matches = edges_df[edges_df["station_name"].str.lower() == station_name.lower()]
    if matches.empty:
        return f"No Munros found near station: {station_name}"

    munros = matches.sort_values("distance_km")[["munro_name", "distance_km"]]
    result = "\n".join(
        [
            f"- {row['munro_name']} ({row['distance_km']} km)"
            for _, row in munros.iterrows()
        ]
    )
    return f"Munros near {station_name}:\n{result}"


@tool
def find_nearby_munros(lat: float, lon: float, max_km: int = 30) -> list:
    """
    Returns a list of Munros within a certain distance of a lat/lon coordinate.
    """
    results = []
    for _, row in munros_df.iterrows():
        dist = haversine_distance(lat, lon, row["lat"], row["lon"])
        if dist <= max_km:
            results.append(f"{row['name']} ({round(dist, 2)} km)")
    return results


@tool
def get_munro_info(name: str) -> str:
    """
    Returns basic metadata about a Munro by name.
    Note: difficulty is not available in munros_osm.csv.
    """
    row = munros_df[munros_df["name"].str.lower() == name.lower()]
    if row.empty:
        return "Munro not found."
    r = row.iloc[0]
    return f"{r['name']} is {r['height']}m tall. Location: ({r['lat']}, {r['lon']})"
