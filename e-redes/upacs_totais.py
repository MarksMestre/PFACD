from pathlib import Path
import re
import csv
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import plotly.express as px
import json

# Mostrar todas as colunas
pd.set_option('display.max_columns', None)

# Mostrar todas as linhas
pd.set_option('display.max_rows', None)

# Não cortar a largura da tabela
pd.set_option('display.width', None)

# Mostrar
pd.set_option('display.max_colwidth', None)

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURAÇÃO
# ============================================================
FILENAME = "8-unidades-de-producao-para-autoconsumo.csv"
TOP_N = 15  # número de categorias a mostrar em alguns gráficos


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def detectar_delimitador(file_path: Path, encoding: str = "utf-8"):
    """
    Tenta detetar automaticamente o delimitador do CSV.
    """
    with open(file_path, "r", encoding=encoding, newline="") as f:
        sample = f.read(5000)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter
    except Exception:
        # fallback razoável para ficheiros portugueses/europeus
        return ";"


def ler_csv_robusto(file_path: Path) -> pd.DataFrame:
    """
    Lê o CSV tentando diferentes encodings e delimitadores.
    Não força parse de números logo à entrada, para evitar erros.
    """
    encodings_teste = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]

    ultimo_erro = None
    for enc in encodings_teste:
        try:
            sep = detectar_delimitador(file_path, encoding=enc)
            df = pd.read_csv(
                file_path,
                sep=sep,
                encoding=enc,
                dtype=str,  # ler tudo como texto primeiro
                engine="python"
            )
            print(f"[OK] Ficheiro lido com encoding='{enc}' e separador='{sep}'")
            return df
        except Exception as e:
            ultimo_erro = e

    raise RuntimeError(f"Não foi possível ler o ficheiro CSV. Último erro: {ultimo_erro}")


def normalizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa espaços extra e caracteres invisíveis dos nomes das colunas.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    return df


def limpar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove espaços extra dos valores string.
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(
                {"": np.nan, "nan": np.nan, "None": np.nan, "NULL": np.nan}
            )
    return df


def converter_numerico_serie(s: pd.Series) -> pd.Series:
    """
    Converte séries com números no formato europeu:
    - remove separadores de milhar
    - troca vírgula decimal por ponto
    - preserva NaN
    - devolve float/int quando possível
    """
    s = s.astype(str).str.strip()

    # Tratar valores vazios ou pseudo-missing
    s = s.replace({
        "": np.nan,
        "nan": np.nan,
        "None": np.nan,
        "NULL": np.nan
    })

    # exemplos:
    # "2.669,05" -> "2669.05"
    # "45" -> "45"
    # "0,001" -> "0.001"
    s = (
        s.str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^\d\.\-]", "", regex=True)
    )

    return pd.to_numeric(s, errors="coerce")


def extrair_intervalo_escalao(df: pd.DataFrame, col: str = "Escalão de potência instalada (kW)"):
    """
    Extrai limites inferior e superior de colunas do tipo:
    ]30, 1000]  ou [0, 30]
    """
    df = df.copy()
    if col not in df.columns:
        return df

    # Extrair 2 números da string
    extraido = df[col].astype(str).str.extract(
        r"[-\]\[]?\s*([\d.,]+)\s*,\s*([\d.,]+)\s*[\]\[]?"
    )

    if extraido.shape[1] == 2:
        df["Escalao_kW_min"] = converter_numerico_serie(extraido[0])
        df["Escalao_kW_max"] = converter_numerico_serie(extraido[1])

    return df


def imprimir_resumo_inicial(df: pd.DataFrame):
    print("\n" + "=" * 80)
    print("DIMENSÃO DA BASE DE DADOS")
    print("=" * 80)
    print(f"Linhas: {df.shape[0]:,}")
    print(f"Colunas: {df.shape[1]}")

    print("\n" + "=" * 80)
    print("COLUNAS")
    print("=" * 80)
    for c in df.columns:
        print(f"- {c}")

    print("\n" + "=" * 80)
    print("TIPOS DE DADOS")
    print("=" * 80)
    print(df.dtypes)

    print("\n" + "=" * 80)
    print("PRIMEIRAS 5 LINHAS")
    print("=" * 80)
    print(df.head())

    print("\n" + "=" * 80)
    print("VALORES EM FALTA")
    print("=" * 80)
    missing = df.isna().sum().sort_values(ascending=False)
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "n_missing": missing,
        "%_missing": missing_pct
    })
    print(missing_df[missing_df["n_missing"] > 0] if (missing > 0).any() else "Sem valores em falta detetados.")

    print("\n" + "=" * 80)
    print("LINHAS DUPLICADAS")
    print("=" * 80)
    print(f"Número de linhas duplicadas: {df.duplicated().sum()}")

    print("\n" + "=" * 80)
    print("NÚMERO DE VALORES ÚNICOS POR COLUNA")
    print("=" * 80)
    print(df.nunique(dropna=True).sort_values(ascending=False))


