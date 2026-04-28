import sqlite3
import folium
import pandas as pd
import meteostat as ms
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import METEOSTAT_INVENTORY_STATIONS_DATA, METEOSTAT_STATIONS_MAP


def describe_database(db_path):
    # 1. Conectar à base de dados
    conn = sqlite3.connect(db_path)
    
    # 2. Listar todas as tabelas existentes no ficheiro .db
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"🗄️ Tabelas encontradas: {[t[0] for t in tables]}")
    
    for table_name in [t[0] for t in tables]:
        print(f"\n{'='*50}")
        print(f"📊 DESCREVENDO A TABELA: {table_name}")
        print(f"{'='*50}")
        
        # Carregar a tabela para um DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # A. Estrutura e tipos de dados
        print("\n🔎 Informação Geral (Tipos e Nulos):")
        print(df.info())
        
        # B. Descrição estatística (Numéricos)
        print("\n📈 Estatísticas Descritivas (Média, Quartis, etc.):")
        print(df.describe())
        
        # C. Verificar se existem valores nulos
        print("\n❓ Valores em falta por coluna:")
        print(df.isnull().sum())
        
        # D. Amostra dos dados
        print("\n📋 Primeiras 5 linhas:")
        print(df.head())
    
    conn.close()


def load_inventory_data(db_path, start_filter="2020-01-01", end_filter="2024-12-31", provider_filter=None):
    conn = sqlite3.connect(db_path)
    query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query_tables, conn)
    
    if tables.empty:
        print("❌ Nenhuma tabela encontrada.")
        conn.close()
        return None

    table_name = tables.iloc[0]['name']
    df_raw = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    # --- Alteração 1: Filtragem por Datas ---
    df_raw['start'] = pd.to_datetime(df_raw['start'])
    df_raw['end'] = pd.to_datetime(df_raw['end'])
    s_filter = pd.to_datetime(start_filter)
    e_filter = pd.to_datetime(end_filter)

    mask = (df_raw['end'] >= s_filter) & (df_raw['start'] <= e_filter)
    df_filtered = df_raw.loc[mask].copy()

    # --- Alteração 3 (Nova): Filtragem por Provider ---
    if provider_filter is not None:
        # Se passares apenas uma string, convertemos para lista para o .isin() funcionar
        if isinstance(provider_filter, str):
            provider_filter = [provider_filter]
        
        df_filtered = df_filtered[df_filtered['provider'].isin(provider_filter)].copy()
        print(f"🎯 Filtro de provider aplicado: {provider_filter}")

    if df_filtered.empty:
        print("⚠️ Nenhum dado encontrado após os filtros aplicados.")
        return df_filtered

    # --- Alteração 2: Agrupamento em Listas ---
    df_grouped = df_filtered.groupby(['station', 'provider']).agg({
        'parameter': lambda x: list(x),
        'completeness': lambda x: list(x),
        'start': 'min',
        'end': 'max'
    }).reset_index()

    print(f"📥 Dados carregados e colapsados. Estações no intervalo: {len(df_grouped)}")
    return df_grouped


def get_all_stations_metadata():
    print("📥 Extraindo metadados de todas as estações do METEOSTAT...")
    
    # Fazemos uma query SQL direta à base de dados interna do Meteostat
    # Esta query junta a tabela 'stations' com a tabela 'names' (em inglês)
    query = """
        SELECT 
            s.*, 
            n.name 
        FROM stations s
        LEFT JOIN names n ON s.id = n.station AND n.language = 'en'
    """
    
    # Executamos a query via instância interna da biblioteca
    df_all_meta = ms.stations.query(query)
    
    # Definimos o ID como índice para facilitar merges futuros
    df_all_meta = df_all_meta.set_index('id')
    
    print(f"✅ Sucesso! Foram encontradas {len(df_all_meta)} estações.")
    return df_all_meta


def merge_metadata_inventory_data(metadata_df, inventory_df):
    print("🔗 A realizar o merge dos metadados com o inventário...")
    
    # Fazemos o merge: a coluna 'station' do inventory_df 
    # vai procurar correspondência no INDEX do metadata_df
    df_merged = inventory_df.merge(
        metadata_df, 
        left_on='station', 
        right_index=True, 
        how='inner' # 'inner' garante que só ficamos com estações que têm coordenadas
    )
    
    print(f"✅ Merge concluído. Total de registos: {len(df_merged)}")
    return df_merged


