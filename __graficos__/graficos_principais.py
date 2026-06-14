# pip install pandas matplotlib seaborn adjustText
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
from clean_princ_test_folder import main as limpar_pasta
import sys

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

OUTPUT_DIR = os.path.join(BASE_DIR, "__graficos__", "principais", "test")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# CONFIGURAÇÕES GLOBAIS DE ESTILO (IDEAL PARA AUDITÓRIOS / ACESSIBILIDADE)
# =========================
sns.set_theme(style="whitegrid")

plt.rcParams["figure.figsize"] = (16, 9)        # Resolução ideal 16:9 widescreen para projeções
plt.rcParams["axes.titlesize"] = 22             # Títulos principais gigantes
plt.rcParams["axes.titleweight"] = "bold"       # Título principal a NEGRITO
plt.rcParams["axes.titlepad"] = 20              # Espaçamento do título ao gráfico
plt.rcParams["axes.labelsize"] = 16             # Nomes dos eixos (X e Y) grandes
plt.rcParams["axes.labelweight"] = "bold"       # Nomes dos eixos a NEGRITO
plt.rcParams["xtick.labelsize"] = 14            # Valores das escalas numéricas do eixo X
plt.rcParams["ytick.labelsize"] = 14            # Valores das escalas numéricas do eixo Y
plt.rcParams["legend.fontsize"] = 14            # Texto dentro da legenda ampliado
plt.rcParams["legend.title_fontsize"] = 16      # Título da legenda ampliado


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
# LEITURA DOS DADOS
# =========================

upacs = pd.read_csv(PATH_UPACS, sep=",", encoding="utf-8-sig")
precos = pd.read_csv(PATH_PRECOS, sep=",", encoding="utf-8-sig")

upacs.columns = upacs.columns.str.strip()
precos.columns = precos.columns.str.strip()

upacs["Data"] = upacs["Trimestre"].apply(trimestre_para_data)
upacs["Ano"] = upacs["Data"].dt.year
ultimo_trimestre = upacs["Data"].max()
upacs_ultimo = upacs[upacs["Data"] == ultimo_trimestre].copy()

upacs = upacs[upacs["Tipo de Tecnologia"] == "Solar"].copy()

upacs["Potência Total Instalada UPAC (kW)"] = pd.to_numeric(upacs["Potência Total Instalada UPAC (kW)"], errors="coerce")
upacs["Número de instalacões"] = pd.to_numeric(upacs["Número de instalacões"], errors="coerce")

precos_long = precos.melt(var_name="Ano", value_name="Preco_USD_kW")
precos_long["Ano"] = precos_long["Ano"].astype(int)
precos_long["Preco_USD_kW"] = pd.to_numeric(precos_long["Preco_USD_kW"], errors="coerce")

upacs_anual = upacs.groupby("Ano").agg({"Número de instalacões": "sum", "Potência Total Instalada UPAC (kW)": "sum"}).reset_index()
upacs_anual["Potência média por instalação (kW)"] = upacs_anual["Potência Total Instalada UPAC (kW)"] / upacs_anual["Número de instalacões"]

upacs_preco_anual = upacs_anual.merge(precos_long, on="Ano", how="inner")

# =========================
# LEITURA DA BASE ENERGIA INJETADA
# =========================

PATH_ENERGIA = os.path.join(BASE_DIR, "e-redes", "data_input", "energia_injectada_upac.csv")
energia = pd.read_csv(PATH_ENERGIA, sep=";", encoding="utf-8-sig")
energia.columns = energia.columns.str.strip()

energia["Data"] = pd.to_datetime(energia["Data"], format="%Y-%m")
energia["Ano"] = energia["Data"].dt.year
energia["Mês"] = energia["Data"].dt.month

energia["Potência Instalada (kW)"] = pd.to_numeric(energia["Potência Instalada (kW)"], errors="coerce")
energia["Número de Instalações"] = pd.to_numeric(energia["Número de Instalações"], errors="coerce")
energia["Energia Injetada (kWh)"] = pd.to_numeric(energia["Energia Injetada (kWh)"], errors="coerce")