def imprimir_resumo_numerico(df: pd.DataFrame):
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        print("\nNão existem colunas numéricas para descrever.")
        return

    print("\n" + "=" * 80)
    print("ESTATÍSTICAS DESCRITIVAS DAS COLUNAS NUMÉRICAS")
    print("=" * 80)
    print(df[num_cols].describe().T)




def mostrar_top_categorias(df: pd.DataFrame, colunas):
    for col in colunas:
        if col in df.columns:
            print("\n" + "=" * 80)
            print(f"TOP VALORES - {col}")
            print("=" * 80)
            print(df[col].value_counts(dropna=False).head(15))


# ============================================================
# FUNÇÕES DE GRÁFICOS
# ============================================================
def grafico_barras_contagem(df: pd.DataFrame, coluna: str, top_n: int = 15, titulo: str = None):
    if coluna not in df.columns:
        return

    contagens = df[coluna].value_counts(dropna=False).head(top_n)
    if contagens.empty:
        return

    plt.figure(figsize=(12, 6))
    contagens.sort_values().plot(kind="barh")
    plt.title(titulo or f"Top {top_n} categorias por número de registos - {coluna}")
    plt.xlabel("Número de registos")
    plt.ylabel(coluna)
    plt.tight_layout()
    plt.show()


def grafico_barras_soma(df: pd.DataFrame, grupo: str, valor: str, top_n: int = 15, titulo: str = None):
    if grupo not in df.columns or valor not in df.columns:
        return

    dados = (
        df.groupby(grupo, dropna=False)[valor]
        .sum(min_count=1)
        .sort_values(ascending=False)
        .head(top_n)
    )

    if dados.empty:
        return

    plt.figure(figsize=(12, 6))
    dados.sort_values().plot(kind="barh")
    plt.title(titulo or f"Top {top_n} por soma de {valor}")
    plt.xlabel(valor)
    plt.ylabel(grupo)
    plt.tight_layout()
    plt.show()




def histograma(df: pd.DataFrame, coluna: str, bins: int = 30, titulo: str = None):
    if coluna not in df.columns:
        return
    serie = df[coluna].dropna()
    if serie.empty:
        return

    plt.figure(figsize=(10, 6))
    plt.hist(serie, bins=bins)
    plt.title(titulo or f"Distribuição de {coluna}")
    plt.xlabel(coluna)
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.show()


def boxplot_por_categoria(df: pd.DataFrame, categoria: str, valor: str, top_n: int = 10, titulo: str = None):
    if categoria not in df.columns or valor not in df.columns:
        return

    top_cats = df[categoria].value_counts().head(top_n).index
    temp = df[df[categoria].isin(top_cats)][[categoria, valor]].dropna()

    if temp.empty:
        return

    grupos = [temp.loc[temp[categoria] == cat, valor].values for cat in top_cats]

    plt.figure(figsize=(12, 6))
    plt.boxplot(grupos, labels=top_cats, vert=True)
    plt.title(titulo or f"Distribuição de {valor} por {categoria}")
    plt.xlabel(categoria)
    plt.ylabel(valor)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def scatter_relacao(df: pd.DataFrame, x: str, y: str, tamanho: str = None, titulo: str = None):
    if x not in df.columns or y not in df.columns:
        return

    cols = [x, y]
    if tamanho and tamanho in df.columns:
        cols.append(tamanho)

    temp = df[cols].dropna()
    if temp.empty:
        return

    plt.figure(figsize=(10, 6))

    if tamanho and tamanho in temp.columns:
        size = temp[tamanho].copy()
        size = size.fillna(size.median())
        size = 20 + 180 * (size - size.min()) / (size.max() - size.min() + 1e-9)
        plt.scatter(temp[x], temp[y], s=size, alpha=0.6)
    else:
        plt.scatter(temp[x], temp[y], alpha=0.6)

    plt.title(titulo or f"{y} vs {x}")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.show()


