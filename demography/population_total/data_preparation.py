import os
import pandas as pd
import numpy as np
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import POP_PRED_OFFICIAL_2025, POP_TOTAL_CSV, POP_TOTAL_INPUT_FOLDER, POP_TOTAL_INTERMEDIATE_FOLDER, POP_WEIGHTS_CSV, POP_ML_DATA_CSV

os.makedirs(POP_TOTAL_INPUT_FOLDER, exist_ok=True)

# Criar dataset com vars de IDs unicos para NUTS de 2024
def create_territory_code_pure_nuts2024(df):
    # 1. Identificação básica e limpeza de nomes
    # Mantemos o Level original: se é NUTS III no ficheiro, fica NUTS3
    df["Level"] = df["Âmbito Geográfico"].apply(lambda x: "NUTS3" if "NUTS III" in x else "MUN")
    df.rename(columns={"Anos": "Name"}, inplace=True)
    df["Name"] = df["Name"].str.strip()
    
    df["NUTS3_Name"] = None
    df["NUTS3"] = None
    last_NUTS3_name = None
    last_NUTS3_code = None
    NUTS3_count = 0
    mun_count = 0
    anos = [str(ano) for ano in range(1982, 2025)]

    # Passo 1: Limpeza numérica mínima (apenas para manter consistência com a outra função)
    for ano in anos:
        if ano in df.columns:
            df[ano] = df[ano].astype(str).str.replace(r'[\s\xa0┴x/]+', '', regex=True)
            df[ano] = pd.to_numeric(df[ano], errors='coerce').fillna(0)

    # Passo 2: Atribuir códigos seguindo estritamente a ordem do ficheiro (NUTS 2024)
    for index, row in df.iterrows():
        if row["Level"] == 'NUTS3':
            last_NUTS3_name = row["Name"]
            last_NUTS3_code = f"NUTS3_{NUTS3_count}"
            
            df.at[index, 'NUTS3_Name'] = last_NUTS3_name
            df.at[index, 'NUTS3'] = last_NUTS3_code
            df.at[index, 'territory_code'] = last_NUTS3_code
            NUTS3_count += 1
        else:
            # Aqui não há IFs para Sertã ou Vila de Rei, 
            # eles herdam a NUTS3 que estiver imediatamente acima (Beira Baixa)
            df.at[index, 'NUTS3_Name'] = last_NUTS3_name
            df.at[index, 'NUTS3'] = last_NUTS3_code
            df.at[index, 'territory_code'] = f"MUN_{mun_count}"
            mun_count += 1

    # Ordenar colunas conforme desejado
    cols = ["Level", "NUTS3", "NUTS3_Name", "territory_code", "Name"] + anos
    return df[cols]