energia = energia.dropna(subset=["Potência Instalada (kW)", "Número de Instalações", "Energia Injetada (kWh)"])
energia["kWh por instalação"] = energia["Energia Injetada (kWh)"] / energia["Número de Instalações"]
energia["kWh por kW instalado"] = energia["Energia Injetada (kWh)"] / energia["Potência Instalada (kW)"]

energia_limpa = energia.dropna(subset=["Distrito", "Concelho"]).copy()
energia_limpa = energia_limpa[(energia_limpa["Potência Instalada (kW)"] > 0) & (energia_limpa["Número de Instalações"] > 0)].copy()

# =========================
# LEITURA DAS BASES DEMOGRÁFICAS
# =========================

pop_total = pd.read_csv(PATH_POP_TOTAL, sep=",", encoding="utf-8-sig")
pop_total.columns = pop_total.columns.str.strip()
if "Unnamed: 0" in pop_total.columns:
    pop_total = pop_total.drop(columns=["Unnamed: 0"])

anos_pop = [col for col in pop_total.columns if col.isdigit()]
for col in anos_pop:
    pop_total[col] = pd.to_numeric(pop_total[col], errors="coerce")

densidade = pd.read_csv(PATH_DENSIDADE, sep=";", encoding="utf-8-sig")
densidade.columns = densidade.columns.str.strip()
anos_densidade = [col for col in densidade.columns if col.isdigit()]

for col in anos_densidade:
    print(col)
    if col in ["2009", "2010", "2011", "2012"]:
        densidade.drop(columns=[col], inplace=True)
        continue
    densidade[col] = densidade[col].astype(str).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False)
    densidade[col] = pd.to_numeric(densidade[col], errors="coerce")

print(densidade.columns)

concelhos_eredes = set(upacs["Concelho"].dropna().unique())
pop_municipios = pop_total[pop_total["Name"].isin(concelhos_eredes)].copy()
densidade_municipios = densidade[densidade["Local"].isin(concelhos_eredes)].copy()

ano_pop_usado = "2025" if "2025" in pop_municipios.columns else max(anos_pop)
pop_municipios = pop_municipios[["Name", ano_pop_usado]].rename(columns={"Name": "Concelho", ano_pop_usado: "População"})

ano_densidade_usado = "2024"
densidade_municipios = densidade_municipios[["Local", ano_densidade_usado]].rename(columns={"Local": "Concelho", ano_densidade_usado: "Densidade populacional"})

upacs_concelho_ultimo = upacs_ultimo.groupby("Concelho").agg({"Número de instalacões": "sum", "Potência Total Instalada UPAC (kW)": "sum"}).reset_index()
base_demo = upacs_concelho_ultimo.merge(pop_municipios, on="Concelho", how="inner").merge(densidade_municipios, on="Concelho", how="inner")
base_demo = base_demo[(base_demo["População"] > 0) & (base_demo["Densidade populacional"] > 0)].copy()

base_demo["UPAC por 1000 habitantes"] = base_demo["Número de instalacões"] / base_demo["População"] * 1000
base_demo["kW por 1000 habitantes"] = base_demo["Potência Total Instalada UPAC (kW)"] / base_demo["População"] * 1000
base_demo["Potência média por instalação (kW)"] = base_demo["Potência Total Instalada UPAC (kW)"] / base_demo["Número de instalacões"]

energia_concelho = energia_limpa.groupby("Concelho").agg({"Energia Injetada (kWh)": "sum", "Potência Instalada (kW)": "sum", "Número de Instalações": "sum"}).reset_index()
energia_concelho["Excedente por kW"] = energia_concelho["Energia Injetada (kWh)"] / energia_concelho["Potência Instalada (kW)"]
energia_concelho["Excedente por instalação"] = energia_concelho["Energia Injetada (kWh)"] / energia_concelho["Número de Instalações"]