def heatmap_correlacao(df: pd.DataFrame, titulo: str = "Mapa de correlação"):
    num_df = df.select_dtypes(include=[np.number]).copy()
    if num_df.shape[1] < 2:
        return

    corr = num_df.corr(numeric_only=True)

    plt.figure(figsize=(10, 8))
    im = plt.imshow(corr, aspect="auto")
    plt.colorbar(im)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title(titulo)

    # escrever valor em cada célula
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)

    plt.tight_layout()
    plt.show()


def grafico_evolucao_trimestre(df: pd.DataFrame, valor: str, titulo: str = None):
    if "Trimestre" not in df.columns or valor not in df.columns:
        return

    temp = df[["Trimestre", valor]].dropna().copy()
    if temp.empty:
        return

    # ordenar por ano e trimestre no formato 2024T2
    def chave_trimestre(x):
        m = re.match(r"(\d{4})T(\d)", str(x))
        if m:
            return int(m.group(1)), int(m.group(2))
        return (9999, 9)

    ordem = sorted(temp["Trimestre"].unique(), key=chave_trimestre)

    serie = temp.groupby("Trimestre")[valor].sum().reindex(ordem)

    plt.figure(figsize=(12, 6))
    plt.plot(serie.index, serie.values, marker="o")
    plt.title(titulo or f"Evolução temporal de {valor}")
    plt.xlabel("Trimestre")
    plt.ylabel(valor)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# ============================================================
# LEITURA E PREPARAÇÃO DOS DADOS
# ============================================================
project_dir = Path.cwd()
file_path = project_dir / FILENAME

if not file_path.exists():
    raise FileNotFoundError(
        f"Não encontrei o ficheiro em: {file_path}\n"
        f"Confirma que o CSV está no diretório atual do teu projeto Python."
    )

df = ler_csv_robusto(file_path)
df = normalizar_nomes_colunas(df)
df = limpar_texto(df)

# Conversão de colunas numéricas prováveis
cols_to_numeric = [
    "Número de instalacões",
    "Potência Total Instalada UPAC (kW)",
    "CPE's",
    "relacao_instalacoes_por_cpe",
    "relacao_potencia_por_cpe"
]

for col in cols_to_numeric:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Garantir que códigos postais ficam como texto
if "Código Postal" in df.columns:
    df["Código Postal"] = df["Código Postal"].astype(str).str.extract(r"(\d+)")[0]

# Extrair limites do escalão de potência, se existir
df = extrair_intervalo_escalao(df)

# ============================================================
# ANÁLISE EXPLORATÓRIA INICIAL
# ============================================================
imprimir_resumo_inicial(df)
imprimir_resumo_numerico(df)

mostrar_top_categorias(df, [
    "Trimestre",
    "Distrito",
    "Concelho",
    "Freguesia",
    "Tipo de Tecnologia",
    "Nível de Tensão",
    "Escalão de potência instalada (kW)"
])


# ============================================================
# INDICADORES ÚTEIS
# ============================================================
print("\n" + "=" * 80)
print("INDICADORES GERAIS")
print("=" * 80)

if "Número de instalacões" in df.columns:
    print(f"Total de instalações: {df['Número de instalacões'].sum():,.0f}")

if "Potência Total Instalada UPAC (kW)" in df.columns:
    print(f"Potência total instalada (kW): {df['Potência Total Instalada UPAC (kW)'].sum():,.2f}")

if "CPE's" in df.columns:
    print(f"Total de CPE's: {df['CPE\'s'].sum():,.0f}")
# workaround para nome da coluna com apóstrofo
col_cpes = None
for c in df.columns:
    if c.lower() == "cpe's":
        col_cpes = c
        break

if col_cpes:
    print(f"Total de CPE's: {df[col_cpes].sum():,.0f}")



# ============================================================
# GRÁFICOS
# ============================================================
# 1) Distribuições simples
grafico_barras_contagem(df, "Tipo de Tecnologia", titulo="Distribuição por Tipo de Tecnologia")
grafico_barras_contagem(df, "Nível de Tensão", titulo="Distribuição por Nível de Tensão")
grafico_barras_contagem(df, "Distrito", top_n=20, titulo="Número de registos por Distrito")
grafico_barras_contagem(df, "Concelho", top_n=20, titulo="Top concelhos por número de registos")

# 2) Potência instalada por geografia
grafico_barras_soma(
    df,
    grupo="Distrito",
    valor="Potência Total Instalada UPAC (kW)",
    top_n=20,
    titulo="Potência total instalada por Distrito"
)

