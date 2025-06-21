from langchain.tools import tool
import pandas as pd

# Load train stations from OSM
stations = pd.read_csv("data/train_stations_osm.csv")  # expects 'name', 'lat', 'lon'


@tool
def station_lookup(location_name: str) -> str:
    """
    Returns a list of known train stations in Scotland that include the given location name.
    Useful when a user says 'Find hikes from Fort William' — this resolves station name matches.
    """
    matches = stations[stations["name"].str.lower().str.contains(location_name.lower())]
    if matches.empty:
        return f"No train stations found matching '{location_name}'"

    result = "\n".join(
        [
            f"- {row['name']} ({row['lat']}, {row['lon']})"
            for _, row in matches.iterrows()
        ]
    )
    return f"Train stations matching '{location_name}':\n{result}"
