import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CSV_FILE = "15paises_14anos_kW.csv"


def load_csv_flexibly(file_path: str) -> pd.DataFrame:
    """
    Tenta ler o CSV com diferentes separadores/comas decimais.
    """
    attempts = [
        {"sep": ",", "decimal": "."},
        {"sep": ";", "decimal": ","},
        {"sep": ";", "decimal": "."},
        {"sep": ",", "decimal": ","},
    ]

    last_error = None
    for opts in attempts:
        try:
            df = pd.read_csv(file_path, **opts)
            if df.shape[1] > 1:
                return df
        except Exception as exc:
            last_error = exc

    raise ValueError(f"Não consegui ler o ficheiro {file_path}. Erro: {last_error}")


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa nomes das colunas.
    """
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def find_country_column(df: pd.DataFrame) -> str:
    """
    Procura a coluna do país. Se não encontrar, assume a 1.ª coluna.
    """
    candidates = ["country", "pais", "país", "country_name", "nome_pais", "nome_país"]
    lower_map = {col.lower(): col for col in df.columns}

    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]

    return df.columns[0]


def extract_year_columns(df: pd.DataFrame) -> list[str]:
    """
    Encontra colunas que são anos, ex: 2010, 2011, ..., 2023.
    """
    year_cols = []
    for col in df.columns:
        if re.fullmatch(r"\d{4}", str(col).strip()):
            year_cols.append(col)
    return year_cols


def to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte tabela wide para formato longo:
    country | year | cost_usd_per_kw
    """
    df = clean_column_names(df)
    country_col = find_country_column(df)
    year_cols = extract_year_columns(df)

    if not year_cols:
        raise ValueError(
            "Não encontrei colunas de anos no CSV. "
            "As colunas devem ter nomes como 2010, 2011, ..., 2023."
        )

    long_df = df[[country_col] + year_cols].copy()
    long_df = long_df.rename(columns={country_col: "country"})

    long_df = long_df.melt(
        id_vars="country",
        value_vars=year_cols,
        var_name="year",
        value_name="cost_usd_per_kw",
    )

    long_df["country"] = long_df["country"].astype(str).str.strip()
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df["cost_usd_per_kw"] = pd.to_numeric(long_df["cost_usd_per_kw"], errors="coerce")

    long_df = long_df.dropna(subset=["country", "year", "cost_usd_per_kw"]).copy()
    long_df["year"] = long_df["year"].astype(int)

    # Mantém só custos positivos, porque vamos usar log()
    long_df = long_df[long_df["cost_usd_per_kw"] > 0].copy()

    return long_df.sort_values(["country", "year"]).reset_index(drop=True)


def build_model() -> Pipeline:
    """
    Modelo:
        log(cost) ~ year + country
    com one-hot encoding para o país.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("country", OneHotEncoder(handle_unknown="ignore", drop=None), ["country"]),
            ("year", "passthrough", ["year"]),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )

    return model


def temporal_train_test_split(df_long: pd.DataFrame, test_years: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide temporalmente:
    - treino: anos fora de test_years
    - teste: anos em test_years
    """
    train_df = df_long[~df_long["year"].isin(test_years)].copy()
    test_df = df_long[df_long["year"].isin(test_years)].copy()
    return train_df, test_df


def evaluate_model(model: Pipeline, test_df: pd.DataFrame) -> None:
    """
    Avalia o modelo no conjunto de teste.
    """
    X_test = test_df[["country", "year"]]
    y_test = np.log(test_df["cost_usd_per_kw"])

    y_pred_log = model.predict(X_test)
    y_pred = np.exp(y_pred_log)
    y_true = test_df["cost_usd_per_kw"].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    print("\n=== Avaliação no conjunto de teste ===")
    print(f"MAE  : {mae:.2f} USD/kW")
    print(f"RMSE : {rmse:.2f} USD/kW")
    print(f"R²   : {r2:.4f}")
    print(f"MAPE : {mape:.2f}%")

    results = test_df[["country", "year", "cost_usd_per_kw"]].copy()
    results["predicted_usd_per_kw"] = y_pred
    results["abs_error"] = np.abs(results["cost_usd_per_kw"] - results["predicted_usd_per_kw"])

    print("\n=== Exemplos de previsões no teste ===")
    print(results.sort_values(["country", "year"]).head(20).to_string(index=False))


