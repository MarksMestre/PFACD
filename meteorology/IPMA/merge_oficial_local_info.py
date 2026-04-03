import os
import pandas as pd
import numpy as np
import folium
from folium.features import DivIcon
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from paths import IPMA_STATIONS_CSV, IPMA_STATIONS_OFICIAL_CORRECTED, IPMA_STATIONS_OFFICIAL, IPMA_STATIONS_MERGED, IPMA_STATIONS_CONFLICT, IPMA_STATIONS_DONT_MATCH, IPMA_CONFLICT_MAPS, IPMA_MERGED_MAPS, IPMA_MERGED_MAPS_DIST


def correct_location_cols(oficial_df):

    df = oficial_df.copy()

    df = df.rename(columns={
        'Latitude': 'longitude',  # Onde está -31.13
        'Longitude': 'latitude' ,  # Onde está 39.45
    })

    df = df.rename(columns={
        'latitude': 'Latitude',  # Onde está -31.13
        'longitude': 'Longitude'   # Onde está 39.45
    })

    return df


def compare_names(stations_df, oficial_df):
    names_stations = set(stations_df["localEstacao"])
    names_oficial = set(oficial_df["Nome_oficial"])

    both = names_oficial & names_stations

    print(f'''

{40*"-"}
COMPARANDO OS NOMES EM AMBOS OS DATASETS

Número no dataset adquirido na API: {len(names_stations)}
Número no dataset oficial: {len(names_oficial)}



Presentes em ambos: {both}
Presentes apenas no dataset adquirido na API: {names_stations - both}
Presentes apenas no dataset oficial: {names_oficial - both}
''')


def merge_dfs(stations_df_input, corrected_df_input):

    from difflib import SequenceMatcher

    def similaridade(a, b):
        return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()
    
    def haversine(lat1, lon1, lat2, lon2):
        # Raio da Terra em km
        R = 6371.0
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c * 1000 # Distância em metros

    stations_df = stations_df_input.copy()
    corrected_df = corrected_df_input.copy()

    # 2. Criar chaves de arredondamento (2 casas decimais)
    # stations_df usa 'latitude' e 'longitude' (API)
    stations_df['lat_round'] = stations_df['latitude'].astype(float).round(2)
    stations_df['lon_round'] = stations_df['longitude'].astype(float).round(2)

    # corrected_df usa 'Latitude' e 'Longitude' (Oficial corrigido)
    corrected_df['lat_round'] = corrected_df['Latitude'].astype(float).round(2)
    corrected_df['lon_round'] = corrected_df['Longitude'].astype(float).round(2)
    # 3. Remover duplicados no dataset oficial para evitar explosão de linhas no merge
    # Se houver duas estações muito próximas no oficial, pegamos apenas a primeira
    corrected_lookup = corrected_df.drop_duplicates(subset=['lat_round', 'lon_round'])

    # 4. Executar o Merge
    # Mantemos todas as estações da API (left) e trazemos a Altitude do oficial
    merged_df = pd.merge(
        stations_df,
        corrected_lookup[['lat_round', 'lon_round', 'Altitude', 'Municipio', 'Distrito', 'Nome_oficial', 'Latitude', 'Longitude']],
        on=['lat_round', 'lon_round'],
        how='left'
    )

    # 5. Limpeza (Opcional: remover as colunas de arredondamento)
    merged_df = merged_df.drop(columns=['lat_round', 'lon_round'])

    # Visualização do resultado
    print(f"Total de estações na API: {len(stations_df)}")
    print(f"Total de estações nos dados oficiais: {len(corrected_df)}")
    print(f"Estações com Altitude encontrada: {merged_df['Altitude'].notna().sum()}")
    
    print("\nExemplo das primeiras linhas com Altitude:")
    print(merged_df[['localEstacao', 'latitude', 'longitude', 'Altitude']].head())

    print(f"Nulls: {len(merged_df[merged_df["Altitude"].isnull()])}")

    # Após o merge:
    # Assumindo que 'localEstacao' vem da API e 'Nome_oficial' vem do Oficial
    merged_df['score_nome'] = merged_df.apply(
        lambda row: similaridade(row['localEstacao'], row['Nome_oficial']) if pd.notna(row['Nome_oficial']) else 0, 
        axis=1
    )

    # Após o merge:
    merged_df['distancia_erro_m'] = merged_df.apply(
        lambda row: haversine(row['latitude'], row['longitude'], row['Latitude'], row['Longitude']) 
        if pd.notna(row['Latitude']) else 0, 
        axis=1
    )



    merged_df.rename(columns={
        'Latitude' : 'latitude_oficial',
        'Longitude': 'longitude_oficial'
    }, inplace=True)

    cols = [
        'idEstacao', 'localEstacao','Nome_oficial', 'longitude', 'latitude', 'longitude_oficial', 'latitude_oficial',
        'Altitude', 'Municipio', 'Distrito',
        'score_nome', 'distancia_erro_m'
    ]

    merged_df = merged_df[cols]

    final_df = merged_df[merged_df['Altitude'].notna()]

    # Filtra para ver onde o merge pode ter falhado (nomes muito diferentes)
    dont_have_correspondence = merged_df[merged_df['Altitude'].isna()]
    conflituosos = merged_df[
        ((merged_df['score_nome'] < 0.4) | (merged_df['distancia_erro_m'] > 2000)) & (merged_df['Altitude'].notna())
    ]
    conflituosos["Check"] = False
    print(dont_have_correspondence.columns)
    print(conflituosos.columns)
    print("Possíveis erros de correspondência (Nomes muito diferentes ou distancia maior que 2000):")
    print(conflituosos[['localEstacao', 'Nome_oficial', 'score_nome', 'distancia_erro_m']])

    return final_df, conflituosos, dont_have_correspondence


