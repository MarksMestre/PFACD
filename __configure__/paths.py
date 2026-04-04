import os

# Pasta Raiz do Projeto 
__configure__path = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.dirname(__configure__path)


# ======================================================================================================================================
# --- METEOROLOGY DATA ---
METEO_FOLDER = os.path.join(BASE_FOLDER, "meteorology")




# CAMS
CAMS_FOLDER = os.path.join(METEO_FOLDER, "CAMS")
CAMS_1DAY = os.path.join(CAMS_FOLDER, "1day")
CAMS_1MONTH = os.path.join(CAMS_FOLDER, "1month")
CAMS_PROGRESS_FILE = os.path.join(CAMS_FOLDER, "progress.json")

# Folder para data agregada
CAMS_MERGED_FOLDER = os.path.join(CAMS_FOLDER, "data_merged")


# Final Data Folder
CAMS_FINAL_DATA = os.path.join(CAMS_FOLDER, "data_final")






# IPMA
IPMA = os.path.join(METEO_FOLDER, "IPMA")

# input data
IPMA_INPUT_DATA = os.path.join(IPMA, "data_input")
IPMA_STATIONS_CSV = os.path.join(IPMA_INPUT_DATA, "IPMA_stations.csv")
IPMA_STATIONS_JSON = os.path.join(IPMA_INPUT_DATA, "IPMA_stations.json")
IPMA_STATIONS_LOCATION_INFO = os.path.join(IPMA_INPUT_DATA, "IPMA_stations_with_location_info.csv")
IPMA_STATIONS_OFFICIAL = os.path.join(IPMA_INPUT_DATA, "IPMA_stations_data_oficial.csv")
IPMA_STATIONS_OFICIAL_CORRECTED = os.path.join(IPMA_INPUT_DATA, "IPMA_stations_data_oficial_corrected.csv")

# merged data
IPMA_MERGED_DATA = os.path.join(IPMA, "data_merged")
IPMA_STATIONS_MERGED = os.path.join(IPMA_MERGED_DATA, "IPMA_stations_merged.csv")
IPMA_STATIONS_DONT_MATCH = os.path.join(IPMA_MERGED_DATA, "IPMA_stations_dont_match.csv")
IPMA_STATIONS_CONFLICT = os.path.join(IPMA_MERGED_DATA, "IPMA_stations_conflict.csv")

# Conflict maps data
IPMA_CONFLICT_MAPS = os.path.join(IPMA_MERGED_DATA, "conflict_maps_dist.html")
IPMA_MERGED_MAPS = os.path.join(IPMA_MERGED_DATA, "merged_df_maps.html")
IPMA_MERGED_MAPS_DIST = os.path.join(IPMA_MERGED_DATA, "merged_df_maps_dist.html")

# final data
IPMA_FINAL_DATA = os.path.join(IPMA, "data_final")
IPMA_FINAL_FILE = os.path.join(IPMA_FINAL_DATA, "final_IPMA_data.csv")




# METEOSTAT
METEOSTAT_FOLDER = os.path.join(METEO_FOLDER, "METEOSTAT")
# ======================================================================================================================================




# ======================================================================================================================================
# --- Demography DATA ---
DEMOGRAPHY_FOLDER = os.path.join(BASE_FOLDER, "demography")




# Densidade
DENSIDADE_FOLDER = os.path.join(DEMOGRAPHY_FOLDER, "population_density")
DENSIDADE_CSV = os.path.join(DENSIDADE_FOLDER, "population_density.csv")




# População Total
POP_TOTAL_FOLDER = os.path.join(DEMOGRAPHY_FOLDER, "population_total")
POP_TOTAL_DATA_FOLDER = os.path.join(POP_TOTAL_FOLDER, "data")
POP_TOTAL_CSV = os.path.join(POP_TOTAL_DATA_FOLDER, "populacao_total.csv")
POP_WEIGHTS_CSV = os.path.join(POP_TOTAL_DATA_FOLDER, "populacao_total_weights.csv")
POP_ML_DATA_CSV = os.path.join(POP_TOTAL_DATA_FOLDER, "ml_data.csv")
POP_PRED_OFFICIAL_2025 = os.path.join(POP_TOTAL_DATA_FOLDER, "previsao_oficial_2025.csv")
POP_PREDICTION_OUTPUT = os.path.join(POP_TOTAL_DATA_FOLDER, "prediction.csv")
POP_FINAL_DF = os.path.join(POP_TOTAL_DATA_FOLDER, "populacao_com_previsao_2025.csv")
# ======================================================================================================================================




def main():
    """
    Varre as variáveis globais do script e cria automaticamente 
    qualquer caminho que termine em 'FOLDER', 'DATA' ou 'DIR'.
    """
    print("--- Verificando e criando estrutura de pastas ---")
    
    # Obtém o dicionário de variáveis globais
    current_globals = globals().copy()
    
    for var_name, var_value in current_globals.items():
        # Filtramos apenas strings que pareçam ser definições de pastas
        # Você pode ajustar os sufixos conforme o seu padrão de nomenclatura
        if isinstance(var_value, str) and any(var_name.endswith(suf) for suf in ["_FOLDER", "_DATA", "_DIR", "IPMA", "CAMS"]):
            
            # Evitamos tentar criar caminhos que são claramente ficheiros (contêm extensão)
            if "." not in os.path.basename(var_value):
                if not os.path.exists(var_value):
                    try:
                        os.makedirs(var_value, exist_ok=True)
                        print(f"[OK] Pasta criada: {var_name} -> {var_value}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao criar {var_value}: {e}")

    # Pastas específicas que não estão em variáveis globais mas são necessárias
    extra_folders = [
        os.path.join(CAMS_1DAY, "processed_data"),
        os.path.join(CAMS_1DAY, "raw_data"),
        os.path.join(CAMS_1MONTH, "processed_data"),
        os.path.join(CAMS_1MONTH, "raw_data"),
    ]
    
    for folder in extra_folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"[OK] Pasta extra criada: {folder}")
    print("--- Toda a estrutura foi criada com sucesso ---")

if __name__ == "__main__":
    print(f"Base Folder: {BASE_FOLDER}")
    main()