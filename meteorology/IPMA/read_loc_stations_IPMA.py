import os
import json
import pandas as pd
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from paths import IPMA_STATIONS_JSON, IPMA_STATIONS_CSV


def read_stations(stations_file_json):
    with open(stations_file_json, "r") as f:
        data = json.load(f)
    return data


def create_stations_list(stations):
    stations_list = []
    for i, station in enumerate(stations):
        geometry = station.get("geometry", {})
        coordinates = geometry.get("coordinates", {})
        properties = station.get("properties", {})
        id = properties.get("idEstacao", "N/A")
        local = properties.get("localEstacao", "N/A")
        local = local.strip('"') # Remove espaços em branco extras
        print(f"Station {i} of {len(stations)}: ID={id}, Local={local}, Coordinates={coordinates}")
        stations_list.append({
            "idEstacao": id,
            "localEstacao": local,
            "longitude": coordinates[0],
            "latitude": coordinates[1]
        })
    return stations_list


def create_stations_csv(stations_list, output_file_csv):
    df = pd.DataFrame(stations_list)
    df.to_csv(output_file_csv, index=False, encoding='utf-8', sep=',')
    print("CSV file 'IPMA_stations.csv' created successfully.")


def main():
    stations = read_stations(stations_file_json=IPMA_STATIONS_JSON)
    stations_list = create_stations_list(stations)
    create_stations_csv(stations_list, output_file_csv=IPMA_STATIONS_CSV)
    return 0


if __name__ == "__main__":
    main()