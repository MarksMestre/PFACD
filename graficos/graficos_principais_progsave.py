# pip install pandas matplotlib seaborn
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
from clean_princ_test_folder import main as limpar_pasta
import sys

# =========================
# CONFIGURAÇÕES
# =========================
# =========================
# CONFIGURAÇÕES
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
from __configure__.paths import BASE_FOLDER as BASE_DIR, POP_PREDICTION_OUTPUT as PATH_POP_TOTAL, DENSIDADE_CSV as PATH_DENSIDADE



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
    plt.close()


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
    sep=";",
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

    # Gráfico maior para acomodar letras grandes
    plt.figure(figsize=(16, 9)) 
    sns.scatterplot(
        data=distritos_ultimo,
        x="Número de instalacões",
        y="Potência Total Instalada UPAC (kW)",
        s=300, # Pontos gigantes para o auditório ver bem
        color="crimson"
    )

    texts = []
    for _, row in distritos_ultimo.iterrows():
        texts.append(
            plt.text(
                row["Número de instalacões"], 
                row["Potência Total Instalada UPAC (kW)"], 
                row["Distrito"], 
                fontsize=14, # Letra significativamente maior
                fontweight='bold'
            )
        )
    
    # Se usar adjustText, ele vai gerir estas letras grandes sem sobrepor:
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre Número de instalações e potência instalada por distrito", fontsize=22, pad=20, fontweight='bold')
    plt.xlabel("Número de instalações", fontsize=16, fontweight='bold')
    plt.ylabel("Potência total instalada (kW)", fontsize=16, fontweight='bold')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    guardar_grafico("06_instalacoes_vs_potencia_distrito.png")