grafico_barras_soma(
    df,
    grupo="Concelho",
    valor="Potência Total Instalada UPAC (kW)",
    top_n=20,
    titulo="Top concelhos por potência total instalada"
)

grafico_barras_soma(
    df,
    grupo="Freguesia",
    valor="Potência Total Instalada UPAC (kW)",
    top_n=20,
    titulo="Top freguesias por potência total instalada"
)

# 3) Instalações por geografia
grafico_barras_soma(
    df,
    grupo="Distrito",
    valor="Número de instalacões",
    top_n=20,
    titulo="Número total de instalações por Distrito"
)

grafico_barras_soma(
    df,
    grupo="Concelho",
    valor="Número de instalacões",
    top_n=20,
    titulo="Top concelhos por número de instalações"
)

# 4) Histograma da potência total
histograma(
    df,
    "Potência Total Instalada UPAC (kW)",
    bins=40,
    titulo="Distribuição da Potência Total Instalada UPAC (kW)"
)

# 5) Histograma do número de instalações
histograma(
    df,
    "Número de instalacões",
    bins=30,
    titulo="Distribuição do Número de Instalações"
)

# 6) Boxplot de potência por tipo de tecnologia
boxplot_por_categoria(
    df,
    categoria="Tipo de Tecnologia",
    valor="Potência Total Instalada UPAC (kW)",
    top_n=10,
    titulo="Potência instalada por Tipo de Tecnologia"
)

# 7) Boxplot de potência por nível de tensão
boxplot_por_categoria(
    df,
    categoria="Nível de Tensão",
    valor="Potência Total Instalada UPAC (kW)",
    top_n=10,
    titulo="Potência instalada por Nível de Tensão"
)

# 8) Relação entre CPE's e instalações
if col_cpes:
    scatter_relacao(
        df,
        x=col_cpes,
        y="Número de instalações",
        tamanho="Potência Total Instalada UPAC (kW)",
        titulo="Relação entre CPE's, número de instalações e potência"
    )

# 9) Relação entre número de instalações e potência total
scatter_relacao(
    df,
    x="Número de instalações",
    y="Potência Total Instalada UPAC (kW)",
    tamanho=col_cpes if col_cpes else None,
    titulo="Potência total vs número de instalações"
)

# 10) Evolução temporal, se existir mais de um trimestre
grafico_evolucao_trimestre(
    df,
    valor="Número de instalações",
    titulo="Evolução trimestral do número de instalações"
)

grafico_evolucao_trimestre(
    df,
    valor="Potência Total Instalada UPAC (kW)",
    titulo="Evolução trimestral da potência instalada"
)

# 11) Escalões de potência (se a coluna existir)
grafico_barras_contagem(
    df,
    "Escalão de potência instalada (kW)",
    top_n=20,
    titulo="Distribuição por escalão de potência instalada"
)

# 12) Correlações
heatmap_correlacao(df, titulo="Correlação entre variáveis numéricas")

# ============================================================
# ANÁLISES ADICIONAIS ÚTEIS
# ============================================================
summary = df[[
    "Potência Total Instalada UPAC (kW)",
    "Número de instalacões",
    "CPE's"
]].describe()

fig, ax = plt.subplots()

ax.axis("off")

table = ax.table(
    cellText=summary.values,
    colLabels=summary.columns,
    rowLabels=summary.index,
    loc="center"
)

table.scale(1.2, 1.2)

plt.savefig("summary_table_analise.png", bbox_inches="tight", dpi=300)

def detectar_outliers_iqr(df, coluna):
    serie = df[coluna]

    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return df[(df[coluna] < lower) | (df[coluna] > upper)]


for column in df.select_dtypes(include=["number"]).columns:
    outliers = detectar_outliers_iqr(df, column)

    if outliers is not None and not outliers.empty:
        print("\n" + "="*60)
        print(f"Outliers da coluna: {column}")
        print(outliers[[column]].sort_values(column, ascending=False).head(5))


print("\n" + "=" * 80)
print("TOP 10 REGISTOS POR POTÊNCIA TOTAL INSTALADA")
print("=" * 80)
if "Potência Total Instalada UPAC (kW)" in df.columns:
    cols_interesse = [c for c in [
        "Trimestre", "Distrito", "Concelho", "Freguesia",
        "Tipo de Tecnologia", "Nível de Tensão",
        "Número de instalacões", "Potência Total Instalada UPAC (kW)"
    ] if c in df.columns]
    print(df[cols_interesse].sort_values("Potência Total Instalada UPAC (kW)", ascending=False).head(10))

