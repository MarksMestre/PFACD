import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from meteorology.CAMS.process_time_and_concat_api import main as data_process
from meteorology.CAMS.aggregation_day import main as aggregate_day_data


def main():
    print("Inicializando processamento dos dados de radiação solar da DB CAMS")
    start_time = time.time()
    data_process()
    aggregate_day_data()
    finish_time = time.time()
    final_time = finish_time - start_time
    print(f"Processamento de dados de CAMS finalizado em {final_time}s")
    return 0


