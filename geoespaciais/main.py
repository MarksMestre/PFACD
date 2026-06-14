import time
import os
import sys

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_path)

from generateparq import main as generateparq
from geoespacial_w_dbsm import main as geospacial_w_dbsm
from geoespaciais.geoespacial import main as geoespacial

def main():
    print("\n\n\nIniciando processamento de dados geográficos\n\n\n")
    start = time.time()

    generateparq()
    geoespacial()
    geospacial_w_dbsm()

    finish = time.time()
    final_time = finish - start
    print(f"\n\n\nProcessamento de dados demográficos finalizado em {final_time}s\n\n\n")
    return 0


if __name__ == "__main__":
    main()
