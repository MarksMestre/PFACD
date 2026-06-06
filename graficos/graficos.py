# pip install pandas matplotlib seaborn
import os
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import scipy
import seaborn as sns
import sys
import numpy as np
from clean_princ_test_folder import main as clean_test_folder

# =========================
# CONFIGURAÇÕES DE DIRETÓRIOS
# =========================

# 1. Encontra o caminho absoluto do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Sobe de forma dinâmica até encontrar a pasta raiz do projeto ('PFACD')
base_path = script_dir
while os.path.basename(base_path) != "PFACD" and base_path != os.path.dirname(base_path):
    base_path = os.path.dirname(base_path)

# 3. Insere a raiz do projeto no sys.path do Python
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Agora o Python sabe exatamente onde procurar a pasta '__configure__'
from __configure__.paths import BASE_FOLDER as BASE_DIR, POP_PREDICTION_OUTPUT as PATH_POP_TOTAL, DENSIDADE_FINAL_CSV as PATH_DENSIDADE


# =========================
# CONFIGURAÇÕES
# =========================

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_UPACS = os.path.join(
    BASE_DIR,
    "e-redes",
    "data_input",
    "upacs_totais_limpo.csv"
)

PATH_PRECOS = os.path.join(
    BASE_DIR,
    "economy",
    "portugal_2018-2025_kW.csv"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "graficos", "output_test")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


# =========================
# FUNÇÕES AUXILIARES
# =========================

def guardar_grafico(nome="grafico", path=None):

    if path is None:
        path = os.path.join(OUTPUT_DIR, nome)
        dir = os.path.dirname(path)
    else:
        dir = os.path.dirname(path)
    os.makedirs(dir, exist_ok=True)

    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


# =========================
# FUNÇÃO TIPO summary() DO R
# =========================

def summary_df(df, nome="DataFrame"):
    print("\n" + "=" * 80)
    print(f"SUMMARY — {nome}")
    print("=" * 80)

    print("\nDimensões:")
    print(df.shape)

    print("\nColunas:")
    print(df.columns.tolist())

    print("\nTipos de dados:")
    print(df.dtypes)

    print("\nValores omissos:")
    print(df.isna().sum())

    print("\nDuplicados:")
    print(df.duplicated().sum())

    print("\nPrimeiras linhas:")
    print(df.head())

    print("\nEstatísticas descritivas:")
    print(df.describe(include="all"))


# =========================
# LEITURA DOS DADOS
# =========================

upacs = pd.read_csv(
    PATH_UPACS,
    sep=",",
    encoding="utf-8-sig"
)

precos = pd.read_csv(
    PATH_PRECOS,
    sep=",",
    encoding="utf-8-sig"
)

# Limpar nomes das colunas
upacs.columns = upacs.columns.str.strip()
precos.columns = precos.columns.str.strip()

# Ver estrutura dos dados
# summary_df(upacs, "UPACs")
# summary_df(precos, "Preços")

# Criar coluna data
def trimestre_para_data(trimestre):
    ano = int(trimestre[:4])
    t = int(trimestre[-1])
    mes = {1: 1, 2: 4, 3: 7, 4: 10}[t]
    return pd.Timestamp(year=ano, month=mes, day=1)


upacs["Data"] = upacs["Trimestre"].apply(trimestre_para_data)
upacs["Ano"] = upacs["Data"].dt.year
ultimo_trimestre = upacs["Data"].max()
upacs_ultimo = upacs[upacs["Data"] == ultimo_trimestre].copy()

# Limpar nomes das colunas
upacs.columns = upacs.columns.str.strip()
precos.columns = precos.columns.str.strip()

# Filtrar apenas Solar
upacs = upacs[upacs["Tipo de Tecnologia"] == "Solar"].copy()

# Converter variáveis numéricas
upacs["Potência Total Instalada UPAC (kW)"] = pd.to_numeric(
    upacs["Potência Total Instalada UPAC (kW)"],
    errors="coerce"
)

upacs["Número de instalacões"] = pd.to_numeric(
    upacs["Número de instalacões"],
    errors="coerce"
)

# Converter trimestre
upacs["Data"] = upacs["Trimestre"].apply(trimestre_para_data)
upacs["Ano"] = upacs["Data"].dt.year

# Preços: ficheiro tem anos como colunas
precos_long = precos.melt(
    var_name="Ano",
    value_name="Preco_USD_kW"
)

precos_long["Ano"] = precos_long["Ano"].astype(int)
precos_long["Preco_USD_kW"] = pd.to_numeric(precos_long["Preco_USD_kW"], errors="coerce")

# Dados anuais agregados das UPACs
upacs_anual = (
    upacs
    .groupby("Ano")
    .agg({
        "Número de instalacões": "sum",
        "Potência Total Instalada UPAC (kW)": "sum"
    })
    .reset_index()
)

upacs_anual["Potência média por instalação (kW)"] = (
    upacs_anual["Potência Total Instalada UPAC (kW)"]
    / upacs_anual["Número de instalacões"]
)

# Juntar com preços
upacs_preco_anual = upacs_anual.merge(precos_long, on="Ano", how="inner")


# =========================
# LEITURA DA BASE ENERGIA INJETADA
# =========================

PATH_ENERGIA = os.path.join(
    BASE_DIR,
    "e-redes",
    "data_input",
    "energia_injectada_upac.csv"
)

energia = pd.read_csv(
    PATH_ENERGIA,
    sep=";",
    encoding="utf-8-sig"
)

energia.columns = energia.columns.str.strip()

energia["Data"] = pd.to_datetime(energia["Data"], format="%Y-%m")
energia["Ano"] = energia["Data"].dt.year
energia["Mês"] = energia["Data"].dt.month

energia["Potência Instalada (kW)"] = pd.to_numeric(
    energia["Potência Instalada (kW)"],
    errors="coerce"
)

energia["Número de Instalações"] = pd.to_numeric(
    energia["Número de Instalações"],
    errors="coerce"
)

energia["Energia Injetada (kWh)"] = pd.to_numeric(
    energia["Energia Injetada (kWh)"],
    errors="coerce"
)

energia = energia.dropna(
    subset=[
        "Potência Instalada (kW)",
        "Número de Instalações",
        "Energia Injetada (kWh)"
    ]
)

energia["kWh por instalação"] = (
    energia["Energia Injetada (kWh)"] / energia["Número de Instalações"]
)

energia["kWh por kW instalado"] = (
    energia["Energia Injetada (kWh)"] / energia["Potência Instalada (kW)"]
)

# =========================
# LIMPEZA AUXILIAR PARA GRÁFICOS 56–70
# =========================

energia_limpa = energia.dropna(subset=["Distrito", "Concelho"]).copy()

# Evitar divisões por zero
energia_limpa = energia_limpa[
    (energia_limpa["Potência Instalada (kW)"] > 0) &
    (energia_limpa["Número de Instalações"] > 0)
].copy()

# summary_df(energia, "Injetada")

# =========================
# LEITURA DAS BASES DEMOGRÁFICAS
# =========================

# PATH_POP_TOTAL = r"C:\Users\franc\Desktop\PROJETO\PFACD\demography\population_total\data_final\prediction.csv"

# PATH_DENSIDADE = r"C:\Users\franc\Desktop\PROJETO\PFACD\demography\population_density\population_density.csv"


# -------------------------
# População total
# -------------------------

pop_total = pd.read_csv(
    PATH_POP_TOTAL,
    sep=",",
    encoding="utf-8-sig"
)

pop_total.columns = pop_total.columns.str.strip()

# Remover coluna índice se existir
if "Unnamed: 0" in pop_total.columns:
    pop_total = pop_total.drop(columns=["Unnamed: 0"])

# Converter colunas de anos para numérico
anos_pop = [col for col in pop_total.columns if col.isdigit()]

for col in anos_pop:
    pop_total[col] = pd.to_numeric(pop_total[col], errors="coerce")


# -------------------------
# Densidade populacional
# -------------------------

densidade = pd.read_csv(
    PATH_DENSIDADE,
    sep=",",
    encoding="utf-8-sig"
)

densidade.columns = densidade.columns.str.strip()

anos_densidade = [col for col in densidade.columns if col.isdigit()]

for col in anos_densidade:
    densidade[col] = (
        densidade[col]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    densidade[col] = pd.to_numeric(densidade[col], errors="coerce")



# =========================
# FILTRAR APENAS CONCELHOS PRESENTES NAS BASES E-REDES
# =========================

concelhos_eredes = set(upacs["Concelho"].dropna().unique())

pop_municipios = pop_total[
    pop_total["Name"].isin(concelhos_eredes)
].copy()

densidade_municipios = densidade[
    densidade["Local"].isin(concelhos_eredes)
].copy()


# =========================
# PREPARAR DADOS DEMOGRÁFICOS PARA MERGE
# =========================

# Usar 2025 para população total, se existir
ano_pop_usado = "2025" if "2025" in pop_municipios.columns else max(anos_pop)

pop_municipios = pop_municipios[["Name", ano_pop_usado]].rename(
    columns={
        "Name": "Concelho",
        ano_pop_usado: "População"
    }
)

# Usar 2024 para densidade, porque é o último ano disponível no ficheiro
ano_densidade_usado = "2024"

densidade_municipios = densidade_municipios[["Local", ano_densidade_usado]].rename(
    columns={
        "Local": "Concelho",
        ano_densidade_usado: "Densidade populacional"
    }
)


# =========================
# BASE MUNICIPAL FINAL
# =========================

upacs_concelho_ultimo = (
    upacs_ultimo
    .groupby("Concelho")
    .agg({
        "Número de instalacões": "sum",
        "Potência Total Instalada UPAC (kW)": "sum"
    })
    .reset_index()
)

base_demo = (
    upacs_concelho_ultimo
    .merge(pop_municipios, on="Concelho", how="inner")
    .merge(densidade_municipios, on="Concelho", how="inner")
)

base_demo = base_demo[
    (base_demo["População"] > 0) &
    (base_demo["Densidade populacional"] > 0)
].copy()

base_demo["UPAC por 1000 habitantes"] = (
    base_demo["Número de instalacões"]
    / base_demo["População"]
    * 1000
)

base_demo["kW por 1000 habitantes"] = (
    base_demo["Potência Total Instalada UPAC (kW)"]
    / base_demo["População"]
    * 1000
)

base_demo["Potência média por instalação (kW)"] = (
    base_demo["Potência Total Instalada UPAC (kW)"]
    / base_demo["Número de instalacões"]
)

# =========================
# BASE INTEGRADA: ENERGIA INJETADA + DEMOGRAFIA
# =========================

energia_concelho = (
    energia_limpa
    .groupby("Concelho")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum",
        "Número de Instalações": "sum"
    })
    .reset_index()
)

energia_concelho["Excedente por kW"] = (
    energia_concelho["Energia Injetada (kWh)"]
    / energia_concelho["Potência Instalada (kW)"]
)

energia_concelho["Excedente por instalação"] = (
    energia_concelho["Energia Injetada (kWh)"]
    / energia_concelho["Número de Instalações"]
)

# Juntar com base demográfica já criada anteriormente
energia_demo = energia_concelho.merge(
    base_demo[[
        "Concelho",
        "População",
        "Densidade populacional",
        "UPAC por 1000 habitantes",
        "kW por 1000 habitantes",
        "Potência média por instalação (kW)"
    ]],
    on="Concelho",
    how="inner"
)

energia_demo = energia_demo[
    (energia_demo["População"] > 0) &
    (energia_demo["Densidade populacional"] > 0) &
    (energia_demo["Potência Instalada (kW)"] > 0) &
    (energia_demo["Número de Instalações"] > 0)
].copy()

energia_demo["Energia injetada por 1000 habitantes"] = (
    energia_demo["Energia Injetada (kWh)"]
    / energia_demo["População"]
    * 1000
)

energia_demo_1000 = energia_demo[
    energia_demo["Densidade populacional"] <= 1000
].copy()

energia_demo_200000 = energia_demo[
    energia_demo["População"] <= 200000
].copy()

instalacoes_trimestre = (
        upacs
        .groupby("Data")["Número de instalacões"]
        .sum()
        .reset_index()
    )

potencia_trimestre = (
        upacs
        .groupby("Data")["Potência Total Instalada UPAC (kW)"]
        .sum()
        .reset_index()
    )

# =========================
# 1. EVOLUÇÃO DO NÚMERO TOTAL DE INSTALAÇÕES
# =========================
def graph_1():

    plt.figure()
    sns.lineplot(
        data=instalacoes_trimestre,
        x="Data",
        y="Número de instalacões",
        marker="o"
    )
    plt.title("Evolução do número total de instalações UPAC solares")
    plt.xlabel("Trimestre")
    plt.ylabel("Número de instalacões")
    guardar_grafico("01_evolucao_instalacoes_solares.png")


# =========================
# 2. EVOLUÇÃO DA POTÊNCIA TOTAL INSTALADA
# =========================
def graph_2():

    plt.figure()
    sns.lineplot(
        data=potencia_trimestre,
        x="Data",
        y="Potência Total Instalada UPAC (kW)",
        marker="o"
    )
    plt.title("Evolução da potência total instalada em UPAC solares")
    plt.xlabel("Trimestre")
    plt.ylabel("Potência total instalada (kW)")
    guardar_grafico("02_evolucao_potencia_solar.png")


# =========================
# 3. POTÊNCIA MÉDIA POR INSTALAÇÃO
# =========================
def graph_3():
    media_trimestre = potencia_trimestre.merge(instalacoes_trimestre, on="Data")
    media_trimestre["Potência média por instalação (kW)"] = (
        media_trimestre["Potência Total Instalada UPAC (kW)"]
        / media_trimestre["Número de instalacões"]
    )

    plt.figure()
    sns.lineplot(
        data=media_trimestre,
        x="Data",
        y="Potência média por instalação (kW)",
        marker="o"
    )
    plt.title("Potência média por instalação UPAC solar")
    plt.xlabel("Trimestre")
    plt.ylabel("kW por instalação")
    guardar_grafico("03_potencia_media_por_instalacao.png")


