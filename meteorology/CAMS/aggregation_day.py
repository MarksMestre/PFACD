import os
import pandas as pd
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from paths import CAMS_MERGED_FOLDER, CAMS_FINAL_DATA


def aplicar_metricas(df, group_cols):
    # 1. Listas de colunas
    VARS_RADIACAO = [
        "TOA", "Clear sky GHI", "Clear sky BHI", "Clear sky DHI", 
        "Clear sky BNI", "GHI", "BHI", "DHI", "BNI"
    ]
    
    # Agregações separadas
    df_rad = df.groupby(group_cols)[VARS_RADIACAO].agg(['sum', 'mean', 'std', 'min', 'max'])
    df_rel = df.groupby(group_cols)[['Reliability']].agg(['mean', 'std', 'min', 'max'])
    
    # Unir os dois - aqui as colunas ainda são MultiIndex
    df_agg = pd.concat([df_rad, df_rel], axis=1)
    
    # CORREÇÃO DO NOME DAS COLUNAS:
    # col[0] é o nome da variável (ex: GHI), col[1] é a função (ex: sum)
    df_agg.columns = [f"{col[0]}_{col[1]}" for col in df_agg.columns]
    
    # 2. Cálculo do CV apenas para RADIAÇÃO
    for var in VARS_RADIACAO:
        # Verifica se as colunas existem antes de dividir para evitar erros
        col_std = f'{var}_std'
        col_mean = f'{var}_mean'
        df_agg[f'{var}_cv'] = df_agg[col_std] / df_agg[col_mean]
        df_agg[f'{var}_cv'] = df_agg[f'{var}_cv'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # 3. Índice de Claridade
    df_agg['clearness_index'] = df_agg['GHI_sum'] / df_agg['TOA_sum']
    df_agg['clearness_index'] = df_agg['clearness_index'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    return df_agg.reset_index()


def aggregate_by_day(df):
    # Se o dataset for horário e quiseres o total/média do dia
    return aplicar_metricas(df, ["station_id", "location_name", "data"])


def aggregate_by_month(df):
    # Agrupamento por Estação, Ano e Mês
    return aplicar_metricas(df, ["station_id", "location_name", "ano", "mes"])


def aggregate_by_trimester(df):
    return aplicar_metricas(df, ["station_id", "location_name", "ano", "trimestre"])


def aggregate_by_semester(df):
    return aplicar_metricas(df, ["station_id", "location_name", "ano", "semestre"])


def aggreggate_selection(df, time_agg):
    # Correção: Usar IFs para não executar as 4 agregações desnecessariamente
    if time_agg == "month":
        return aggregate_by_month(df)
    elif time_agg == "trimester":
        return aggregate_by_trimester(df)
    elif time_agg == "semester":
        return aggregate_by_semester(df)
    else:
        raise ValueError("Opção de agregação inválida")


def main(using_copy: bool = False):

    if using_copy:

        copy_extension = "_copy"
    else:
        copy_extension = ""

    
    name_file = f"merged_1day{copy_extension}"
    file_path = os.path.join(CAMS_MERGED_FOLDER, name_file+".csv") # Usando o ficheiro consolidado

    output_file_path = os.path.join(CAMS_FINAL_DATA, name_file)
    if os.path.exists(file_path):
        df_raw = pd.read_csv(file_path, sep=",")

        for time_agg in ["month", "trimester", "semester"]:

            time_agg_output_path = output_file_path +  f"_{time_agg}.csv"
        
            df = aggreggate_selection(df_raw, time_agg=time_agg)

            
            # print(f"Amostra da Agregação {time_agg} (GHI):")
            # print(df[["location_name", "ano", "mes", "GHI_sum", "GHI_mean", "GHI_std"]].head())
            
            # Guardar resultados
            df.to_csv(time_agg_output_path, sep=",", index=False)


if __name__ == "__main__":
    main()