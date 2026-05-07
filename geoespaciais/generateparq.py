import os
import geopandas as gpd
import pandas as pd


west_gdf = gpd.read_parquet("pt_west.parquet")
east_gdf = gpd.read_parquet("pt_east.parquet")

#Combinar
buildings_gdf = gpd.GeoDataFrame(pd.concat([west_gdf, east_gdf], ignore_index=True))

#Guardar o resultado
buildings_gdf.to_parquet("pt_buildings_complete.parquet")

print(f"Total Buildings: {len(buildings_gdf)}")
print(f"Full Extent: {buildings_gdf.total_bounds}")