import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error, make_scorer
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import POP_ML_DATA_CSV, POP_WEIGHTS_CSV, POP_PRED_OFFICIAL_2025




# Criamos versões das métricas que arredondam o y_pred antes do cálculo
def mae_rounded(y_true, y_pred):
    return mean_absolute_error(y_true, np.round(y_pred).astype(int))


def mape_rounded(y_true, y_pred):
    return mean_absolute_percentage_error(y_true, np.round(y_pred).astype(int))


def r2_rounded(y_true, y_pred):
    return r2_score(y_true, np.round(y_pred).astype(int))


def train_and_predict_population_cv(df_ml, model):
    """
    Pipeline com TimeSeriesSplit para validar a robustez temporal.
    """
    # 1. Definir colunas
    drop_cols = ['target_pop', 'territory_code', 'Ano', 'NUTS3', "NUTS3_Name", "Name"]
    features = [col for col in df_ml.columns if col not in drop_cols]
    
    # 2. Preparar dados (Ordenados por Ano para CV temporal)
    df_sorted = df_ml.sort_values('Ano')
    X = df_sorted[features]
    y = df_sorted['target_pop']
    
    # 3. Configurar Cross-Validation Temporal
    # n_splits=5 treinará o modelo em 5 janelas de tempo diferentes
    tscv = TimeSeriesSplit(n_splits=5)
    
    # 5. Executar Cross Validation
    # Definimos as métricas que queremos monitorar
    # Transformamos em objetos que o sklearn entende
    rounded_scoring = {
        'mae': make_scorer(mae_rounded, greater_is_better=False),
        'r2': make_scorer(r2_rounded),
        'mape': make_scorer(mape_rounded, greater_is_better=False)
    }
    
    cv_results = cross_validate(model, X, y, cv=tscv, scoring=rounded_scoring, n_jobs=-1)
    
    # 6. Exibir resultados de Cross-Validation
    print(f"--- RESULTADOS CROSS-VALIDATION ({tscv.n_splits} folds) ---")
    print(f"R² Médio: {cv_results['test_r2'].mean():.4f} (+/- {cv_results['test_r2'].std():.4f})")
    print(f"MAE Médio: {abs(cv_results['test_mae'].mean()):.2f} habitantes")
    print(f"MAPE Médio: {abs(cv_results['test_mape'].mean()):.4f}")

    # 7. Treino Final (com todos os dados até 2024) para prever 2025
    model.fit(X, y)
    
    # Importância das Features do modelo final
    importance = pd.DataFrame({'feature': features, 'importance': model.feature_importances_})
    print("\nTop 5 Features (Modelo Final):")
    print(importance.sort_values(by='importance', ascending=False).head(5))

    return model, features, cv_results['test_mape'].mean()