# =========================
# 4. TOP 10 DISTRITOS POR Número de instalacões
# =========================
def graph_4():
    ultimo_trimestre = upacs["Data"].max()
    upacs_ultimo = upacs[upacs["Data"] == ultimo_trimestre]

    top_distritos_inst = (
        upacs_ultimo
        .groupby("Distrito")["Número de instalacões"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    plt.figure()
    sns.barplot(
        data=top_distritos_inst,
        x="Número de instalacões",
        y="Distrito"
    )
    plt.title(f"Top 10 distritos por Número de instalacões solares — último trimestre")
    plt.xlabel("Número de instalacões")
    plt.ylabel("Distrito")
    guardar_grafico("04_top10_distritos_instalacoes.png")


# =========================
# 5. TOP 10 DISTRITOS POR POTÊNCIA INSTALADA
# =========================
def graph_5():
    top_distritos_pot = (
        upacs_ultimo
        .groupby("Distrito")["Potência Total Instalada UPAC (kW)"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    plt.figure()
    sns.barplot(
        data=top_distritos_pot,
        x="Potência Total Instalada UPAC (kW)",
        y="Distrito"
    )
    plt.title("Top 10 distritos por potência solar instalada")
    plt.xlabel("Potência total instalada (kW)")
    plt.ylabel("Distrito")
    guardar_grafico("05_top10_distritos_potencia.png")


# =========================
# 6. COMPARAÇÃO: INSTALAÇÕES VS POTÊNCIA POR DISTRITO
# =========================
def graph_6():
    distritos_ultimo = (
        upacs_ultimo
        .groupby("Distrito")
        .agg({
            "Número de instalacões": "sum",
            "Potência Total Instalada UPAC (kW)": "sum"
        })
        .reset_index()
    )

    plt.figure()
    sns.scatterplot(
        data=distritos_ultimo,
        x="Número de instalacões",
        y="Potência Total Instalada UPAC (kW)",
        s=100
    )

    for _, row in distritos_ultimo.iterrows():
        plt.text(
            row["Número de instalacões"],
            row["Potência Total Instalada UPAC (kW)"],
            row["Distrito"],
            fontsize=8
        )

    plt.title("Relação entre Número de instalacões e potência instalada por distrito")
    plt.xlabel("Número de instalacões")
    plt.ylabel("Potência total instalada (kW)")
    guardar_grafico("06_instalacoes_vs_potencia_distrito.png")


# =========================
# 7. EVOLUÇÃO POR DISTRITO — TOP 5 DISTRITOS
# =========================
def graph_7():
    top5_distritos = (
        upacs_ultimo
        .groupby("Distrito")["Número de instalacões"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    evolucao_top5 = (
        upacs[upacs["Distrito"].isin(top5_distritos)]
        .groupby(["Data", "Distrito"])["Número de instalacões"]
        .sum()
        .reset_index()
    )

    plt.figure()
    sns.lineplot(
        data=evolucao_top5,
        x="Data",
        y="Número de instalacões",
        hue="Distrito",
        marker="o"
    )
    plt.title("Evolução das instalações solares nos 5 distritos com mais UPAC")
    plt.xlabel("Trimestre")
    plt.ylabel("Número de instalacões")
    guardar_grafico("07_evolucao_top5_distritos.png")


# =========================
# 8. PREÇO USD/kW EM PORTUGAL
# =========================
def graph_8():
    plt.figure()
    sns.lineplot(
        data=precos_long,
        x="Ano",
        y="Preco_USD_kW",
        marker="o"
    )
    plt.title("Evolução do preço de instalação solar em Portugal")
    plt.xlabel("Ano")
    plt.ylabel("Preço USD/kW")
    guardar_grafico("08_preco_usd_kw_portugal.png")


# =========================
# 9. PREÇO VS POTÊNCIA INSTALADA ANUAL
# =========================

potencia_anual = (
    upacs
    .groupby("Ano")["Potência Total Instalada UPAC (kW)"]
    .sum()
    .reset_index()
)

preco_potencia = potencia_anual.merge(precos_long, on="Ano", how="inner")

def graph_9():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        preco_potencia["Ano"],
        preco_potencia["Potência Total Instalada UPAC (kW)"],
        marker="o",
        label="Potência instalada"
    )
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Potência total instalada (kW)")

    ax2 = ax1.twinx()
    ax2.plot(
        preco_potencia["Ano"],
        preco_potencia["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        label="Preço USD/kW"
    )
    ax2.set_ylabel("Preço USD/kW")

    plt.title("Potência instalada vs preço de instalação solar")
    guardar_grafico("09_potencia_vs_preco.png")


# =========================
# 10. PREÇO VS Número de instalacões ANUAL
# =========================

instalacoes_anual = (
    upacs
    .groupby("Ano")["Número de instalacões"]
    .sum()
    .reset_index()
)

preco_instalacoes = instalacoes_anual.merge(precos_long, on="Ano", how="inner")

def graph_10():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        preco_instalacoes["Ano"],
        preco_instalacoes["Número de instalacões"],
        marker="o"
    )
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Número de instalacões")

    ax2 = ax1.twinx()
    ax2.plot(
        preco_instalacoes["Ano"],
        preco_instalacoes["Preco_USD_kW"],
        marker="o",
        linestyle="--"
    )
    ax2.set_ylabel("Preço USD/kW")

    plt.title("Número de instalacões solares vs preço de instalação")
    guardar_grafico("10_instalacoes_vs_preco.png")

# =========================
# 11. DISTRIBUIÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# =========================


instalacoes_escalao = (
    upacs
    .groupby("Escalão de potência instalada (kW)")["Número de instalacões"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

def graph_11():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=instalacoes_escalao,
        x="Número de instalacões",
        y="Escalão de potência instalada (kW)"
    )
    plt.title("Distribuição do número de instalações por escalão de potência")
    plt.xlabel("Número de instalações")
    plt.ylabel("Escalão de potência instalada (kW)")
    guardar_grafico("11_instalacoes_por_escalao.png")


# =========================
# 12. POTÊNCIA TOTAL POR ESCALÃO DE POTÊNCIA
# =========================

potencia_escalao = (
    upacs
    .groupby("Escalão de potência instalada (kW)")["Potência Total Instalada UPAC (kW)"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

def graph_12():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=potencia_escalao,
        x="Potência Total Instalada UPAC (kW)",
        y="Escalão de potência instalada (kW)"
    )
    plt.title("Potência total instalada por escalão de potência")
    plt.xlabel("Potência total instalada (kW)")
    plt.ylabel("Escalão de potência instalada (kW)")
    guardar_grafico("12_potencia_por_escalao.png")


# =========================
# 13. EVOLUÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# =========================

instalacoes_escalao_tempo = (
    upacs
    .groupby(["Data", "Escalão de potência instalada (kW)"])["Número de instalacões"]
    .sum()
    .reset_index()
)

def graph_13():
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=instalacoes_escalao_tempo,
        x="Data",
        y="Número de instalacões",
        hue="Escalão de potência instalada (kW)",
        marker="o"
    )
    plt.title("Evolução do número de instalações por escalão de potência")
    plt.xlabel("Trimestre")
    plt.ylabel("Número de instalações")
    plt.legend(title="Escalão", bbox_to_anchor=(1.05, 1), loc="upper left")
    guardar_grafico("13_evolucao_instalacoes_por_escalao.png")


# =========================
# 14. EVOLUÇÃO DA POTÊNCIA POR ESCALÃO DE POTÊNCIA
# =========================

potencia_escalao_tempo = (
    upacs
    .groupby(["Data", "Escalão de potência instalada (kW)"])["Potência Total Instalada UPAC (kW)"]
    .sum()
    .reset_index()
)

def graph_14():
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=potencia_escalao_tempo,
        x="Data",
        y="Potência Total Instalada UPAC (kW)",
        hue="Escalão de potência instalada (kW)",
        marker="o"
    )
    plt.title("Evolução da potência instalada por escalão de potência")
    plt.xlabel("Trimestre")
    plt.ylabel("Potência total instalada (kW)")
    plt.legend(title="Escalão", bbox_to_anchor=(1.05, 1), loc="upper left")
    guardar_grafico("14_evolucao_potencia_por_escalao.png")


# =========================
# 15. PESO PERCENTUAL DAS INSTALAÇÕES POR ESCALÃO NO ÚLTIMO TRIMESTRE
# =========================

peso_instalacoes_escalao = (
    upacs_ultimo
    .groupby("Escalão de potência instalada (kW)")["Número de instalacões"]
    .sum()
    .reset_index()
)

peso_instalacoes_escalao["Percentagem"] = (
    peso_instalacoes_escalao["Número de instalacões"]
    / peso_instalacoes_escalao["Número de instalacões"].sum()
    * 100
)

peso_instalacoes_escalao = peso_instalacoes_escalao.sort_values("Percentagem", ascending=False)

def graph_15():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=peso_instalacoes_escalao,
        x="Percentagem",
        y="Escalão de potência instalada (kW)"
    )
    plt.title("Peso percentual das instalações por escalão no último trimestre")
    plt.xlabel("Percentagem das instalações (%)")
    plt.ylabel("Escalão de potência instalada (kW)")
    guardar_grafico("15_percentagem_instalacoes_por_escalao.png")


# =========================
# 16. PESO PERCENTUAL DA POTÊNCIA POR ESCALÃO NO ÚLTIMO TRIMESTRE
# =========================

peso_potencia_escalao = (
    upacs_ultimo
    .groupby("Escalão de potência instalada (kW)")["Potência Total Instalada UPAC (kW)"]
    .sum()
    .reset_index()
)

peso_potencia_escalao["Percentagem"] = (
    peso_potencia_escalao["Potência Total Instalada UPAC (kW)"]
    / peso_potencia_escalao["Potência Total Instalada UPAC (kW)"].sum()
    * 100
)

peso_potencia_escalao = peso_potencia_escalao.sort_values("Percentagem", ascending=False)

def graph_16():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=peso_potencia_escalao,
        x="Percentagem",
        y="Escalão de potência instalada (kW)"
    )
    plt.title("Peso percentual da potência instalada por escalão no último trimestre")
    plt.xlabel("Percentagem da potência instalada (%)")
    plt.ylabel("Escalão de potência instalada (kW)")
    guardar_grafico("16_percentagem_potencia_por_escalao.png")


# =========================
# 17. TOP 15 CONCELHOS POR NÚMERO DE INSTALAÇÕES
# =========================

top_concelhos_inst = (
    upacs_ultimo
    .groupby("Concelho")["Número de instalacões"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

def graph_17():
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=top_concelhos_inst,
        x="Número de instalacões",
        y="Concelho"
    )
    plt.title("Top 15 concelhos por número de instalações solares")
    plt.xlabel("Número de instalações")
    plt.ylabel("Concelho")
    guardar_grafico("17_top15_concelhos_instalacoes.png")


# =========================
# 18. TOP 15 CONCELHOS POR POTÊNCIA INSTALADA
# =========================

top_concelhos_pot = (
    upacs_ultimo
    .groupby("Concelho")["Potência Total Instalada UPAC (kW)"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

def graph_18():
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=top_concelhos_pot,
        x="Potência Total Instalada UPAC (kW)",
        y="Concelho"
    )
    plt.title("Top 15 concelhos por potência solar instalada")
    plt.xlabel("Potência total instalada (kW)")
    plt.ylabel("Concelho")
    guardar_grafico("18_top15_concelhos_potencia.png")


# =========================
# 19. POTÊNCIA MÉDIA POR INSTALAÇÃO POR DISTRITO
# =========================

pot_media_distrito = (
    upacs_ultimo
    .groupby("Distrito")
    .agg({
        "Número de instalacões": "sum",
        "Potência Total Instalada UPAC (kW)": "sum"
    })
    .reset_index()
)

pot_media_distrito["Potência média por instalação (kW)"] = (
    pot_media_distrito["Potência Total Instalada UPAC (kW)"]
    / pot_media_distrito["Número de instalacões"]
)

pot_media_distrito = pot_media_distrito.sort_values(
    "Potência média por instalação (kW)",
    ascending=False
)

def graph_19():
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=pot_media_distrito,
        x="Potência média por instalação (kW)",
        y="Distrito"
    )
    plt.title("Potência média por instalação por distrito")
    plt.xlabel("Potência média por instalação (kW)")
    plt.ylabel("Distrito")
    guardar_grafico("19_potencia_media_por_distrito.png")


# =========================
# 20. RELAÇÃO ENTRE PREÇO USD/kW E POTÊNCIA MÉDIA POR INSTALAÇÃO
# =========================

pot_media_anual = (
    upacs
    .groupby("Ano")
    .agg({
        "Número de instalacões": "sum",
        "Potência Total Instalada UPAC (kW)": "sum"
    })
    .reset_index()
)

pot_media_anual["Potência média por instalação (kW)"] = (
    pot_media_anual["Potência Total Instalada UPAC (kW)"]
    / pot_media_anual["Número de instalacões"]
)

preco_pot_media = pot_media_anual.merge(precos_long, on="Ano", how="inner")

def graph_20():
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=preco_pot_media,
        x="Preco_USD_kW",
        y="Potência média por instalação (kW)",
        s=120
    )

    for _, row in preco_pot_media.iterrows():
        plt.text(
            row["Preco_USD_kW"],
            row["Potência média por instalação (kW)"],
            int(row["Ano"]), # pyright: ignore[reportArgumentType]
            fontsize=9
        )

    plt.title("Relação entre preço USD/kW e potência média por instalação")
    plt.xlabel("Preço USD/kW")
    plt.ylabel("Potência média por instalação (kW)")
    guardar_grafico("20_preco_vs_potencia_media.png")


# =========================
# 21. POTÊNCIA TOTAL INSTALADA VS PREÇO USD/kW
# =========================
def graph_21():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Linha 1 (potência)
    ax1.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Potência Total Instalada UPAC (kW)"],
        marker="o",
        linewidth=2,
        color="tab:blue",
        label="Potência instalada"
    )
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Potência total instalada (kW)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # Linha 2 (preço)
    ax2 = ax1.twinx()
    ax2.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        linewidth=2,
        color="tab:red",
        label="Preço USD/kW"
    )
    ax2.set_ylabel("Preço USD/kW", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    plt.title("Potência total instalada vs preço USD/kW")

    # Legenda combinada
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    guardar_grafico("21_potencia_vs_preco_colorido.png")


# =========================
# 22. NÚMERO TOTAL DE INSTALAÇÕES VS PREÇO USD/kW
# =========================
def graph_22():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Número de instalacões"],
        marker="o",
        linewidth=2,
        color="tab:blue"
    )
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Número total de instalações")
    ax1.tick_params(axis="y")

    ax2 = ax1.twinx()
    ax2.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        linewidth=2,
        color="tab:red"
    )
    ax2.set_ylabel("Preço USD/kW")
    ax2.tick_params(axis="y")

    plt.title("Número total de instalações UPAC solares vs preço USD/kW")
    guardar_grafico("22_instalacoes_totais_vs_preco_duplo_eixo.png")


