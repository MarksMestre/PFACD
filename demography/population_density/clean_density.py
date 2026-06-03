import os
import pandas as pd
import numpy as np
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import DENSIDADE_CSV, DENSIDADE_FINAL_FOLDER, DENSIDADE_FINAL_CSV

def main():
    # Carregar os dados
    df = pd.read_csv(DENSIDADE_CSV, sep=";")

    # Limpar os dados
    df_cleaned = df.copy()
    anos_densidade = [col for col in df_cleaned.columns if col.isdigit()]
    years_to_remove = [str(year) for year in range(2009, 2013)]

    for col in anos_densidade:
        if col in years_to_remove:
            df_cleaned.drop(columns=col, inplace=True)
            continue
        df_cleaned[col] = (
            df_cleaned[col]
            .astype(str)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce")


    print("df_cleaned.head()")


    # Criar a pasta de destino se não existir
    os.makedirs(DENSIDADE_FINAL_FOLDER, exist_ok=True)

    # Salvar o arquivo limpo
    df_cleaned.to_csv(DENSIDADE_FINAL_CSV, index=False)
    print(f"Arquivo limpo salvo em: {DENSIDADE_FINAL_CSV}")


if __name__ == "__main__":
    main()