def create_territory_code_convert_nuts2021(df):
    # 1. Identificação básica
    # Forçamos a identificação de NUTS3 se o nome for uma das regiões autónomas ou contiver NUTS III
    regioes_autonomas = ['Região Autónoma dos Açores', 'Região Autónoma da Madeira', 'Área Metropolitana de Lisboa']
    
    df["Level"] = df.apply(
        lambda row: "NUTS3" if ("NUTS III" in str(row["Âmbito Geográfico"]) or row["Anos"] in regioes_autonomas) else "MUN", 
        axis=1
    )
    
    df.rename(columns={"Anos": "Name"}, inplace=True)
    df["Name"] = df["Name"].str.strip()
    
    mapa_nuts_2021 = {
        'Grande Lisboa': 'Área Metropolitana de Lisboa',
        'Península de Setúbal': 'Área Metropolitana de Lisboa',
        'Ilha de São Miguel': 'Região Autónoma dos Açores',
        'Ilha Terceira': 'Região Autónoma dos Açores',
        'Ilha do Faial': 'Região Autónoma dos Açores',
        'Ilha do Pico': 'Região Autónoma dos Açores',
        'Ilha de São Jorge': 'Região Autónoma dos Açores',
        'Ilha Graciosa': 'Região Autónoma dos Açores',
        'Ilha das Flores': 'Região Autónoma dos Açores',
        'Ilha de Santa Maria': 'Região Autónoma dos Açores',
        'Ilha do Corvo': 'Região Autónoma dos Açores',
        'Ilha da Madeira': 'Região Autónoma da Madeira',
        'Ilha de Porto Santo': 'Região Autónoma da Madeira'
    }
    
    df["NUTS3_Name"] = None
    last_NUTS3_name = None
    mun_count = 0
    anos = [str(ano) for ano in range(1982, 2025)]

    # Limpeza numérica
    for ano in anos:
        df[ano] = pd.to_numeric(df[ano].astype(str).str.replace(r'[\s\xa0┴x/]+', '', regex=True), errors='coerce').fillna(0)

    # Passo 2: Atribuição de nomes e filtragem
    for index, row in df.iterrows():
        name_clean = row["Name"]
        
        if row["Level"] == 'NUTS3':
            last_NUTS3_name = mapa_nuts_2021.get(name_clean, name_clean)
            df.at[index, 'NUTS3_Name'] = last_NUTS3_name
            df.at[index, 'Name'] = last_NUTS3_name 
        else:
            # Proteção: Se o nome do "município" for igual a uma região, mudamos para NUTS3
            if name_clean in regioes_autonomas:
                df.at[index, 'Level'] = 'NUTS3'
                last_NUTS3_name = name_clean
                df.at[index, 'NUTS3_Name'] = name_clean
            else:
                if name_clean in ['Sertã', 'Vila de Rei']:
                    df.at[index, 'NUTS3_Name'] = 'Médio Tejo'
                else:
                    df.at[index, 'NUTS3_Name'] = last_NUTS3_name
                
                df.at[index, 'territory_code'] = f"MUN_{mun_count}"
                mun_count += 1

    # Passo 3: Agregação rigorosa
    # Isto remove as duplicatas da Madeira e Açores
    df_mun = df[df['Level'] == 'MUN'].copy()
    df_nuts = df[df['Level'] == 'NUTS3'].copy()

    # Agregamos NUTS3 pelo nome (garante que só existe 1 Madeira e 1 Açores)
    df_nuts_grouped = df_nuts.groupby('NUTS3_Name')[anos].sum().reset_index()
    df_nuts_grouped['Level'] = 'NUTS3'
    df_nuts_grouped['Name'] = df_nuts_grouped['NUTS3_Name']

    df_final = pd.concat([df_nuts_grouped, df_mun], ignore_index=True)
    
    # Gerar IDs finais
    nomes_unicos_nuts = sorted(df_final[df_final['Level'] == 'NUTS3']['NUTS3_Name'].unique())
    mapa_id_nuts = {nome: f"NUTS3_{i}" for i, nome in enumerate(nomes_unicos_nuts)}
    df_final['NUTS3'] = df_final['NUTS3_Name'].map(mapa_id_nuts)
    
    mask_nuts = df_final['Level'] == 'NUTS3'
    df_final.loc[mask_nuts, 'territory_code'] = df_final.loc[mask_nuts, 'NUTS3']

    # DROP DUPLICATES FINAL (Apólice de seguro)
    df_final = df_final.drop_duplicates(subset=['territory_code', 'Level'])

    return df_final[["Level", "NUTS3", "NUTS3_Name", "territory_code", "Name"] + anos]

# Implementar as funcoes anteriores com mudanca de um argument
def create_territory_code(df, convert_nuts2021=True):
    if convert_nuts2021:
        df = create_territory_code_convert_nuts2021(df.copy())
    else:
        df = create_territory_code_convert_nuts2021(df.copy())

    return df 