energia_demo = energia_concelho.merge(base_demo[["Concelho", "População", "Densidade populacional", "UPAC por 1000 habitantes", "kW por 1000 habitantes", "Potência média por instalação (kW)"]], on="Concelho", how="inner")
energia_demo = energia_demo[(energia_demo["População"] > 0) & (energia_demo["Densidade populacional"] > 0) & (energia_demo["Potência Instalada (kW)"] > 0) & (energia_demo["Número de Instalações"] > 0)].copy()
energia_demo["Energia injetada por 1000 habitantes"] = energia_demo["Energia Injetada (kWh)"] / energia_demo["População"] * 1000

base_demo["Classe de densidade"] = pd.cut(base_demo["Densidade populacional"], bins=[0, 50, 100, 250, 500, 1000, float("inf")], labels=["0-50", "50-100", "100-250", "250-500", "500-1000", ">1000"])

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


# =========================
# FUNÇÕES DE GRÁFICOS
# =========================

def graph_6():
    distritos_ultimo = upacs_ultimo.groupby("Distrito").agg({"Número de instalacões": "sum", "Potência Total Instalada UPAC (kW)": "sum"}).reset_index()
    plt.figure(figsize=(16, 9)) 
    sns.scatterplot(data=distritos_ultimo, x="Número de instalacões", y="Potência Total Instalada UPAC (kW)", s=300, color="crimson")

    texts = []
    for _, row in distritos_ultimo.iterrows():
        texts.append(plt.text(row["Número de instalacões"], row["Potência Total Instalada UPAC (kW)"], row["Distrito"], fontsize=14, fontweight='bold'))
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre Número de instalações e potência instalada por distrito")
    plt.xlabel("Número de instalações")
    plt.ylabel("Potência total instalada (kW)")
    guardar_grafico("06_instalacoes_vs_potencia_distrito.png")


def graph_13():
    instalacoes_escalao_tempo = upacs.groupby(["Data", "Escalão de potência instalada (kW)"])["Número de instalacões"].sum().reset_index()
    plt.figure(figsize=(16, 9))
    sns.lineplot(data=instalacoes_escalao_tempo, x="Data", y="Número de instalacões", hue="Escalão de potência instalada (kW)", marker="o", linewidth=4, markersize=10)
    plt.title("Evolução do número de instalações por escalão de potência")
    plt.xlabel("Trimestre")
    plt.ylabel("Número de instalações")
    plt.legend(title="Escalão", bbox_to_anchor=(1.02, 1), loc="upper left")
    guardar_grafico("13_evolucao_instalacoes_por_escalao.png")


def graph_14():
    potencia_escalao_tempo = upacs.groupby(["Data", "Escalão de potência instalada (kW)"])["Potência Total Instalada UPAC (kW)"].sum().reset_index()
    plt.figure(figsize=(16, 9))
    sns.lineplot(data=potencia_escalao_tempo, x="Data", y="Potência Total Instalada UPAC (kW)", hue="Escalão de potência instalada (kW)", marker="o", linewidth=4, markersize=10)
    plt.title("Evolução da potência instalada por escalão de potência")
    plt.xlabel("Trimestre")
    plt.ylabel("Potência total instalada (kW)")
    plt.legend(title="Escalão", bbox_to_anchor=(1.02, 1), loc="upper left")
    guardar_grafico("14_evolucao_potencia_por_escalao.png")


def graph_28():
    potencia_distrito_ultimo = upacs_ultimo.groupby("Distrito")["Potência Total Instalada UPAC (kW)"].sum().sort_values(ascending=False).reset_index()
    potencia_distrito_ultimo["Percentagem acumulada"] = potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"].cumsum() / potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"].sum() * 100
    potencia_distrito_ultimo["Posição"] = range(1, len(potencia_distrito_ultimo) + 1)

    plt.figure(figsize=(18, 10))
    sns.lineplot(data=potencia_distrito_ultimo, x="Posição", y="Percentagem acumulada", marker="o", linewidth=4, markersize=10, color="darkorange")

    for _, row in potencia_distrito_ultimo.iterrows():
        plt.text(row["Posição"], row["Percentagem acumulada"] + 2.5, row["Distrito"], fontsize=14, rotation=60, ha='left', fontweight='bold')

    plt.xticks(range(1, len(potencia_distrito_ultimo) + 1, 1))
    plt.title("Concentração acumulada da potência instalada por distrito")
    plt.xlabel("Distritos ordenados por potência instalada")
    plt.ylabel("Percentagem acumulada da potência (%)")
    plt.ylim(0, 115)
    plt.yticks(range(0, 101, 10))
    guardar_grafico("28_concentracao_acumulada_potencia_distrito.png")


