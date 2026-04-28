# pip install pandas matplotlib seaborn
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# CONFIGURAÇÕES
# =========================

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

OUTPUT_DIR = os.path.join(BASE_DIR, "graficos", "output")
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
    plt.show()


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
summary_df(upacs, "UPACs")
summary_df(precos, "Preços")

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


# # =========================
# # 1. EVOLUÇÃO DO NÚMERO TOTAL DE INSTALAÇÕES
# # =========================
#
# instalacoes_trimestre = (
#     upacs
#     .groupby("Data")["Número de instalacões"]
#     .sum()
#     .reset_index()
# )
#
# plt.figure()
# sns.lineplot(
#     data=instalacoes_trimestre,
#     x="Data",
#     y="Número de instalacões",
#     marker="o"
# )
# plt.title("Evolução do número total de instalações UPAC solares")
# plt.xlabel("Trimestre")
# plt.ylabel("Número de instalacões")
# guardar_grafico("01_evolucao_instalacoes_solares.png")
#
#
# # =========================
# # 2. EVOLUÇÃO DA POTÊNCIA TOTAL INSTALADA
# # =========================
#
# potencia_trimestre = (
#     upacs
#     .groupby("Data")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .reset_index()
# )
#
# plt.figure()
# sns.lineplot(
#     data=potencia_trimestre,
#     x="Data",
#     y="Potência Total Instalada UPAC (kW)",
#     marker="o"
# )
# plt.title("Evolução da potência total instalada em UPAC solares")
# plt.xlabel("Trimestre")
# plt.ylabel("Potência total instalada (kW)")
# guardar_grafico("02_evolucao_potencia_solar.png")
#
#
# # =========================
# # 3. POTÊNCIA MÉDIA POR INSTALAÇÃO
# # =========================
#
# media_trimestre = potencia_trimestre.merge(instalacoes_trimestre, on="Data")
# media_trimestre["Potência média por instalação (kW)"] = (
#     media_trimestre["Potência Total Instalada UPAC (kW)"]
#     / media_trimestre["Número de instalacões"]
# )
#
# plt.figure()
# sns.lineplot(
#     data=media_trimestre,
#     x="Data",
#     y="Potência média por instalação (kW)",
#     marker="o"
# )
# plt.title("Potência média por instalação UPAC solar")
# plt.xlabel("Trimestre")
# plt.ylabel("kW por instalação")
# guardar_grafico("03_potencia_media_por_instalacao.png")
#
#
# # =========================
# # 4. TOP 10 DISTRITOS POR Número de instalacões
# # =========================
#
# ultimo_trimestre = upacs["Data"].max()
# upacs_ultimo = upacs[upacs["Data"] == ultimo_trimestre]
#
# top_distritos_inst = (
#     upacs_ultimo
#     .groupby("Distrito")["Número de instalacões"]
#     .sum()
#     .sort_values(ascending=False)
#     .head(10)
#     .reset_index()
# )
#
# plt.figure()
# sns.barplot(
#     data=top_distritos_inst,
#     x="Número de instalacões",
#     y="Distrito"
# )
# plt.title(f"Top 10 distritos por Número de instalacões solares — último trimestre")
# plt.xlabel("Número de instalacões")
# plt.ylabel("Distrito")
# guardar_grafico("04_top10_distritos_instalacoes.png")
#
#
# # =========================
# # 5. TOP 10 DISTRITOS POR POTÊNCIA INSTALADA
# # =========================
#
# top_distritos_pot = (
#     upacs_ultimo
#     .groupby("Distrito")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .sort_values(ascending=False)
#     .head(10)
#     .reset_index()
# )
#
# plt.figure()
# sns.barplot(
#     data=top_distritos_pot,
#     x="Potência Total Instalada UPAC (kW)",
#     y="Distrito"
# )
# plt.title("Top 10 distritos por potência solar instalada")
# plt.xlabel("Potência total instalada (kW)")
# plt.ylabel("Distrito")
# guardar_grafico("05_top10_distritos_potencia.png")
#
#
# # =========================
# # 6. COMPARAÇÃO: INSTALAÇÕES VS POTÊNCIA POR DISTRITO
# # =========================
#
# distritos_ultimo = (
#     upacs_ultimo
#     .groupby("Distrito")
#     .agg({
#         "Número de instalacões": "sum",
#         "Potência Total Instalada UPAC (kW)": "sum"
#     })
#     .reset_index()
# )
#
# plt.figure()
# sns.scatterplot(
#     data=distritos_ultimo,
#     x="Número de instalacões",
#     y="Potência Total Instalada UPAC (kW)",
#     s=100
# )
#
# for _, row in distritos_ultimo.iterrows():
#     plt.text(
#         row["Número de instalacões"],
#         row["Potência Total Instalada UPAC (kW)"],
#         row["Distrito"],
#         fontsize=8
#     )
#
# plt.title("Relação entre Número de instalacões e potência instalada por distrito")
# plt.xlabel("Número de instalacões")
# plt.ylabel("Potência total instalada (kW)")
# guardar_grafico("06_instalacoes_vs_potencia_distrito.png")
#
#
# # =========================
# # 7. EVOLUÇÃO POR DISTRITO — TOP 5 DISTRITOS
# # =========================
#
# top5_distritos = (
#     upacs_ultimo
#     .groupby("Distrito")["Número de instalacões"]
#     .sum()
#     .sort_values(ascending=False)
#     .head(5)
#     .index
# )
#
# evolucao_top5 = (
#     upacs[upacs["Distrito"].isin(top5_distritos)]
#     .groupby(["Data", "Distrito"])["Número de instalacões"]
#     .sum()
#     .reset_index()
# )
#
# plt.figure()
# sns.lineplot(
#     data=evolucao_top5,
#     x="Data",
#     y="Número de instalacões",
#     hue="Distrito",
#     marker="o"
# )
# plt.title("Evolução das instalações solares nos 5 distritos com mais UPAC")
# plt.xlabel("Trimestre")
# plt.ylabel("Número de instalacões")
# guardar_grafico("07_evolucao_top5_distritos.png")
#
#
# # =========================
# # 8. PREÇO USD/kW EM PORTUGAL
# # =========================
#
# plt.figure()
# sns.lineplot(
#     data=precos_long,
#     x="Ano",
#     y="Preco_USD_kW",
#     marker="o"
# )
# plt.title("Evolução do preço de instalação solar em Portugal")
# plt.xlabel("Ano")
# plt.ylabel("Preço USD/kW")
# guardar_grafico("08_preco_usd_kw_portugal.png")
#
#
# # =========================
# # 9. PREÇO VS POTÊNCIA INSTALADA ANUAL
# # =========================
#
# potencia_anual = (
#     upacs
#     .groupby("Ano")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .reset_index()
# )
#
# preco_potencia = potencia_anual.merge(precos_long, on="Ano", how="inner")
#
# fig, ax1 = plt.subplots(figsize=(12, 6))
#
# ax1.plot(
#     preco_potencia["Ano"],
#     preco_potencia["Potência Total Instalada UPAC (kW)"],
#     marker="o",
#     label="Potência instalada"
# )
# ax1.set_xlabel("Ano")
# ax1.set_ylabel("Potência total instalada (kW)")
#
# ax2 = ax1.twinx()
# ax2.plot(
#     preco_potencia["Ano"],
#     preco_potencia["Preco_USD_kW"],
#     marker="o",
#     linestyle="--",
#     label="Preço USD/kW"
# )
# ax2.set_ylabel("Preço USD/kW")
#
# plt.title("Potência instalada vs preço de instalação solar")
# guardar_grafico("09_potencia_vs_preco.png")
#
#
# # =========================
# # 10. PREÇO VS Número de instalacões ANUAL
# # =========================
#
# instalacoes_anual = (
#     upacs
#     .groupby("Ano")["Número de instalacões"]
#     .sum()
#     .reset_index()
# )
#
# preco_instalacoes = instalacoes_anual.merge(precos_long, on="Ano", how="inner")
#
# fig, ax1 = plt.subplots(figsize=(12, 6))
#
# ax1.plot(
#     preco_instalacoes["Ano"],
#     preco_instalacoes["Número de instalacões"],
#     marker="o"
# )
# ax1.set_xlabel("Ano")
# ax1.set_ylabel("Número de instalacões")
#
# ax2 = ax1.twinx()
# ax2.plot(
#     preco_instalacoes["Ano"],
#     preco_instalacoes["Preco_USD_kW"],
#     marker="o",
#     linestyle="--"
# )
# ax2.set_ylabel("Preço USD/kW")
#
# plt.title("Número de instalacões solares vs preço de instalação")
# guardar_grafico("10_instalacoes_vs_preco.png")
#
# # =========================
# # 11. DISTRIBUIÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# # =========================
#
#
# instalacoes_escalao = (
#     upacs
#     .groupby("Escalão de potência instalada (kW)")["Número de instalacões"]
#     .sum()
#     .sort_values(ascending=False)
#     .reset_index()
# )
#
# plt.figure(figsize=(12, 6))
# sns.barplot(
#     data=instalacoes_escalao,
#     x="Número de instalacões",
#     y="Escalão de potência instalada (kW)"
# )
# plt.title("Distribuição do número de instalações por escalão de potência")
# plt.xlabel("Número de instalações")
# plt.ylabel("Escalão de potência instalada (kW)")
# guardar_grafico("11_instalacoes_por_escalao.png")
#
#
# # =========================
# # 12. POTÊNCIA TOTAL POR ESCALÃO DE POTÊNCIA
# # =========================
#
# potencia_escalao = (
#     upacs
#     .groupby("Escalão de potência instalada (kW)")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .sort_values(ascending=False)
#     .reset_index()
# )
#
# plt.figure(figsize=(12, 6))
# sns.barplot(
#     data=potencia_escalao,
#     x="Potência Total Instalada UPAC (kW)",
#     y="Escalão de potência instalada (kW)"
# )
# plt.title("Potência total instalada por escalão de potência")
# plt.xlabel("Potência total instalada (kW)")
# plt.ylabel("Escalão de potência instalada (kW)")
# guardar_grafico("12_potencia_por_escalao.png")
#
#
# # =========================
# # 13. EVOLUÇÃO DAS INSTALAÇÕES POR ESCALÃO DE POTÊNCIA
# # =========================
#
# instalacoes_escalao_tempo = (
#     upacs
#     .groupby(["Data", "Escalão de potência instalada (kW)"])["Número de instalacões"]
#     .sum()
#     .reset_index()
# )
#
# plt.figure(figsize=(14, 7))
# sns.lineplot(
#     data=instalacoes_escalao_tempo,
#     x="Data",
#     y="Número de instalacões",
#     hue="Escalão de potência instalada (kW)",
#     marker="o"
# )
# plt.title("Evolução do número de instalações por escalão de potência")
# plt.xlabel("Trimestre")
# plt.ylabel("Número de instalações")
# plt.legend(title="Escalão", bbox_to_anchor=(1.05, 1), loc="upper left")
# guardar_grafico("13_evolucao_instalacoes_por_escalao.png")
#
#
# # =========================
# # 14. EVOLUÇÃO DA POTÊNCIA POR ESCALÃO DE POTÊNCIA
# # =========================
#
# potencia_escalao_tempo = (
#     upacs
#     .groupby(["Data", "Escalão de potência instalada (kW)"])["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .reset_index()
# )
#
# plt.figure(figsize=(14, 7))
# sns.lineplot(
#     data=potencia_escalao_tempo,
#     x="Data",
#     y="Potência Total Instalada UPAC (kW)",
#     hue="Escalão de potência instalada (kW)",
#     marker="o"
# )
# plt.title("Evolução da potência instalada por escalão de potência")
# plt.xlabel("Trimestre")
# plt.ylabel("Potência total instalada (kW)")
# plt.legend(title="Escalão", bbox_to_anchor=(1.05, 1), loc="upper left")
# guardar_grafico("14_evolucao_potencia_por_escalao.png")

