import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import plotly.express as px

sheets = ["RGlobal_diarios"] #, "Tminima_diarios", "Tmaxima_diarios", "Precipitacao_diarios"]
df1 = pd.read_excel('CapitaisDistrito_Valores_dia_Tn_Tx_Prec_RG.xlsx', sheet_name=sheets)
distritos = ['Évora', 'Portalegre', 'Viana do Castelo', 'Castelo Branco', 'Guarda', 'Bragança', 'Vila Real', 'Braga', 'Faro', 'Beja', 'Setúbal', 'Lisboa', 'Santarém', 'Leiria', 'Coimbra', 'Aveiro', 'Porto', 'Viseu']

results_tracker = []


def intro(sheet_name, source, timeframe, stage_name):
    df = source[sheet_name].replace(-990, np.nan)
    distritos = df.columns.difference(["ANO", "MÊS", "DIA"], sort=False)

    units = df.shape[0]
    num_distritos = len(distritos)
    readings_total = units * num_distritos

    missing_count = df[distritos].isnull().sum().sum()
    missing_perc = round((missing_count / readings_total * 100), 3) if readings_total > 0 else 0

    results_tracker.append({
        "Sheet": sheet_name,
        "Stage": stage_name,
        "Total_Units": units,
        "Missing_Count": int(missing_count),
        "Missing_%": missing_perc
    })


def to_monthly(df):
    df_clean = df.replace(-990, np.nan)
    monthly_df = df_clean.groupby(['ANO', 'MÊS']).mean()
    monthly_df = monthly_df.fillna(-990)
    if 'DIA' in monthly_df.columns:
        monthly_df = monthly_df.drop(columns=['DIA'])
    return monthly_df


def save_df_as_png(df, filename, title):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')
    ax.axis('tight')

    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=df.index,
                     loc='center',
                     cellLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)

    plt.title(title, fontsize=14, pad=20)
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()


for sheet in sheets:
    intro(sheet, df1, "Days", "1. Original Daily")

dfs_monthly = {s: to_monthly(df1[s]) for s in sheets}
for sheet in sheets:
    intro(sheet, dfs_monthly, "Months", "2. Full Monthly")

dfs_daily_windowed = {s: df1[s][df1[s]["ANO"] >= 2020] for s in sheets}
for sheet in sheets:
    intro(sheet, dfs_daily_windowed, "Days", "3. Windowed Daily")

dfs_monthly_windowed = {s: to_monthly(dfs_daily_windowed[s]) for s in sheets}
for sheet in sheets:
    intro(sheet, dfs_monthly_windowed, "Months", "4. Windowed Monthly")

summary_df = pd.DataFrame(results_tracker)

count_table = summary_df.pivot(index="Sheet", columns="Stage", values="Missing_Count")
save_df_as_png(count_table, "NA_Count_Comparison.png", "Comparison of Missing Value Counts")

perc_table = summary_df.pivot(index="Sheet", columns="Stage", values="Missing_%")
save_df_as_png(perc_table, "NA_Percentage_Comparison.png", "Comparison of Missing Value Percentages (%)")


import pandas as pd
import numpy as np

sheets = ["Tminima_diarios", "Tmaxima_diarios", "Precipitacao_diarios", "RGlobal_diarios"]

df1 = pd.read_excel('CapitaisDistrito_Valores_dia_Tn_Tx_Prec_RG.xlsx', sheet_name=sheets)
#df_Tmin, df_Tmax, df_Precip, df_Rglo = df1["Tminima_diarios"], df1["Tmaxima_diarios"], df1["Precipitacao_diarios"], df1["RGlobal_diarios"]
"""
def intro(dataframe, source, timeframe):
    print("Sheet: ", dataframe)
    dataframe = source[dataframe].replace(-990, np.nan, regex=True)
    days = dataframe.shape[0]
    readings_total = days*18
    print(f"Total {timeframe}: {days}")
    print("Total readings: ", readings_total)
    missing_count = dataframe.isnull().sum().sum()
    print(f"Total missing values: {missing_count}, {round(missing_count/readings_total*100, 3)}% of the total readings")
    distritos = dataframe.columns.difference(["ANO", "MÊS", "DIA"])
    print("Total missing values per district: ")
    highest_missing = (None, 1)
    for distrito in distritos:
        missing_count = dataframe[distrito].isna().sum().sum()
        missing_ratio = round(missing_count/dataframe.shape[0]*100, 3)
    if missing_count > highest_missing[1]:
        highest_missing = (distrito, missing_count, missing_ratio)
        print(f"{distrito}: {missing_count}, {missing_ratio}% of the total readings for this district \n")
        print(f"Highest number of missing entries: {highest_missing[1]}/{highest_missing[2]}%({highest_missing[0]})\n\n")
"""


def intro(dataframe, source, timeframe):
    print("Sheet: ", dataframe)

    dataframe = source[dataframe].replace(-990, np.nan, regex=True)

    days = dataframe.shape[0]

    readings_total = days * 18

    print(f"Total {timeframe}: {days}")

    print("Total readings: ", readings_total)

    missing_count = dataframe.isnull().sum().sum()

    print(
        f"Total missing values: {missing_count}, {round(missing_count / readings_total * 100, 3)}% of the total readings")

    distritos = dataframe.columns.difference(["ANO", "MÊS", "DIA"])

    print("Total missing values per district: ")

    highest_missing = (None, 1)

    for distrito in distritos:

        missing_count = dataframe[distrito].isna().sum().sum()

        missing_ratio = round(missing_count / dataframe.shape[0] * 100, 3)

        if missing_count > highest_missing[1]:
            highest_missing = (distrito, missing_count, missing_ratio)

        print(f"{distrito}: {missing_count}, {missing_ratio}% of the total readings for this district \n")

    print(f"Highest number of missing entries: {highest_missing[1]}/{highest_missing[2]}%({highest_missing[0]})\n\n")