def graph_29():
    instalacoes_distrito_ultimo = upacs_ultimo.groupby("Distrito")["Número de instalacões"].sum().sort_values(ascending=False).reset_index()
    instalacoes_distrito_ultimo["Percentagem acumulada"] = instalacoes_distrito_ultimo["Número de instalacões"].cumsum() / instalacoes_distrito_ultimo["Número de instalacões"].sum() * 100
    instalacoes_distrito_ultimo["Posição"] = range(1, len(instalacoes_distrito_ultimo) + 1)

    plt.figure(figsize=(18, 10))
    sns.lineplot(data=instalacoes_distrito_ultimo, x="Posição", y="Percentagem acumulada", marker="o", linewidth=4, markersize=10, color="darkblue")

    for _, row in instalacoes_distrito_ultimo.iterrows():
        plt.text(row["Posição"], row["Percentagem acumulada"] + 2.5, row["Distrito"], fontsize=14, rotation=60, ha='left', fontweight='bold')

    plt.xticks(range(1, len(instalacoes_distrito_ultimo) + 1, 1))
    plt.title("Concentração acumulada das instalações por distrito")
    plt.xlabel("Distritos ordenados por número de instalações")
    plt.ylabel("Percentagem acumulada das instalações (%)")
    plt.ylim(0, 115)
    plt.yticks(range(0, 101, 10))
    guardar_grafico("29_concentracao_acumulada_instalacoes_distrito.png")


def graph_38():
    energia_distrito_scatter = energia.groupby("Distrito").agg({"Potência Instalada (kW)": "sum", "Energia Injetada (kWh)": "sum"}).reset_index()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_distrito_scatter, x="Potência Instalada (kW)", y="Energia Injetada (kWh)", s=300, color="darkgreen")

    texts = []
    for _, row in energia_distrito_scatter.iterrows():
        # Linha corrigida aqui:
        texts.append(plt.text(row["Potência Instalada (kW)"], row["Energia Injetada (kWh)"], row["Distrito"], fontsize=14, fontweight='bold'))
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre potência instalada e energia injetada por distrito")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("38_potencia_vs_energia_por_distrito.png")


def graph_39():
    energia_inst_scatter = energia.groupby("Distrito").agg({"Número de Instalações": "sum", "Energia Injetada (kWh)": "sum"}).reset_index()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_inst_scatter, x="Número de Instalações", y="Energia Injetada (kWh)", s=300, color="teal")

    texts = []
    for _, row in energia_inst_scatter.iterrows():
        texts.append(plt.text(row["Número de Instalações"], row["Energia Injetada (kWh)"], row["Distrito"], fontsize=14, fontweight='bold'))
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    plt.title("Relação entre número de instalações e energia injetada por distrito")
    plt.xlabel("Número de instalações")
    plt.ylabel("Energia injetada (kWh)")
    guardar_grafico("39_instalacoes_vs_energia_por_distrito.png")