print("\n" + "=" * 80)
print("TOP 10 REGISTOS POR NÚMERO DE INSTALAÇÕES")
print("=" * 80)
if "Número de instalações" in df.columns:
    cols_interesse = [c for c in [
        "Trimestre", "Distrito", "Concelho", "Freguesia",
        "Tipo de Tecnologia", "Nível de Tensão",
        "Número de instalações", "Potência Total Instalada UPAC (kW)"
    ] if c in df.columns]
    print(df[cols_interesse].sort_values("Número de instalações", ascending=False).head(10))

print("\nAnálise exploratória concluída.")

df_tech = df.groupby("Tipo de Tecnologia")[["Potência Total Instalada UPAC (kW)", "Número de instalacões"]].sum().reset_index()
plt.figure(figsize=(10, 8))
bars = plt.bar(df_tech["Tipo de Tecnologia"], df_tech["Potência Total Instalada UPAC (kW)"], color="green")
plt.grid(False)
plt.title("Potência total instalada por tipo de tecnologia")
plt.xlabel("Tecnologia")
plt.xticks(df_tech["Tipo de Tecnologia"], rotation=45)
plt.ylabel("Potência total instalada")
total_power = df_tech["Potência Total Instalada UPAC (kW)"].sum()
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f'{height/total_power*100:.1f}%',
        ha='center',
        va='bottom'
    )

plt.savefig("renewable_type.png")

plt.figure(figsize=(10, 8))
bars = plt.bar(df_tech["Tipo de Tecnologia"], df_tech["Número de instalacões"], color="green")
plt.grid(False)
plt.title("Número de instalações por tipo de tecnologia")
plt.xlabel("Tecnologia")
plt.xticks(df_tech["Tipo de Tecnologia"], rotation=45)
plt.ylabel("Número de instalacões")
total_units = df_tech["Número de instalacões"].sum()
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f'{height/total_units*100:.1f}%',
        ha='center',
        va='bottom'
    )

plt.savefig("renewable_count.png")

print("Número de instalações ND", str(sum(df["Nível de Tensão"] == "ND")))
print("Número de instalações ND", str(sum(df["Nível de Tensão"] == ">1000")))
print("Fotovoltaico em vez de Solar",df[df["Tipo de Tecnologia"] == "Fotovoltaica"]["Número de instalacões"].sum())
df.loc[df["Tipo de Tecnologia"] == "Fotovoltaica", "Tipo de Tecnologia"] = "Solar"
df = df[df["Tipo de Tecnologia"] == "Solar"]
df = df[df["Nível de Tensão"] != "ND"]
df = df[df["Nível de Tensão"] != ">1000"]
print("Omissos após remoção de tensões:\n", df.isna().sum())
df = df.dropna(subset=["Nível de Tensão"])
df_trimestre = df.groupby("Trimestre", dropna=False)[
    ["Número de instalacões", "Potência Total Instalada UPAC (kW)"]].sum().reset_index()

plt.figure(figsize=(10, 6))
plt.bar(df_trimestre["Trimestre"], df_trimestre["Número de instalacões"], color="green")
plt.grid(False)
plt.title("Total de instalações por trimestre")
plt.xlabel("Trimestre")
plt.ylabel("Número de instalacões")
plt.xticks(df_trimestre["Trimestre"], rotation=45, ha="right")
plt.tight_layout()
plt.savefig("instalacoes_por_trimestre.png", dpi=150)
plt.close()

plt.figure(figsize=(10, 6))
plt.bar(df_trimestre["Trimestre"], df_trimestre["Potência Total Instalada UPAC (kW)"], color="green")
plt.grid(False)
plt.title("Potência total instalada por trimestre(kW)")
plt.xlabel("Trimestre")
plt.ylabel("Potência total instalada(kW)")
plt.xticks(df_trimestre["Trimestre"], rotation=45, ha="right")
plt.tight_layout()
plt.savefig("kw_por_trimestre.png", dpi=150)
plt.close()

print("Escalao cat", pd.unique(df["Escalão de potência instalada (kW)"]))
order = ["]0, 4]", "]4, 20.7]", "]20.7, 30]", "]30, 1000]"] # , ">1000", "ND"]
df["Escalão de potência instalada (kW)"] = pd.Categorical(
    df["Escalão de potência instalada (kW)"],
    categories=order,
    ordered=True
)

