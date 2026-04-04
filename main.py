import subprocess
import sys
import os
import time
from __configure__.main import main as configure

def main():
    print("Iniciando main process")
    start = time.time()
    # 1. Corre a configuração (instala dependências na .venv)
    configure()

    # 2. Verifica se já estamos a correr dentro da .venv
    # Se não estivermos, relançamos o script usando o python da .venv
    venv_python = os.path.join(".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".venv", "bin", "python")
    
    if sys.executable != os.path.abspath(venv_python):
        print(f"🚀 Reiniciando o script dentro do ambiente virtual...")
        # Relança o comando original mas com o python da .venv
        subprocess.run([venv_python] + sys.argv)
        return

    # 3. Se chegamos aqui, já estamos na .venv e os imports vão funcionar
    from __pipeline__.main import main as pipeline
    pipeline()
    finish = time.time()
    final_time = finish - start

    print(f"Finalizado main process em {final_time}s")

if __name__ == "__main__":
    main()