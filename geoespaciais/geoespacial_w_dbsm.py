import geopandas as gpd
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from dask.dataframe import to_csv


def vector_map(geojson_directory):
    districts_gdf = gpd.read_file(geojson_directory)  # Ficheiro com mapa de distritos, já está em formato WGS84
    districts_gdf = districts_gdf[~districts_gdf['name'].isin(['Azores', 'Madeira'])]
    print(districts_gdf.geometry.head())
    portugal_geom = [districts_gdf.union_all().buffer(0.1)]
    print("Função Vector_map completada")
    district_names_series = districts_gdf['name']
    return districts_gdf, portugal_geom, district_names_series


def main():

    file_name = 'dbsm-portugal-R2025.gpkg'
    layer_name = 'dbsm-portugal-R2025'

    gdf = gpd.read_file(file_name, layer=layer_name)

    print("\n--- GeoDataFrame Info ---")
    print(gdf.info())
    print("\n--- First 5 Rows ---")
    print(gdf.head())


    print(f"\nOriginal CRS: {gdf.crs}")

    gdf['centroid'] = gdf.centroid#Considerar cada telhado como um ponto para simplificar as contas
    gdf = gdf.to_crs(epsg=4326)#Conversão para wgs84


    print(f"\nTotal features: {len(gdf)}")
    print(f"Geometry type: {gdf.geom_type.unique()}")


    invalid_geoms = gdf[~gdf.is_valid]
    if not invalid_geoms.empty:
        print(f"Found {len(invalid_geoms)} invalid geometries. Fixing...")
        gdf['geometry'] = gdf.make_valid()



    conn = sqlite3.connect(file_name)

    query = """
    SELECT 
        COUNT(*) as total_buildings,
        SUM(rooftop_pv_potential_MWh_per_y) as total_mwh_year,
        AVG(rooftop_pv_potential_MWh_per_y) as avg_mwh_year
    FROM "dbsm-portugal-R2025"
    """

    df_stats = pd.read_sql_query(query, conn)
    conn.close()


    total_mwh = df_stats['total_mwh_year'][0]
    print(f"--- Solar Potential Summary ---")
    print(f"Total Buildings Analyzed: {df_stats['total_buildings'][0]:,}")
    print(f"Total Solar Potential:    {total_mwh:,.2f} MWh/year")
    print(f"Average per Building:     {df_stats['avg_mwh_year'][0]:.2f} MWh/year")
    print(f"In Terawatt-hours:        {total_mwh / 1_000_000:.2f} TWh/year")



    districts_gdf, portugal_geom, district_names_series = vector_map("pt.json")




    #Consistência CRS
    if gdf.crs != districts_gdf.crs:
        print("CRS mismatch", districts_gdf.crs, gdf.crs)
        gdf = gdf.to_crs(districts_gdf.crs)

    #Spatial Joindos distritos com os telhados
    joined_gdf = gpd.sjoin(gdf, districts_gdf[['name', 'geometry']], how='left', predicate='within')

    #Soma por distrito
    district_potential = joined_gdf.groupby('name')['rooftop_pv_potential_MWh_per_y'].sum().reset_index()

    district_potential['TWh_per_year'] = district_potential['rooftop_pv_potential_MWh_per_y'] / 1_000_000
    print(district_potential[['name', 'TWh_per_year']].sort_values(by='TWh_per_year', ascending=False))
    district_potential = district_potential.rename(columns={'name': 'Distrito'})

    district_potential.to_csv("district_potential.csv", index=False)


if __name__ == "__main__":
    main()