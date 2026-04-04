import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)


from demography.population_total.data_preparation import main as data_prepare
from demography.population_total.prediction_and_validation import main as predict_validate
from demography.population_total.results_visualization import main as visualization


def main():
    print("Iniciando o processamento dos dados de população total")
    start_time = time.time()
    data_prepare()
    predict_validate()
    visualization()
    finish_time = time.time()
    final_time = finish_time - start_time
    print(f"Processamento dos dados de população total terminado em {final_time}s")
    return 0 


if __name__ == "__main__":
    main()