# Comparar ambos os df com NUTS diferentes, para ter a certeza que o mapeamento foi utilizado corretamente
def compare_mapping_nuts3(df_nuts2021, df_nuts2024):
    print("\n" + "="*50)
    print("VALIDAÇÃO DE MAPEAMENTO: NUTS 2024 vs 2021")
    print("="*50)
    
    mun_2024 = set(df_nuts2024[df_nuts2024['Level'] == 'MUN']["Name"])
    mun_2021 = set(df_nuts2021[df_nuts2021['Level'] == 'MUN']["Name"])
    both_mun = set(mun_2021) & set(mun_2024)
    
    print(f"Número de Municípios no dataset original (2024): {len(mun_2024)}")
    print(f"Número de Municípios no dataset convertido (2021): {len(mun_2021)}")
    print(f"Número de Municípios em ambos: {len(both_mun)}")
    
    
    if len(mun_2024) == len(mun_2021) == len(both_mun):
        print("✅ Sucesso: O número de municípios mantém-se inalterado.")
        print(f"Lista de munícipios em ambos:{both_mun}")
        
    else:
        print("⚠️ Atenção: Há uma discrepância no número de municípios!")
        print(f"Lista de municípios antes da conversão: {mun_2024}")
        print(f"Lista de municípios após a conversão: {mun_2021}")


# Analisar concelhos e nuts para garantir que nao ha erros nos dados presentes
def analysis_concelhos(df, municipio=True):
    if municipio:
        level = "MUN"
    else:
        level = "NUTS3"
    print("\n" + "="*80)
    print("RELATÓRIO DETALHADO DE ERROS E METADADOS POR " + level.upper())
    print("="*80)

    mapa_erros = {
        '┴': 'Quebra de série',
        'Pro': 'Valor provisório',
        'N': 'Valor negligenciável',
        '...': 'Confidencial',
        'x': 'Valor não disponível',
        's': 'Valor estimado',
        '//': 'Não aplicável',
        'f': 'Valor previsto',
        'u': 'Valor incerto ou não confiável',
        '-': 'Ausência de valor',
        'Rv': 'Valor revisto',
        '§': 'Dado com coeficiente de variação elevado',
        'Pre': 'Valor preliminar',
        'e': 'Dado inferior a metade do módulo da unidade utilizada',
        '(R)': 'Dados retificados pela entidade responsável',
        'fr': 'Dado de fiabilidade reduzida'
    }

    anos = [str(ano) for ano in range(1982, 2025)]
    # Filtrar apenas municípios para não analisar os totais das NUTS
    municipios_df = df[df['Level'] == level].copy()
    
    erros_detectados = []

    for ano in anos:
        if ano not in municipios_df.columns:
            continue
            
        for idx, valor_bruto in municipios_df[ano].items():
            # Se for NaN (nulo), tratamos como ausência de valor
            if pd.isna(valor_bruto):
                erros_detectados.append({
                    'NUTS3': municipios_df.at[idx, 'NUTS3'],
                    'Ano': ano,
                    'Municipio': municipios_df.at[idx, 'Name'],
                    'Tipo de Erro': 'Ausência de valor',
                    'Valor Original': 'null'
                })
                continue

            # Converter para string para poder procurar os símbolos da legenda
            valor_str = str(valor_bruto).strip()
            encontrados = []
            
            for simbolo, descricao in mapa_erros.items():
                if simbolo in valor_str:
                    encontrados.append(descricao)
            
            if encontrados:
                erros_detectados.append({
                    'NUTS3': municipios_df.at[idx, 'NUTS3'],
                    'Ano': ano,
                    'Municipio': municipios_df.at[idx, 'Name'],
                    'Tipo de Erro': " | ".join(encontrados),
                    'Valor Original': valor_str
                })

    if not erros_detectados:
        print("✅ Nenhum erro ou metadado detectado nos municípios.")
        return pd.DataFrame(columns=['NUTS3', 'Ano', 'Municipio', 'Tipo de Erro', 'Valor Original']), municipios_df

    df_report = pd.DataFrame(erros_detectados)

    df_report = df_report.sort_values(by=['Ano','NUTS3', 'Municipio'], ascending=[False, True, True])

    print(df_report.to_string(index=False, columns=['NUTS3', 'Ano', 'Municipio', 'Tipo de Erro', 'Valor Original']))

    resumo_viabilidade = df_report.groupby(['NUTS3', 'Ano']).size().reset_index(name='Qtd_Problemas')
    n_recuperaveis = len(resumo_viabilidade[resumo_viabilidade['Qtd_Problemas'] == 1])
    n_criticos = len(resumo_viabilidade[resumo_viabilidade['Qtd_Problemas'] > 1])

    print("\n" + "-"*30)
    print(f"RESUMO DE VIABILIDADE:")
    print(f"Total de ocorrências: {len(df_report)}")
    print(f"Anos/NUTS recuperáveis (máx 1 erro): {n_recuperaveis}")
    print(f"Anos/NUTS críticos (>1 erro): {n_criticos}")
    print("="*80)

    return df_report, municipios_df


