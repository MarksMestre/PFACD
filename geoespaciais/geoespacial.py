import rasterio
from rasterio.warp import reproject, Resampling
from rasterio import features
from rasterio.plot import plotting_extent, show
from rasterio.mask import mask
import json
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import cv2
import os
import math
from tqdm import tqdm
import matplotlib.pyplot as plt


def vector_map(geojson_directory):
    districts_gdf = gpd.read_file(geojson_directory, layer='cont_distritos')

    #CRS mais comum
    if districts_gdf.crs != "EPSG:4326":
        districts_gdf = districts_gdf.to_crs("EPSG:4326")

    districts_gdf = districts_gdf.rename(columns={'distrito': 'name'})

    #Tirar os arquipélagos
    districts_gdf = districts_gdf[~districts_gdf['name'].isin(['Azores', 'Madeira'])]

    #Dissolução
    districts_gdf = districts_gdf.dissolve(by='name', as_index=False)


    district_names_series = districts_gdf['name']

    return districts_gdf, district_names_series

def manipulate_raster_solar(solar_directory, districts_gdf):
    with rasterio.open(solar_directory) as src: #Ficheiro com dados de radiação solar médios(kWh)
        solar_meta = src.meta
        print(solar_meta)

        out_image, out_transform = mask(src, districts_gdf.geometry, crop=True)

        solar_array = out_image[0]
        solar_transform = out_transform
        solar_shape = solar_array.shape
        print("Função Manipulate_raster_solar completada completada")
        return solar_shape, solar_transform, solar_array

def manipulate_raster_OPTA(opta_directory, solar_shape, solar_transform):
    with rasterio.open(opta_directory) as src:
        opta_array = np.empty(solar_shape, dtype='float32')
        
        reproject(
            source=rasterio.band(src, 1),
            destination=opta_array,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=solar_transform,
            dst_crs=src.crs,
            resampling=Resampling.bilinear
        )

        #Subsituição de -9999 por 0
        opta_array = np.where(opta_array == src.nodata, 0.0, opta_array)
        opta_array = np.where(opta_array < -100, 0.0, opta_array)

        #Mapa da área real que 1m2 de painel útil ocupa
        module_footprint_array = 1.65 / np.round(1.65 * np.cos(np.radians(opta_array)), 2)
        module_footprint_array = 1.65 / np.round(1.65 * np.cos(np.radians(opta_array)), 2)
        module_footprint_array = np.where(opta_array == 0.0, 0.0, module_footprint_array)

        return opta_array,module_footprint_array

