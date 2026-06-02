# pip install pandas matplotlib seaborn
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from clean_princ_test_folder import main as limpar_pasta


# =========================
# CONFIGURAÇÕES
# =========================

limpar_pasta()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

OUTPUT_DIR = os.path.join(BASE_DIR, "graficos", "principais", "test")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


# =========================
# FUNÇÕES AUXILIARES
# =========================

def guardar_grafico(nome):
    path = os.path.join(OUTPUT_DIR, nome)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")


def trimestre_para_data(trimestre):
    ano = int(trimestre[:4])
    t = int(trimestre[-1])
    mes = {1: 1, 2: 4, 3: 7, 4: 10}[t]
    return pd.Timestamp(year=ano, month=mes, day=1)

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


energia_limpa = energia.dropna(subset=["Distrito", "Concelho"]).copy()


# =========================
# 6. COMPARAÇÃO: INSTALAÇÕES VS POTÊNCIA POR DISTRITO
# =========================
def graf_6():
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
# 13. EVOLUÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# =========================
def graf_13():
    instalacoes_escalao_tempo = (
        upacs
        .groupby(["Data", "Escalão de potência instalada (kW)"])["Número de instalacões"]
        .sum()
        .reset_index()
    )

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
def graph_14():
    potencia_escalao_tempo = (
        upacs
        .groupby(["Data", "Escalão de potência instalada (kW)"])["Potência Total Instalada UPAC (kW)"]
        .sum()
        .reset_index()
    )

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
# 28. CONCENTRAÇÃO DA POTÊNCIA INSTALADA POR DISTRITO
# =========================
def graph_28():
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
def graph_29():
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
# 38. POTÊNCIA INSTALADA VS ENERGIA INJETADA
# =========================
def graph_38():
    energia_distrito_scatter = (
        energia
        .groupby("Distrito")
        .agg({
            "Potência Instalada (kW)": "sum",
            "Energia Injetada (kWh)": "sum"
        })
        .reset_index()
    )

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
def graph_39():
    energia_inst_scatter = (
        energia
        .groupby("Distrito")
        .agg({
        "Número de Instalações": "sum",
        "Energia Injetada (kWh)": "sum"
        }).reset_index()
    )

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
# 51. DISTRIBUIÇÃO DO kWh POR kW INSTALADO
# =========================
def graph_51():
    plt.figure(figsize=(10, 6))
    sns.histplot(
        energia["kWh por kW instalado"],
        bins=50,
        kde=True
    )
    plt.title("Distribuição da energia injetada por kW instalado")
    plt.xlabel("kWh por kW instalado")
    plt.ylabel("Frequência")
    guardar_grafico("51_distribuicao_kwh_por_kw.png")


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
# 59. HEATMAP DISTRITO × MÊS DO EXCEDENTE POR kW
# =========================
def graph_59():
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
# 66. DISTRIBUIÇÃO LOGARÍTMICA DA ENERGIA INJETADA
# =========================
def graph_66():
    energia_positiva = energia_limpa[
        energia_limpa["Energia Injetada (kWh)"] > 0
    ].copy()

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




print("Gráficos criados com sucesso em:", OUTPUT_DIR)