for sheet in sheets:
    intro(sheet, df1, "Days")


def to_monthly(df):
    df_clean = df.replace(-990, np.nan)
    monthly_df = df_clean.groupby(['ANO', 'MÊS']).mean()
    monthly_df = monthly_df.fillna(-990)
    if 'DIA' in monthly_df.columns:
        monthly_df = monthly_df.drop(columns=['DIA'])
    return monthly_df

dfs_monthly = {}
for sheet in sheets:
    dfs_monthly[sheet] = to_monthly(df1[sheet])
    intro(sheet, dfs_monthly, "Months")


dfs_daily_windowed = {}
def window(dataframe, source, destination):
    dataframe_t = source[dataframe]
    destination[dataframe]= dataframe_t[dataframe_t["ANO"] >= 2020]

for sheet in sheets:
    window(sheet, df1, dfs_daily_windowed)
    intro(sheet, dfs_daily_windowed, "Days")

dfs_monthly_windowed = {}
for sheet in sheets:
    dfs_monthly_windowed[sheet] = to_monthly(dfs_daily_windowed[sheet])
    intro(sheet, dfs_monthly_windowed, "Months")


df_plotting = df1["RGlobal_diarios"]
df_plotting = df_plotting.replace(-990, np.nan, regex=True)


with open("pt.json") as f:
    portugal_geo = json.load(f)

mainland_districts = [
    'Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco', 'Coimbra',
    'Évora', 'Faro', 'Guarda', 'Leiria', 'Lisboa', 'Portalegre', 'Porto',
    'Santarém', 'Setúbal', 'Viana do Castelo', 'Vila Real', 'Viseu'
]

portugal_mainland_geo = {
    "type": "FeatureCollection",
    "features": [
        f for f in portugal_geo['features']
        if f['properties']['name'] in mainland_districts
    ]
}

df_plotting_avg = avg_df = df_plotting.mean().to_frame().T
df_plotting_avg = df_plotting.mean()[df_plotting.columns.intersection(distritos)].to_frame().T
df_melted = df_plotting_avg.melt(var_name='Distrito', value_name='avg_radiation')
mainland_features = [f for f in portugal_geo['features'] if f['properties']['name'] not in ['Azores', 'Madeira']]
mainland_geo = {
    "type": "FeatureCollection",
    "features": [
        f for f in portugal_geo['features']
        if f['properties']['name'] not in ['Açores', 'Madeira', 'Região Autónoma dos Açores', 'Região Autónoma da Madeira']
    ]
}

fig = px.choropleth(
    df_melted,
    geojson=mainland_geo,
    locations='Distrito',
    featureidkey="properties.name",
    color='avg_radiation',
    color_continuous_scale="YlOrRd",
    range_color=[df_melted['avg_radiation'].min(), df_melted['avg_radiation'].max()]
)

fig.update_geos(
    projection_type="transverse mercator",
    fitbounds=False,
    visible=False,
    lataxis_range=[35.8, 43.2],
    lonaxis_range=[-10.7, -5.0]
)

fig.update_layout(
    width=500,
    height=500,
    margin={"r":0, "t":50, "l":0, "b":0},
    title=dict(
        text="Average Daily Radiation (kJ/km²) by District",
        x=0.5,
        y=0.88
    ),
    coloraxis_colorbar=dict(
        x=0.85,
        thickness=15,
        len=0.7
    )
)

fig.write_image("mainland_fixed.png", scale=3)

fig.write_image("mainland_fixed.png", scale=3)


df_plotting = df_plotting.fillna(df_plotting.median())
print(df_plotting.isna().sum())






print(df_melted.columns)

df_upacs = pd.read_csv("upacs_totais_limpo.csv")
print(df_upacs["Número de instalacões"].dtype)

df_upacs_2025 = df_upacs[df_upacs["Trimestre"] == "2025T4"]
df_distritos_2025 = df_upacs_2025.groupby("Distrito").sum(numeric_only=True).reset_index()
df_distritos_2025["Installation/Potency(kW)"] = df_distritos_2025["Potência Total Instalada UPAC (kW)"]/df_distritos_2025["Número de instalacões"]
print(df_distritos_2025["Installation/Potency(kW)"].head(20))
df_upac_merge = df_distritos_2025[["Distrito", "Potência Total Instalada UPAC (kW)"]]
df_combined = pd.merge(
    df_melted,
    df_upac_merge,
    on="Distrito",
    how="inner"
)

print(df_combined.head())

#GERAÇÃO DE VALORES DE RADIAÇÃO MEDANA ANUAL

df_rad = df1["RGlobal_diarios"].copy()
df_rad = df_rad.replace(-990, np.nan)


distritos

for col in distritos:
    median_val = df_rad[col].median()
    df_rad[col] = df_rad[col].fillna(median_val)

total_sum = df_rad[distritos].sum()

#Média anual(15 anos), conversão kJ para kWh
yearly_avg_radiation = total_sum / 15 / 3600

df_final_export = yearly_avg_radiation.reset_index()
df_final_export.columns = ['Distrito', 'Radiation']

df_final_export.to_csv("distrito_radiation_imputed.csv", index=False)

print("Imputation and calculation complete. Preview:")
print(df_final_export.head())