def manipulate_geojson_buildings(buildings_directory, solar_shape, solar_transform, districts_gdf):

    if not os.path.exists("portugal_mainland_buildings.parquet"):
        #isto gerava a versão com clip dos telhados
        buildings_gdf = gpd.read_parquet("pt_buildings_complete.parquet")
        buildings_gdf.sindex
        print(f"Buildings CRS: {buildings_gdf.crs}")

        #O mapa da CAOP é muito complexo para fazer este clip, necessita simplificação
        print("Creating bounding box and simplifying districts geometry to speed up clip...")
        bbox = districts_gdf.total_bounds
        buildings_gdf = buildings_gdf.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]
        simplified_districts = districts_gdf.copy()
        simplified_districts['geometry'] = districts_gdf.geometry.simplify(0.001, preserve_topology=True)

        if buildings_gdf.crs != "EPSG:4326":
            print(f"Reprojecting buildings to {"EPSG:4326"}...")
            buildings_gdf = buildings_gdf.to_crs("EPSG:4326")


        def chunked_clip(buildings, districts):
            clipped_chunks = []

            #Separar o processo do clip em chunks
            for _, district in tqdm(districts.iterrows(), total=len(districts), desc="Clipping districts"):
                district_buildings = buildings.clip(district.geometry)
                clipped_chunks.append(district_buildings)
            "Finished chunked clipping"
            return gpd.GeoDataFrame(pd.concat(clipped_chunks, ignore_index=True), crs=buildings.crs)

        print("Starting chunked clipping process...")
        buildings_gdf = chunked_clip(buildings_gdf, simplified_districts)

        print(f"Saving clipped data to {buildings_directory}...")
        buildings_gdf.to_parquet(buildings_directory)

    buildings_gdf = gpd.read_parquet(buildings_directory)


    #vista de olhos
    print(buildings_gdf.describe())
    print(buildings_gdf.isnull().sum())
    for col in ['roof_shape', 'roof_material']:
        if col in buildings_gdf.columns:
            print(f"\n--- {col} ---")
            print(buildings_gdf[col].value_counts(normalize=True).head(10))


    viable_25 = [None, 'apartments', 'roof', "house", "hotel", "residential", "silo", "detached", "carport", "greenhouse", "hut", "farm", "semidetached_house", "cabin", "bungalow", "allotment_house",
                 "dormitory", "static_caravan"]
    viable_40 = ["public", "industrial", "transportation", "retail", "commercial", "school", "warehouse", "shed", "hospital", "service",
                 "storage_tank", "train_station", "garage", "bridge", "stable", "grandstand", "farm_auxiliary", "pavilion", "office", "library", "kiosk", "cowshed", "barn",
                 "garages", "kindergarten", "post_office", "government", "toilets", "parking", "sports_centre", "sports_hall", "stadium", "fire_station", "college", "university",
                 "hangar", "supermarket", "civic", "bunker", "guardhouse", "outbuilding", "sty", "wayside_shrine", "manufacture", "military", "factory", "boathouse"]
    not_viable = ["church", "terrace", "chapel", "transformer_tower", "religious", "monastery", "ger", "synagogue", "temple", "cathedral", "mosque", "wayside_shrine", "digester", "shrine", "houseboat", "presbytery", "bridge_structure"]

    buildings_gdf.crs = "EPSG:4326"
    print(f"Total estimated buildings in Portugal: {len(buildings_gdf)}")

    #ver as porções da área
    areas_in_sqm = buildings_gdf.to_crs(epsg=3763).geometry.area

    buildings_gdf['category'] = 'not_viable'
    buildings_gdf.loc[buildings_gdf['class'].isin(viable_25), 'category'] = 'residential'
    buildings_gdf.loc[buildings_gdf['class'].isin(viable_40), 'category'] = 'commercial'

    area_stats = areas_in_sqm.groupby(buildings_gdf['category']).sum()

    print("Area by category (in m2):")
    print(area_stats)

    if not os.path.exists("portugal_building_mask.tif"):
        "portugal building mask not found, calculating: \n"
        if buildings_gdf.crs != "EPSG:4326":
            buildings_gdf = buildings_gdf.to_crs("EPSG:4326")
        #Esta linha simplesmente multiplica os píxeis por 10
        fine_shape = (solar_shape[0] * 100, solar_shape[1] * 100)
        #esta linha mantém a origem do mapa, mas muda os steps de cada pixel para uma fração. como há 10x píxeis, fica 10/10==1 vezes o tamanho original
        fine_transform = solar_transform * solar_transform.scale(1 / 100, 1 / 100)

        buildings_gdf['usable_fraction'] = buildings_gdf["class"].map(lambda x: 0.4 if x in viable_40 else 0.25 if x in viable_25 else 0.0)

        #isto cria o mapa rasterizado com píxeis mais pequenos
        fine_mask = features.rasterize(
            ((row.geometry, row.usable_fraction) for row in buildings_gdf.itertuples()),
            out_shape=fine_shape,
            transform=fine_transform,
            fill=0.0,
            dtype='float32'
        )

        fractional_mask = cv2.resize(#isto vai agregar a máscara, cada 25x25 píxeis tornam-se 1
            fine_mask.astype('float32'),#conversão de binário para float
            (solar_shape[1], solar_shape[0]),#Mudança para a escala do mapa da radiação
            interpolation=cv2.INTER_AREA#isto é a parte que especifica que estamos a fazer a média para cada píxel, em vez de a maioria
        )
        fractional_mask = np.nan_to_num(fractional_mask, nan=0.0)

        with rasterio.open(
                'portugal_building_mask.tif',
                'w',
                driver='GTiff',
                height=solar_shape[0],
                width=solar_shape[1],
                count=1,
                dtype='float32',
                crs='EPSG:4326',
                transform=solar_transform,
        ) as dst:
            dst.write(fractional_mask, 1)



        print("MASKBULT")

    with rasterio.open("portugal_building_mask.tif") as src:
        fractional_mask = src.read(1)

    fractional_mask = np.nan_to_num(fractional_mask, nan=0.0)
    print("Completed building mask")

    non_numeric_cols = buildings_gdf.select_dtypes(exclude=[np.number, 'geometry']).columns
    print("--- Non-Numeric Columns and Unique Values ---")

    #exploração básica
    for col in non_numeric_cols:
        print(f"\nColumn: {col}")
        try:
            unique_vals = buildings_gdf[col].unique()
            print(f"Number of unique values: {len(unique_vals)}")
            print(f"Sample values: {unique_vals[:10]}")
        except TypeError:
            print("Status: Contains unhashable nested data (ndarray/dict/list).")
            sample = buildings_gdf[col].iloc[0]
            print(f"Data type in column: {type(sample)}")


    print(buildings_gdf["is_underground"].value_counts(dropna=False))
    print(buildings_gdf["roof_shape"].value_counts(dropna=False))
    buildings_gdf = buildings_gdf[buildings_gdf["is_underground"] == False]
    buildings_gdf = buildings_gdf[buildings_gdf["roof_material"] != "glass"]
    print(buildings_gdf["roof_shape"].value_counts(dropna=False))




    return buildings_gdf, fractional_mask


