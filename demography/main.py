import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_path)

from demography.population_total.main import main as pop_total
from demography.population_density.main import main as pop_density


def main():
    print("Iniciando processamento de dados demográficos")
    start = time.time()

    pop_total()
    pop_density()

    finish = time.time()
    final_time = finish - start
    print(f"Processamento de dados demográficos finalizado em {final_time}s")
    return 0


if __name__ == "__main__":
    main()
