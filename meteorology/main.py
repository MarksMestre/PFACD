import time 

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