def graph_49():
    # 1. Configuração do tamanho da figura para corresponder ao padrão dos anteriores (18x10)
    # ou mantendo proporções limpas com fontes legíveis
    plt.figure(figsize=(18, 10))

    # 2. Plot da linha com marcadores destacados e cores corporativas fortes
    sns.lineplot(
        data=energia_distrito_acumulada,
        x="Posição",
        y="Percentagem acumulada",
        marker="o",
        linewidth=4,
        markersize=10,
        color="darkgreen"  # Uma cor distinta para diferenciar de Potência (laranja) e Instalações (azul)
    )

    # 3. Iteração e posicionamento cirúrgico das etiquetas com rotação a 60°
    # O acréscimo de + 2.5 no Y previne que o texto atropele o marcador redondo
    for _, row in energia_distrito_acumulada.iterrows():
        plt.text(
            row["Posição"], 
            row["Percentagem acumulada"] + 2.5, 
            row["Distrito"], 
            fontsize=14, 
            rotation=60, 
            ha='left', 
            fontweight='bold'
        )

    # 4. Escala X definida de 1 em 1 para garantir correspondência com cada ponto
    plt.xticks(range(1, len(energia_distrito_acumulada) + 1, 1))

    # 5. Margem técnica Y estendida até 115 para acomodar perfeitamente os textos do topo da curva
    plt.ylim(0, 115)
    plt.yticks(range(0, 101, 10))

    # 6. Títulos e legendas estruturados
    plt.title("Concentração acumulada da energia injetada por distrito")
    plt.xlabel("Distritos ordenados por energia injetada")
    plt.ylabel("Percentagem acumulada da energia (%)")

    # 7. Exportação do asset gráfico para a diretoria local
    guardar_grafico("49_concentracao_acumulada_energia_distrito.png")

def graph_51():
    plt.figure(figsize=(16, 9))
    sns.histplot(energia["kWh por kW instalado"], bins=50, kde=True)
    plt.title("Distribuição da energia injetada por kW instalado")
    plt.xlabel("kWh por kW instalado")
    plt.ylabel("Frequência")
    guardar_grafico("51_distribuicao_kwh_por_kw.png")


def graph_53():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia, x="Potência Instalada (kW)", y="kWh por kW instalado", alpha=0.4, s=100)
    plt.title("Relação entre potência instalada e excedente relativo")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("53_potencia_vs_excedente.png")


def graph_59():
    excedente_mes_distrito = energia_limpa.groupby(["Distrito", "Mês"]).agg({"Energia Injetada (kWh)": "sum", "Potência Instalada (kW)": "sum"}).reset_index()
    excedente_mes_distrito["Excedente por kW"] = excedente_mes_distrito["Energia Injetada (kWh)"] / excedente_mes_distrito["Potência Instalada (kW)"]
    heatmap_excedente_pivot = excedente_mes_distrito.pivot(index="Distrito", columns="Mês", values="Excedente por kW")

    plt.figure(figsize=(16, 10))
    sns.heatmap(heatmap_excedente_pivot, cmap="YlOrRd", linewidths=0.5, cbar_kws={'label': 'Excedente por kW instalado'})
    plt.title("Heatmap do excedente relativo por distrito e mês")
    plt.xlabel("Mês")
    plt.ylabel("Distrito")
    guardar_grafico("59_heatmap_excedente_kw_distrito_mes.png")


def graph_66():
    energia_positiva = energia_limpa[energia_limpa["Energia Injetada (kWh)"] > 0].copy()
    plt.figure(figsize=(16, 9))
    sns.histplot(data=energia_positiva, x="Energia Injetada (kWh)", bins=60, log_scale=True)
    plt.title("Distribuição logarítmica da energia injetada")
    plt.xlabel("Energia injetada (kWh) - escala logarítmica")
    plt.ylabel("Frequência")
    guardar_grafico("66_distribuicao_log_energia_injetada.png")


def graph_67():
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

    # Tamanho expandido 16:9 ideal para projeção
    plt.figure(figsize=(16, 9))

    # Gráfico de dispersão com bolhas aumentadas (150 a 1200) para o auditório conseguir diferenciar
    sns.scatterplot(
        data=scatter_distrito_excedente,
        x="Potência Instalada (kW)",
        y="Excedente por kW",
        size="Número de Instalações",
        sizes=(150, 1200),
        alpha=0.7,
        legend=True
    )

    # Criação dos textos gigantes (14pt) a negrito para os distritos
    texts = []
    for _, row in scatter_distrito_excedente.iterrows():
        texts.append(
            plt.text(
                row["Potência Instalada (kW)"],
                row["Excedente por kW"],
                row["Distrito"],
                fontsize=14,
                fontweight='bold'
            )
        )
    
    # O adjust_text garante que as letras grandes não colidam com as bolhas
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='black', lw=1))

    # Títulos e labels gerados limpos para usarem as regras globais do rcParams
    plt.title("Potência instalada vs excedente relativo por distrito")
    plt.xlabel("Potência instalada (kW)")
    plt.ylabel("kWh injetados por kW instalado")

    guardar_grafico("67_potencia_vs_excedente_size_instalacoes.png")