def calculate_and_save_potential(solar_array, building_mask, transform):
    ###Transformação para m2 para os cálculos
    height, width = solar_array.shape
    #estes são os tamanohs dos píxeis no sistema de coordenadas WGS84, para fazer cálculos
    deg_lon_step = abs(transform[0])
    deg_lat_step = abs(transform[4])
    pixel_height_meters = deg_lat_step * 111132.0 #Como são expressos em degraus, e cada degrau de latitude é 111132m, para a latitude é só necessário multiplicar, porque é constante
    #Aqui encontramos as latitudes das diferentes linhas do mapa
    row_indices = np.arange(height)
    max_y_height = transform[3]
    row_latitudes = max_y_height - (deg_lat_step * (row_indices + 0.5))
    #row_latitudes tem as latitudes dos píxeis. isto é convertido para radianos. Calculamos o cosseno deste ângulo para saber a sua proporção relativa ao equador. depois multiplicamos pelo tamanho de um degrau no equador. Assim tempos o comprimento lateral de um grau para os píxeis. Por fim multiplicamos pelo número de graus do píxel.
    pixel_widths_meters = np.cos(np.radians(row_latitudes)) * 111412.0 * deg_lon_step
    pixel_area_matrix = pixel_widths_meters[:, np.newaxis] * pixel_height_meters #Conversão de 1D para 2D

    ###CONSTANTES
    ##Aqui registam-se as constantes necessárias para modificar os cálculos de energia potencial
    #Aqui assume-se uma eficiência igual àquela utilizada pelo DBSM R
    efficiency_percentage = 0.22
    ##Para além disso, PVOUT assume a instalação de painéis solares de nível industrial, montados ao ângulo ótimo e virados para sul. Realisticamente, os telhados residênciais requererão uma inclinação mais realista de 20%, resultando numa perda por volta de 3%
    tilt_mismatch_factor = 0.97
    ##Agora, fazem-se os raios de acordo com a tabela deles em https://globalsolaratlas.info/support/methodology
    inv_euro_eff = 95.9 / 97.8
    soiling_loss = (100-4.5) / (100-3.5)
    cable_dc_loss = (100-1) / (100-2)
    mismatch_loss = (100-0.8)/(100-0.3)
    transformer_loss = (100) / (100-0.9)
    cable_ac_loss = (100-0.2) / (100-0.5)
    availability = 0.97 / 0.995

    #isto toma em conta a inclinação e o efeito que isso tem na área instalada.
    footprint_factor = 1.65 / round(1.65*math.cos(math.radians(20)),2)
    #combinando isto tudo, dá cerca de 96%
    industrial_to_residential = inv_euro_eff * soiling_loss * cable_dc_loss * mismatch_loss * transformer_loss * cable_ac_loss * availability
    print(industrial_to_residential)

    print("Calculating potential energy...")

    potential_energy = solar_array * building_mask * pixel_area_matrix * efficiency_percentage * footprint_factor * tilt_mismatch_factor * industrial_to_residential #22% eficácia implica 0.22 kWp/m²



    potential_energy = np.nan_to_num(potential_energy, nan=0.0)
    potential_energy = np.where(potential_energy < 1e-5, 0, potential_energy)

    return potential_energy