# Preparar o dataset tendo em conta os erros que podemos alcancar
def prepare_dataset(df):
    anos = [str(ano) for ano in range(2013, 2025)]
    
    for ano in anos:
        if ano in df.columns:
            # 1. Converter para string e limpar espaços
            df[ano] = df[ano].astype(str).str.strip()
            
            # 2. Lidar com o símbolo ┴ (Quebra de série)
            # Se o símbolo existir, apanhamos o valor que vem DEPOIS dele
            # Ex: "107 251;┴ 89 677" -> "89 677"
            df[ano] = df[ano].str.split('┴').str[-1]
            
            # 3. Remover caracteres não numéricos restantes (espaços, x, //, etc)
            # O regex [^\d] mantém apenas dígitos
            df[ano] = df[ano].str.replace(r'[^\d]', '', regex=True)
            
            # 4. Converter para float (numérico)
            # errors='coerce' transforma o que sobrar de texto vazio em NaN
            df[ano] = pd.to_numeric(df[ano], errors='coerce')
            
    return df


# Obter o dataset com os pesos relativos de municipios face ao NUTS3
def get_weights(df):
    anos = [str(ano) for ano in range(2013, 2025)]
    
    # Criar dicionário para os totais das NUTS3
    nuts_totais = df[df['Level'] == 'NUTS3'].set_index('territory_code')[anos]

    for ano in anos:
        weight_col = f"weight_{ano}"
        
        # Cálculo inicial
        def initial_weight(row):
            if row['Level'] == 'NUTS3': return 1.0
            total_regiao = nuts_totais.loc[row['NUTS3'], ano]
            valor_mun = row[ano]
            if pd.isna(valor_mun) or total_regiao == 0 or pd.isna(total_regiao):
                return np.nan
            return valor_mun / total_regiao

        df[weight_col] = df.apply(initial_weight, axis=1)

        # Lógica de Preenchimento e Normalização por NUTS3
        mask_mun = df['Level'] == 'MUN'
        
        for nuts in df['NUTS3'].unique():
            curr_nuts_mask = (df['NUTS3'] == nuts) & (mask_mun)
            
            nans = df.loc[curr_nuts_mask, weight_col].isnull().sum()
            soma_conhecida = df.loc[curr_nuts_mask, weight_col].sum()

            # Caso A: Apenas 1 município em falta -> Peso Residual
            if nans == 1:
                residual = max(0, 1.0 - soma_conhecida)
                df.loc[curr_nuts_mask & df[weight_col].isnull(), weight_col] = residual
            
            # Caso B: Mais que 1 em falta -> Preenche com 0 (ou outra lógica)
            elif nans > 1:
                df.loc[curr_nuts_mask & df[weight_col].isnull(), weight_col] = 0.0
            
            # 3. NORMALIZAÇÃO FINAL (O "Pulo do Gato")
            # Força a soma de todos os municípios da NUTS a ser exatamente 1.0
            soma_final = df.loc[curr_nuts_mask, weight_col].sum()
            if soma_final > 0 and not np.isclose(soma_final, 1.0):
                df.loc[curr_nuts_mask, weight_col] = df.loc[curr_nuts_mask, weight_col] / soma_final

    return df