def graph_73_200k():
    base_demo_200000 = base_demo[base_demo["População"] <= 200000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_200000, x="População", y="Número de instalacões", alpha=0.7, s=150)
    plt.xlim(0, 200000)
    plt.title("Relação entre população e número de instalações UPAC (Até 200k hab.)")
    plt.xlabel("População")
    plt.ylabel("Número de instalações")
    guardar_grafico("73_populacao_vs_instalacoes_200000.png")


def graph_73_25k():
    base_demo_25000 = base_demo[base_demo["População"] <= 25000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_25000, x="População", y="Número de instalacões", alpha=0.7, s=150)
    plt.xlim(0, 25000)
    plt.title("Relação entre população e número de instalações UPAC (Até 25k hab.)")
    plt.xlabel("População")
    plt.ylabel("Número de instalações")
    guardar_grafico("73_populacao_vs_instalacoes_25000.png")


def graph_74():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo, x="População", y="Potência Total Instalada UPAC (kW)", alpha=0.7, s=150)
    plt.title("Relação entre população e potência instalada")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")
    guardar_grafico("74_populacao_vs_potencia.png")


def graph_74_200k():
    base_demo_200000 = base_demo[base_demo["População"] <= 200000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_200000, x="População", y="Potência Total Instalada UPAC (kW)", alpha=0.7, s=150)
    plt.xlim(0, 200000)
    plt.title("Relação entre população e potência instalada (Até 200k hab.)")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")
    guardar_grafico("74_populacao_vs_potencia_200000.png")


def graph_75():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo, x="Densidade populacional", y="UPAC por 1000 habitantes", alpha=0.7, s=150)
    plt.title("Densidade populacional vs UPAC por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")
    guardar_grafico("75_densidade_vs_upac_por_1000.png")


def graph_75_1000():
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_1000, x="Densidade populacional", y="UPAC por 1000 habitantes", alpha=0.7, s=150)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs UPAC por 1000 habitantes (Até 1000 hab./km²)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")
    guardar_grafico("75_densidade_vs_upac_por_1000_1000.png")


def graph_76():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo, x="Densidade populacional", y="kW por 1000 habitantes", alpha=0.7, s=150)
    plt.title("Densidade populacional vs potência instalada por 1000 habitantes")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kW por 1000 habitantes")
    guardar_grafico("76_densidade_vs_kw_por_1000.png")


def graph_76_1000():
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_1000, x="Densidade populacional", y="kW por 1000 habitantes", alpha=0.7, s=150)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs potência instalada por 1000 habitantes (Até 1000 hab./km²)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kW por 1000 habitantes")
    guardar_grafico("76_densidade_vs_kw_por_1000_1000.png")


def graph_77():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo, x="Densidade populacional", y="Potência média por instalação (kW)", alpha=0.7, s=150)
    plt.title("Densidade populacional vs potência média por instalação")
    plt.xlabel("Densidade populacional")
    plt.ylabel("Potência média por instalação (kW)")
    guardar_grafico("77_densidade_vs_potencia_media.png")


def graph_77_1000():
    base_demo_1000 = base_demo[base_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo_1000, x="Densidade populacional", y="Potência média por instalação (kW)", alpha=0.7, s=150)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs potência média por instalação (Até 1000 hab./km²)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("Potência média por instalação (kW)")
    guardar_grafico("77_densidade_vs_potencia_media_1000.png")