def fit_and_test(df_long: pd.DataFrame) -> Pipeline:
    """
    Treina e testa o modelo.
    Estratégia:
    - teste nos anos mais recentes conhecidos: 2022 e 2023
    - treino no resto
    """
    test_years = [2022, 2023]
    train_df, test_df = temporal_train_test_split(df_long, test_years=test_years)

    if train_df.empty or test_df.empty:
        raise ValueError("Split treino/teste inválido. Verifica os anos disponíveis no CSV.")

    model = build_model()

    X_train = train_df[["country", "year"]]
    y_train = np.log(train_df["cost_usd_per_kw"])

    model.fit(X_train, y_train)

    print("Modelo treinado com sucesso.")
    print(f"Nº observações treino: {len(train_df)}")
    print(f"Nº observações teste : {len(test_df)}")

    evaluate_model(model, test_df)

    return model


def refit_full_model(df_long: pd.DataFrame) -> Pipeline:
    """
    Re-treina o modelo com todos os dados disponíveis
    para depois prever Portugal 2024 e 2025.
    """
    model = build_model()
    X_full = df_long[["country", "year"]]
    y_full = np.log(df_long["cost_usd_per_kw"])
    model.fit(X_full, y_full)
    return model


def find_portugal_name(df_long: pd.DataFrame) -> str | None:
    """
    Tenta encontrar o nome usado para Portugal no CSV.
    """
    countries = set(df_long["country"].str.lower().unique())

    for name in ["portugal", "portugal "]:
        if name in countries:
            original = df_long.loc[df_long["country"].str.lower() == name, "country"].iloc[0]
            return original

    return None


def predict_portugal(model: Pipeline, portugal_name: str) -> pd.DataFrame:
    """
    Prevê 2024 e 2025 para Portugal.
    """
    future_df = pd.DataFrame(
        {
            "country": [portugal_name, portugal_name],
            "year": [2024, 2025],
        }
    )

    pred_log = model.predict(future_df)
    pred = np.exp(pred_log)

    future_df["predicted_usd_per_kw"] = pred
    return future_df


def main() -> None:
    file_path = Path(__file__).resolve().parent / CSV_FILE

    if not file_path.exists():
        raise FileNotFoundError(f"Não encontrei o ficheiro: {file_path}")

    raw_df = load_csv_flexibly(str(file_path))
    long_df = to_long_format(raw_df)

    print("=== Dados preparados ===")
    print(long_df.head().to_string(index=False))
    print(f"\nTotal de linhas: {len(long_df)}")
    print(f"Países: {long_df['country'].nunique()}")
    print(f"Anos: {long_df['year'].min()} - {long_df['year'].max()}")

    # 1) Treinar e testar
    _ = fit_and_test(long_df)

    # 2) Re-treinar com todos os dados
    final_model = refit_full_model(long_df)

    # 3) Prever Portugal
    portugal_name = find_portugal_name(long_df)
    if portugal_name is None:
        available = sorted(long_df["country"].unique())
        raise ValueError(
            "Não encontrei Portugal no CSV. "
            f"Países disponíveis: {available}"
        )

    portugal_predictions = predict_portugal(final_model, portugal_name)

    print("\n=== Previsões para Portugal ===")
    print(portugal_predictions.to_string(index=False))

    # Guarda previsões em CSV
    output_path = Path(__file__).resolve().parent / "previsoes_portugal_2024_2025.csv"
    portugal_predictions.to_csv(output_path, index=False)
    print(f"\nPrevisões guardadas em: {output_path}")


if __name__ == "__main__":
    main()