# =========================
# 23. POTÊNCIA MÉDIA POR INSTALAÇÃO VS PREÇO USD/kW
# =========================
def graph_23():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Potência média por instalação (kW)"],
        marker="o",
        linewidth=2,
        color="tab:green"
    )
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Potência média por instalação (kW)")
    ax1.tick_params(axis="y")

    ax2 = ax1.twinx()
    ax2.plot(
        upacs_preco_anual["Ano"],
        upacs_preco_anual["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        linewidth=2,
        color="tab:orange"
    )
    ax2.set_ylabel("Preço USD/kW")
    ax2.tick_params(axis="y")

    plt.title("Potência média por instalação vs preço USD/kW")
    guardar_grafico("23_potencia_media_vs_preco_duplo_eixo.png")


# =========================
# 24. CRESCIMENTO PERCENTUAL ANUAL DA POTÊNCIA INSTALADA
# =========================
def graph_24():
    crescimento_potencia = upacs_anual.copy()
    crescimento_potencia["Crescimento percentual da potência (%)"] = (
        crescimento_potencia["Potência Total Instalada UPAC (kW)"]
        .pct_change()
        * 100
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=crescimento_potencia.dropna(),
        x="Ano",
        y="Crescimento percentual da potência (%)"
    )
    plt.title("Crescimento percentual anual da potência instalada")
    plt.xlabel("Ano")
    plt.ylabel("Crescimento da potência (%)")
    guardar_grafico("24_crescimento_percentual_potencia.png")


# =========================
# 25. CRESCIMENTO PERCENTUAL ANUAL DAS INSTALAÇÕES
# =========================
def graph_25():
    crescimento_instalacoes = upacs_anual.copy()
    crescimento_instalacoes["Crescimento percentual das instalações (%)"] = (
        crescimento_instalacoes["Número de instalacões"]
        .pct_change()
        * 100
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=crescimento_instalacoes.dropna(),
        x="Ano",
        y="Crescimento percentual das instalações (%)"
    )
    plt.title("Crescimento percentual anual do número de instalações")
    plt.xlabel("Ano")
    plt.ylabel("Crescimento das instalações (%)")
    guardar_grafico("25_crescimento_percentual_instalacoes.png")


# =========================
# 26. VARIAÇÃO ANUAL DO PREÇO USD/kW
# =========================

variacao_preco = precos_long.sort_values("Ano").copy()
variacao_preco["Variação percentual do preço (%)"] = (
    variacao_preco["Preco_USD_kW"]
    .pct_change()
    * 100
)

def graph_26():
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=variacao_preco.dropna(),
        x="Ano",
        y="Variação percentual do preço (%)"
    )
    plt.title("Variação percentual anual do preço USD/kW")
    plt.xlabel("Ano")
    plt.ylabel("Variação do preço (%)")
    guardar_grafico("26_variacao_percentual_preco.png")


# =========================
# 27. ÍNDICE BASE 100: POTÊNCIA, INSTALAÇÕES E PREÇO
# =========================

indice = upacs_preco_anual.sort_values("Ano").copy()

base_potencia = indice["Potência Total Instalada UPAC (kW)"].iloc[0]
base_instalacoes = indice["Número de instalacões"].iloc[0]
base_preco = indice["Preco_USD_kW"].iloc[0]

indice["Índice potência"] = indice["Potência Total Instalada UPAC (kW)"] / base_potencia * 100
indice["Índice instalações"] = indice["Número de instalacões"] / base_instalacoes * 100
indice["Índice preço"] = indice["Preco_USD_kW"] / base_preco * 100

indice_long = indice.melt(
    id_vars="Ano",
    value_vars=["Índice potência", "Índice instalações", "Índice preço"],
    var_name="Indicador",
    value_name="Índice base 100"
)

def graph_27():
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=indice_long,
        x="Ano",
        y="Índice base 100",
        hue="Indicador",
        marker="o"
    )
    plt.title("Evolução indexada: potência, instalações e preço")
    plt.xlabel("Ano")
    plt.ylabel("Índice base 100")
    guardar_grafico("27_indice_base100_potencia_instalacoes_preco.png")


# =========================
# 28. CONCENTRAÇÃO DA POTÊNCIA INSTALADA POR DISTRITO
# =========================

potencia_distrito_ultimo = (
    upacs_ultimo
    .groupby("Distrito")["Potência Total Instalada UPAC (kW)"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

potencia_distrito_ultimo["Percentagem acumulada"] = (
    potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"]
    .cumsum()
    / potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"].sum()
    * 100
)

potencia_distrito_ultimo["Posição"] = range(1, len(potencia_distrito_ultimo) + 1)

def graph_28():
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=potencia_distrito_ultimo,
        x="Posição",
        y="Percentagem acumulada",
        marker="o"
    )

    # Adicionar nomes dos distritos
    for _, row in potencia_distrito_ultimo.iterrows():
        plt.text(
            row["Posição"] + 0.1,
            row["Percentagem acumulada"],
            row["Distrito"],
            fontsize=8
        )

    # Escala de 2 em 2
    plt.xticks(range(1, len(potencia_distrito_ultimo) + 1, 1))

    plt.title("Concentração acumulada da potência instalada por distrito")
    plt.xlabel("Distritos ordenados por potência instalada")
    plt.ylabel("Percentagem acumulada da potência (%)")
    plt.ylim(0, 100)
    plt.yticks(range(0, 101, 10))

    guardar_grafico("28_concentracao_acumulada_potencia_distrito.png")


# =========================
# 29. CONCENTRAÇÃO DAS INSTALAÇÕES POR DISTRITO
# =========================

instalacoes_distrito_ultimo = (
    upacs_ultimo
    .groupby("Distrito")["Número de instalacões"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

instalacoes_distrito_ultimo["Percentagem acumulada"] = (
    instalacoes_distrito_ultimo["Número de instalacões"]
    .cumsum()
    / instalacoes_distrito_ultimo["Número de instalacões"].sum()
    * 100
)

instalacoes_distrito_ultimo["Posição"] = range(1, len(instalacoes_distrito_ultimo) + 1)

def graph_29():
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=instalacoes_distrito_ultimo,
        x="Posição",
        y="Percentagem acumulada",
        marker="o"
    )

    # Adicionar nomes dos distritos
    for _, row in instalacoes_distrito_ultimo.iterrows():
        plt.text(
            row["Posição"] + 0.1,
            row["Percentagem acumulada"],
            row["Distrito"],
            fontsize=8
        )

    # Escala de 2 em 2
    plt.xticks(range(1, len(instalacoes_distrito_ultimo) + 1, 1))

    plt.title("Concentração acumulada das instalações por distrito")
    plt.xlabel("Distritos ordenados por número de instalações")
    plt.ylabel("Percentagem acumulada das instalações (%)")
    plt.ylim(0, 100)
    plt.yticks(range(0, 101, 10))

    guardar_grafico("29_concentracao_acumulada_instalacoes_distrito.png")


# =========================
# 30. DISTRITOS COM MAIOR PESO RELATIVO NA POTÊNCIA NACIONAL
# =========================

peso_distrito_potencia = potencia_distrito_ultimo.copy()

peso_distrito_potencia["Peso nacional (%)"] = (
    peso_distrito_potencia["Potência Total Instalada UPAC (kW)"]
    / peso_distrito_potencia["Potência Total Instalada UPAC (kW)"].sum()
    * 100
)

peso_distrito_potencia = peso_distrito_potencia.sort_values(
    "Peso nacional (%)",
    ascending=False
)

def graph_30():
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=peso_distrito_potencia,
        x="Peso nacional (%)",
        y="Distrito"
    )
    plt.title("Peso de cada distrito na potência solar instalada nacional")
    plt.xlabel("Peso na potência nacional (%)")
    plt.ylabel("Distrito")
    guardar_grafico("30_peso_distrito_potencia_nacional.png")

# =========================
# 31. EVOLUÇÃO DA POTÊNCIA POR ESCALÃO + PREÇO USD/kW
# =========================

potencia_escalao_tempo = (
    upacs
    .groupby(["Data", "Escalão de potência instalada (kW)"])["Potência Total Instalada UPAC (kW)"]
    .sum()
    .reset_index()
)

# Preço anual como data real
preco_anual = precos_long.copy()
preco_anual["Data"] = pd.to_datetime(preco_anual["Ano"].astype(str) + "-01-01")

# Cortar preço para começar apenas a partir do início dos dados das UPACs
data_inicio = potencia_escalao_tempo["Data"].min()
data_fim = potencia_escalao_tempo["Data"].max()

preco_anual = preco_anual[
    (preco_anual["Data"] >= data_inicio) &
    (preco_anual["Data"] <= data_fim)
].copy()


def graph_31():
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Usar exatamente a lógica de cores do seaborn como no gráfico 14
    sns.lineplot(
        data=potencia_escalao_tempo,
        x="Data",
        y="Potência Total Instalada UPAC (kW)",
        hue="Escalão de potência instalada (kW)",
        marker="o",
        ax=ax1
    )

    ax1.set_xlabel("Trimestre")
    ax1.set_ylabel("Potência total instalada (kW)")
    ax1.legend(title="Escalão", bbox_to_anchor=(1.08, 1), loc="upper left")

    # Eixo direito para o preço
    ax2 = ax1.twinx()

    ax2.plot(
        preco_anual["Data"],
        preco_anual["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        linewidth=3,
        color="black",
        label="Preço USD/kW"
    )

    ax2.set_ylabel("Preço USD/kW", color="black")
    ax2.tick_params(axis="y", labelcolor="black")
    ax2.legend(loc="upper right")

    plt.title("Evolução da potência instalada por escalão de potência e preço USD/kW")

    guardar_grafico("31_potencia_por_escalao_vs_preco_corrigido.png")


# =========================
# 32. EVOLUÇÃO MENSAL DA ENERGIA TOTAL INJETADA
# =========================

energia_mensal = (
    energia
    .groupby("Data")["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

def graph_32():
    plt.figure(figsize=(14, 6))
    sns.lineplot(
        data=energia_mensal,
        x="Data",
        y="Energia Injetada (kWh)",
        marker="o"
    )
    plt.title("Evolução mensal da energia total injetada pelas UPAC")
    plt.xlabel("Data")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("32_evolucao_mensal_energia_injetada.png")


# =========================
# 33. ENERGIA MÉDIA INJETADA POR MÊS
# =========================

energia_mes = (
    energia
    .groupby("Mês")["Energia Injetada (kWh)"]
    .mean()
    .reset_index()
)

def graph_33():
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=energia_mes,
        x="Mês",
        y="Energia Injetada (kWh)",
        marker="o"
    )
    plt.title("Energia média injetada por mês")
    plt.xlabel("Mês")
    plt.ylabel("Energia média injetada (kWh)")
    plt.xticks(range(1, 13))
    guardar_grafico("33_energia_media_por_mes.png")


# =========================
# 34. ENERGIA INJETADA POR MÊS E ANO
# =========================

energia_mes_ano = (
    energia
    .groupby(["Ano", "Mês"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

def graph_34():
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=energia_mes_ano,
        x="Mês",
        y="Energia Injetada (kWh)",
        hue="Ano",
    marker="o"
    )
    plt.title("Energia injetada por mês e ano")
    plt.xlabel("Mês")
    plt.ylabel("Energia injetada (kWh)")
    plt.xticks(range(1, 13))
    guardar_grafico("34_energia_por_mes_e_ano.png")


# =========================
# 35. TOP 10 DISTRITOS POR ENERGIA INJETADA
# =========================

energia_distrito = (
    energia
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

def graph_35():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=energia_distrito,
        x="Energia Injetada (kWh)",
        y="Distrito"
    )
    plt.title("Top 10 distritos por energia total injetada")
    plt.xlabel("Energia injetada (kWh)")
    plt.ylabel("Distrito")
    guardar_grafico("35_top10_distritos_energia_injetada.png")


# =========================
# 36. TOP 10 DISTRITOS POR kWh POR INSTALAÇÃO
# =========================

eficiencia_inst_distrito = (
    energia
    .groupby("Distrito")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Número de Instalações": "sum"
    })
    .reset_index()
)

eficiencia_inst_distrito["kWh por instalação"] = (
    eficiencia_inst_distrito["Energia Injetada (kWh)"]
    / eficiencia_inst_distrito["Número de Instalações"]
)

eficiencia_inst_distrito = (
    eficiencia_inst_distrito
    .sort_values("kWh por instalação", ascending=False)
    .head(10)
)

def graph_36():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=eficiencia_inst_distrito,
        x="kWh por instalação",
        y="Distrito"
    )
    plt.title("Top 10 distritos por energia injetada por instalação")
    plt.xlabel("kWh por instalação")
    plt.ylabel("Distrito")
    guardar_grafico("36_top10_distritos_kwh_por_instalacao.png")


# =========================
# 37. TOP 10 DISTRITOS POR kWh POR kW INSTALADO
# =========================

excedente_kw_distrito = (
    energia
    .groupby("Distrito")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_kw_distrito["Excedente por kW (kWh/kW)"] = (
    excedente_kw_distrito["Energia Injetada (kWh)"]
    / excedente_kw_distrito["Potência Instalada (kW)"]
)

excedente_kw_distrito = excedente_kw_distrito.sort_values(
    "Excedente por kW (kWh/kW)",
    ascending=False
)

def graph_37():
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=excedente_kw_distrito,
        x="Excedente por kW (kWh/kW)",
        y="Distrito"
    )
    plt.title("Excedente de energia por kW instalado por distrito")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Distrito")
    guardar_grafico("37_excedente_kw_distrito.png")


# =========================
# 38. POTÊNCIA INSTALADA VS ENERGIA INJETADA
# =========================

energia_distrito_scatter = (
    energia
    .groupby("Distrito")
    .agg({
        "Potência Instalada (kW)": "sum",
        "Energia Injetada (kWh)": "sum"
    })
    .reset_index()
)

def graph_38():
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=energia_distrito_scatter,
        x="Potência Instalada (kW)",
        y="Energia Injetada (kWh)",
        s=120
    )

    for _, row in energia_distrito_scatter.iterrows():
        plt.text(
            row["Potência Instalada (kW)"],
            row["Energia Injetada (kWh)"],
            row["Distrito"],
            fontsize=8
        )

    plt.title("Relação entre potência instalada e energia injetada por distrito")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("38_potencia_vs_energia_por_distrito.png")


# =========================
# 39. NÚMERO DE INSTALAÇÕES VS ENERGIA INJETADA
# =========================

energia_inst_scatter = (
    energia
    .groupby("Distrito")
    .agg({
        "Número de Instalações": "sum",
        "Energia Injetada (kWh)": "sum"
    })
    .reset_index()
)

def graph_39():
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=energia_inst_scatter,
        x="Número de Instalações",
        y="Energia Injetada (kWh)",
        s=120
    )

    for _, row in energia_inst_scatter.iterrows():
        plt.text(
            row["Número de Instalações"],
            row["Energia Injetada (kWh)"],
            row["Distrito"],
            fontsize=8
        )

    plt.title("Relação entre número de instalações e energia injetada por distrito")
    plt.xlabel("Número de instalações")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("39_instalacoes_vs_energia_por_distrito.png")


