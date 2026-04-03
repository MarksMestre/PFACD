import pandas as pd
import os 
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from paths import POP_PREDICTION_OUTPUT, POP_WEIGHTS_CSV, POP_FINAL_DF


def main():
    # 1. Carregar os dados
    preds_df = pd.read_csv(POP_PREDICTION_OUTPUT, sep=",")
    data_df = pd.read_csv(POP_WEIGHTS_CSV, sep=",")
    cols_data = [
        "Level","NUTS3","NUTS3_Name","territory_code","Name",
    ] + [str(ano) for ano in range(2013,2025)]
    data_df = data_df[cols_data]

    # 2. Preparar o DataFrame de previsões
    # Assumindo que o teu prediction.csv tem as colunas 'territory_code' e a predição (ex: 'prediction_2025')
    # Vamos renomear a coluna de predição para '2025' para seguir o padrão do dataset original
    preds_to_join = preds_df[['territory_code', 'target_pop']].rename(
        columns={'target_pop': '2025'}
    )

    # 3. Fazer o Merge (Juntar os dados)
    # Usamos 'left' para manter todos os dados originais (incluindo as linhas NUTS3)
    # Mesmo que a predição só exista para MUN, as NUTS3 ficarão com NaN (que podemos somar depois)
    final_df = pd.merge(data_df, preds_to_join, on='territory_code', how='left')

    # 4. (Opcional) Reordenar as colunas para o '2025' ficar logo após o '2024'
    # Isto evita que a coluna nova fique no fim de todas as colunas 'weight_'
    cols = list(final_df.columns)
    idx_2024 = cols.index('2024')
    
    # Movemos a coluna '2025' do final para a posição idx_2024 + 1
    cols.insert(idx_2024 + 1, cols.pop(cols.index('2025')))
    final_df = final_df[cols]

    # 5. Recalcular os totais das NUTS3 para 2025
    # Como as NUTS3 no prediction.csv provavelmente estão vazias, vamos somar os municípios
    nuts_totals_2025 = final_df[final_df["Level"] == "MUN"].groupby("NUTS3")["2025"].sum()
    
    # Preencher os valores das linhas NUTS3 onde a coluna 2025 está vazia
    final_df.loc[final_df["Level"] == "NUTS3", "2025"] = final_df["NUTS3"].map(nuts_totals_2025)

    # 6. Salvar o resultado final
    final_df.to_csv(POP_FINAL_DF, sep=",", index=False)
    
    print(f"Sucesso! Ficheiro guardado em: {POP_FINAL_DF}")
    print(final_df[['Name', '2024', '2025']].head())


if __name__ == "__main__":
    main()