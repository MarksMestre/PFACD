# data_api_manual.py corrigido
from data_api_opt import api_get, processar_ficheiro_cams
import pandas as pd
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import IPMA_STATIONS_CSV


def process_station_manual(row, time_step="1month"):
    station_id = str(row['idEstacao'])
    location_name = str(row['localEstacao'])
    longitude = round(row['longitude'], 4)
    latitude = round(row['latitude'], 4)

    print(f"🚀 Iniciando recuperação manual: {location_name} ({station_id})")

    status = api_get(
        station_id=station_id, location_name=location_name,
        longitude=longitude, latitude=latitude,
        time_step=time_step
    ) 
    
    if status == 0:
        processar_ficheiro_cams(station_id, location_name, time_step)
        return 0
    return -1


def main():
    # Carregar o CSV garantindo que o ID é string
    station_df = pd.read_csv(IPMA_STATIONS_CSV, sep=',', encoding='utf-8', dtype={'idEstacao': str})
    
    input_id = input("Introduza o ID da Estação (ex: 1210881): ").strip()

    input_time_step = int(input('''Introduza o time_step (1month ou 1day):
    [ 0 ] Both (processa ambos os time_steps)
    [ 1 ] 1month
    [ 2 ] 1day                   
''').strip())
    
    if input_time_step == 0:
        time_steps = ["1month", "1day"]
    elif input_time_step == 1:
        time_steps = ["1month"]
    elif input_time_step == 2:
        time_steps = ["1day"]
    else:
        print("Opção inválida. Usando 1day por padrão.")
        time_steps = ["1day"]
    
    # Filtrar pela coluna correta: 'idEstacao'
    station_row = station_df[station_df['idEstacao'] == input_id]
    
    if station_row.empty:
        print(f"❌ Nenhuma estação encontrada com o ID {input_id}.")
        return
    
    # Tentar processar para 1month e 1day se necessário
    for t_step in time_steps:
        print(f"\n--- Processando {t_step} ---")
        result = process_station_manual(station_row.iloc[0], time_step=t_step)
        if result == 0:
            print(f"✅ Estação {input_id} ({t_step}) processada com sucesso.")
        else:
            print(f"❌ Falha ao processar {t_step}.")

if __name__ == "__main__":
    main()