def create_maps(df, output_file, distance):
    if df.empty:
        print("Não existem conflitos para mapear.")
        return

    
    mapa = folium.Map(
        location=[df['latitude'].mean(), df['longitude'].mean()], 
        zoom_start=7,
        tiles='CartoDB Positron'
    )

    if distance:

        for _, row in df.iterrows():
            p_api = [row['latitude'], row['longitude']]
            p_oficial = [row['latitude_oficial'], row['longitude_oficial']]
            distancia = row['distancia_erro_m']

            # 1. Marcadores de Pontos (API e Oficial)
            folium.CircleMarker(location=p_api, radius=6, color='red', fill=True, fill_opacity=0.7).add_to(mapa)
            folium.CircleMarker(location=p_oficial, radius=6, color='blue', fill=True, fill_opacity=0.7).add_to(mapa)

            # 2. Etiquetas de Nome e ID
            folium.Marker(
                location=p_api,
                icon=DivIcon(
                    icon_size=(150,36), icon_anchor=(0,0),
                    html=f'<div style="font-size: 9pt; color: red; font-weight: bold;">ID: {row["idEstacao"]}<br>{row["localEstacao"]}</div>'
                )
            ).add_to(mapa)

            folium.Marker(
                location=p_oficial,
                icon=DivIcon(
                    icon_size=(150,36), icon_anchor=(0,20),
                    html=f'<div style="font-size: 9pt; color: blue; font-weight: bold;">{row["Nome_oficial"]}</div>'
                )
            ).add_to(mapa)

            # 3. Linha Tracejada
            folium.PolyLine(
                locations=[p_api, p_oficial], color='black', weight=2, dash_array='5'
            ).add_to(mapa)

            # 4. CÁLCULO E ETIQUETA DA DISTÂNCIA (No ponto médio da linha)
            ponto_medio = [
                (p_api[0] + p_oficial[0]) / 2,
                (p_api[1] + p_oficial[1]) / 2
            ]

            folium.Marker(
                location=ponto_medio,
                icon=DivIcon(
                    icon_size=(80,20),
                    icon_anchor=(40,10), # Centraliza o texto sobre o ponto
                    html=f'<div style="font-size: 8pt; color: black; background-color: white; border: 1px solid black; '
                        f'border-radius: 3px; text-align: center; font-weight: bold; padding: 1px;">'
                        f'{distancia:.0f} m</div>',
                )
            ).add_to(mapa)
    
    else:

        for _, row in df.iterrows():
            p_oficial = [row['latitude_oficial'], row['longitude_oficial']]


            folium.CircleMarker(location=p_oficial, radius=6, color='blue', fill=True, fill_opacity=0.7).add_to(mapa)


            folium.Marker(
                location=p_oficial,
                icon=DivIcon(
                    icon_size=(150,36), icon_anchor=(0,20),
                    html=f'<div style="font-size: 9pt; color: blue; font-weight: bold;">{row["Nome_oficial"]}</div>'
                )
            ).add_to(mapa)



    mapa.save(output_file)
    print(f"✅ Mapa salvo com distâncias em: {output_file}")


def main():
    stations_df = pd.read_csv(IPMA_STATIONS_CSV, sep=",")
    try: 
        corrected_df = pd.read_csv(IPMA_STATIONS_OFICIAL_CORRECTED, sep=",")
    except FileNotFoundError:
        oficial_df = pd.read_csv(IPMA_STATIONS_OFFICIAL, sep=",")
        corrected_df = correct_location_cols(oficial_df=oficial_df)
        corrected_df = corrected_df.rename(columns={
            "Nome": "Nome_oficial"
        })
        corrected_df.to_csv(IPMA_STATIONS_OFICIAL_CORRECTED, sep=",", index=False)

    
    # Nomes muito diferentes e nao seguem um padrao para limpeza automatica
    compare_names(
        stations_df=stations_df,
        oficial_df=corrected_df
    )

    print(stations_df.head())
    print(corrected_df.head())

    merged_df, conflict, dont_have_correspondence = merge_dfs(
        stations_df_input=stations_df,
        corrected_df_input=corrected_df
    )

    merged_df.to_csv(IPMA_STATIONS_MERGED, sep=",", index=False)
    conflict.to_csv(IPMA_STATIONS_CONFLICT, sep=",", index=False)
    dont_have_correspondence.to_csv(IPMA_STATIONS_DONT_MATCH, sep=",", index=False)

    create_maps(df=merged_df, output_file=IPMA_MERGED_MAPS_DIST, distance=True)
    create_maps(df=merged_df, output_file=IPMA_MERGED_MAPS, distance=False)
    create_maps(df=conflict, output_file=IPMA_CONFLICT_MAPS, distance=True)

if __name__ == "__main__":
    main()