def pvout_map(solar_array, solar_transform, districts_gdf):
    fig, ax = plt.subplots(figsize=(7, 13))
    plot_data = np.where(solar_array < 10, np.nan, solar_array)
    max_val = np.nanmax(plot_data)
    print(max_val, "Máximo")
    extent = plotting_extent(plot_data, transform=solar_transform)
    im = ax.imshow(plot_data, extent=extent, cmap='YlOrRd', vmin=1200, vmax=1800)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, extend='both')
    cbar.set_label('Produtividade anual específica (kWh/kWp)', fontsize=14, rotation=270, labelpad=20)
    districts_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=0.7)
    ax.set_title("Produtividade específica anual (kWh/kWp)")

    plt.savefig("mapa_rad.png", bbox_inches='tight')
    plt.close()
    return


def make_plot_raster_under_vectors(fractional_mask, solar_transform, buildings_gdf, x_zoom, y_zoom, local):
    fig, ax = plt.subplots(figsize=(12, 12))
    ext = rasterio.plot.plotting_extent(fractional_mask, solar_transform)

    im = ax.imshow(
        fractional_mask,
        extent=ext,
        cmap='viridis',
        alpha=1.0,
        origin='upper',
        vmin=0,
        vmax=1
    )

    buildings_gdf.geometry.boundary.plot(
        ax=ax,
        color='red',
        linewidth=0.5,
        alpha=0.8
    )

    ax.set_xlim(x_zoom)
    ax.set_ylim(y_zoom)

    plt.colorbar(im, ax=ax, label='Densidade de prédios (Fração)', pad = 0.1)
    ax.set_title(f"Vetores de prédios sobrepostos num mapa de {local}")
    plt.savefig(f"building_density_overlay_{local}.png")


def plot_fractional_raster(mask_array, transform, solar_array, title, name, districts_gdf):
    data = np.nan_to_num(mask_array, nan=0.0)
    data[data < 1e-5] = 0.0

    ocean_mask = (solar_array <= 1e-30)

    display_data = np.ma.masked_where(ocean_mask, data)
    fig, ax = plt.subplots(figsize=(10, 15), facecolor='white')
    im = ax.imshow(display_data,
                   extent=rasterio.plot.plotting_extent(data, transform),
                   cmap='Blues',
                   origin='upper',
                   vmin=0,
                   vmax=np.nanmax(data))

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Potential Energy (kWh)')
    districts_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=1)


    ax.set_title(title)
    ax.set_axis_off()

    plt.savefig(name)


def sum_potential_by_district(potential_array, transform, districts_gdf):
    #raster temporário
    from rasterio.io import MemoryFile

    results = []

    #metadadis di memfuke
    #*metadados do memfile
    height, width = potential_array.shape
    new_dataset_meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': str(potential_array.dtype),
        'crs': 'EPSG:4326',
        'transform': transform,
        'nodata': 0
    }

    with MemoryFile() as memfile:
        with memfile.open(**new_dataset_meta) as dataset:
            dataset.write(potential_array, 1)

            for _, row in districts_gdf.iterrows():
                district_name = row['name']
                geom = [row['geometry']]

                try:
                    out_image, _ = mask(dataset, geom, crop=True, nodata=0)

                    total_potential = out_image.sum()
                    results.append({'district': district_name, 'total_kWh': total_potential})

                except ValueError:
                    results.append({'district': district_name, 'total_kWh': 0})

    summary_df = pd.DataFrame(results).sort_values(by='total_kWh', ascending=False)


    return summary_df