# Ter a certeza que a soma das partes e igual a 100%
def test_weight_df(df):
    print("\n" + "="*50)
    print("TESTE DE VALIDAÇÃO: SOMA DOS PESOS (MUN por NUTS3)")
    print("="*50)
    
    anos = [str(ano) for ano in range(2013, 2025)]
    df_mun = df[df['Level'] == 'MUN']
    
    # Agrupar por NUTS3 e somar os pesos de cada ano
    test_sum = df_mun.groupby('NUTS3')[[f"weight_{ano}" for ano in anos]].sum()
    
    # Verificação com tolerância (devido a floats, 0.999999999 é considerado 1.0)
    is_correct = np.isclose(test_sum, 1.0, atol=1e-5)
    
    # Criar relatório de erros
    erros = []
    for row_idx, nuts_name in enumerate(test_sum.index):
        for col_idx, ano_col in enumerate(test_sum.columns):
            if not is_correct[row_idx, col_idx]:
                erros.append({
                    'NUTS3': nuts_name,
                    'Coluna': ano_col,
                    'Soma Encontrada': test_sum.iloc[row_idx, col_idx]
                })

    if not erros:
        print("✅ SUCESSO: Todos os municípios somam 100% em todas as NUTS e anos!")
    else:
        print(f"❌ ERRO: Encontradas {len(erros)} inconsistências na soma dos pesos.")
        df_erros = pd.DataFrame(erros)
        print(df_erros.head(20)) # Mostra os primeiros 20 erros

    return test_sum


# Comparar o dataset dos pesos com o das predicoes para ter a certeza que comparamos a mesma realidade
def compare_weights(df_weight, prediction_df):
    prediction_df['Geopolitical entity (reporting)'] = (
        prediction_df['Geopolitical entity (reporting)']
        .str.replace(" (NUTS 2021)", "", regex=False)
        .str.strip()
    )


    both_nuts3 = set(df_weight[df_weight['Level'] == 'NUTS3']['Name'].unique()) & set(prediction_df['Geopolitical entity (reporting)'].unique())
    print(f"Previsão oficial para 2025:\n{prediction_df.head()}")
    print(f"Número de NUTS3 com previsão oficial para 2025: {prediction_df['Geopolitical entity (reporting)'].nunique()}")
    print(f"Número de NUTS3 únicos no dataset com pesos: {df_weight['NUTS3'].nunique()}")
    print("Comparação entre NUTS3 do dataset e previsão oficial para 2025:")
    print(f"NUTS3 presentes em ambos os datasets: {both_nuts3}")
    print(f"NUTS3 presentes apenas no dataset de pesos: {set(df_weight[df_weight['Level'] == 'NUTS3']['Name'].unique()) - both_nuts3}")
    print(f"NUTS3 presentes apenas na previsão oficial: {set(prediction_df['Geopolitical entity (reporting)'].unique()) - both_nuts3}")


