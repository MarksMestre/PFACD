import json
import pandas as pd
import os
import pgeocode
from scipy.spatial import KDTree
import numpy as np
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import IPMA_STATIONS_JSON, IPMA_STATIONS_LOCATION_INFO

# Configurar base de dados de Portugal (faz o download na 1ª vez)
nomi = pgeocode.Nominatim('pt')
df_pt = nomi._data.copy().dropna(subset=['latitude', 'longitude'])

# Criar uma árvore de busca para encontrar o CP mais próximo das coordenadas GPS
tree = KDTree(df_pt[['latitude', 'longitude']].values)


def read_stations(stations_json):
    with open(stations_json, "r") as f:
        data = json.load(f)
    return data


def create_stations_list(stations):
    stations_list = []
    for _, station in enumerate(stations):
        geometry = station.get("geometry", {})
        coordinates = geometry.get("coordinates", {})
        properties = station.get("properties", {})
        id = properties.get("idEstacao", "N/A")
        local = properties.get("localEstacao", "N/A")
        local = local.strip('"') # Remove caracteres ' " ' do nome do local, se existirem
        loc_info = get_loc_info(coordinates[1], coordinates[0]) # Obtém todas as informações do local usando latitude e longitude
        print(loc_info)
        station_info = {
            "idEstacao": id,
            "localEstacao": local,
            "longitude": coordinates[0],
            "latitude": coordinates[1]
        }
        for col in loc_info.index:
            print(f"{col}: {loc_info[col]}")
            station_info[col] = loc_info[col]
        # print(f"Station {i} of {len(stations)}: ID={id}, Local={local}, Coordinates={coordinates}, Postal Code={postal_code}, Concelho={concelho}")
        stations_list.append(station_info)
    return stations_list


def get_loc_info(latitude, longitude):
    dist, idx = tree.query([latitude, longitude])
    return df_pt.iloc[idx]


def main():
    stations = read_stations(
        stations_json=IPMA_STATIONS_JSON
    )
    stations_list = create_stations_list(stations)
    df = pd.DataFrame(stations_list)
    df.to_csv(IPMA_STATIONS_LOCATION_INFO, index=False, encoding='utf-8', sep=',')
    print(df.head())
    return 0
            

if __name__ == "__main__":
    main()
    