def graph_78():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=base_demo, x="População", y="Potência Total Instalada UPAC (kW)", size="Número de instalacões", sizes=(100, 1000), alpha=0.6, legend=True)
    plt.title("População vs potência instalada (Dimensão pelo número de instalações)")
    plt.xlabel("População")
    plt.ylabel("Potência instalada (kW)")
    guardar_grafico("78_populacao_potencia_size_instalacoes.png")


def graph_80():
    plt.figure(figsize=(16, 9))
    sns.histplot(data=base_demo, x="UPAC por 1000 habitantes", bins=40, kde=True)
    plt.title("Distribuição relativa de UPACs por concelho")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("Frequência")
    guardar_grafico("80_distribuicao_upac_por_1000_habitantes.png")


def graph_81():
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_demo_1000, x="Densidade populacional", y="Excedente por kW", alpha=0.7, s=150)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs excedente por kW instalado (Até 1000 hab./km²)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("81_densidade_vs_excedente_por_kw_1000.png")


def graph_82():
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_demo_1000, x="Densidade populacional", y="Excedente por instalação", alpha=0.7, s=150)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs excedente por instalação (Até 1000 hab./km²)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por instalação")
    guardar_grafico("82_densidade_vs_excedente_por_instalacao_1000.png")


def graph_83():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_demo, x="UPAC por 1000 habitantes", y="Excedente por kW", alpha=0.7, s=150)
    plt.title("Penetração de UPAC vs excedente relativo")
    plt.xlabel("UPAC por 1000 habitantes")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("83_upac_por_1000_vs_excedente_kw.png")


def graph_84():
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_demo, x="kW por 1000 habitantes", y="Excedente por kW", alpha=0.7, s=150)
    plt.title("Potência instalada por habitante vs excedente relativo")
    plt.xlabel("kW por 1000 habitantes")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("84_kw_por_1000_vs_excedente_kw.png")


def graph_89():
    energia_demo_1000 = energia_demo[energia_demo["Densidade populacional"] <= 1000].copy()
    plt.figure(figsize=(16, 9))
    sns.scatterplot(data=energia_demo_1000, x="Densidade populacional", y="Excedente por kW", size="Potência Instalada (kW)", sizes=(100, 1000), alpha=0.6, legend=True)
    plt.xlim(0, 1000)
    plt.title("Densidade populacional vs excedente por kW (Dimensão pela potência instalada)")
    plt.xlabel("Densidade populacional")
    plt.ylabel("kWh injetados por kW instalado")
    guardar_grafico("89_densidade_vs_excedente_kw_size_potencia_1000.png")


def graph_91():
    plt.figure(figsize=(16, 9))
    sns.boxplot(data=base_demo, x="Classe de densidade", y="UPAC por 1000 habitantes")
    plt.title("Distribuição das UPAC por 1000 habitantes por classe de densidade")
    plt.xlabel("Classe de densidade populacional")
    plt.ylabel("UPAC por 1000 habitantes")
    guardar_grafico("91_boxplot_upac_por_1000_por_classe_densidade.png")


def graph_92():
    plt.figure(figsize=(16, 9))
    sns.boxplot(data=base_demo, x="Classe de densidade", y="kW por 1000 habitantes")
    plt.title("Distribuição da potência instalada por 1000 habitantes por classe de densidade")
    plt.xlabel("Classe de densidade populacional")
    plt.ylabel("kW por 1000 habitantes")
    guardar_grafico("92_boxplot_kw_por_1000_por_classe_densidade.png")


# =========================
# FLUXO PRINCIPAL
# =========================

def main():
    limpar_pasta(OUTPUT_DIR)
    func_excl = []
    # for i, func in enumerate(func_excl):
    #     func = "graph_" + func
    #     func_excl[i] = func

    for func in globals():
        if func in func_excl: continue
        elif func.startswith("graph_") and callable(globals()[func]):
            print(f"Criando gráfico: {func}...")
            globals()[func]()


    
    print("Gráficos criados com sucesso em:", OUTPUT_DIR)


if __name__ == "__main__":
    main()