df_pivot_nr = df.pivot_table(
    index="Trimestre",
    columns="Escalão de potência instalada (kW)",
    values="Número de instalacões",
    aggfunc="sum",
    fill_value=0
)
colors = ["Brown", "Orange", "DarkBlue", "Green", "Red", "Yellow"]
ax = df_pivot_nr.plot(kind="bar", figsize=(20, 16), color=colors, width=0.8, fontsize=18)
ax.set_title("Número de UPACs por trimestre/escalão de potência", fontsize=22)
ax.set_xlabel("Trimestre", fontsize=18)
ax.set_ylabel("Número de UPACs", fontsize=18)
ax.legend(title="Escalão", fontsize=16, title_fontsize=18)
ax.tick_params(axis="both", labelsize=14)
plt.tight_layout()
plt.savefig("instalacoes_trimestre_escalao.png")
plt.close()

df_pivot_kW = df.pivot_table(
    index="Trimestre",
    columns="Escalão de potência instalada (kW)",
    values="Potência Total Instalada UPAC (kW)",
    aggfunc="sum",
    fill_value=0
)

ax = df_pivot_kW.plot(kind="bar", figsize=(20, 16), color=colors, width=0.8)
ax.set_title("Potência de UPACs (kW) por trimestre/escalão de potência", fontsize=22)
ax.set_xlabel("Trimestre", fontsize=18)
ax.set_ylabel("Potência instalada(kW)", fontsize=18)
ax.legend(title="Escalão", fontsize=16, title_fontsize=18)
ax.tick_params(axis="both", labelsize=14)
plt.tight_layout()
plt.savefig("energia_trimestre_escalao.png")
plt.close()

trimestres = sorted(list(df["Trimestre"].unique()))
diff_list = []
for i in range(len(trimestres)):
    if i != 0:
        trim_atual = df_trimestre[df_trimestre["Trimestre"] == trimestres[i]]["Número de instalacões"].values[0]
        trim_anterior = df_trimestre[df_trimestre["Trimestre"] == trimestres[i - 1]]["Número de instalacões"].values[0]
        diff_list.append(trim_atual - trim_anterior)

print(diff_list)

print(df_trimestre.head())

with open("pt.json") as f:
    portugal_geo = json.load(f)

print("Top-level keys:", portugal_geo.keys())
if "features" not in portugal_geo:
    print("Warning: 'features' key missing!")
portugal_geo["features"] = portugal_geo["features"][:18]

features = portugal_geo["features"]
print("Number of features (regions):", len(features))

df_distrito = df.groupby(["Distrito", "Trimestre"])[
    ["Número de instalacões", "Potência Total Instalada UPAC (kW)"]].sum().reset_index()

district_names = [feature["properties"]["name"] for feature in portugal_geo["features"]]
print(district_names)
for distrito in pd.unique(df["Distrito"]):
    print(distrito)


def make_choropleth(data, variable, title, range_col, figname):
    fig = px.choropleth(
        data,
        geojson=portugal_geo,
        locations="Distrito",
        featureidkey="properties.name",
        color=variable,
        color_continuous_scale="YlGn",
        title=title,
        hover_name="Distrito",
        width=1200,
        height=1000,
        range_color=range_col
    )
    fig.update_layout(width=2000, height=1000, font=dict(size=30))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.write_image(figname, scale=1)
    return


make_choropleth(df_distrito[df_distrito["Trimestre"] == "2022T4"], "Número de instalacões",
                "Número de instalações existentes no último trimestre de 2022",[0, 40000] ,"mapa_2022_install.png")
make_choropleth(df_distrito[df_distrito["Trimestre"] == "2025T4"], "Número de instalacões",
                "Número de instalações existentes no último trimestre de 2025", [0,40000], "mapa_2025_install.png")
make_choropleth(df_distrito[df_distrito["Trimestre"] == "2022T4"], "Potência Total Instalada UPAC (kW)",
                "Potência total instalada (UPACs) no último semestre de 2022", [0, 350000], "mapa_2022_potency.png")
make_choropleth(df_distrito[df_distrito["Trimestre"] == "2025T4"], "Potência Total Instalada UPAC (kW)",
                "Potência total instalada (UPACs) no último semestre de 2025", [0, 350000], "mapa_2025_potency.png")


# print(df[df["Trimestre"] == "2025T4"]["Número de instalacões"].sum())
# print(df[df["Trimestre"] == "2025T4"]["Potência Total Instalada UPAC (kW)"].sum())

print(df_distrito[df_distrito["Trimestre"] == "2025T4"])
# df_distrito_gr = df_distrito.groupby("Distrito")["Número de instalacões"].sum().reset_index()
# print(df_distrito_gr)