def prepare_for_ml(df_weight):
    """
    Prepara os dados para o modelo de Machine Learning, transformando dados em formato wide
    (por ano em colunas) para formato long (por linha), e criar features avançadas para predição.
    
    Args:
        df_weight (pd.DataFrame): DataFrame com população e pesos por território e ano
        
    Returns:
        pd.DataFrame: Dataset preparado para ML com features engineered e apenas municípios
    """
    anos = [str(ano) for ano in range(2013, 2025)]
    id_cols = ["Level", "NUTS3", "NUTS3_Name", "territory_code", "Name"]
    
    # ===== PASSO 1: TRANSFORMAR DADOS DE WIDE PARA LONG =====
    # Converter colunas de anos (2013, 2014, ..., 2024) em linhas
    # Resultado: cada linha = um território em um ano específico
    df_pop_long = pd.melt(df_weight, id_vars=id_cols, value_vars=anos, 
                          var_name='Ano', value_name='Populacao')
    
    # Fazer o mesmo para os pesos (weight_2013, weight_2014, ..., weight_2024)
    weight_cols = [f"weight_{ano}" for ano in anos]
    df_weight_long = pd.melt(df_weight, id_vars=['territory_code'], value_vars=weight_cols, 
                             var_name='Ano_Weight', value_name='Peso')
    
    # ===== PASSO 2: SINCRONIZAR ANOS ENTRE POPULAÇÃO E PESOS =====
    # Remover o prefixo "weight_" da coluna Ano_Weight para poder fazer merge
    # Ex: "weight_2013" -> "2013"
    df_weight_long['Ano'] = df_weight_long['Ano_Weight'].str.replace('weight_', '').astype(int)
    df_pop_long['Ano'] = df_pop_long['Ano'].astype(int)
    
    # Combinar população e peso na mesma linha, alinhados pelo território e ano
    df_long = pd.merge(df_pop_long, df_weight_long[['territory_code', 'Ano', 'Peso']], 
                       on=['territory_code', 'Ano'])

    # ===== PASSO 3: PREPARAR PARA CRIAR LAGS (HISTÓRICO) =====
    # Ordenar por território e ano para que o shift() funcione corretamente
    # (shift cria valores do período anterior)
    df_long = df_long.sort_values(['territory_code', 'Ano'])

    # ===== PASSO 4: CRIAR FEATURES DE LAG (VALORES ANTERIORES) =====
    # Para cada território, criar colunas com valores de 1, 2 e 3 anos anteriores
    # Exemplo: se estamos em 2024, pop_lag_1 = população 2023, pop_lag_2 = população 2022, etc.
    for i in range(1, 5):
        df_long[f'pop_lag_{i}'] = df_long.groupby('territory_code')['Populacao'].shift(i)
        df_long[f'weight_lag_{i}'] = df_long.groupby('territory_code')['Peso'].shift(i)

    # ===== PASSO 5: CRIAR FEATURES DE DINÂMICA TEMPORAL =====
    # Taxa de crescimento simples entre anos consecutivos
    # Fórmula: (Pop(t-1) - Pop(t-2)) / Pop(t-2)
    # Representa: "Quantos % cresceu a população no último ano?"
    df_long['growth_rate'] = (df_long['pop_lag_1'] - df_long['pop_lag_2']) / df_long['pop_lag_2']
    
    # Aceleração: mudança na taxa de crescimento
    # Fórmula: growth_rate(t) - growth_rate(t-1)
    # Representa: "A tendência de crescimento está a acelerar ou desacelerar?"
    df_long['acceleration'] = df_long['growth_rate'] - df_long.groupby('territory_code')['growth_rate'].shift(1)

    # ===== PASSO 6: MÉTRICAS AVANÇADAS - CONTEXTO DA NUTS3 =====
    # Isolar apenas as linhas de NUTS3 (totais regionais) para calcular o contexto regional
    df_nuts_only = df_long[df_long['Level'] == 'NUTS3'].copy()
    
    # Para cada lag (1, 2, 3 anos atrás), calcular a taxa de crescimento da NUTS3
    # Isto permite ao modelo entender a dinâmica regional
    for i in range(1, 4):
        # Fórmula: (Pop_NUTS(Ano-i) - Pop_NUTS(Ano-i-1)) / Pop_NUTS(Ano-i-1)
        df_nuts_only[f'nuts_growth_lag_{i}'] = (df_nuts_only[f'pop_lag_{i}'] - df_nuts_only[f'pop_lag_{i+1}']) / df_nuts_only[f'pop_lag_{i+1}']

    # Criar um mapa (dicionário) para lookup rápido: (NUTS3_ID, Ano) -> crescimentos
    # Isto facilita aplicar estas métricas aos municípios depois
    nuts_growth_map = df_nuts_only.set_index(['NUTS3', 'Ano'])[[f'nuts_growth_lag_{i}' for i in range(1, 4)]].to_dict('index')

    # ===== PASSO 7: APLICAR MÉTRICAS REGIONAIS AO NÍVEL MUNICIPAL =====
    # Para cada município, calcular como ele cresceu RELATIVAMENTE à sua NUTS3
    for i in range(1, 4):
        # a) Taxa de crescimento do município (igual à da NUTS3, mas calculada pro município)
        # Fórmula: (Pop_Mun(t-i) - Pop_Mun(t-i-1)) / Pop_Mun(t-i-1)
        df_long[f'mun_growth_lag_{i}'] = (df_long[f'pop_lag_{i}'] - df_long[f'pop_lag_{i+1}']) / df_long[f'pop_lag_{i+1}']

        # b) Diferença entre crescimento do município e crescimento da região
        # Fórmula: growth_mun - growth_nuts3
        # Interpretação: 
        #   - Positivo: município cresce mais que a região (atrai população)
        #   - Negativo: município cresce menos que a região (perde população relativamente)
        def get_rel_growth(row, lag_num):
            # Buscar os crescimentos da NUTS3 para este território e ano
            nuts_vals = nuts_growth_map.get((row['NUTS3'], row['Ano']), {})
            n_growth = nuts_vals.get(f'nuts_growth_lag_{lag_num}', 0)
            m_growth = row[f'mun_growth_lag_{lag_num}']
            return m_growth - n_growth

        df_long[f'relative_to_nuts_growth_lag_{i}'] = df_long.apply(lambda x: get_rel_growth(x, i), axis=1)

    # ===== PASSO 8: ESTABILIDADE DEMOGRÁFICA =====
    # Calcular a variabilidade da população nos últimos 3 anos
    # Desvio padrão dos valores de população (pop_lag_1, pop_lag_2, pop_lag_3)
    # Alto = população muito volátil; Baixo = população estável
    df_long['stability_score'] = df_long[['pop_lag_1', 'pop_lag_2', 'pop_lag_3']].std(axis=1)

    # Normalizar pela média da população para tornar comparable entre territórios
    # Fórmula: stability_score / média_população
    # Interpreta-se como: "Desvio padrão em % da população média"
    # Exemplo: Um desvio de 100 pessoas é muito em Barrancos (1000 hab) mas pouco em Lisboa (500k hab)
    df_long['stability_score_norm'] = df_long['stability_score'] / df_long[['pop_lag_1', 'pop_lag_2', 'pop_lag_3']].mean(axis=1)

    # ===== PASSO 9: CONTEXTO REGIONAL (TAMANHO DA NUTS3) =====
    # Adicionar o tamanho total da NUTS3 nos últimos 3 anos
    # Isto ajuda o modelo a entender se um município é de uma região pequena ou grande
    nuts_totals = df_long[df_long['Level'] == 'NUTS3'].set_index(['NUTS3', 'Ano'])['Populacao']
    
    df_long['nuts_total_lag_1'] = df_long.apply(
        lambda x: nuts_totals.get((x['NUTS3'], x['Ano']-1), np.nan), axis=1
    )
    df_long['nuts_total_lag_2'] = df_long.apply(
        lambda x: nuts_totals.get((x['NUTS3'], x['Ano']-2), np.nan), axis=1
    )
    df_long['nuts_total_lag_3'] = df_long.apply(
        lambda x: nuts_totals.get((x['NUTS3'], x['Ano']-3), np.nan), axis=1
    )

    # ===== PASSO 10: MARCAR ANOS ESPECIAIS =====
    # Indentificar dados de censo (2021)
    # Pode ser importante porque censos têm mais precisão que estimativas
    df_long['is_census'] = (df_long['Ano'] == 2021).astype(int)
    
    # ===== PASSO 11: DEFINIR TARGET (VARIÁVEL A PREVER) =====
    # A população do ano atual é o que queremos prever
    df_long['target_pop'] = df_long['Populacao']

    # ===== PASSO 12: CRESCIMENTO DE LONGO PRAZO =====
    # Guardar a população de 2013 (baseline) para cada território
    pop_2013 = df_long[df_long['Ano'] == 2013].set_index('territory_code')['Populacao']

    # Calcular a taxa média anual de crescimento desde 2013
    # Fórmula: (Pop(t-1) - Pop_2013) / (Anos desde 2013)
    # Isto mostra a "tendência de longo prazo" do território
    def calc_long_term_growth(row):
        p2013 = pop_2013.get(row['territory_code'], np.nan)
        n_anos = row['Ano'] - 1 - 2013
        
        # Se não há dados suficientes, retornar 0
        if n_anos <= 0 or pd.isna(p2013) or p2013 == 0:
            return 0
        
        # Crescimento acumulado até ao ano anterior, dividido pelo número de anos
        return (row['pop_lag_1'] - p2013) / n_anos

    df_long['avg_growth_since_2013'] = df_long.apply(calc_long_term_growth, axis=1)

    # ===== PASSO 13: LIMPEZA FINAL E RETORNO =====
    # Manter apenas municípios (não NUTS3) e remover linhas com valores missing
    # NUTS3 são usadas para contexto mas não são usadas no treino do modelo
    df_ml = df_long[df_long['Level'] == 'MUN'].dropna()

    cols = [
        "NUTS3","territory_code","NUTS3_Name", "Name", "Ano",
        "pop_lag_1","weight_lag_1","pop_lag_2","weight_lag_2","pop_lag_3","weight_lag_3","pop_lag_4","weight_lag_4",
        ,"acceleration",
        "mun_growth_lag_1","relative_to_nuts_growth_lag_1","mun_growth_lag_2","relative_to_nuts_growth_lag_2","mun_growth_lag_3","relative_to_nuts_growth_lag_3",
        "stability_score","stability_score_norm","nuts_total_lag_1","nuts_total_lag_2","nuts_total_lag_3",
        "is_census","avg_growth_since_2013", "target_pop"
    ]

    df_ml = df_ml[cols].copy()


    
    return df_ml