# =========================
# 13. EVOLUÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# =========================
def graph_13():
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

    plt.figure(figsize=(16, 9))
    sns.lineplot(
        data=potencia_escalao_tempo,
        x="Data",
        y="Potência Total Instalada UPAC (kW)",
        hue="Escalão de potência instalada (kW)",
        marker="o",
        linewidth=4, # Linha bem grossa para ecrãs de projeção
        markersize=10
    )
    plt.title("Evolução da potência instalada por escalão de potência", fontsize=22, pad=20, fontweight='bold')
    plt.xlabel("Trimestre", fontsize=16, fontweight='bold')
    plt.ylabel("Potência total instalada (kW)", fontsize=16, fontweight='bold')
    
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    # Legenda gigante posicionada fora para não tapar as linhas
    plt.legend(title="Escalão", title_fontsize=16, fontsize=14, bbox_to_anchor=(1.02, 1), loc="upper left")
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

    plt.figure(figsize=(18, 10)) # Aumentado o espaço para as letras não saírem das bordas

    sns.lineplot(
        data=potencia_distrito_ultimo,
        x="Posição",
        y="Percentagem acumulada",
        marker="o",
        linewidth=4,
        markersize=10,
        color="darkorange"
    )

    # Nomes a 14pt e rotação de 60° para evitar colisões
    for _, row in potencia_distrito_ultimo.iterrows():
        plt.text(
            row["Posição"], 
            row["Percentagem acumulada"] + 2.5, # Mais espaço acima do ponto
            row["Distrito"], 
            fontsize=14, 
            rotation=60, 
            ha='left',
            fontweight='bold'
        )

    plt.xticks(range(1, len(potencia_distrito_ultimo) + 1, 1), fontsize=14)
    plt.title("Concentração acumulada da potência instalada por distrito", fontsize=22, pad=25, fontweight='bold')
    plt.xlabel("Distritos ordenados por potência instalada", fontsize=16, fontweight='bold')
    plt.ylabel("Percentagem acumulada da potência (%)", fontsize=16, fontweight='bold')
    plt.ylim(0, 115) # Teto aumentado para 115 para acomodar o texto inclinado gigante no topo
    plt.yticks(range(0, 101, 10), fontsize=14)

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

    plt.figure(figsize=(18, 10)) 

    sns.lineplot(
        data=instalacoes_distrito_ultimo,
        x="Posição",
        y="Percentagem acumulada",
        marker="o",
        linewidth=4,
        markersize=10,
        color="darkblue"
    )

    # Alinhamento e tamanhos macro para auditórios
    for _, row in instalacoes_distrito_ultimo.iterrows():
        plt.text(
            row["Posição"], 
            row["Percentagem acumulada"] + 2.5, 
            row["Distrito"], 
            fontsize=14, 
            rotation=60, 
            ha='left',
            fontweight='bold'
        )

    plt.xticks(range(1, len(instalacoes_distrito_ultimo) + 1, 1), fontsize=14)
    plt.title("Concentração acumulada das instalações por distrito", fontsize=22, pad=25, fontweight='bold')
    plt.xlabel("Distritos ordenados por número de instalações", fontsize=16, fontweight='bold')
    plt.ylabel("Percentagem acumulada das instalações (%)", fontsize=16, fontweight='bold')
    plt.ylim(0, 115) 
    plt.yticks(range(0, 101, 10), fontsize=14)

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

    plt.figure(figsize=(16, 9))
    sns.scatterplot(
        data=energia_distrito_scatter,
        x="Potência Instalada (kW)",
        y="Energia Injetada (kWh)",
        s=300,
        color="darkgreen"
    )

    texts = []
    for _, row in energia_distrito_scatter.iterrows():
        texts.append(
            plt.text(
                row["Potência Instalada (kW)"], 
                row["Energia Injetada (kWh)"], 
                row["Distrito"], 
                fontsize=14, 
                fontweight='bold'
            )
        )
        
    # Se usar adjustText:
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre potência instalada e energia injetada por distrito", fontsize=22, pad=20, fontweight='bold')
    plt.xlabel("Potência instalada (kW)", fontsize=16, fontweight='bold')
    plt.ylabel("Energia injetada (kWh)", fontsize=16, fontweight='bold')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
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

    plt.figure(figsize=(16, 9))
    sns.scatterplot(
        data=energia_inst_scatter,
        x="Número de Instalações",
        y="Energia Injetada (kWh)",
        s=300,
        color="teal"
    )

    texts = []
    for _, row in energia_inst_scatter.iterrows():
        texts.append(
            plt.text(
                row["Número de Instalações"], 
                row["Energia Injetada (kWh)"], 
                row["Distrito"], 
                fontsize=14, 
                fontweight='bold'
            )
        )
        
    # Se usar adjustText:
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre número de instalações e energia injetada por distrito", fontsize=22, pad=20, fontweight='bold')
    plt.xlabel("Número de instalações", fontsize=16, fontweight='bold')
    plt.ylabel("Energia injetada (kWh)", fontsize=16, fontweight='bold')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
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

# =========================
# 73_200000. POPULAÇÃO VS NÚMERO DE INSTALAÇÕES (ZOOM)
# =========================
def graph_73_200k():
    base_demo_200000 = base_demo[base_demo["População"] <= 200000].copy()

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
def graph_73_25k():
    base_demo_25000 = base_demo[base_demo["População"] <= 25000].copy()

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
    base_demo_200000 = base_demo[base_demo["População"] <= 200000].copy()
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
def graph_75_1000():
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()

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
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()
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
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()
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
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()

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
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()
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
# 89. DENSIDADE VS EXCEDENTE POR kW COM TAMANHO PELA POTÊNCIA INSTALADA
# =========================
def graph_89():
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()
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


def main():
    limpar_pasta()
    graph_6()
    graph_13()
    graph_14()
    graph_28()
    graph_29()
    graph_38()
    graph_39()
    graph_51()
    graph_53()
    graph_59()
    graph_66()
    graph_73_200k()
    graph_73_25k()
    graph_74()
    graph_74_200k()
    graph_75()
    graph_75_1000()
    graph_76()
    graph_76_1000()
    graph_77()
    graph_77_1000()
    graph_78()
    graph_80()
    graph_81()
    graph_82()
    graph_83()
    graph_84()
    graph_89()
    graph_91()
    graph_92()
    print("Gráficos criados com sucesso em:", OUTPUT_DIR)


if __name__ == "__main__":
    main()

