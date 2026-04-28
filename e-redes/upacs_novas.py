import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("26-centrais.csv", delimiter=";")

print(0, df.isna().sum())
print("Duplicados: ", df.duplicated().sum())
df = df.dropna()

df["Ratio"] = df["Connection Power"] / df["Completed Processes"]

df2 = df.groupby("Year")[["Completed Processes"]].sum().reset_index()
df_meses = df.groupby("Month").sum().reset_index()

plt.figure()
plt.plot(df_meses["Month"], df_meses["Completed Processes"], marker="o", color="#2E6F40")
plt.xlabel("Mês")
plt.ylabel("Processos completados")
plt.subplots_adjust(left=0.18)
plt.savefig("Monthly_completed.png")
plt.close()

print(df2)

df["Semester"] = df["Month"].apply(lambda x: 1 if x <= 6 else 2)
df_semester = df.groupby(["Year", "Semester"])[["Completed Processes", "Connection Power", "Ratio"]].sum().reset_index()
df_semester["YearSemester"] = df_semester["Year"].astype(str) + "S" + df_semester["Semester"].astype(str)

print(df["Month"].values)

summary = df[[
    "Connection Power", "Completed Processes"
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
plt.subplots_adjust(left=0.18)
plt.savefig("summary_table_upacs_novas.png", bbox_inches="tight", dpi=300)
plt.close()

plt.figure()
plt.bar(df_semester["YearSemester"], df_semester["Completed Processes"], color="#2E6F40")
plt.xlabel("Ano/Semestre")
plt.ylabel("Nr de processos novos completados")
plt.title("Processos Novos Completados por Ano e Semestre")
plt.xticks(rotation=30)
plt.subplots_adjust(left=0.18)
plt.savefig("Instalacoes_Completadas_por_Semestre.png")
plt.close()

plt.figure()
plt.bar(df_semester["YearSemester"], df_semester["Connection Power"], color="#2E6F40")
plt.xlabel("Ano/Semestre")
plt.ylabel("Potência de Conexão Nova")
plt.title("Potência Nova por Ano e Semestre")
plt.xticks(rotation=30)
plt.subplots_adjust(left=0.18)
plt.savefig("Potência_Nova_por_semestre.png")
plt.close()

plt.figure()
plt.bar(df_semester["YearSemester"], df_semester["Ratio"], color="#2E6F40")
plt.xlabel("Ano/Semestre")
plt.ylabel("Potência por instalação nova")
plt.title("Rácio de potência por instalação nova por Ano/Semestre")
plt.xticks(rotation=30)
plt.subplots_adjust(left=0.18)
plt.savefig("Racio_semestre.png")
plt.close()

print(df.shape[0])
