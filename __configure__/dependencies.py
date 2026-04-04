import subprocess
import sys
import os
import time

# Garante que a raiz está no path para os imports funcionarem
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

def setup():
    # 1. Criar o ambiente virtual (.venv)
    print("--- Criando ambiente virtual (.venv) ---")
    try:
        # Usamos --with-pip para garantir que ele vem instalado
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar venv: {e}")
        return

    # Pequena pausa para o sistema de ficheiros do Windows processar a criação
    time.sleep(1)

    # 2. Definir caminhos
    if os.name == "nt":  # Windows
        python_venv = os.path.join(".venv", "Scripts", "python.exe")
    else:  # Linux / Mac
        python_venv = os.path.join(".venv", "bin", "python")

    # VERIFICAÇÃO CRÍTICA: O executável existe?
    if not os.path.exists(python_venv):
        print(f"Erro: Não foi possível encontrar o Python em {python_venv}")
        return

    # 3. Atualizar o pip e instalar requirements
    # DICA DE OURO: No Windows, em vez de chamar 'pip.exe', chama 'python -m pip'
    # Isto evita o erro de "Acesso Negado" ou ficheiro bloqueado.
    print("--- Atualizando o pip ---")
    try:
        subprocess.run([python_venv, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        if os.path.exists("requirements.txt"):
            print("--- Instalando dependências ---")
            subprocess.run([python_venv, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("\n--- Setup concluído com sucesso! ---")
        else:
            print("\n--- Aviso: requirements.txt não encontrado! ---")
            
    except subprocess.CalledProcessError as e:
        print(f"\n--- Erro durante a instalação: {e} ---")


def main():
    setup()


if __name__ == "__main__":
    main()