# =========================
# 40. HEATMAP: ENERGIA INJETADA POR DISTRITO E MÊS
# =========================

heatmap_energia = (
    energia
    .groupby(["Distrito", "Mês"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

heatmap_pivot = heatmap_energia.pivot(
    index="Distrito",
    columns="Mês",
    values="Energia Injetada (kWh)"
)

def graph_40():
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        heatmap_pivot,
        cmap="YlOrRd",
        linewidths=0.5
    )
    plt.title("Heatmap da energia injetada por distrito e mês")
    plt.xlabel("Mês")
    plt.ylabel("Distrito")
    guardar_grafico("40_heatmap_energia_distrito_mes.png")


# =========================
# 41. EVOLUÇÃO DO kWh POR kW INSTALADO AO LONGO DO TEMPO
# =========================

excedente_tempo = (
    energia
    .groupby("Data")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_tempo["Excedente por kW"] = (
    excedente_tempo["Energia Injetada (kWh)"]
    / excedente_tempo["Potência Instalada (kW)"]
)

def graph_41():
    plt.figure(figsize=(14, 6))
    sns.lineplot(
        data=excedente_tempo,
        x="Data",
        y="Excedente por kW",
        marker="o"
    )
    plt.title("Evolução do excedente de energia por kW instalado")
    plt.xlabel("Data")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("41_evolucao_excedente_kw.png")

# =========================
# 42. BOXPLOT DA ENERGIA INJETADA POR MÊS
# =========================

def graph_42():
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=energia,
        x="Mês",
        y="Energia Injetada (kWh)"
    )
    plt.title("Distribuição da energia injetada por mês")
    plt.xlabel("Mês")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("42_boxplot_energia_por_mes.png")


# =========================
# 43. BOXPLOT DO kWh POR kW INSTALADO POR MÊS
# =========================
def graph_43():
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=energia,
        x="Mês",
        y="kWh por kW instalado"
    )
    plt.title("Distribuição da energia por kW instalado por mês")
    plt.xlabel("Mês")
    plt.ylabel("kWh por kW instalado")
    guardar_grafico("43_boxplot_kwh_por_kw_mes.png")


# =========================
# 44. EVOLUÇÃO DA ENERGIA INJETADA POR DISTRITO — TOP 5
# =========================

top5_energia_distritos = (
    energia
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

energia_top5_tempo = (
    energia[energia["Distrito"].isin(top5_energia_distritos)]
    .groupby(["Data", "Distrito"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

def graph_44():
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=energia_top5_tempo,
        x="Data",
        y="Energia Injetada (kWh)",
        hue="Distrito",
        marker="o"
    )
    plt.title("Evolução da energia injetada nos 5 distritos com maior energia total")
    plt.xlabel("Data")
    plt.ylabel("Energia injetada (kWh)")
    plt.legend(title="Distrito", bbox_to_anchor=(1.05, 1), loc="upper left")
    guardar_grafico("44_evolucao_energia_top5_distritos.png")


# =========================
# 45. EVOLUÇÃO DO kWh POR INSTALAÇÃO
# =========================

kwh_inst_tempo = (
    energia
    .groupby("Data")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Número de Instalações": "sum"
    })
    .reset_index()
)

kwh_inst_tempo["kWh por instalação"] = (
    kwh_inst_tempo["Energia Injetada (kWh)"]
    / kwh_inst_tempo["Número de Instalações"]
)

def graph_45():
    plt.figure(figsize=(14, 6))
    sns.lineplot(
        data=kwh_inst_tempo,
        x="Data",
        y="kWh por instalação",
        marker="o"
    )
    plt.title("Evolução da energia injetada por instalação")
    plt.xlabel("Data")
    plt.ylabel("kWh por instalação")
    guardar_grafico("45_evolucao_kwh_por_instalacao.png")


# =========================
# 46. ENERGIA INJETADA POR NÍVEL DE TENSÃO
# =========================

energia_tensao = (
    energia
    .groupby("Nível de Tensão")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

def graph_46():
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=energia_tensao,
        x="Energia Injetada (kWh)",
        y="Nível de Tensão"
    )
    plt.title("Energia total injetada por nível de tensão")
    plt.xlabel("Energia injetada (kWh)")
    plt.ylabel("Nível de tensão")
    guardar_grafico("46_energia_por_nivel_tensao.png")


# =========================
# 47. POTÊNCIA INSTALADA POR NÍVEL DE TENSÃO
# =========================

potencia_tensao = (
    energia
    .groupby("Nível de Tensão")["Potência Instalada (kW)"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

def graph_47():
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=potencia_tensao,
        x="Potência Instalada (kW)",
        y="Nível de Tensão"
    )
    plt.title("Potência instalada por nível de tensão")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("Nível de tensão")
    guardar_grafico("47_potencia_por_nivel_tensao.png")


# =========================
# 48. kWh POR kW INSTALADO POR NÍVEL DE TENSÃO
# =========================

eficiencia_tensao = (
    energia
    .groupby("Nível de Tensão")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

eficiencia_tensao["kWh por kW instalado"] = (
    eficiencia_tensao["Energia Injetada (kWh)"]
    / eficiencia_tensao["Potência Instalada (kW)"]
)

eficiencia_tensao = eficiencia_tensao.sort_values(
    "kWh por kW instalado",
    ascending=False
)


def graph_48():
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=eficiencia_tensao,
        x="kWh por kW instalado",
        y="Nível de Tensão"
    )
    plt.title("Energia injetada por kW instalado por nível de tensão")
    plt.xlabel("kWh por kW instalado")
    plt.ylabel("Nível de tensão")
    guardar_grafico("48_kwh_por_kw_por_nivel_tensao.png")


# =========================
# 49. CURVA ACUMULADA DA ENERGIA INJETADA POR DISTRITO
# =========================

energia_distrito_acumulada = (
    energia
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

energia_distrito_acumulada["Percentagem acumulada"] = (
    energia_distrito_acumulada["Energia Injetada (kWh)"].cumsum()
    / energia_distrito_acumulada["Energia Injetada (kWh)"].sum()
    * 100
)

energia_distrito_acumulada["Posição"] = range(
    1,
    len(energia_distrito_acumulada) + 1
)

def graph_49():
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=energia_distrito_acumulada,
        x="Posição",
        y="Percentagem acumulada",
        marker="o"
    )

    # Adicionar nomes dos distritos
    for _, row in energia_distrito_acumulada.iterrows():
        plt.text(
            row["Posição"] + 0.1,
            row["Percentagem acumulada"],
            row["Distrito"],
            fontsize=8
        )

    # Escala X de 1 em 1
    plt.xticks(range(1, len(energia_distrito_acumulada) + 1, 1))

    # Escala Y de 0 a 100 de 10 em 10
    plt.ylim(0, 100)
    plt.yticks(range(0, 101, 10))

    plt.title("Concentração acumulada da energia injetada por distrito")
    plt.xlabel("Distritos ordenados por energia injetada")
    plt.ylabel("Percentagem acumulada da energia (%)")

    guardar_grafico("49_concentracao_acumulada_energia_distrito.png")


# =========================
# 50. PREÇO USD/kW VS ENERGIA INJETADA ANUAL
# =========================

energia_anual = (
    energia
    .groupby("Ano")["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

energia_preco_anual = energia_anual.merge(precos_long, on="Ano", how="inner")

def graph_50():
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        energia_preco_anual["Ano"],
        energia_preco_anual["Energia Injetada (kWh)"],
        marker="o",
        linewidth=2,
        color="tab:blue",
        label="Energia injetada"
    )

    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Energia injetada (kWh)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()

    ax2.plot(
        energia_preco_anual["Ano"],
        energia_preco_anual["Preco_USD_kW"],
        marker="o",
        linestyle="--",
        linewidth=2,
        color="black",
        label="Preço USD/kW"
    )

    ax2.set_ylabel("Preço USD/kW", color="black")
    ax2.tick_params(axis="y", labelcolor="black")

    plt.title("Energia injetada anual vs preço USD/kW")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    guardar_grafico("50_energia_anual_vs_preco.png")

# =========================
# 51. DISTRIBUIÇÃO DO kWh POR kW INSTALADO
# =========================

def graph_51():
    plt.figure(figsize=(10, 6))
    sns.histplot(
        energia["kWh por kW instalado"], # pyright: ignore[reportArgumentType]
        bins=50,
        kde=True
    )
    plt.title("Distribuição da energia injetada por kW instalado")
    plt.xlabel("kWh por kW instalado")
    plt.ylabel("Frequência")
    guardar_grafico("51_distribuicao_kwh_por_kw.png")
# =========================
# 51A-51D. DISTRIBUIÇÃO DO kWh POR kW INSTALADO POR ESCALÃO MÉDIO DE POTÊNCIA
# =========================
energia_escalao = energia[
        (energia["Potência Instalada (kW)"] > 0) &
        (energia["Número de Instalações"] > 0) &
        (energia["kWh por kW instalado"].notna())
    ].copy()

energia_escalao["Potência média por instalação (kW)"] = (
    energia_escalao["Potência Instalada (kW)"]
    / energia_escalao["Número de Instalações"]
)

energia_escalao["Escalão médio de potência"] = pd.cut(
    energia_escalao["Potência média por instalação (kW)"],
    bins=[0, 4, 20.7, 30, 1000, float("inf")],
    labels=[
        "]0, 4]",
        "]4, 20.7]",
        "]20.7, 30]",
        "]30, 1000]",
        ">1000"
    ],
    include_lowest=True
)

def graph_51_escalao():

    

    print("\nContagem por escalão médio de potência:")
    print(energia_escalao["Escalão médio de potência"].value_counts(dropna=False))

    for escalao in energia_escalao["Escalão médio de potência"].dropna().unique():
        dados_escalao = energia_escalao[
            energia_escalao["Escalão médio de potência"] == escalao
        ]

        plt.figure(figsize=(10, 6))

        sns.histplot(
            dados_escalao["kWh por kW instalado"],
            bins=50,
            kde=True
        )

        plt.title(f"Distribuição da energia injetada por kW instalado — escalão médio {escalao}")
        plt.xlabel("kWh injetados por kW instalado")
        plt.ylabel("Frequência")

        nome_ficheiro = (
            f"51_distribuicao_kwh_por_kw_escalao_medio_{str(escalao)}"
            .replace("]", "")
            .replace("[", "")
            .replace(",", "")
            .replace(" ", "")
            .replace(".", "_")
            .replace(">", "maior_")
        )

        guardar_grafico(f"{nome_ficheiro}.png")

# =========================
# 51F. LINHAS KDE DO kWh POR kW INSTALADO — ESCALÕES SELECIONADOS
# =========================
def graph_51_kde_escalao():
    plt.figure(figsize=(12, 7))

    escaloes_escolhidos = ["]0, 4]", "]30, 1000]"]

    cores = {
        "]0, 4]": "tab:blue",
        "]30, 1000]": "tab:red"
    }

    for escalao in escaloes_escolhidos:
        dados_escalao = energia_escalao[
            energia_escalao["Escalão médio de potência"] == escalao
        ]["kWh por kW instalado"].dropna()

        if len(dados_escalao) == 0:
            continue

        sns.kdeplot(
            dados_escalao, # pyright: ignore[reportArgumentType]
            label=escalao,
            linewidth=2.5,
            color=cores[escalao]
        )

    plt.title("Distribuição da energia injetada por kW instalado por escalão médio")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Densidade")
    plt.xlim(0, 120)
    plt.ylim(0, 0.035)
    plt.legend(title="Escalão médio")
    guardar_grafico("51_linhas_kde_kwh_por_kw_escalaoes_0_4_e_30_1000.png")


# =========================
# 51G. DISTRIBUIÇÃO POR ESCALÃO — LINHAS COM FREQUÊNCIA
# =========================
def graph_51_hist_escalao():
    plt.figure(figsize=(12, 7))

    escalaoes_escolhidos = ["]0, 4]", "]30, 1000]"]

    cores = {
        "]0, 4]": "tab:blue",
        "]30, 1000]": "tab:red"
    }

    for escalao in escalaoes_escolhidos:
        dados_escalao = energia_escalao[
            energia_escalao["Escalão médio de potência"] == escalao
        ]["kWh por kW instalado"].dropna()

        if len(dados_escalao) == 0:
            continue

        sns.histplot(
            dados_escalao, # pyright: ignore[reportArgumentType]
            bins=50,
            element="step",
            fill=False,
            stat="count",
            linewidth=2.5,
            color=cores[escalao],
            label=escalao
        )

    plt.title("Distribuição da energia injetada por kW instalado por escalão médio")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Frequência")
    plt.xlim(0, 120)
    plt.legend(title="Escalão médio")

    guardar_grafico("51_linhas_frequencia_kwh_por_kw_escalaoes_0_4_e_30_1000.png")

# =========================
# 52. BOXPLOT kWh/kW POR DISTRITO
# =========================
def graph_52():
    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=energia,
        x="Distrito",
        y="kWh por kW instalado"
    )

    plt.xticks(rotation=45)
    plt.title("Distribuição da eficiência (kWh/kW) por distrito")
    plt.xlabel("Distrito")
    plt.ylabel("kWh por kW instalado")
    guardar_grafico("52_boxplot_kwh_kw_por_distrito.png")

# =========================
# 53. POTÊNCIA VS EXCEDENTE
# =========================
def graph_53():
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=energia,
        x="Potência Instalada (kW)",
        y="kWh por kW instalado",
        alpha=0.4
    )

    plt.title("Relação entre potência instalada e excedente relativo")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("53_potencia_vs_excedente.png")

# =========================
# 54. TOP 15 CONCELHOS POR EXCEDENTE
# =========================
excedente_concelho = (
    energia
    .groupby("Concelho")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_concelho["Excedente por kW"] = (
    excedente_concelho["Energia Injetada (kWh)"]
    / excedente_concelho["Potência Instalada (kW)"]
)

top_concelhos_excedente = (
    excedente_concelho
    .sort_values("Excedente por kW", ascending=False)
    .head(15)
)

def graph_54():
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=top_concelhos_excedente,
        x="Excedente por kW",
        y="Concelho"
    )

    plt.title("Top 15 concelhos com maior excedente relativo de energia")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Concelho")
    guardar_grafico("54_top_concelhos_excedente.png")

# =========================
# 55. EVOLUÇÃO DO EXCEDENTE NOS TOP 5 DISTRITOS
# =========================

top5_distritos = (
    energia
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

eficiencia_top5 = (
    energia[energia["Distrito"].isin(top5_distritos)]
    .groupby(["Data", "Distrito"])
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

eficiencia_top5["kWh por kW instalado"] = (
    eficiencia_top5["Energia Injetada (kWh)"]
    / eficiencia_top5["Potência Instalada (kW)"]
)

def graph_55():
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=eficiencia_top5,
        x="Data",
        y="kWh por kW instalado",
        hue="Distrito",
        marker="o"
    )

    plt.title("Evolução da eficiência energética nos principais distritos")
    plt.xlabel("Data")
    plt.ylabel("kWh por kW instalado")
    plt.legend(title="Distrito", bbox_to_anchor=(1.05, 1), loc="upper left")
    guardar_grafico("55_evolucao_eficiencia_top5.png")


# =========================
# 56. CURVA DE LORENZ DA ENERGIA INJETADA POR DISTRITO
# =========================

lorenz_energia = (
    energia_limpa
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values()
    .reset_index()
)

lorenz_energia["Percentagem acumulada energia"] = (
    lorenz_energia["Energia Injetada (kWh)"].cumsum()
    / lorenz_energia["Energia Injetada (kWh)"].sum()
    * 100
)

lorenz_energia["Percentagem acumulada distritos"] = (
    (range(1, len(lorenz_energia) + 1))
)
lorenz_energia["Percentagem acumulada distritos"] = (
    lorenz_energia["Percentagem acumulada distritos"]
    / len(lorenz_energia)
    * 100
)

def graph_56():
    plt.figure(figsize=(8, 8))

    plt.plot(
        lorenz_energia["Percentagem acumulada distritos"],
        lorenz_energia["Percentagem acumulada energia"],
        marker="o",
        label="Energia injetada"
    )

    plt.plot(
        [0, 100],
        [0, 100],
        linestyle="--",
        color="black",
        label="Distribuição igualitária"
    )

    plt.title("Curva de Lorenz da energia injetada por distrito")
    plt.xlabel("Percentagem acumulada de distritos (%)")
    plt.ylabel("Percentagem acumulada da energia injetada (%)")
    plt.legend()
    plt.grid(True)

    guardar_grafico("56_lorenz_energia_injetada_distrito.png")


# =========================
# 57. DISTRITOS COM MENOR EXCEDENTE RELATIVO POR kW
# =========================

excedente_distrito = (
    energia_limpa
    .groupby("Distrito")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_distrito["Excedente por kW"] = (
    excedente_distrito["Energia Injetada (kWh)"]
    / excedente_distrito["Potência Instalada (kW)"]
)

bottom_excedente_distrito = (
    excedente_distrito
    .sort_values("Excedente por kW", ascending=True)
    .head(10)
)

def graph_57():
    plt.figure(figsize=(12, 6))

    sns.barplot(
        data=bottom_excedente_distrito,
        x="Excedente por kW",
        y="Distrito"
    )

    plt.title("10 distritos com menor excedente relativo por kW instalado")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Distrito")

    guardar_grafico("57_distritos_menor_excedente_kw.png")


# =========================
# 58. HEATMAP ANO × MÊS DA ENERGIA INJETADA
# =========================

heatmap_ano_mes = (
    energia_limpa
    .groupby(["Ano", "Mês"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

heatmap_ano_mes_pivot = heatmap_ano_mes.pivot(
    index="Ano",
    columns="Mês",
    values="Energia Injetada (kWh)"
)

def graph_58():
    plt.figure(figsize=(12, 5))

    sns.heatmap(
        heatmap_ano_mes_pivot,
        cmap="YlOrRd",
        linewidths=0.5,
        annot=False
    )

    plt.title("Heatmap da energia injetada por ano e mês")
    plt.xlabel("Mês")
    plt.ylabel("Ano")

    guardar_grafico("58_heatmap_ano_mes_energia_injetada.png")


# =========================
# 59. HEATMAP DISTRITO × MÊS DO EXCEDENTE POR kW
# =========================

excedente_mes_distrito = (
    energia_limpa
    .groupby(["Distrito", "Mês"])
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_mes_distrito["Excedente por kW"] = (
    excedente_mes_distrito["Energia Injetada (kWh)"]
    / excedente_mes_distrito["Potência Instalada (kW)"]
)

heatmap_excedente_pivot = excedente_mes_distrito.pivot(
    index="Distrito",
    columns="Mês",
    values="Excedente por kW"
)

def graph_59():
    plt.figure(figsize=(14, 8))

    sns.heatmap(
        heatmap_excedente_pivot,
        cmap="YlOrRd",
        linewidths=0.5
    )

    plt.title("Heatmap do excedente relativo por distrito e mês")
    plt.xlabel("Mês")
    plt.ylabel("Distrito")

    guardar_grafico("59_heatmap_excedente_kw_distrito_mes.png")


# =========================
# 60. VARIAÇÃO MENSAL DA ENERGIA INJETADA (%)
# =========================

variacao_mensal_energia = (
    energia_limpa
    .groupby("Data")["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
    .sort_values("Data")
)

variacao_mensal_energia["Variação mensal (%)"] = (
    variacao_mensal_energia["Energia Injetada (kWh)"]
    .pct_change()
    * 100
)

def graph_60():
    plt.figure(figsize=(14, 6))

    sns.barplot(
        data=variacao_mensal_energia.dropna(),
        x="Data",
        y="Variação mensal (%)"
    )

    plt.title("Variação mensal da energia injetada")
    plt.xlabel("Data")
    plt.ylabel("Variação mensal (%)")
    plt.xticks(rotation=45)

    guardar_grafico("60_variacao_mensal_energia_injetada.png")


# =========================
# 61. RANKING DINÂMICO DOS DISTRITOS POR ENERGIA INJETADA
# =========================

top8_distritos_energia = (
    energia_limpa
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(8)
    .index
)

ranking_distritos = (
    energia_limpa[energia_limpa["Distrito"].isin(top8_distritos_energia)]
    .groupby(["Data", "Distrito"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

ranking_distritos["Ranking"] = (
    ranking_distritos
    .groupby("Data")["Energia Injetada (kWh)"]
    .rank(ascending=False, method="dense")
)

def graph_61():
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=ranking_distritos,
        x="Data",
        y="Ranking",
        hue="Distrito",
        marker="o"
    )

    plt.gca().invert_yaxis()
    plt.title("Ranking mensal dos principais distritos por energia injetada")
    plt.xlabel("Data")
    plt.ylabel("Ranking mensal")
    plt.legend(title="Distrito", bbox_to_anchor=(1.05, 1), loc="upper left")

    guardar_grafico("61_ranking_dinamico_distritos_energia.png")


# =========================
# 62. EVOLUÇÃO DA DISTRIBUIÇÃO DOS ESCALÕES DE POTÊNCIA
# =========================

escalao_tempo = (
    upacs
    .groupby(["Data", "Escalão de potência instalada (kW)"])["Número de instalacões"]
    .sum()
    .reset_index()
)

escalao_pivot = escalao_tempo.pivot(
    index="Data",
    columns="Escalão de potência instalada (kW)",
    values="Número de instalacões"
).fillna(0)

escalao_percent = escalao_pivot.div(escalao_pivot.sum(axis=1), axis=0) * 100

def graph_62():
    plt.figure(figsize=(14, 7))

    escalao_percent.plot.area(
        figsize=(14, 7),
        alpha=0.8
    )

    plt.title("Evolução da distribuição percentual das instalações por escalão")
    plt.xlabel("Data")
    plt.ylabel("Percentagem das instalações (%)")
    plt.legend(title="Escalão", bbox_to_anchor=(1.05, 1), loc="upper left")

    guardar_grafico("62_area_percentual_instalacoes_por_escalao.png")


# =========================
# 63. PREÇO USD/kW VS EXCEDENTE RELATIVO ANUAL
# =========================

excedente_anual = (
    energia_limpa
    .groupby("Ano")
    .agg({
        "Energia Injetada (kWh)": "sum",
        "Potência Instalada (kW)": "sum"
    })
    .reset_index()
)

excedente_anual["Excedente por kW"] = (
    excedente_anual["Energia Injetada (kWh)"]
    / excedente_anual["Potência Instalada (kW)"]
)

excedente_preco_anual = excedente_anual.merge(
    precos_long,
    on="Ano",
    how="inner"
)

def graph_63():
    plt.figure(figsize=(10, 6))

    sns.scatterplot(
        data=excedente_preco_anual,
        x="Preco_USD_kW",
        y="Excedente por kW",
        s=140
    )

    for _, row in excedente_preco_anual.iterrows():
        plt.text(
            row["Preco_USD_kW"],
            row["Excedente por kW"],
            int(row["Ano"]), # pyright: ignore[reportArgumentType]
            fontsize=9
        )

    plt.title("Relação entre preço USD/kW e excedente relativo anual")
    plt.xlabel("Preço USD/kW")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("63_preco_vs_excedente_relativo_anual.png")


# =========================
# 64. CURVA ACUMULADA TEMPORAL DA ENERGIA INJETADA
# =========================

energia_acumulada_tempo = (
    energia_limpa
    .groupby("Data")["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
    .sort_values("Data")
)

energia_acumulada_tempo["Energia acumulada (kWh)"] = (
    energia_acumulada_tempo["Energia Injetada (kWh)"].cumsum()
)

energia_acumulada_tempo["Percentagem acumulada (%)"] = (
    energia_acumulada_tempo["Energia acumulada (kWh)"]
    / energia_acumulada_tempo["Energia Injetada (kWh)"].sum()
    * 100
)

def graph_64():
    plt.figure(figsize=(14, 6))

    sns.lineplot(
        data=energia_acumulada_tempo,
        x="Data",
        y="Percentagem acumulada (%)",
        marker="o"
    )

    plt.title("Curva acumulada temporal da energia injetada")
    plt.xlabel("Data")
    plt.ylabel("Percentagem acumulada da energia injetada (%)")
    plt.ylim(0, 100)
    plt.yticks(range(0, 101, 10))

    guardar_grafico("64_curva_acumulada_temporal_energia.png")


# =========================
# 65. DENSIDADE DO EXCEDENTE RELATIVO NOS TOP 5 DISTRITOS
# =========================

top5_excedente_distritos = (
    energia_limpa
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

energia_top5_kde = energia_limpa[
    energia_limpa["Distrito"].isin(top5_excedente_distritos)
].copy()

def graph_65():
    plt.figure(figsize=(12, 6))

    for distrito in top5_excedente_distritos:
        subset = energia_top5_kde[
            energia_top5_kde["Distrito"] == distrito
        ]

        sns.kdeplot(
            data=subset,
            x="kWh por kW instalado",
            fill=False,
            label=distrito
        )

    plt.title("Distribuição do excedente relativo nos 5 distritos com mais energia injetada")
    plt.xlabel("kWh injetados por kW instalado")
    plt.ylabel("Densidade")
    plt.legend(title="Distrito", bbox_to_anchor=(1.05, 1), loc="upper left")

    guardar_grafico("65_kde_excedente_top5_distritos.png")


# =========================
# 66. DISTRIBUIÇÃO LOGARÍTMICA DA ENERGIA INJETADA
# =========================

energia_positiva = energia_limpa[
    energia_limpa["Energia Injetada (kWh)"] > 0
].copy()

def graph_66():
    plt.figure(figsize=(10, 6))

    sns.histplot(
        data=energia_positiva,
        x="Energia Injetada (kWh)",
        bins=60,
        log_scale=True
    )

    plt.title("Distribuição logarítmica da energia injetada")
    plt.xlabel("Energia injetada (kWh) - escala logarítmica")
    plt.ylabel("Frequência")

    guardar_grafico("66_distribuicao_log_energia_injetada.png")


# =========================
# 67. POTÊNCIA VS EXCEDENTE RELATIVO COM TAMANHO DAS INSTALAÇÕES
# =========================

scatter_distrito_excedente = (
    energia_limpa
    .groupby("Distrito")
    .agg({
        "Potência Instalada (kW)": "sum",
        "Energia Injetada (kWh)": "sum",
        "Número de Instalações": "sum"
    })
    .reset_index()
)

scatter_distrito_excedente["Excedente por kW"] = (
    scatter_distrito_excedente["Energia Injetada (kWh)"]
    / scatter_distrito_excedente["Potência Instalada (kW)"]
)

def graph_67():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=scatter_distrito_excedente,
        x="Potência Instalada (kW)",
        y="Excedente por kW",
        size="Número de Instalações",
        sizes=(80, 800),
        alpha=0.7,
        legend=True
    )

    for _, row in scatter_distrito_excedente.iterrows():
        plt.text(
            row["Potência Instalada (kW)"],
            row["Excedente por kW"],
            row["Distrito"],
            fontsize=8
        )

    plt.title("Potência instalada vs excedente relativo por distrito")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("67_potencia_vs_excedente_size_instalacoes.png")


# =========================
# 68. EVOLUÇÃO DA PARTICIPAÇÃO DOS TOP 5 DISTRITOS NA ENERGIA NACIONAL
# =========================

top5_participacao = (
    energia_limpa
    .groupby("Distrito")["Energia Injetada (kWh)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

energia_data_total = (
    energia_limpa
    .groupby("Data")["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
    .rename(columns={"Energia Injetada (kWh)": "Energia nacional"})
)

energia_top5_data = (
    energia_limpa[energia_limpa["Distrito"].isin(top5_participacao)]
    .groupby(["Data", "Distrito"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

energia_top5_data = energia_top5_data.merge(
    energia_data_total,
    on="Data",
    how="left"
)

energia_top5_data["Participação nacional (%)"] = (
    energia_top5_data["Energia Injetada (kWh)"]
    / energia_top5_data["Energia nacional"]
    * 100
)

def graph_68():
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=energia_top5_data,
        x="Data",
        y="Participação nacional (%)",
        hue="Distrito",
        marker="o"
    )

    plt.title("Participação dos principais distritos na energia injetada nacional")
    plt.xlabel("Data")
    plt.ylabel("Participação nacional (%)")
    plt.legend(title="Distrito", bbox_to_anchor=(1.05, 1), loc="upper left")

    guardar_grafico("68_participacao_top5_distritos_energia.png")


# =========================
# 69. EVOLUÇÃO DA ENERGIA INJETADA POR NÍVEL DE TENSÃO
# =========================

energia_tensao_tempo = (
    energia_limpa
    .groupby(["Data", "Nível de Tensão"])["Energia Injetada (kWh)"]
    .sum()
    .reset_index()
)

energia_tensao_pivot = energia_tensao_tempo.pivot(
    index="Data",
    columns="Nível de Tensão",
    values="Energia Injetada (kWh)"
).fillna(0)

energia_tensao_percent = energia_tensao_pivot.div(
    energia_tensao_pivot.sum(axis=1),
    axis=0
) * 100

def graph_69():
    plt.figure(figsize=(14, 7))

    energia_tensao_percent.plot.area(
        figsize=(14, 7),
        alpha=0.8
    )

    plt.title("Evolução percentual da energia injetada por nível de tensão")
    plt.xlabel("Data")
    plt.ylabel("Percentagem da energia injetada (%)")
    plt.legend(title="Nível de tensão", bbox_to_anchor=(1.05, 1), loc="upper left")

    guardar_grafico("69_area_percentual_energia_por_nivel_tensao.png")


# =========================
# 70. MATRIZ DE CORRELAÇÃO DAS VARIÁVEIS NUMÉRICAS
# =========================

corr_vars = energia_limpa[
    [
        "Potência Instalada (kW)",
        "Número de Instalações",
        "Energia Injetada (kWh)",
        "kWh por instalação",
        "kWh por kW instalado"
    ]
].copy()

corr_matrix = corr_vars.corr()

def graph_70():
    plt.figure(figsize=(9, 7))

    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5
    )

    plt.title("Matriz de correlação das variáveis da energia injetada")

    guardar_grafico("70_matriz_correlacao_energia.png")

# =========================
# 71. TOP 15 CONCELHOS POR UPAC POR 1000 HABITANTES
# =========================

top_upac_1000 = (
    base_demo
    .sort_values("UPAC por 1000 habitantes", ascending=False)
    .head(15)
)

def graph_71():
    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=top_upac_1000,
        x="UPAC por 1000 habitantes",
        y="Concelho"
    )

    plt.title("Top 15 concelhos por número de UPAC por 1000 habitantes")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("Concelho")

    guardar_grafico("71_top15_upac_por_1000_habitantes.png")


# =========================
# 72. TOP 15 CONCELHOS POR POTÊNCIA INSTALADA POR 1000 HABITANTES
# =========================

top_kw_1000 = (
    base_demo
    .sort_values("kW por 1000 habitantes", ascending=False)
    .head(15)
)

def graph_72():
    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=top_kw_1000,
        x="kW por 1000 habitantes",
        y="Concelho"
    )

    plt.title("Top 15 concelhos por potência instalada por 1000 habitantes")
    plt.xlabel("kW por 1000 habitantes")
    plt.ylabel("Concelho")

    guardar_grafico("72_top15_kw_por_1000_habitantes.png")


# =========================
# 73. POPULAÇÃO VS NÚMERO DE INSTALAÇÕES
# =========================
def graph_73():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="População",
        y="Número de instalacões",
        alpha=0.7
    )

    plt.title("Relação entre população e número de instalações UPAC")
    plt.xlabel("População")
    plt.ylabel("Número de instalações")

    guardar_grafico("73_populacao_vs_instalacoes.png")

# =========================
# 73_200000. POPULAÇÃO VS NÚMERO DE INSTALAÇÕES (ZOOM)
# =========================

base_demo_200000 = base_demo[base_demo["População"] <= 200000].copy()

def graph_73_200k():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_200000,
        x="População",
        y="Número de instalacões",
        alpha=0.7
    )

    plt.xlim(0, 200000)

    plt.title("Relação entre população e número de instalações UPAC")
    plt.xlabel("População")
    plt.ylabel("Número de instalações")

    guardar_grafico("73_populacao_vs_instalacoes_200000.png")

# =========================
# 73_25000. POPULAÇÃO VS NÚMERO DE INSTALAÇÕES (ZOOM)
# =========================

base_demo_25000 = base_demo[base_demo["População"] <= 25000].copy()

def graph_73_25k():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_25000,
        x="População",
        y="Número de instalacões",
        alpha=0.7
    )

    plt.xlim(0, 25000)

    plt.title("Relação entre população e número de instalações UPAC")
    plt.xlabel("População")
    plt.ylabel("Número de instalações")

    guardar_grafico("73_populacao_vs_instalacoes_25000.png")

# =========================
# 74. POPULAÇÃO VS POTÊNCIA INSTALADA
# =========================
def graph_74():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="População",
        y="Potência Total Instalada UPAC (kW)",
        alpha=0.7
    )

    plt.title("Relação entre população e potência instalada")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")

    guardar_grafico("74_populacao_vs_potencia.png")

# =========================
# 74_200000. POPULAÇÃO VS POTÊNCIA INSTALADA (ZOOM)
# =========================
def graph_74_200k():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_200000,
        x="População",
        y="Potência Total Instalada UPAC (kW)",
        alpha=0.7
    )

    plt.xlim(0, 200000)

    plt.title("Relação entre população e potência instalada")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")

    guardar_grafico("74_populacao_vs_potencia_200000.png")


# =========================
# 75. DENSIDADE POPULACIONAL VS UPAC POR 1000 HABITANTES
# =========================
def graph_75():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="Densidade populacional",
        y="UPAC por 1000 habitantes",
        alpha=0.7
    )

    plt.title("Densidade populacional vs UPAC por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")

    guardar_grafico("75_densidade_vs_upac_por_1000.png")

# =========================
# 75_1000. DENSIDADE POPULACIONAL VS UPAC POR 1000 HABITANTES (ZOOM)
# =========================

base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()

def graph_75_1000():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_1000,
        x="Densidade populacional",
        y="UPAC por 1000 habitantes",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs UPAC por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")

    guardar_grafico("75_densidade_vs_upac_por_1000_1000.png")


# =========================
# 76. DENSIDADE POPULACIONAL VS POTÊNCIA POR 1000 HABITANTES
# =========================
def graph_76():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="Densidade populacional",
        y="kW por 1000 habitantes",
        alpha=0.7
    )

    plt.title("Densidade populacional vs potência instalada por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kW por 1000 habitantes")

    guardar_grafico("76_densidade_vs_kw_por_1000.png")

# =========================
# 76_1000. DENSIDADE POPULACIONAL VS POTÊNCIA POR 1000 HABITANTES (ZOOM)
# =========================
def graph_76_1000():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_1000,
        x="Densidade populacional",
        y="kW por 1000 habitantes",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs potência instalada por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kW por 1000 habitantes")

    guardar_grafico("76_densidade_vs_kw_por_1000_1000.png")


# =========================
# 77. POTÊNCIA MÉDIA POR INSTALAÇÃO VS DENSIDADE POPULACIONAL
# =========================
def graph_77():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="Densidade populacional",
        y="Potência média por instalação (kW)",
        alpha=0.7
    )

    plt.title("Densidade populacional vs potência média por instalação")
    plt.xlabel("Densidade populacional")
    plt.ylabel("Potência média por instalação (kW)")

    guardar_grafico("77_densidade_vs_potencia_media.png")

# =========================
# 77_1000. POTÊNCIA MÉDIA POR INSTALAÇÃO VS DENSIDADE POPULACIONAL (ZOOM)
# =========================
def graph_77_1000():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo_1000,
        x="Densidade populacional",
        y="Potência média por instalação (kW)",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs potência média por instalação")
    plt.xlabel("Densidade populacional")
    plt.ylabel("Potência média por instalação (kW)")

    guardar_grafico("77_densidade_vs_potencia_media_1000.png")

# =========================
# 78. SCATTER COM TAMANHO: POPULAÇÃO, POTÊNCIA E INSTALAÇÕES
# =========================
def graph_78():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=base_demo,
        x="População",
        y="Potência Total Instalada UPAC (kW)",
        size="Número de instalacões",
        sizes=(40, 700),
        alpha=0.6,
        legend=True
    )

    plt.title("População vs potência instalada com dimensão pelo número de instalações")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")

    guardar_grafico("78_populacao_potencia_size_instalacoes.png")


# =========================
# 79. MATRIZ DE CORRELAÇÃO COM VARIÁVEIS DEMOGRÁFICAS
# =========================
corr_demo = base_demo[
    [
        "População",
        "Densidade populacional",
        "Número de instalacões",
        "Potência Total Instalada UPAC (kW)",
        "UPAC por 1000 habitantes",
        "kW por 1000 habitantes",
        "Potência média por instalação (kW)"
    ]
].corr()

def graph_79():
    plt.figure(figsize=(10, 8))

    sns.heatmap(
        corr_demo,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5
    )

    plt.title("Matriz de correlação entre autoconsumo e variáveis demográficas")

    guardar_grafico("79_correlacao_demografia_autoconsumo.png")


# =========================
# 80. DISTRIBUIÇÃO DAS UPAC POR 1000 HABITANTES
# =========================
def graph_80():
    plt.figure(figsize=(10, 6))

    sns.histplot(
        data=base_demo,
        x="UPAC por 1000 habitantes",
        bins=40,
        kde=True
    )

    plt.title("Distribuição relativa de UPACs por concelho")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("Frequência")

    guardar_grafico("80_distribuicao_upac_por_1000_habitantes.png")

# =========================
# 81. DENSIDADE POPULACIONAL VS EXCEDENTE POR kW
# =========================
def graph_81():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo_1000,
        x="Densidade populacional",
        y="Excedente por kW",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs excedente por kW instalado")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("81_densidade_vs_excedente_por_kw_1000.png")

# =========================
# 82. DENSIDADE POPULACIONAL VS EXCEDENTE POR INSTALAÇÃO
# =========================
def graph_82():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo_1000,
        x="Densidade populacional",
        y="Excedente por instalação",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs excedente por instalação")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por instalação")

    guardar_grafico("82_densidade_vs_excedente_por_instalacao_1000.png")

# =========================
# 83. UPAC POR 1000 HABITANTES VS EXCEDENTE POR kW
# =========================
def graph_83():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo,
        x="UPAC por 1000 habitantes",
        y="Excedente por kW",
        alpha=0.7
    )

    plt.title("Penetração de UPAC vs excedente relativo")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("83_upac_por_1000_vs_excedente_kw.png")

# =========================
# 84. POTÊNCIA POR 1000 HABITANTES VS EXCEDENTE POR kW
# =========================
def graph_84():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo,
        x="kW por 1000 habitantes",
        y="Excedente por kW",
        alpha=0.7
    )

    plt.title("Potência instalada por habitante vs excedente relativo")
    plt.xlabel("kW por 1000 habitantes")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("84_kw_por_1000_vs_excedente_kw.png")

# =========================
# 85. POPULAÇÃO VS ENERGIA INJETADA TOTAL
# =========================
def graph_85():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo_200000,
        x="População",
        y="Energia Injetada (kWh)",
        alpha=0.7
    )

    plt.xlim(0, 200000)

    plt.title("População vs energia excedente injetada")
    plt.xlabel("População")
    plt.ylabel("Energia injetada (kWh)")

    guardar_grafico("85_populacao_vs_energia_injetada_200000.png")

# =========================
# 86. EXCEDENTE POR kW POR CLASSES DE DENSIDADE
# =========================
energia_demo["Classe de densidade"] = pd.cut(
    energia_demo["Densidade populacional"],
    bins=[0, 50, 100, 250, 500, 1000, float("inf")],
    labels=[
        "0-50",
        "50-100",
        "100-250",
        "250-500",
        "500-1000",
        ">1000"
    ]
)

def graph_86():
    plt.figure(figsize=(12, 7))

    sns.boxplot(
        data=energia_demo,
        x="Classe de densidade",
        y="Excedente por kW"
    )

    plt.title("Distribuição do excedente por kW por classe de densidade populacional")
    plt.xlabel("Classe de densidade populacional")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("86_boxplot_excedente_kw_por_classe_densidade.png")

# =========================
# 87. DENSIDADE POPULACIONAL VS ENERGIA INJETADA POR 1000 HABITANTES
# =========================
def graph_87():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo_1000,
        x="Densidade populacional",
        y="Energia injetada por 1000 habitantes",
        alpha=0.7
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs energia injetada por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("Energia injetada por 1000 habitantes (kWh)")

    guardar_grafico("87_densidade_vs_energia_por_1000hab_1000.png")

# =========================
# 88. MATRIZ DE CORRELAÇÃO: DEMOGRAFIA + EXCEDENTE
# =========================

corr_integrada = energia_demo[
    [
        "População",
        "Densidade populacional",
        "UPAC por 1000 habitantes",
        "kW por 1000 habitantes",
        "Potência média por instalação (kW)",
        "Energia Injetada (kWh)",
        "Excedente por kW",
        "Excedente por instalação",
        "Energia injetada por 1000 habitantes"
    ]
].corr()

def graph_88():
    plt.figure(figsize=(11, 9))

    sns.heatmap(
        corr_integrada,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5
    )

    plt.title("Matriz de correlação entre demografia, autoconsumo e excedente")

    guardar_grafico("88_correlacao_demografia_autoconsumo_excedente.png")

# =========================
# 89. DENSIDADE VS EXCEDENTE POR kW COM TAMANHO PELA POTÊNCIA INSTALADA
# =========================
def graph_89():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo_1000,
        x="Densidade populacional",
        y="Excedente por kW",
        size="Potência Instalada (kW)",
        sizes=(40, 700),
        alpha=0.6,
        legend=True
    )

    plt.xlim(0, 1000)

    plt.title("Densidade populacional vs excedente por kW com dimensão pela potência instalada")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("89_densidade_vs_excedente_kw_size_potencia_1000.png")

