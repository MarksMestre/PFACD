import sys
import os
import time

# Garante que a raiz está no path para os imports funcionarem
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from meteorology.main import main as metereology
from demography.main import main as demography
from geoespaciais.main import main as geoespacial
from economy.main import main as economy

def main():
    print(f"Iniciando a gerar os ficheiros do projeto")

    start_time = time.time()

    print("A gerar dados metereológicos")
    metereology()
    print("Geração de dados metereológicos terminada")

    print("A gerar dados demográficos")
    demography()
    print("Geração de dados demográficos terminada")

    print("A gerar dados económicos")
    economy()
    print("Geração de dados económicos terminada")


    # print("A gerar dados geoespaciais")
    # geoespacial()
    # print("Geração de dados geoespaciais")

    finish_time = time.time()
    final_time = finish_time - start_time
    print(f"Processo de geração de ficheiros terminado em {final_time}s")

if __name__ == "__main__":
    main()
