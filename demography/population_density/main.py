
import time
import os
import sys


# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from demography.population_density.clean_density import main as data_prep


def main():
    start_time = time.time()
    print("Iniciando processamento de dados de densidade populacional")
    data_prep()
    print("Processamento de dados de densidade populacional finalizado")
    end_time = time.time()
    print(f"Tempo total de execução (densidade populacional): {end_time - start_time} segundos")
    return 0


if __name__ == "__main__":
    main()
    