def prepare_2025_dataset(df_ml, df_data):
    """
    Cria o input para a predição de 2025 seguindo as fórmulas da prepare_for_ml.
    df_ml: O dataset retornado pela tua função original (usaremos para pegar os últimos estados)
    df_data: O data.csv original (formato wide) para buscar baselines como o ano 2013.
    """
    
    # 1. Filtrar apenas os dados mais recentes (2024) para cada município
    # Isso serve de base para "empurrar" os lags para a frente
    df_2024 = df_ml[df_ml['Ano'] == 2024].copy()

    cols = df_2024.columns
    
    df_2025 = df_2024.copy()
    df_2025['Ano'] = 2025
    
    # ===== PASSO 4: DESLOCAR LAGS (SHIFT MANUAL) =====
    # O que era target_pop em 2024 vira pop_lag_1 em 2025
    for i in range(4, 1, -1):
        df_2025[f'pop_lag_{i}'] = df_2025[f'pop_lag_{i-1}']
        df_2025[f'weight_lag_{i}'] = df_2025[f'weight_lag_{i-1}']
    
    # Para o lag_1, usamos os valores reais de 2024
    # Nota: No teu Passo 13 da prepare_for_ml, apagaste a coluna 'Populacao' e 'Peso', 
    # mas o valor de 2024 está guardado na 'target_pop'.
    df_2025['pop_lag_1'] = df_2024['target_pop']
    
    # Para o weight_lag_1, vamos buscar ao data.csv (coluna weight_2024)
    weights_2024 = df_data.set_index('territory_code')['weight_2024']
    df_2025['weight_lag_1'] = df_2025['territory_code'].map(weights_2024)

    # ===== PASSO 5: DINÂMICA TEMPORAL =====
    # Crescimento entre 2024 e 2023
    df_2025['growth_rate'] = (df_2025['pop_lag_1'] - df_2025['pop_lag_2']) / df_2025['pop_lag_2']
    
    # Aceleração (Crescimento 2024 - Crescimento 2023)
    # O growth_rate de 2024 está na linha df_2024['growth_rate']
    df_2025['acceleration'] = df_2025['growth_rate'] - df_2024['growth_rate'].values

    # ===== PASSO 7 & 9: CONTEXTO NUTS3 =====
    # Recalcular totais da NUTS3 para 2024 (que será o lag_1 de 2025)
    nuts_totals_2024 = df_2025.groupby('NUTS3')['pop_lag_1'].transform('sum')
    
    df_2025['nuts_total_lag_3'] = df_2025['nuts_total_lag_2']
    df_2025['nuts_total_lag_2'] = df_2025['nuts_total_lag_1']
    df_2025['nuts_total_lag_1'] = nuts_totals_2024

    # Crescimento da NUTS3 para cálculo do relative_to_nuts
    nuts_growth_2024 = df_2025.groupby('NUTS3').apply(
        lambda x: (x['nuts_total_lag_1'].iloc[0] - x['nuts_total_lag_2'].iloc[0]) / x['nuts_total_lag_2'].iloc[0]
    ).to_dict()

    for i in range(3, 1, -1):
        df_2025[f'mun_growth_lag_{i}'] = df_2025[f'mun_growth_lag_{i-1}']
        df_2025[f'relative_to_nuts_growth_lag_{i}'] = df_2025[f'relative_to_nuts_growth_lag_{i-1}']

    df_2025['mun_growth_lag_1'] = df_2025['growth_rate']
    
    def calc_rel_growth_2025(row):
        n_growth = nuts_growth_2024.get(row['NUTS3'], 0)
        return row['mun_growth_lag_1'] - n_growth

    df_2025['relative_to_nuts_growth_lag_1'] = df_2025.apply(calc_rel_growth_2025, axis=1)

    # ===== PASSO 8: ESTABILIDADE =====
    df_2025['stability_score'] = df_2025[['pop_lag_1', 'pop_lag_2', 'pop_lag_3']].std(axis=1)
    df_2025['stability_score_norm'] = df_2025['stability_score'] / df_2025[['pop_lag_1', 'pop_lag_2', 'pop_lag_3']].mean(axis=1)

    # ===== PASSO 10 & 11: FLAGS E TARGET =====
    df_2025['is_census'] = 0 # 2025 não é censo
    # A target_pop de 2025 é o que o modelo vai preencher, 
    # mas para o DataFrame ter a mesma estrutura, podemos inicializar a NaN ou 0
    df_2025['target_pop'] = np.nan 

    # ===== PASSO 12: LONGO PRAZO =====
    pop_2013 = df_data.set_index('territory_code')['2013']
    
    def calc_long_term_2025(row):
        p13 = pop_2013.get(row['territory_code'], np.nan)
        n_anos = 2025 - 1 - 2013 # anos entre 2013 e 2024
        if n_anos <= 0 or pd.isna(p13) or p13 == 0: return 0
        return (row['pop_lag_1'] - p13) / n_anos

    df_2025['avg_growth_since_2013'] = df_2025.apply(calc_long_term_2025, axis=1)
    
    df_2025 = df_2025[cols]

    # Ordenar colunas para garantir que estão na mesma ordem que o modelo espera (features)
    # (Importante: Remover as colunas que não são features se necessário)
    return df_2025


def predict_2025_ml(model, features, df_prepared_for_2025):
    """
    Usa o modelo treinado para gerar a coluna de 2025.
    """
    X_2025 = df_prepared_for_2025[features]
    predictions = model.predict(X_2025)
    
    return np.round(predictions)


