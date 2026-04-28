import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)
import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_path)

from __configure__.paths import *

df = pd.read_csv("energia_injectada_upac.csv", sep=";")

print(df.isna().sum())
print("Duplicados: ", df.duplicated().sum())

df_missing = df[df["Distrito"].isna() == True]
print(df_missing["Código Freguesia"].unique())
print(df_missing["Código Concelho"].unique())
print(df_missing["Código Distrito"].unique())

print(270/ df.shape[0])

# Dictionary mapping first two digits to Distrito
distrito_map = {
    "02": "Beja", "03": "Braga", "04": "Bragança", "05": "Castelo Branco",
    "06": "Coimbra", "07": "Évora", "08": "Faro", "09": "Lisboa",
    "10": "Leiria", "11": "Lisboa", "12": "Portalegre", "14": "Santarém",
    "15": "Setúbal", "16": "Viana do Castelo", "17": "Vila Real", "18": "Viseu"
}
df["Código Freguesia"] = df["Código Freguesia"].str.replace("----", "", regex=False)
df["Distrito_code"] = df["Código Freguesia"].str[:2]
df["Distrito"] = df["Código Distrito"].map(distrito_map)


df = df.dropna(subset="Distrito")
print("123", df["Código Freguesia"])
print("Omissos após  tentativa de imputação: ", df.isna().sum())


df["kWh/instalação"] = df["Energia Injetada (kWh)"] / df["Número de Instalações"]
df["kWh/instalação"].replace([np.inf, -np.inf], np.nan, inplace=True)

print("----------------------Summary Table----------------------")
print(df[["Potência Instalada (kW)", "Número de Instalações", "Energia Injetada (kWh)", "kWh/instalação"]].describe())
print("---------------------------------------------------------")


summary = df[[
    "Potência Instalada (kW)",
    "Número de Instalações",
    "Energia Injetada (kWh)",
    "kWh/instalação"
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

plt.savefig("summary_table.png", bbox_inches="tight", dpi=300)

print(df.columns)


print(33333)
df_m_eff23 = df[df["Ano"]==2023].groupby("Mês")[["Número de Instalações", "Energia Injetada (kWh)"]].sum().reset_index()
df_m_eff23["Energia/Instalação(Mensal) kWh"] = df_m_eff23["Energia Injetada (kWh)"] / df_m_eff23["Número de Instalações"]
print(df_m_eff23)

df_m_eff24 = df[df["Ano"]==2024].groupby("Mês")[["Número de Instalações", "Energia Injetada (kWh)"]].sum().reset_index()
df_m_eff24["Energia/Instalação(Mensal) kWh"] = df_m_eff24["Energia Injetada (kWh)"] / df_m_eff24["Número de Instalações"]
print(df_m_eff24)

df_a_eff = df.groupby("Ano")[["Número de Instalações", "Energia Injetada (kWh)"]].sum().reset_index()
df_a_eff["Energia/Instalação(Anual) kWh"] = df_a_eff["Energia Injetada (kWh)"] / df_a_eff["Número de Instalações"]
print(df_a_eff)




plt.figure(figsize=(7, 6))

plt.plot(
    df_m_eff24["Mês"],
    df_m_eff24["Energia/Instalação(Mensal) kWh"], label="2024",
    marker="o", color="green"
)
plt.plot(
    df_m_eff23["Mês"],
    df_m_eff23["Energia/Instalação(Mensal) kWh"], label="2023",
    marker="o", color="brown"
)


plt.title("Energia Média Mensal Injetada por Instalação (2023/2024)")
plt.xlabel("Mês")
plt.ylabel("Energia por instalação(kWh)")
plt.xticks(df_m_eff24["Mês"])
plt.legend()

plt.savefig("Energia_injetada_23_24_mensal")

plt.figure()

plt.bar(
    df_a_eff["Ano"],
    df_a_eff["Energia/Instalação(Anual) kWh"], color=["brown", "green"]
)

plt.title("Energia Mensal média injetada por instalação ao longo do ano")
plt.xlabel("Ano")
plt.xticks([2023, 2024])
plt.ylabel("Energia por Instalação")

plt.savefig("Energia injetada média anual")

plt.bar(
    df_a_eff["Ano"],
    df_a_eff["Energia Injetada (kWh)"], color=["brown", "green"]
)

plt.title("Energia Anual Injetada na Rede")
plt.xlabel("Ano")
plt.xticks([2023, 2024])
plt.ylabel("Energia(kWh)")

plt.savefig("Energia injetada anual")


e_total_23 = df_m_eff23["Energia Injetada (kWh)"].sum()
e_total_24 = df_m_eff24["Energia Injetada (kWh)"].sum()
print(e_total_24/e_total_23 * 100 - 100)


df_plot = df.groupby("Nível de Tensão")["Energia Injetada (kWh)"].sum().reset_index()

plt.figure(figsize=(8,5))
plt.bar(df_plot["Nível de Tensão"], df_plot["Energia Injetada (kWh)"], color="green")
plt.title("Energia Injetada (kWh) por Nível de Tensão")
plt.xlabel("Nível de Tensão")
plt.ylabel("Energia Injetada (kWh)")
plt.xticks(rotation=45)
plt.savefig("escalao_injetada.png")


df_sorted = df.sort_values("kWh/instalação", ascending=False)

print(df_sorted.head(10))