#Esta função é para estimar energia aproveitada por kW em cada distrito, em média. varia bastante mas deve ser melhor do que as estações do ipma pois é mais abrangente
def average_radiation_by_district(solar_array, transform, districts_gdf):
    from rasterio.io import MemoryFile

    results = []
    height, width = solar_array.shape

    # isto prepara os metadados do nosso mapa temporário
    meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': str(solar_array.dtype),
        'crs': 'EPSG:4326',
        'transform': transform,
        'nodata': -9999
    }
    #aqui cria-se um ficheiro temporário que vai para a nossa RAM, e depois fazemos os calculos dentro do loop for
    with MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:
            dataset.write(solar_array, 1)

            for _, row in districts_gdf.iterrows():
                district_name = row['name']
                geom = [row['geometry']]

                try:
                    #isto vai fazer um retangulo à volta do distrito, tudo o resto é -9999. Para os pixeis dentro do retangulo, apenas os válidos para o distrito sao contados, o resto é convertido para NA
                    out_image, _ = mask(dataset, geom, crop=True, nodata=-9999)
                    district_pixels = out_image[0].astype(float)
                    district_pixels[district_pixels == -9999] = np.nan

                    #Média do distrito, isto vai ser kWh/kWp médio, ou seja depois podemos pultiplicar o agregado dos painéis por isto para fazer estimativas
                    avg_radiation = np.nanmean(district_pixels)

                    results.append({'Distrito': district_name, 'Radiation': avg_radiation})

                except ValueError:
                    # Se um pixel nao esta no distrito torna-se np.nan par nao afetar os calculos. isto faz-nos perder pixeis mas a grande escala não importará muito, cada distrito tem muitos muitos pixeis
                    results.append({'Distrito': district_name, 'Radiation': np.nan})

    # dataframe resultante
    result = pd.DataFrame(results).sort_values(by='Radiation', ascending=False)
    result.to_csv("estimativas_rad_raster.csv")
    return result

def main():
    plt.rcParams.update({
    'font.size': 20,
    'axes.titlesize': 23,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'figure.titlesize': 60,
    "axes.titlepad": 20
    })

    districts_gdf, district_names_series = vector_map("Continente_CAOP2025.gpkg")
    solar_shape, solar_transform, solar_array = manipulate_raster_solar("PVOUT.tif", districts_gdf)
    OPTA_array, footprint = manipulate_raster_OPTA("OPTA.tif", solar_shape=solar_shape, solar_transform=solar_transform)
    print(f"DEBUG: Min={np.nanmin(solar_array)}, Max={np.nanmax(solar_array)}")
    buildings_gdf, building_mask = manipulate_geojson_buildings("portugal_mainland_buildings.parquet", solar_shape, solar_transform, districts_gdf)
    potential_energy_array = calculate_and_save_potential(solar_array,building_mask, solar_transform)


    #Chamar gráficos
    pvout_map(solar_array, solar_transform, districts_gdf)
    plot_fractional_raster(building_mask, solar_transform, solar_array, "buildings", "buildings.png", districts_gdf)
    plot_fractional_raster(potential_energy_array, solar_transform, solar_array, "Solar Potential: Land Only", "Solar potential.png", districts_gdf)
    make_plot_raster_under_vectors(building_mask, solar_transform, buildings_gdf, [-9.18, -9.10], [38.70, 38.76], "Lisboa")
    make_plot_raster_under_vectors(building_mask, solar_transform, buildings_gdf, [-9.7, -6.0], [36.8, 42.2], "Portugal")



    summary_results = sum_potential_by_district(potential_energy_array, solar_transform, districts_gdf)
    total_national_kwh = summary_results['total_kWh'].sum()

    print(f"Total National Potential: {total_national_kwh:.2e} kWh")
    print(f"Total National Potential: {total_national_kwh / 1e9:.2f} TWh")
    print(f"Total: {total_national_kwh:.0f} kWh")
    print(sum_potential_by_district(potential_energy_array, solar_transform, districts_gdf))


    avg_solar_df = average_radiation_by_district(solar_array, solar_transform, districts_gdf)

    print("--- Average Solar Radiation by District (kWh/m²/year) ---")
    print(avg_solar_df.to_string(index=False))


    #tipos de prédios por contribuição para a área
    percentage_breakdown = buildings_gdf['class'].value_counts(normalize=True, dropna=False) * 100

    print("Percentage of building types:")
    print(percentage_breakdown.head(20))

    direction_breakdown = buildings_gdf['roof_shape'].value_counts(normalize=True, dropna=False) * 100

    print("Percentage distribution of roof_shape:")
    print(direction_breakdown)

    print("end")

    print(np.nanmax(OPTA_array))
    print(np.unique(footprint))

if __name__ == "__main__":
    main()