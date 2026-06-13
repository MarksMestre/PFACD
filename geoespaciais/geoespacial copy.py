import rasterio
from rasterio import features
from rasterio.plot import show
from rasterio.mask import mask
import json
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import cv2
import os


def vector_map(geojson_directory):
    districts_gdf = gpd.read_file(geojson_directory)  # Ficheiro com mapa de distritos, já está em formato WGS84
    districts_gdf = districts_gdf[~districts_gdf['name'].isin(['Azores', 'Madeira'])]
    print(districts_gdf.geometry.head())
    portugal_geom = [districts_gdf.union_all().buffer(0.1)]
    print("Função Vector_map completada")
    district_names_series = districts_gdf['name']
    return districts_gdf, portugal_geom, district_names_series

def manipulate_raster_solar(solar_directory, portugal_geom):
    with rasterio.open(solar_directory) as src: #Ficheiro com dados de radiação solar médios(kWh)
        solar_meta = src.meta
        print(solar_meta)

        out_image, out_transform = mask(src, portugal_geom, crop=True)

        solar_array = out_image[0]
        solar_transform = out_transform
        solar_shape = solar_array.shape
        print("Função Manipulate_raster_solar completada completada")
        return solar_shape, solar_transform, solar_array



def manipulate_geojson_buildings(buildings_directory, solar_shape, solar_transform):

    if not os.path.exists("portugal_mainland_buildings.parquet"):
        ##isto gerava a versão com clip dos telhados
        buildings_gdf = gpd.read_parquet("pt_buildings_complete.parquet")
        buildings_gdf = buildings_gdf.clip(portugal_geom[0])
        buildings_gdf.to_parquet("portugal_mainland_buildings.parquet")

    buildings_gdf = gpd.read_parquet(buildings_directory)

    buildings_gdf.crs = "EPSG:4326"
    print(f"Total estimated buildings in Portugal: {len(buildings_gdf)}")


    if not os.path.exists("portugal_building_mask.tif"):
        if buildings_gdf.crs != "EPSG:4326":
            buildings_gdf = buildings_gdf.to_crs("EPSG:4326")
        #Esta linha simplesmente multiplica os píxeis por 10
        fine_shape = (solar_shape[0] * 25, solar_shape[1] * 25)
        #esta linha mantém a origem do mapa, mas muda os steps de cada pixel para um décimo. como há 10x píxeis, fica 10/10==1 vezes o tamanho original
        fine_transform = solar_transform * solar_transform.scale(1 / 25, 1 / 25)

        #isto cria o mapa rasterizado com píxeis mais pequenos
        fine_mask = features.rasterize(
            [(geom, 1) for geom in buildings_gdf.geometry],
            out_shape=fine_shape,
            transform=fine_transform,
            fill=0,
            dtype='uint8')


        fractional_mask = cv2.resize(#isto vai agregar a máscara, cada 10x10 píxeis tornam-se 1
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

    # --- CONSTANTS ---
    # Fraction of roof area actually usable for PV (e.g., 0.75 = 25% is blocked)
    USABLE_FRACTION = 0.25
    #Solar panels are large, about let's say 7m², so for every square meter you have 1/7 solar panels
    PANEL_SiZE = 1*1.6
    #Solar efficiency
    KWP=0.45

    print("Calculating potential energy...")

    # Element-wise multiplication: Solar (kWh/m2) * Mask (Fractional Area) * Usability
    # Result is in kWh per pixel
    potential_energy = solar_array * building_mask * USABLE_FRACTION * 800*800 / PANEL_SiZE * KWP
    potential_energy = solar_array * building_mask * USABLE_FRACTION * 220000
    potential_energy = np.nan_to_num(potential_energy, nan=0.0)
    potential_energy = np.where(potential_energy < 1e-5, 0, potential_energy)

    #potential_energy = gpd.read_parquet(output_filename)
    return potential_energy





districts_gdf, portugal_geom, district_names_series = vector_map("pt.json")
solar_shape, solar_transform, solar_array = manipulate_raster_solar("PVOUT.tif", portugal_geom)
print(f"DEBUG: Min={np.nanmin(solar_array)}, Max={np.nanmax(solar_array)}")
buildings_gdf, building_mask = manipulate_geojson_buildings("portugal_mainland_buildings.parquet", solar_shape, solar_transform)
potential_energy_array = calculate_and_save_potential(solar_array,building_mask, solar_transform)


def radiation_map():
    fig, ax = plt.subplots(figsize=(7, 12))

    plot_data = np.where(solar_array < 10, np.nan, solar_array)
    print(np.nanmax(plot_data), "Máximo")
    im = show(plot_data, transform=solar_transform, ax=ax, cmap='YlOrRd')

    cbar = fig.colorbar(im.get_images()[0], ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Yearly PV Power Potential (kWh/m²)', rotation=270, labelpad=20)
    districts_gdf.boundary.plot(ax=ax, edgecolor='black', linewidth=1)

    ax.set_title("Solar Potential Pixels vs. District Boundaries")
    plt.savefig("mapa_rad.png")
    plt.show()
    plt.close()
    return




def make_plot_raster_under_vectors(fractional_mask, solar_transform, buildings_gdf, x_zoom, y_zoom):
    fig, ax = plt.subplots(figsize=(12, 12))
    ext = rasterio.plot.plotting_extent(fractional_mask, solar_transform)

    # --- THE CHANGE IS HERE ---
    # 1. Do NOT use np.ma.masked_where. Use the raw array.
    # 2. Use 'Blues' as you requested for that strong blue look.
    # 3. Set vmin=0 so that 0% coverage is the lightest blue, not white.
    im = ax.imshow(
        fractional_mask,
        extent=ext,
        cmap='viridis',
        alpha=1.0,
        origin='upper',
        vmin=0,
        vmax=1
    )
    # ---------------------------

    buildings_gdf.geometry.boundary.plot(
        ax=ax,
        color='red',
        linewidth=0.5,
        alpha=0.8
    )

    ax.set_xlim(x_zoom)
    ax.set_ylim(y_zoom)

    plt.colorbar(im, ax=ax, label='Building Density (Fraction)')
    ax.set_title("Overlay: Building Vector Outlines on Fractional Mask")
    plt.savefig("building_density_overlay.png")


def plot_fractional_raster(mask_array, transform, solar_array, title, name):
    # 1. Clean data
    data = np.nan_to_num(mask_array, nan=0.0)
    data[data < 1e-5] = 0.0

    # 2. THE FIX: Create an "Ocean Mask"
    # We look at the original solar_array. If the solar value is <= 0
    # or equal to that e-38 constant, it's the ocean.
    ocean_mask = (solar_array <= 1e-30)

    # 3. Apply the ocean mask only
    # This keeps land-zeros as 0.0 (dark) but makes ocean NaNs/Zeros transparent
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





# Call the functions

radiation_map()
plot_fractional_raster(building_mask, solar_transform, solar_array, "buildings", "buildings.png")
plot_fractional_raster(potential_energy_array, solar_transform, solar_array, "Solar Potential: Land Only", "Solar potential.png")
make_plot_raster_under_vectors(building_mask, solar_transform, buildings_gdf, [-9.18, -9.10], [38.70, 38.76])
make_plot_raster_under_vectors(building_mask, solar_transform, buildings_gdf, [-9.7, -6.0], [36.8, 42.2])

def sum_potential_by_district(potential_array, transform, districts_gdf):
    # 1. We must temporarily "wrap" the array as a raster dataset for masking
    # We'll use an in-memory dataset to keep it fast
    from rasterio.io import MemoryFile

    results = []

    # Prepare metadata for the memory file
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

            # 2. Iterate through each district
            for _, row in districts_gdf.iterrows():
                district_name = row['name']
                geom = [row['geometry']]

                try:
                    # Mask the raster to the district geometry
                    # crop=True keeps the extracted array small and fast
                    out_image, _ = mask(dataset, geom, crop=True, nodata=0)

                    # Sum the values (kWh)
                    total_potential = out_image.sum()
                    results.append({'district': district_name, 'total_kWh': total_potential})

                except ValueError:
                    # Handles cases where a district might fall outside the raster bounds
                    results.append({'district': district_name, 'total_kWh': 0})

    # 3. Return as a nicely sorted DataFrame
    summary_df = pd.DataFrame(results).sort_values(by='total_kWh', ascending=False)


    return summary_df

print(sum_potential_by_district(potential_energy_array, solar_transform, districts_gdf))

summary_results = sum_potential_by_district(potential_energy_array, solar_transform, districts_gdf)
total_national_kwh = summary_results['total_kWh'].sum()

print(f"Total National Potential: {total_national_kwh:.2e} kWh")
print(f"Total National Potential: {total_national_kwh / 1e9:.2f} TWh")










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



avg_solar_df = average_radiation_by_district(solar_array, solar_transform, districts_gdf)

print("--- Average Solar Radiation by District (kWh/m²/year) ---")
print(avg_solar_df.to_string(index=False))