# =========================
# 90. QUADRANTES: PENETRAÇÃO DE UPAC VS EXCEDENTE RELATIVO
# =========================
def graph_90():
    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=energia_demo,
        x="UPAC por 1000 habitantes",
        y="Excedente por kW",
        alpha=0.7
    )

    media_upac_1000 = energia_demo["UPAC por 1000 habitantes"].mean()
    media_excedente_kw = energia_demo["Excedente por kW"].mean()

    plt.axvline(
        media_upac_1000,
        linestyle="--",
        color="black",
        linewidth=1
    )

    plt.axhline(
        media_excedente_kw,
        linestyle="--",
        color="black",
        linewidth=1
    )

    plt.title("Quadrantes: penetração de UPAC e excedente relativo")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("kWh injetados por kW instalado")

    plt.text(
        media_upac_1000 * 1.05,
        media_excedente_kw * 1.05,
        "Alta penetração\nalto excedente",
        fontsize=9
    )

    plt.text(
        energia_demo["UPAC por 1000 habitantes"].min(),
        media_excedente_kw * 1.05,
        "Baixa penetração\nalto excedente",
        fontsize=9
    )

    plt.text(
        media_upac_1000 * 1.05,
        energia_demo["Excedente por kW"].min(),
        "Alta penetração\nbaixo excedente",
        fontsize=9
    )

    plt.text(
        energia_demo["UPAC por 1000 habitantes"].min(),
        energia_demo["Excedente por kW"].min(),
        "Baixa penetração\nbaixo excedente",
        fontsize=9
    )

    guardar_grafico("90_quadrantes_upac_por_1000_excedente_kw.png")

