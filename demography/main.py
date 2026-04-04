import time
from demography.population_total.main import main as pop_total


def main():
    print("Iniciando processamento de dados demográficos")
    start = time.time()

    pop_total()

    finish = time.time()
    final_time = finish - start
    print(f"Processamento de dados demográficos finalizado em {final_time}s")
    return 0