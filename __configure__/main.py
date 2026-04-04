import os
import sys
import time

# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_path)

from __configure__.dependencies import main as install_dependencies
from __configure__.paths import main as ensure_paths


def main():
    start_time = time.time()
    print("Iniciando a configuração do projeto")
    install_dependencies()
    ensure_paths()
    finish_time = time.time()
    final_time = finish_time - start_time
    print(f"Configuração de projeto finalizado em {final_time}s")
    return 0


if __name__ == "__main__":
    main()