def get_better_results(data_ml, df_input, pred_oficial):
    """
    Testa diferentes modelos e retorna o DataFrame com as previsões do melhor.
    """
    configs = [
        {'n_estimators': 100, 'max_depth': None},
        {'n_estimators': 200, 'max_depth': 20},
        {'n_estimators': 300, 'max_depth': 10},
        {'n_estimators': 500, 'max_depth': 15}
    ]

    best_score = float('inf')
    best_features = best_n_estimators = best_max_depth = best_model_trained = None 
    

    for config in configs:
        print(f"\n> Testando configuração: {config}")
        
        # Criar o modelo com a configuração do loop
        model_instance: RandomForestRegressor = RandomForestRegressor(
            n_estimators=config['n_estimators'], 
            max_depth=config['max_depth'],
            random_state=42, 
            n_jobs=-1
        )

        # Treinar e obter o score (MAPE Médio da Cross-Validation)
        trained_model, features, neg_score = train_and_predict_population_cv(data_ml, model_instance)
        
        # O sklearn devolve negativo, convertemos para positivo para comparar
        current_score = abs(neg_score)
        
        if current_score < best_score:
            best_score = current_score
            best_model_trained = trained_model
            best_n_estimators=config['n_estimators'], 
            best_max_depth=config['max_depth'],
            best_features = features
            print(f"✨ Novo melhor modelo encontrado! MAPE: {best_score:.4f}")

    # 2. Fazer as previsões com o Vencedor
    print(f"\n🏆 Melhor Score obtido (MAPE CV: {best_score:.4f})")
    best_model_config = {"n_estimators": best_n_estimators, "max_depth": best_max_depth}
    print(f"Melhor modelo escolhido: {best_model_config}")
    preds_2025 = predict_2025_ml(best_model_trained, best_features, df_input)

    df_input['target_pop'] = preds_2025 
    
    # 3. Comparação Final com dados Oficiais
    compare_results(pred_df=df_input, oficial_pred_df=pred_oficial)

    return df_input


def compare_results(pred_df, oficial_pred_df):
    """
    Agrupa as previsões dos municípios por NUTS3 e compara com os dados oficiais.
    """
    # 1. Limpeza do DataFrame oficial
    oficial_pred_df['Name'] = (
        oficial_pred_df['Geopolitical entity (reporting)']
        .str.replace(" (NUTS 2021)", "", regex=False)
        .str.strip()
    )
    
    # Filtrar apenas o ano de 2025 e colunas necessárias
    oficial_2025 = oficial_pred_df[oficial_pred_df["TIME_PERIOD"] == 2025][["Name", "OBS_VALUE"]]
    oficial_2025.columns = ["NUTS3_Name", "Valor_Oficial"]

    # 2. Agrupar as tuas previsões municipais por NUTS3
    # Somamos a 'target_pop' de todos os municípios que pertencem à mesma NUTS3_Name
    minhas_preds_agrupadas = pred_df.groupby("NUTS3_Name")["target_pop"].sum().reset_index()
    minhas_preds_agrupadas.columns = ["NUTS3_Name", "Minha_Previsao"]

    # 3. Juntar os dois datasets para comparação
    comparativo = pd.merge(minhas_preds_agrupadas, oficial_2025, on="NUTS3_Name", how="inner")

    y_true = comparativo['Valor_Oficial']
    y_pred = comparativo['Minha_Previsao']

    # Calculamos as métricas
    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # 4. Exibir Resultados Detalhados
    print("\n" + "="*85)
    print(f"{'NUTS3 (Região)':<30} | {'Soma Mun (2025)':>15} | {'Oficial (2025)':>15} | {'Erro %':>10}")
    print("-" * 85)
    
    # Cálculo de erro por linha para o print
    comparativo['Erro_Perc'] = ((y_pred - y_true) / y_true) * 100
    
    for _, row in comparativo.sort_values("Erro_Perc").iterrows():
        print(f"{row['NUTS3_Name']:<30} | {row['Minha_Previsao']:>15.0f} | {row['Valor_Oficial']:>15.0f} | {row['Erro_Perc']:>9.2f}%")

    print("-" * 85)
    print(f"MÉTRICAS GLOBAIS (NUTS3 Level):")
    print(f"MAE (Erro Médio Absoluto): {mae:.2f} habitantes")
    print(f"MAPE (Erro Médio Percentual): {mape*100:.2f}%")
    print(f"R² Score (Correlação): {r2:.4f}")
    print("="*85)

    return comparativo
    

def main():

    data_ml = pd.read_csv(POP_ML_DATA_CSV, sep=",")
    df_data = pd.read_csv(POP_WEIGHTS_CSV, sep=",")
    pred_oficial = pd.read_csv(POP_PRED_OFFICIAL_2025, sep=",")

    # 1. Preparar os dados de entrada para 2025
    df_input_2025 = prepare_2025_dataset(df_ml=data_ml, df_data=df_data)
    df_try = df_input_2025.copy()

    better_results = get_better_results(
        data_ml=data_ml, 
        df_input=df_try, 
        pred_oficial=pred_oficial)
    
    
    # Opcional: Salvar para CSV
    # better_results.to_csv(output_file, index=False)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")