def create_maps_stations(df_merged, map_filepath):
    if df_merged is None or df_merged.empty:
        print("⚠️ Sem dados para mapear.")
        return

    print("🗺️ A gerar mapa de estações Meteostat...")
    
    # Criar mapa centrado na média das coordenadas das estações
    mapa = folium.Map(
        location=[df_merged['latitude'].mean(), df_merged['longitude'].mean()], 
        zoom_start=6,
        tiles='CartoDB Positron'
    )

    for _, row in df_merged.iterrows():
        # Formatação das listas para exibição bonita no HTML
        params_str = ", ".join(row['parameter'])
        completeness_str = ", ".join([str(c) for c in row['completeness']])
        
        # Construção do Quadro de Detalhes (HTML)
        conteudo_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; width: 300px; line-height: 1.4; color: #2c3e50;">
            
            <h5 style="margin: 0 0 5px 0; color: #2980b9; border-bottom: 2px solid #3498db; padding-bottom: 3px;">
                Identification Metadata
            </h5>
            <table style="width: 100%; font-size: 12px; margin-bottom: 10px;">
                <tr><td style="width: 80px;"><b>ID:</b></td><td><code>{row['station']}</code></td></tr>
                <tr><td><b>Name:</b></td><td>{row['name']}</td></tr>
            </table>

            <h5 style="margin: 10px 0 5px 0; color: #27ae60; border-bottom: 2px solid #2ecc71; padding-bottom: 3px;">
                Location Metadata
            </h5>
            <table style="width: 100%; font-size: 12px; margin-bottom: 10px;">
                <tr><td style="width: 80px;"><b>Latitude:</b></td><td>{row['latitude']:.4f}</td></tr>
                <tr><td><b>Longitude:</b></td><td>{row['longitude']:.4f}</td></tr>
                <tr><td><b>Altitude:</b></td><td>{row['elevation']} m</td></tr>
            </table>

            <h5 style="margin: 10px 0 5px 0; color: #e67e22; border-bottom: 2px solid #f39c12; padding-bottom: 3px;">
                Provider Data
            </h5>
            <div style="font-size: 11px; background-color: #fdf2e9; padding: 8px; border-radius: 4px; border: 1px solid #fbe4d5;">
                <p style="margin: 2px 0;"><b>Provider:</b> <span style="text-transform: uppercase;">{row['provider']}</span></p>
                <p style="margin: 2px 0;"><b>Parameters:</b> {params_str}</p>
                <p style="margin: 2px 0;"><b>Completeness:</b> {completeness_str}</p>
                <p style="margin: 2px 0; font-style: italic; color: #7f8c8d; font-size: 10px;">
                    Period: {row['start'].strftime('%Y-%m-%d')} to {row['end'].strftime('%Y-%m-%d')}
                </p>
            </div>
        </div>
        """
        
        # Criação do ponto no mapa
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6,
            color='#2980b9',
            fill=True,
            fill_color='#3498db',
            fill_opacity=0.7,
            popup=folium.Popup(conteudo_html, max_width=350),
            tooltip=f"Estação: {row['name']}"
        ).add_to(mapa)

    # Salvar o mapa
    mapa.save(map_filepath)
    print(f"✅ Mapa guardado com sucesso em: {map_filepath}")
          

def main():
    df_inventory_stations = load_inventory_data(
        METEOSTAT_INVENTORY_STATIONS_DATA,
        provider_filter=None)

    print(df_inventory_stations.head())

    # Execução
    df_metadata = get_all_stations_metadata()

    # Agora podes ver as coordenadas (latitude, longitude) e altitude
    print(df_metadata[['name', 'latitude', 'longitude', 'elevation']].head())

    merged_df = merge_metadata_inventory_data(
        metadata_df=df_metadata,
        inventory_df=df_inventory_stations
    )

    # FILTRO CRÍTICO: Portugal apenas
    df_portugal = merged_df[merged_df['country'] == 'PT'].copy()

    print(df_portugal.head())

    create_maps_stations(
        df_merged=df_portugal,
        map_filepath=METEOSTAT_STATIONS_MAP
    )

    return 0



if __name__ == "__main__":
    main()

