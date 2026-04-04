import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_path)

from meteorology.IPMA.main import main as IPMA
from meteorology.CAMS.main import main as CAMS
from meteorology.METEOSTAT.main import main as METEOSTAT


def main():
    print("Iniciando processamento de dados metereológicos")
    start_time = time.time()

    IPMA()
    CAMS()
    METEOSTAT()

    finis_time = time.time()
    final_time = finis_time-start_time
    print(f"Processamento de dados metereológicos finalizado em {final_time}s")
    return 0

if __name__ == "__main__":
    main()