# =========================
# 91. BOXPLOT UPAC POR 1000 HABITANTES POR CLASSE DE DENSIDADE
# =========================

base_demo["Classe de densidade"] = pd.cut(
    base_demo["Densidade populacional"],
    bins=[0, 50, 100, 250, 500, 1000, float("inf")],
    labels=[
        "0-50",
        "50-100",
        "100-250",
        "250-500",
        "500-1000",
        ">1000"
    ]
)

def graph_91():
    plt.figure(figsize=(12, 7))

    sns.boxplot(
        data=base_demo,
        x="Classe de densidade",
        y="UPAC por 1000 habitantes"
    )

    plt.title("Distribuição das UPAC por 1000 habitantes por classe de densidade")
    plt.xlabel("Classe de densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")

    guardar_grafico("91_boxplot_upac_por_1000_por_classe_densidade.png")

# =========================
# 92. BOXPLOT kW POR 1000 HABITANTES POR CLASSE DE DENSIDADE
# =========================
def graph_92():
    plt.figure(figsize=(12, 7))

    sns.boxplot(
        data=base_demo,
        x="Classe de densidade",
        y="kW por 1000 habitantes"
    )

    plt.title("Distribuição da potência instalada por 1000 habitantes por classe de densidade")
    plt.xlabel("Classe de densidade populacional")
    plt.ylabel("kW por 1000 habitantes")

    guardar_grafico("92_boxplot_kw_por_1000_por_classe_densidade.png")