#
# # =========================
# # 15. PESO PERCENTUAL DAS INSTALAÇÕES POR ESCALÃO NO ÚLTIMO TRIMESTRE
# # =========================
#
# peso_instalacoes_escalao = (
#     upacs_ultimo
#     .groupby("Escalão de potência instalada (kW)")["Número de instalacões"]
#     .sum()
#     .reset_index()
# )
#
# peso_instalacoes_escalao["Percentagem"] = (
#     peso_instalacoes_escalao["Número de instalacões"]
#     / peso_instalacoes_escalao["Número de instalacões"].sum()
#     * 100
# )
#
# peso_instalacoes_escalao = peso_instalacoes_escalao.sort_values("Percentagem", ascending=False)
#
# plt.figure(figsize=(12, 6))
# sns.barplot(
#     data=peso_instalacoes_escalao,
#     x="Percentagem",
#     y="Escalão de potência instalada (kW)"
# )
# plt.title("Peso percentual das instalações por escalão no último trimestre")
# plt.xlabel("Percentagem das instalações (%)")
# plt.ylabel("Escalão de potência instalada (kW)")
# guardar_grafico("15_percentagem_instalacoes_por_escalao.png")
#
#
# # =========================
# # 16. PESO PERCENTUAL DA POTÊNCIA POR ESCALÃO NO ÚLTIMO TRIMESTRE
# # =========================
#
# peso_potencia_escalao = (
#     upacs_ultimo
#     .groupby("Escalão de potência instalada (kW)")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .reset_index()
# )
#
# peso_potencia_escalao["Percentagem"] = (
#     peso_potencia_escalao["Potência Total Instalada UPAC (kW)"]
#     / peso_potencia_escalao["Potência Total Instalada UPAC (kW)"].sum()
#     * 100
# )
#
# peso_potencia_escalao = peso_potencia_escalao.sort_values("Percentagem", ascending=False)
#
# plt.figure(figsize=(12, 6))
# sns.barplot(
#     data=peso_potencia_escalao,
#     x="Percentagem",
#     y="Escalão de potência instalada (kW)"
# )
# plt.title("Peso percentual da potência instalada por escalão no último trimestre")
# plt.xlabel("Percentagem da potência instalada (%)")
# plt.ylabel("Escalão de potência instalada (kW)")
# guardar_grafico("16_percentagem_potencia_por_escalao.png")
#
#
# # =========================
# # 17. TOP 15 CONCELHOS POR NÚMERO DE INSTALAÇÕES
# # =========================
#
# top_concelhos_inst = (
#     upacs_ultimo
#     .groupby("Concelho")["Número de instalacões"]
#     .sum()
#     .sort_values(ascending=False)
#     .head(15)
#     .reset_index()
# )
#
# plt.figure(figsize=(12, 7))
# sns.barplot(
#     data=top_concelhos_inst,
#     x="Número de instalacões",
#     y="Concelho"
# )
# plt.title("Top 15 concelhos por número de instalações solares")
# plt.xlabel("Número de instalações")
# plt.ylabel("Concelho")
# guardar_grafico("17_top15_concelhos_instalacoes.png")
#
#
# # =========================
# # 18. TOP 15 CONCELHOS POR POTÊNCIA INSTALADA
# # =========================
#
# top_concelhos_pot = (
#     upacs_ultimo
#     .groupby("Concelho")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .sort_values(ascending=False)
#     .head(15)
#     .reset_index()
# )
#
# plt.figure(figsize=(12, 7))
# sns.barplot(
#     data=top_concelhos_pot,
#     x="Potência Total Instalada UPAC (kW)",
#     y="Concelho"
# )
# plt.title("Top 15 concelhos por potência solar instalada")
# plt.xlabel("Potência total instalada (kW)")
# plt.ylabel("Concelho")
# guardar_grafico("18_top15_concelhos_potencia.png")
#
#
# # =========================
# # 19. POTÊNCIA MÉDIA POR INSTALAÇÃO POR DISTRITO
# # =========================
#
# pot_media_distrito = (
#     upacs_ultimo
#     .groupby("Distrito")
#     .agg({
#         "Número de instalacões": "sum",
#         "Potência Total Instalada UPAC (kW)": "sum"
#     })
#     .reset_index()
# )
#
# pot_media_distrito["Potência média por instalação (kW)"] = (
#     pot_media_distrito["Potência Total Instalada UPAC (kW)"]
#     / pot_media_distrito["Número de instalacões"]
# )
#
# pot_media_distrito = pot_media_distrito.sort_values(
#     "Potência média por instalação (kW)",
#     ascending=False
# )
#
# plt.figure(figsize=(12, 7))
# sns.barplot(
#     data=pot_media_distrito,
#     x="Potência média por instalação (kW)",
#     y="Distrito"
# )
# plt.title("Potência média por instalação por distrito")
# plt.xlabel("Potência média por instalação (kW)")
# plt.ylabel("Distrito")
# guardar_grafico("19_potencia_media_por_distrito.png")
#
#
# # =========================
# # 20. RELAÇÃO ENTRE PREÇO USD/kW E POTÊNCIA MÉDIA POR INSTALAÇÃO
# # =========================
#
# pot_media_anual = (
#     upacs
#     .groupby("Ano")
#     .agg({
#         "Número de instalacões": "sum",
#         "Potência Total Instalada UPAC (kW)": "sum"
#     })
#     .reset_index()
# )
#
# pot_media_anual["Potência média por instalação (kW)"] = (
#     pot_media_anual["Potência Total Instalada UPAC (kW)"]
#     / pot_media_anual["Número de instalacões"]
# )
#
# preco_pot_media = pot_media_anual.merge(precos_long, on="Ano", how="inner")
#
# plt.figure(figsize=(10, 6))
# sns.scatterplot(
#     data=preco_pot_media,
#     x="Preco_USD_kW",
#     y="Potência média por instalação (kW)",
#     s=120
# )
#
# for _, row in preco_pot_media.iterrows():
#     plt.text(
#         row["Preco_USD_kW"],
#         row["Potência média por instalação (kW)"],
#         int(row["Ano"]),
#         fontsize=9
#     )
#
# plt.title("Relação entre preço USD/kW e potência média por instalação")
# plt.xlabel("Preço USD/kW")
# plt.ylabel("Potência média por instalação (kW)")
# guardar_grafico("20_preco_vs_potencia_media.png")
#
#
# # =========================
# # 21. POTÊNCIA TOTAL INSTALADA VS PREÇO USD/kW
# # =========================
#
# fig, ax1 = plt.subplots(figsize=(12, 6))
#
# # Linha 1 (potência)
# ax1.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Potência Total Instalada UPAC (kW)"],
#     marker="o",
#     linewidth=2,
#     color="tab:blue",
#     label="Potência instalada"
# )
# ax1.set_xlabel("Ano")
# ax1.set_ylabel("Potência total instalada (kW)", color="tab:blue")
# ax1.tick_params(axis="y", labelcolor="tab:blue")
#
# # Linha 2 (preço)
# ax2 = ax1.twinx()
# ax2.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Preco_USD_kW"],
#     marker="o",
#     linestyle="--",
#     linewidth=2,
#     color="tab:red",
#     label="Preço USD/kW"
# )
# ax2.set_ylabel("Preço USD/kW", color="tab:red")
# ax2.tick_params(axis="y", labelcolor="tab:red")
#
# plt.title("Potência total instalada vs preço USD/kW")
#
# # Legenda combinada
# lines_1, labels_1 = ax1.get_legend_handles_labels()
# lines_2, labels_2 = ax2.get_legend_handles_labels()
# plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")
#
# guardar_grafico("21_potencia_vs_preco_colorido.png")
#
#
# # =========================
# # 22. NÚMERO TOTAL DE INSTALAÇÕES VS PREÇO USD/kW
# # =========================
#
# fig, ax1 = plt.subplots(figsize=(12, 6))
#
# ax1.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Número de instalacões"],
#     marker="o",
#     linewidth=2,
#     color="tab:blue"
# )
# ax1.set_xlabel("Ano")
# ax1.set_ylabel("Número total de instalações")
# ax1.tick_params(axis="y")
#
# ax2 = ax1.twinx()
# ax2.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Preco_USD_kW"],
#     marker="o",
#     linestyle="--",
#     linewidth=2,
#     color="tab:red"
# )
# ax2.set_ylabel("Preço USD/kW")
# ax2.tick_params(axis="y")
#
# plt.title("Número total de instalações UPAC solares vs preço USD/kW")
# guardar_grafico("22_instalacoes_totais_vs_preco_duplo_eixo.png")
#
#
# # =========================
# # 23. POTÊNCIA MÉDIA POR INSTALAÇÃO VS PREÇO USD/kW
# # =========================
#
# fig, ax1 = plt.subplots(figsize=(12, 6))
#
# ax1.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Potência média por instalação (kW)"],
#     marker="o",
#     linewidth=2,
#     color="tab:green"
# )
# ax1.set_xlabel("Ano")
# ax1.set_ylabel("Potência média por instalação (kW)")
# ax1.tick_params(axis="y")
#
# ax2 = ax1.twinx()
# ax2.plot(
#     upacs_preco_anual["Ano"],
#     upacs_preco_anual["Preco_USD_kW"],
#     marker="o",
#     linestyle="--",
#     linewidth=2,
#     color="tab:orange"
# )
# ax2.set_ylabel("Preço USD/kW")
# ax2.tick_params(axis="y")
#
# plt.title("Potência média por instalação vs preço USD/kW")
# guardar_grafico("23_potencia_media_vs_preco_duplo_eixo.png")
#
#
# # =========================
# # 24. CRESCIMENTO PERCENTUAL ANUAL DA POTÊNCIA INSTALADA
# # =========================
#
# crescimento_potencia = upacs_anual.copy()
# crescimento_potencia["Crescimento percentual da potência (%)"] = (
#     crescimento_potencia["Potência Total Instalada UPAC (kW)"]
#     .pct_change()
#     * 100
# )
#
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     data=crescimento_potencia.dropna(),
#     x="Ano",
#     y="Crescimento percentual da potência (%)"
# )
# plt.title("Crescimento percentual anual da potência instalada")
# plt.xlabel("Ano")
# plt.ylabel("Crescimento da potência (%)")
# guardar_grafico("24_crescimento_percentual_potencia.png")
#
#
# # =========================
# # 25. CRESCIMENTO PERCENTUAL ANUAL DAS INSTALAÇÕES
# # =========================
#
# crescimento_instalacoes = upacs_anual.copy()
# crescimento_instalacoes["Crescimento percentual das instalações (%)"] = (
#     crescimento_instalacoes["Número de instalacões"]
#     .pct_change()
#     * 100
# )
#
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     data=crescimento_instalacoes.dropna(),
#     x="Ano",
#     y="Crescimento percentual das instalações (%)"
# )
# plt.title("Crescimento percentual anual do número de instalações")
# plt.xlabel("Ano")
# plt.ylabel("Crescimento das instalações (%)")
# guardar_grafico("25_crescimento_percentual_instalacoes.png")
#
#
# # =========================
# # 26. VARIAÇÃO ANUAL DO PREÇO USD/kW
# # =========================
#
# variacao_preco = precos_long.sort_values("Ano").copy()
# variacao_preco["Variação percentual do preço (%)"] = (
#     variacao_preco["Preco_USD_kW"]
#     .pct_change()
#     * 100
# )
#
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     data=variacao_preco.dropna(),
#     x="Ano",
#     y="Variação percentual do preço (%)"
# )
# plt.title("Variação percentual anual do preço USD/kW")
# plt.xlabel("Ano")
# plt.ylabel("Variação do preço (%)")
# guardar_grafico("26_variacao_percentual_preco.png")
#
#
# # =========================
# # 27. ÍNDICE BASE 100: POTÊNCIA, INSTALAÇÕES E PREÇO
# # =========================
#
# indice = upacs_preco_anual.sort_values("Ano").copy()
#
# base_potencia = indice["Potência Total Instalada UPAC (kW)"].iloc[0]
# base_instalacoes = indice["Número de instalacões"].iloc[0]
# base_preco = indice["Preco_USD_kW"].iloc[0]
#
# indice["Índice potência"] = indice["Potência Total Instalada UPAC (kW)"] / base_potencia * 100
# indice["Índice instalações"] = indice["Número de instalacões"] / base_instalacoes * 100
# indice["Índice preço"] = indice["Preco_USD_kW"] / base_preco * 100
#
# indice_long = indice.melt(
#     id_vars="Ano",
#     value_vars=["Índice potência", "Índice instalações", "Índice preço"],
#     var_name="Indicador",
#     value_name="Índice base 100"
# )
#
# plt.figure(figsize=(12, 6))
# sns.lineplot(
#     data=indice_long,
#     x="Ano",
#     y="Índice base 100",
#     hue="Indicador",
#     marker="o"
# )
# plt.title("Evolução indexada: potência, instalações e preço")
# plt.xlabel("Ano")
# plt.ylabel("Índice base 100")
# guardar_grafico("27_indice_base100_potencia_instalacoes_preco.png")
#
#
# # =========================
# # 28. CONCENTRAÇÃO DA POTÊNCIA INSTALADA POR DISTRITO
# # =========================
#
# potencia_distrito_ultimo = (
#     upacs_ultimo
#     .groupby("Distrito")["Potência Total Instalada UPAC (kW)"]
#     .sum()
#     .sort_values(ascending=False)
#     .reset_index()
# )
#
# potencia_distrito_ultimo["Percentagem acumulada"] = (
#     potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"]
#     .cumsum()
#     / potencia_distrito_ultimo["Potência Total Instalada UPAC (kW)"].sum()
#     * 100
# )
#
# plt.figure(figsize=(12, 6))
# sns.lineplot(
#     data=potencia_distrito_ultimo,
#     x=range(1, len(potencia_distrito_ultimo) + 1),
#     y="Percentagem acumulada",
#     marker="o"
# )
# plt.title("Concentração acumulada da potência instalada por distrito")
# plt.xlabel("Distritos ordenados por potência instalada")
# plt.ylabel("Percentagem acumulada da potência (%)")
# guardar_grafico("28_concentracao_acumulada_potencia_distrito.png")
#
#
# # =========================
# # 29. CONCENTRAÇÃO DAS INSTALAÇÕES POR DISTRITO
# # =========================
#
# instalacoes_distrito_ultimo = (
#     upacs_ultimo
#     .groupby("Distrito")["Número de instalacões"]
#     .sum()
#     .sort_values(ascending=False)
#     .reset_index()
# )
#
# instalacoes_distrito_ultimo["Percentagem acumulada"] = (
#     instalacoes_distrito_ultimo["Número de instalacões"]
#     .cumsum()
#     / instalacoes_distrito_ultimo["Número de instalacões"].sum()
#     * 100
# )
#
# plt.figure(figsize=(12, 6))
# sns.lineplot(
#     data=instalacoes_distrito_ultimo,
#     x=range(1, len(instalacoes_distrito_ultimo) + 1),
#     y="Percentagem acumulada",
#     marker="o"
# )
# plt.title("Concentração acumulada das instalações por distrito")
# plt.xlabel("Distritos ordenados por número de instalações")
# plt.ylabel("Percentagem acumulada das instalações (%)")
# guardar_grafico("29_concentracao_acumulada_instalacoes_distrito.png")
#
#
# # =========================
# # 30. DISTRITOS COM MAIOR PESO RELATIVO NA POTÊNCIA NACIONAL
# # =========================
#
# peso_distrito_potencia = potencia_distrito_ultimo.copy()
#
# peso_distrito_potencia["Peso nacional (%)"] = (
#     peso_distrito_potencia["Potência Total Instalada UPAC (kW)"]
#     / peso_distrito_potencia["Potência Total Instalada UPAC (kW)"].sum()
#     * 100
# )
#
# peso_distrito_potencia = peso_distrito_potencia.sort_values(
#     "Peso nacional (%)",
#     ascending=False
# )
#
# plt.figure(figsize=(12, 7))
# sns.barplot(
#     data=peso_distrito_potencia,
#     x="Peso nacional (%)",
#     y="Distrito"
# )
# plt.title("Peso de cada distrito na potência solar instalada nacional")
# plt.xlabel("Peso na potência nacional (%)")
# plt.ylabel("Distrito")
# guardar_grafico("30_peso_distrito_potencia_nacional.png")

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

print("Gráficos criados com sucesso em:", OUTPUT_DIR)