import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from meteorology.IPMA.read_loc_stations_IPMA import main as create_IPMA_csv
from meteorology.IPMA.merge_oficial_local_info import main as compare_API_site_data


def main():
    print("Iniciando processamento de dados das estações do IPMA")
    start_time = time.time()
    create_IPMA_csv()
    compare_API_site_data()
    finish_time = time.time()
    final_time = finish_time - start_time
    print(f"Processamento de dados do IPMA finalizado em {final_time}s")
    return 0