# =========================
# 94. TOP CONCELHOS COM MAIOR PENETRAÇÃO RELATIVA DE UPAC
# =========================

def graph_94():
    top_outliers_upac = (
        base_demo
        .sort_values("UPAC por 1000 habitantes", ascending=False)
        .head(15)
    )

    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=top_outliers_upac,
        x="UPAC por 1000 habitantes",
        y="Concelho"
    )

    plt.title("Top 15 concelhos com maior penetração relativa de UPAC")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("Concelho")

    guardar_grafico("94_top15_concelhos_penetracao_upac.png")

# =========================
# 95. ANÁLISE DOS PERFIS BIMODAIS DE EXCEDENTE REL
# ========================
def graph_95():
    

    # def detetar_todos_os_picos(df_escalao, coluna="kWh por kW instalado", max_picos=4):
    #     """
    #     Analisa a distribuição de um escalão e encontra automaticamente TODOS os
    #     picos (máximos locais) legítimos, ordenados do mais importante para o menos.
    #     """
    #     dados = df_escalao[coluna].dropna()
    #     if len(dados) < 15:
    #         return [35] # Fallback se houver uma amostra quase vazia
            
    #     # Calcular a densidade de kernel (KDE) para suavizar o histograma
    #     kde = scipy.stats.gaussian_kde(dados)
    #     x_axis = np.linspace(dados.min(), dados.max(), 1000)
    #     y_axis = kde(x_axis)
        
    #     # Encontrar os picos. Ajustamos a 'prominence' para ignorar micro-oscilações (ruído)
    #     picos_indices, _ = scipy.signal.find_peaks(
    #         y_axis, 
    #         distance=40, 
    #         prominence=y_axis.max() * 0.08  # Um pico deve ter pelo menos 8% de relevância do maior
    #     )
    #     picos_valores = x_axis[picos_indices]
        
    #     # Ordenar pela altura do pico no KDE (os perfis mais comuns primeiro)
    #     picos_ordenados = [x for _, x in sorted(zip(y_axis[picos_indices], picos_valores), reverse=True)]
        
    #     # Limitar ao máximo de perfis legíveis que queres no gráfico
    #     picos_finais = sorted(picos_ordenados[:max_picos])
        
    #     # Garantir que devolve pelo menos um valor médio se nenhum pico for detetado
    #     if not picos_finais:
    #         picos_finais = [dados.median()]
            
    #     print(f"🎯 Encontrados {len(picos_finais)} perfis/picos para este escalão: " + ", ".join([f"~{p:.1f}" for p in picos_finais]))
    #     return picos_finais
    
    # def analisar_observacoes_escalao_vs_densidade_multipico(folder_path, escalao_nome="]0, 4]", tolerância=3):
    #     print(f"\n🔄 A preparar dados dinâmicos para análise multimodal do escalão {escalao_nome}...")
        
    #     # Isolar o escalão
    #     df_linhas = energia_escalao[energia_escalao["Escalão médio de potência"] == escalao_nome].copy()
        
    #     # DETEÇÃO DINÂMICA DE N PICOS
    #     lista_picos = detetar_todos_os_picos(df_linhas)
        
    #     # Mapeamento dinâmico da densidade ano a ano (Formato Long)
    #     anos_disponiveis = [col for col in densidade.columns if col.isdigit()]
    #     if "Concelho" not in densidade.columns and "Local" in densidade.columns:
    #         densidade["Concelho"] = densidade["Local"]
            
    #     densidade_long = densidade.melt(id_vars=["Concelho"], value_vars=anos_disponiveis, var_name="Ano", value_name="Densidade_Ano")
    #     densidade_long["Ano"] = densidade_long["Ano"].astype(int)
    #     df_linhas["Ano"] = df_linhas["Ano"].astype(int)
        
    #     if 2025 in df_linhas["Ano"].unique() and 2025 not in densidade_long["Ano"].unique():
    #         densidade_2024 = densidade_long[densidade_long["Ano"] == 2024].copy()
    #         densidade_2024["Ano"] = 2025
    #         densidade_long = pd.concat([densidade_long, densidade_2024], ignore_index=True)
            
    #     df_final = df_linhas.merge(densidade_long, on=["Concelho", "Ano"], how="inner")
        
    #     # CRIAR OS PERFIS DINAMICAMENTE NO CICLO FOR
    #     df_final["Perfil"] = None
    #     for i, pico in enumerate(lista_picos):
    #         label_perfil = f"Perfil {i+1} (~{int(pico)})"
            
    #         # Filtro de tolerância aplicado a cada pico da lista
    #         condicao_pico = (df_final["kWh por kW instalado"] >= pico - tolerância) & (df_final["kWh por kW instalado"] <= pico + tolerância)
    #         df_final.loc[condicao_pico, "Perfil"] = label_perfil

    #     # Filtrar para manter apenas as linhas classificadas em algum perfil
    #     df_perfis = df_final[df_final["Perfil"].notna()].copy()
    #     df_perfis = df_perfis[df_perfis["Densidade_Ano"] <= 1200]
        
    #     if df_perfis.empty:
    #         print("⚠️ Nenhuma observação caiu dentro das tolerâncias dos picos detetados.")
    #         return df_final

    #     sufixo_ficheiro = escalao_nome.replace("]", "").replace("[", "").replace(",", "_").replace(" ", "")

    #     # ========================================================
    #     # GRÁFICO LM_PLOT DINÂMICO (Aceita N linhas de regressão)
    #     # ========================================================
    #     plt.figure(figsize=(12, 6))
    #     sns.lmplot(
    #         data=df_perfis, 
    #         x="Densidade_Ano", 
    #         y="kWh por kW instalado", 
    #         hue="Perfil",
    #         palette="tab10", # Atribui automaticamente cores distintas até 10 perfis
    #         scatter_kws={"alpha": 0.15, "s": 8}, 
    #         line_kws={"linewidth": 2.5},
    #         height=6, 
    #         aspect=1.5
    #     )
    #     plt.title(f"Tendência do Excedente vs. Densidade — Escalão {escalao_nome} ({len(lista_picos)} Perfis)")
    #     plt.xlabel("Densidade Populacional Dinâmica (hab/km²)")
    #     plt.ylabel("Excedente no Mês (kWh por kW instalado)")
    #     guardar_grafico(os.path.join(folder_path, f"regressao_multimodal_{sufixo_ficheiro}.png"))
        
    #     # ========================================================
    #     # GRÁFICO KDE PLOT 2D DINÂMICO
    #     # ========================================================
    #     plt.figure(figsize=(12, 7))
    #     sns.kdeplot(
    #         data=df_perfis, 
    #         x="Densidade_Ano", 
    #         y="kWh por kW instalado", 
    #         hue="Perfil",
    #         fill=True, 
    #         alpha=0.3, 
    #         levels=4,
    #         palette="tab10"
    #     )
    #     plt.title(f"Zonas de Concentração (Contornos 2D) — Escalão {escalao_nome}")
    #     plt.xlabel("Densidade Populacional Dinâmica (hab/km²)")
    #     plt.ylabel("Excedente no Mês (kWh por kW instalado)")
    #     guardar_grafico(os.path.join(folder_path, f"kde_multimodal_{sufixo_ficheiro}.png"))
        
    #     return df_perfis

    # 95.A - Analisar os perfis bimodais de excedente relativo (kWh por kW instalado) para o escalão ]0, 4]
    def graph_95A(folder95):
        
        def analisar_observacoes_escalao_vs_densidade(folder_path, centroide_tuple = (20, 55), tolerancia=3):
            print("\n🔄 A preparar dados dinâmicos para análise segmentada por perfil...")
            
            # 1. Isolar o escalão ]0, 4]
            df_linhas = energia_escalao[energia_escalao["Escalão médio de potência"] == "]0, 4]"].copy()
            
            # 2. Mapeamento dinâmico da densidade ano a ano (Formato Long)
            anos_disponiveis = [col for col in densidade.columns if col.isdigit()]

            densidade["Concelho"] = densidade["Local"]
            densidade_long = densidade.melt(
                id_vars=["Concelho"],
                value_vars=anos_disponiveis,
                var_name="Ano",
                value_name="Densidade_Ano"
            )
            densidade_long["Ano"] = densidade_long["Ano"].astype(int)
            df_linhas["Ano"] = df_linhas["Ano"].astype(int)
            
            # Lógica para garantir o suporte a 2025 se a densidade só for até 2024
            if 2025 in df_linhas["Ano"].unique() and 2025 not in densidade_long["Ano"].unique():
                densidade_2024 = densidade_long[densidade_long["Ano"] == 2024].copy()
                densidade_2024["Ano"] = 2025
                densidade_long = pd.concat([densidade_long, densidade_2024], ignore_index=True)
                
            df_final = df_linhas.merge(densidade_long, on=["Concelho", "Ano"], how="inner")
            
            # 3. CRIAR OS DOIS PERFIS (Filtro estrito em torno dos picos que encontraste)
            # Perfil Baixo Excedente (Pico ~20) e Perfil Alto Excedente (Pico ~55)
            df_final["Perfil"] = None
            df_final.loc[(df_final["kWh por kW instalado"] >= centroide_tuple[0] - tolerancia) & (df_final["kWh por kW instalado"] <= centroide_tuple[0] + tolerancia), "Perfil"] = f"Perfil 1 (~{centroide_tuple[0]})"
            df_final.loc[(df_final["kWh por kW instalado"] >= centroide_tuple[1] - tolerancia) & (df_final["kWh por kW instalado"] <= centroide_tuple[1] + tolerancia), "Perfil"] = f"Perfil 2 (~{centroide_tuple[1]})"


            # Filtrar para manter apenas as observações que pertencem nitidamente a um dos dois perfis
            df_perfis = df_final[df_final["Perfil"].notna()].copy()
            
            # Zoom nos concelhos com densidade até 1200 para evitar a distorção das metrópoles
            df_perfis = df_perfis[df_perfis["Densidade_Ano"] <= 1200]

            # ========================================================
            # OPÇÃO A: GRÁFICO DE REGRESSÃO SEGMENTADO (Tendências Lineares)
            # ========================================================
            plt.figure(figsize=(12, 6))
            sns.lmplot(
                data=df_perfis,
                x="Densidade_Ano",
                y="kWh por kW instalado",
                hue="Perfil",
                palette={"Perfil 1 (~20)": "tab:blue", "Perfil 2 (~55)": "tab:orange"},
                scatter_kws={"alpha": 0.2, "s": 10}, # Pontos muito suaves em background
                line_kws={"linewidth": 3},            # Linha de tendência bem forte
                height=6,
                aspect=1.5
            )
            plt.title("Tendência do Excedente vs. Densidade Populacional por Perfil")
            plt.xlabel("Densidade Populacional Dinâmica (hab/km²)")
            plt.ylabel("Excedente no Mês (kWh por kW instalado)")
            path = os.path.join(folder_path, "analise_perfil_regressao_segmentada.png")
            guardar_grafico(path)
            
            # ========================================================
            # OPÇÃO B: KDE PLOT 2D (Curvas de Nível / Densidade de População de Pontos)
            # ========================================================
            plt.figure(figsize=(12, 7))
            sns.kdeplot(
                data=df_perfis,
                x="Densidade_Ano",
                y="kWh por kW instalado",
                hue="Perfil",
                fill=True,
                alpha=0.4,
                levels=5, # Número de anéis de contorno
                palette={"Perfil 1 (~20)": "tab:blue", "Perfil 2 (~55)": "tab:orange"}
            )
            plt.title("Zonas de Concentração (Contornos 2D): Densidade vs. Excedente")
            plt.xlabel("Densidade Populacional Dinâmica (hab/km²)")
            plt.ylabel("Excedente no Mês (kWh por kW instalado)")
            path = os.path.join(folder_path, "analise_perfil_kde_contornos.png")
            guardar_grafico(path)
            
            print("✅ Análise concluída! Gerados gráficos de tendência e contornos.")
            return df_perfis 
    

        def analisar_tendencia_por_perfil_percentual(folder_path):
            print("\n🔄 A preparar dados dinâmicos com filtragem por PERCENTAGEM DE COBERTURA...")
            
            # 1. Isolar o escalão ]0, 4] e mapear a densidade dinâmica (como já tinhas)
            df_linhas = energia_escalao[energia_escalao["Escalão médio de potência"] == "]0, 4]"].copy()
            
            # [O teu código de merge com a densidade_long mantém-se igual aqui]
            anos_disponiveis = [col for col in densidade.columns if col.isdigit()]
            densidade["Concelho"] = densidade["Local"]
            densidade_long = densidade.melt(id_vars=["Concelho"], value_vars=anos_disponiveis, var_name="Ano", value_name="Densidade_Ano")
            densidade_long["Ano"] = densidade_long["Ano"].astype(int)
            df_linhas["Ano"] = df_linhas["Ano"].astype(int)
            
            if 2025 in df_linhas["Ano"].unique() and 2025 not in densidade_long["Ano"].unique():
                densidade_2024 = densidade_long[densidade_long["Ano"] == 2024].copy()
                densidade_2024["Ano"] = 2025
                densidade_long = pd.concat([densidade_long, densidade_2024], ignore_index=True)
                
            df_final = df_linhas.merge(densidade_long, on=["Concelho", "Ano"], how="inner")
            
            # =========================================================================
            # 2. SEPARAÇÃO DINÂMICA POR PERCENTIL (Capturar os 65% mais representativos)
            # =========================================================================
            
            # Primeiro, dividimos o dataset estritamente pelos meses que o teu gráfico provou definir cada perfil
            dados_meses_inverno = df_final[df_final["Mês"].isin([10, 11, 12, 1, 2])].copy()
            dados_meses_verao = df_final[df_final["Mês"].isin([4, 5, 6, 7, 8])].copy()
            
            # Definimos a percentagem desejada (ex: 65% do "coração" do pico)
            percentagem_cobertura = 65.0
            margem_cauda = (100.0 - percentagem_cobertura) / 2.0  # 17.5% de cada lado
            
            # Calcular os limites dinâmicos usando os percentis para o Inverno
            limite_inf_inv = np.percentile(dados_meses_inverno["kWh por kW instalado"], margem_cauda)
            limite_sup_inv = np.percentile(dados_meses_inverno["kWh por kW instalado"], 100.0 - margem_cauda)
            
            # Calcular os limites dinâmicos usando os percentis para o Verão
            limite_inf_ver = np.percentile(dados_meses_verao["kWh por kW instalado"], margem_cauda)
            limite_sup_ver = np.percentile(dados_meses_verao["kWh por kW instalado"], 100.0 - margem_cauda)
            
            # Mostrar no terminal quais foram os valores absolutos calculados pela estatística
            print(f"ℹ️ Limites calculados para cobrir {percentagem_cobertura}% de cada perfil:")
            print(f"   - Perfil Inverno: [{limite_inf_inv:.2f} a {limite_sup_inv:.2f}] kWh/kW")
            print(f"   - Perfil Verão:   [{limite_inf_ver:.2f} a {limite_sup_ver:.2f}] kWh/kW")
            
            # 3. Aplicar os filtros baseados nos percentis calculados
            perfil_inverno_filtrado = dados_meses_inverno[
                (dados_meses_inverno["kWh por kW instalado"] >= limite_inf_inv) & 
                (dados_meses_inverno["kWh por kW instalado"] <= limite_sup_inv)
            ].copy()
            perfil_inverno_filtrado["Perfil"] = f"Perfil Inverno (Centrais {percentagem_cobertura}%)"
            
            perfil_verao_filtrado = dados_meses_verao[
                (dados_meses_verao["kWh por kW instalado"] >= limite_inf_ver) & 
                (dados_meses_verao["kWh por kW instalado"] <= limite_sup_ver)
            ].copy()
            perfil_verao_filtrado["Perfil"] = f"Perfil Verão (Centrais {percentagem_cobertura}%)"
            
            # Juntar os dois perfis filtrados por percentagem
            df_perfis_pct = pd.concat([perfil_inverno_filtrado, perfil_verao_filtrado], ignore_index=True)
            
            # Zoom na densidade para o gráfico não distorcer com Lisboa/Porto
            df_perfis_pct = df_perfis_pct[df_perfis_pct["Densidade_Ano"] <= 1200]

            # =========================================================================
            # 4. GERAR OS VISUAIS (Idêntico ao anterior, mas agora com dados puramente percentuais)
            # =========================================================================
            plt.figure(figsize=(12, 6))
            sns.lmplot(
                data=df_perfis_pct, x="Densidade_Ano", y="kWh por kW instalado", hue="Perfil",
                scatter_kws={"alpha": 0.15, "s": 8}, line_kws={"linewidth": 3},
                height=6, aspect=1.5
            )
            plt.title(f"Regressão Linear: {percentagem_cobertura}% Central de Cada Perfil vs. Densidade")
            plt.xlabel("Densidade Populacional Dinâmica (hab/km²)")
            plt.ylabel("Excedente no Mês (kWh por kW instalado)")
            guardar_grafico(os.path.join(folder_path, "tendencia_percentual_por_perfil.png"))
            
            return df_perfis_pct


        folder_path = os.path.join(folder95, "1. Escalao 0-4")
        # Garantir que usamos a base filtrada do escalão ]0, 4]
        df_residencial = energia_escalao[energia_escalao["Escalão médio de potência"] == "]0, 4]"].copy()
        
        # 1. Definir as janelas em torno dos picos (Pico 1 = ~20, Pico 2 = ~55)
        # Definimos uma margem de +/- 3 unidades para capturar o "coração" de cada pico
        perfil_baixo_excedente = df_residencial[
            (df_residencial["kWh por kW instalado"] >= 17) & 
            (df_residencial["kWh por kW instalado"] <= 23)
        ].copy()
        
        perfil_alto_excedente = df_residencial[
            (df_residencial["kWh por kW instalado"] >= 52) & 
            (df_residencial["kWh por kW instalado"] <= 58)
        ].copy()
        
        # Adicionar uma etiqueta para podermos comparar os dois grupos nos gráficos
        perfil_baixo_excedente["Perfil"] = "Baixo Excedente (~20)"
        perfil_alto_excedente["Perfil"] = "Alto Excedente (~55)"
        
        # Juntar os dois perfis num DataFrame de análise
        df_perfis = pd.concat([perfil_baixo_excedente, perfil_alto_excedente], ignore_index=True)
        
        print(f"Observações no perfil Baixo: {len(perfil_baixo_excedente)}")
        print(f"Observações no perfil Alto: {len(perfil_alto_excedente)}")
        
        # ========================================================
        # ANÁLISE 1: O fator Sazonal (Será que um pico é o Inverno e outro o Verão?)
        # ========================================================
        plt.figure(figsize=(12, 6))
        sns.countplot(data=df_perfis, x="Mês", hue="Perfil", palette="muted")
        plt.title("Distribuição dos Perfis de Injeção ao longo dos Meses do Ano")
        plt.xlabel("Mês do Ano")
        plt.ylabel("Contagem de Observações")
        guardar_grafico(path=os.path.join(folder_path, "analise_perfil_por_mes.png"))
        
        # ========================================================
        # ANÁLISE 2: O fator Geográfico (Os distritos do Norte estão num pico e os do Sul no outro?)
        # ========================================================
        plt.figure(figsize=(14, 7))
        # Contagem percentual por distrito para ver a prevalência de cada perfil
        df_dist = df_perfis.groupby(["Distrito", "Perfil"]).size().unstack(fill_value=0)
        df_dist_pct = df_dist.div(df_dist.sum(axis=1), axis=0) * 100
        
        df_dist_pct.plot(kind="bar", stacked=True, color=["tab:blue", "tab:orange"], figsize=(14, 7))
        plt.title("Prevalência de Perfis de Excedente por Distrito")
        plt.xlabel("Distrito")
        plt.ylabel("Percentagem (%)")
        plt.xticks(rotation=45)
        guardar_grafico(path=os.path.join(folder_path, "analise_perfil_por_distrito.png"))
        
        # ========================================================
        # ANÁLISE 3: Variáveis Numéricas (Boxplot comparativo)
        # ========================================================
        # Vamos ver se a Potência Média instalada deles varia subtilmente
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df_perfis, x="Perfil", y="Potência média por instalação (kW)")
        plt.title("Comparação da Potência Média por Instalação entre Perfis")
        guardar_grafico(path=os.path.join(folder_path, "analise_perfil_boxplot_potencia.png"))

        analisar_observacoes_escalao_vs_densidade(folder_path)
        analisar_tendencia_por_perfil_percentual(folder_path)

    # 95.B - Analisar os perfis bimodais de excedente relativo (kWh por kW instalado) para o escalão ]4, 20.7]
    def graph_95B(folder95):
        folder_path = os.path.join(folder95, "2. Escalao 4-20.7")
        os.makedirs(folder_path, exist_ok=True)
        pass

    # 95.C - Analisar os perfis bimodais de excedente relativo (kWh por kW instalado) para o escalão ]20.7, 30]
    def graph_95C(folder95):
        folder_path = os.path.join(folder95, "3. Escalao 20.7-30")
        os.makedirs(folder_path, exist_ok=True)
        pass

    # 95.D - Analisar os perfis bimodais de excedente relativo (kWh por kW instalado) para o escalão ]30, 1000]
    def graph_95D(folder95):
        folder_path = os.path.join(folder95, "4. Escalao 30-1000")
        os.makedirs(folder_path, exist_ok=True)
        pass

    # 95.E - Analisar os perfis bimodais de excedente relativo (kWh por kW instalado) para o escalão >1000
    def graph_95E(folder95):
        folder_path = os.path.join(folder95, "5. Escalao +1000")
        os.makedirs(folder_path, exist_ok=True)
        pass


    graph_95_dir = os.path.join(OUTPUT_DIR, "graph_95")
    os.makedirs(graph_95_dir, exist_ok=True)
    graph_95A(graph_95_dir)
    graph_95B(graph_95_dir)
    graph_95C(graph_95_dir)
    graph_95D(graph_95_dir)
    graph_95E(graph_95_dir)


