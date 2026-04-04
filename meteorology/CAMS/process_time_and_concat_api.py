import os
import pandas as pd
import time
import sys


# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import CAMS_FOLDER, CAMS_MERGED_FOLDER


def acerto_months(df):
    df['inicio'] = pd.to_datetime(df['inicio'])
    
    # Formata como string: "2024-01"
    df['ano_mes'] = pd.to_datetime(df['inicio']).dt.to_period('M')

    months_mapping = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    df['semestre'] = df['inicio'].dt.month.apply(lambda x: "A" if x <= 6 else "B")
    df['trimestre'] = df['inicio'].dt.month.apply(lambda x: "1T" if x <= 3 else ("2T" if x <= 6 else ("3T" if x <= 9 else "4T")))
    df['ano'] = df['inicio'].dt.year
    df['mes'] = df['inicio'].dt.month.apply(lambda x: months_mapping.get(x, "Desconhecido"))

    cols = [
        "station_id", "location_name", "ano_mes", "ano", "mes", "trimestre", "semestre", "inicio", 
        "TOA", "Clear sky GHI", "Clear sky BHI", "Clear sky DHI", "Clear sky BNI", "GHI", "BHI", "DHI", "BNI", "Reliability"
    ]


    df = df[cols]
    df.sort_values("station_id", inplace=True)
    return df


def acerto_days(df):
    # Converter a coluna 'time' para datetime
    
    df['data'] = pd.to_datetime(df['inicio'], errors='coerce')
    
    # Extrair o dia, mês e ano da coluna 'time'
    df['dia'] = df['data'].dt.day
    df['mes'] = df['data'].dt.month
    df['ano'] = df['data'].dt.year
    df['semestre'] = df['mes'].apply(lambda x: "A" if x <= 6 else "B")
    df['trimestre'] = df['mes'].apply(lambda x: "1T" if x <= 3 else ("2T" if x <= 6 else ("3T" if x <= 9 else "4T")))

    cols = [
        "station_id", "location_name", "data", "dia", "mes", "trimestre", "semestre", "ano",
        "TOA", "Clear sky GHI", "Clear sky BHI", "Clear sky DHI", "Clear sky BNI", "GHI", "BHI", "DHI", "BNI", "Reliability"
    ]
    
    df = df[cols]
    df.sort_values("station_id", inplace=True)
    return df


def generate_report(merged_dfs: dict):
    for time_step, df in merged_dfs.items():
        # Identifica se é um step de mês ou dia (mesmo com "_copy")
        is_month = "1month" in time_step
        
        numero_estacoes = df['station_id'].nunique()
        
        # CORREÇÃO: Usa a coluna correta dependendo do tipo de dado
        if is_month:
            numero_periodos = df['ano_mes'].nunique()
            col_data = 'ano_mes'
        else:
            numero_periodos = df['data'].nunique()
            col_data = 'data'
            
        numero_teorico_registos = numero_estacoes * numero_periodos
        
        print(f"Relatório para {time_step}:")
        print(f"Número total de estações: {numero_estacoes}")
        print(f"Número total de {'meses' if is_month else 'dias'} únicos: {numero_periodos}")
        print(f"Período de dados: {df[col_data].min()} a {df[col_data].max()}")
        print(f"Número teórico de registos: {numero_teorico_registos}")
        print(f"Total de registos: {len(df)}")
        print(f"Tudo OK? {numero_teorico_registos == len(df)}")
        print("-" * 40)


def main_loop(using_copy):

    start_time = time.time()
    print("Iniciando processamento e concatenação dos dados...")
    print(40*"-")
    time_dfs = {}
    merged_dfs = {}
    time_steps = ["1month", "1day"]
    month_ref = "1month"
    day_ref = "1day"
    if using_copy:
        for i, time_step in enumerate(time_steps):
            time_step += "_copy"
            time_steps[i] = time_step
        month_ref += "_copy"
        day_ref += "_copy"
        

    for time_step in time_steps:
        time_dfs[time_step] = []
        time_folder = os.path.join(CAMS_FOLDER, time_step)
        processed_folder = os.path.join(time_folder, "processed_data")
        for file in os.listdir(processed_folder):
            file_path = os.path.join(processed_folder, file)
            df = pd.read_csv(file_path, sep=",")
            if time_step == month_ref:
                df = acerto_months(df)
            elif time_step == day_ref:
                df = acerto_days(df)
                pass
            else: 
                pass
            time_dfs[time_step].append(df)
        merged_df = pd.concat(time_dfs[time_step], ignore_index=True)
        merged_dfs[time_step] = merged_df
        merged_file_path = os.path.join(CAMS_MERGED_FOLDER, f"merged_{time_step}.csv")
        merged_df.to_csv(merged_file_path, index=False, sep=',', encoding='utf-8')

    generate_report(merged_dfs)
    end_time = time.time()

    print(f"Total processing time: {end_time - start_time:.2f} seconds")
    return 0


def main():
    main_loop(using_copy=False)
    return 0 
    
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user. Saving progress...")
        # Aqui podes adicionar código para salvar o progresso atual, se necessário
    except Exception as e:
        print(f"An error occurred: {e}")