def main():
    # Caminhos dos files


    pred_df_ofic = pd.read_csv(POP_PRED_OFFICIAL_2025, sep=",")
    pred_df_ofic = pred_df_ofic[["Geopolitical entity (reporting)", "TIME_PERIOD", "OBS_VALUE"]]

    # Obter o df base e tratá-lo
    #       1. Converter os NUTS3 para 2021
    #       2. Não converter para depois poder comparar se a conversão foi bem feita ou não
    df = pd.read_csv(POP_TOTAL_CSV, sep=",")
    df_no_conversion = create_territory_code(df, convert_nuts2021=False)
    df = create_territory_code(df, convert_nuts2021=True)
    df.to_csv(
        os.path.join(POP_TOTAL_INTERMEDIATE_FOLDER, "populacao_total_nuts2021.csv"), 
        sep=",", index=False)
    df_no_conversion.to_csv(
        os.path.join(POP_TOTAL_INTERMEDIATE_FOLDER, "populacao_total_nuts2024.csv"), 
        sep=",", index=False)
    compare_mapping_nuts3(df, df_no_conversion)

    # Analisar o df que vamos usar por concelho e por nuts3
    view_analysis_concelhos, concelhos_df = analysis_concelhos(df)
    view_analysis_NUTS3, nuts3_df = analysis_concelhos(df, municipio=False)

    # Como as análises sugerem que os erros só acontecem até 2013 e 10 anos (2013-2024) é o bastante: 
    # vamos manter os dados originais a partir de 2013 e usar os pesos para corrigir os anos seguintes
    cols_maior_2013 = ["Level", "NUTS3", "NUTS3_Name", "territory_code", "Name"] + [str(ano) for ano in range(2013, 2025)]
    df = df[cols_maior_2013]
    df = prepare_dataset(df)
    print(f"DataFrame DataTypes:\n{df.dtypes}")
    print(df.describe(include="all"))
    print(f"Valores nulos por coluna:\n{df.isnull().sum()}")


    df_weight = get_weights(df)
    print(f"DataFrame com pesos:\n{df_weight.head()}")
    df_weight.to_csv(POP_WEIGHTS_CSV, sep=",", index=False)

    # Confirmar que a soma dos pesos bate 100% de cada NUTS3
    test_sum = test_weight_df(df_weight)

    compare_weights(
        df_weight=df_weight,
        prediction_df=pred_df_ofic
    )

    print(df_weight.head())
    df_ml = prepare_for_ml(df_weight=df_weight)

    df_ml.to_csv(POP_ML_DATA_CSV, sep=",", index=False)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")

    