def graph_96():

    folder_96 = os.path.join(OUTPUT_DIR, "graph_96")
        
    def graph_por_escalao(folder_path, escalao_nome="]0, 4]"):
        print(f"\n🔄 A preparar dados para o Graph 96 (Correlação: Nº de UPACs vs. Excedente) — Escalão {escalao_nome}...")
        
        # 1. Isolar o escalão escolhido
        df_linhas = energia_escalao[energia_escalao["Escalão médio de potência"] == escalao_nome].copy()
        
        if df_linhas.empty:
            print(f"⚠️ Sem observações suficientes para o escalão {escalao_nome}")
            return
        
        # 2. Configurar o visual
        plt.figure(figsize=(12, 6))
        
        # Scatter plot com linha de regressão linear global
        sns.regplot(
            data=df_linhas,
            x="Número de Instalações",
            y="kWh por kW instalado",
            scatter_kws={"alpha": 0.3, "s": 12, "color": "tab:blue"},
            line_kws={"color": "tab:red", "linewidth": 2.5, "label": "Tendência de Correlação"}
        )
        
        # Calcular o coeficiente de correlação de Pearson de forma dinâmica
        correlacao = df_linhas["Número de Instalações"].corr(df_linhas["kWh por kW instalado"])
        
        # 3. Customização do gráfico
        plt.title(f"Graph 96: Avaliação de Correlação (Nº de UPACs vs. Excedente Relativo)\nEscalão {escalao_nome} (Pearson r: {correlacao:.2f})", fontsize=13)
        plt.xlabel("Número de Instalações (UPACs) por Observação")
        plt.ylabel("Excedente de Energia (kWh por kW instalado)")
        plt.legend(loc="upper right")
        
        # Gravação segura usando o teu sufixo padrão
        sufixo = escalao_nome.replace("]", "").replace("[", "").replace(",", "_").replace(" ", "").replace(">", "+")
        path = os.path.join(folder_path, f"graph_96_correlacao_upacs_{sufixo}.png")
        guardar_grafico(nome=f"graph_96_correlacao_upacs_{sufixo}.png", path=path)
        print(f"✅ Graph 96 para escalao {escalao_nome} guardado ")

    for escalao in energia_escalao["Escalão médio de potência"].unique():
        graph_por_escalao(folder_96, escalao)
    

def graph_97():

    folder_97 = os.path.join(OUTPUT_DIR, "graph_97")

    def graph_por_escalao(folder_path, escalao_nome="]0, 4]"):
        print(f"\n🔄 A preparar dados para o Graph 97 (Série Temporal Dual) — Escalão {escalao_nome}...")
        
        # 1. Isolar o escalão escolhido
        df_linhas = energia_escalao[energia_escalao["Escalão médio de potência"] == escalao_nome].copy()
        
        if df_linhas.empty:
            print(f"⚠️ Sem observações suficientes para o escalão {escalao_nome}")
            return
        
        # 2. Agrupar por 'Data' para ver o comportamento macro/nacional do escalão ao longo dos meses/anos
        df_tempo = df_linhas.groupby("Data").agg({
            "Número de Instalações": "sum",          # Volume total de UPACs ativas naquele período temporal
            "kWh por kW instalado": "mean"           # Comportamento médio do excedente relativo
        }).reset_index().sort_values("Data")
        
        # 3. Construção do gráfico de Duplo Eixo (Dual Axis)
        fig, ax1 = plt.subplots(figsize=(14, 6))
        
        # EIXO 1 (Esquerdo, Azul): Crescimento de UPACs ao longo do tempo
        color_upacs = 'tab:blue'
        ax1.plot(
            df_tempo["Data"], df_tempo["Número de Instalações"], 
            marker="o", color=color_upacs, linewidth=2.5, label="Nº Total de UPACs (Crescimento)"
        )
        ax1.set_xlabel("Linha Temporal (Meses / Anos)")
        ax1.set_ylabel("Capacidade Instalada Total (Número de UPACs)", color=color_upacs, fontsize=11)
        ax1.tick_params(axis='y', labelcolor=color_upacs)
        ax1.grid(True, alpha=0.3)
        
        # EIXO 2 (Direito, Laranja): Flutuação do Excedente Relativo
        ax2 = ax1.twinx()
        color_excedente = 'tab:orange'
        ax2.plot(
            df_tempo["Data"], df_tempo["kWh por kW instalado"], 
            marker="s", linestyle="--", color=color_excedente, linewidth=2, label="Excedente Médio (kWh/kW)"
        )
        ax2.set_ylabel("Excedente Relativo Médio (kWh por kW instalado)", color=color_excedente, fontsize=11)
        ax2.tick_params(axis='y', labelcolor=color_excedente)
        
        # 4. Ajustes finais e união das legendas de ambos os eixos
        plt.title(f"Graph 97: Impacto do Crescimento de UPACs na Injeção de Excedentes\nEvolução Temporal no Escalão {escalao_nome}", fontsize=13)
        
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")
        
        sufixo = escalao_nome.replace("]", "").replace("[", "").replace(",", "_").replace(" ", "").replace(">", "+")
        path = os.path.join(folder_path, f"graph_97_serie_temporal_{sufixo}.png")
        guardar_grafico(nome=f"graph_97_serie_temporal_{sufixo}.png", path=path)
        print(f"✅ Graph 97 para escalao {escalao_nome} guardado com sucesso!")

    for escalao in energia_escalao["Escalão médio de potência"].unique():
        graph_por_escalao(folder_97, escalao)



def main():
    clean_test_folder(OUTPUT_DIR)
    for func in globals():
        if func.startswith("graph_") and callable(globals()[func]):
            print(f"Criando gráfico: {func}...")
            globals()[func]()
    print("Gráficos criados com sucesso em:", OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    main()