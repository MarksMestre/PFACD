import os
import sys
import time
import subprocess

# Garante que a raiz está no path para os imports funcionarem
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Imports dos teus módulos locais (agora funcionam porque o main.py já garantiu a .venv)
from meteorology.main import main as metereology
from demography.main import main as demography
from economy.main import main as economy

def abrir_e_esperar_docker():
    """Garante que o Docker Desktop está aberto e o motor está ativo."""
    print("\n🐳 [Docker] A verificar se o Docker Desktop está ativo...")
    
    try:
        # Se responder, o motor já está ativo em background
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("   -> Docker já se encontra ativo e pronto!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ [Docker] Docker Desktop parece estar fechado. A tentar iniciá-lo...")

    # 1. Tentar abrir o Docker Desktop conforme o Sistema Operativo
    try:
        if os.name == "nt":  # Windows
            caminho_windows = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
            if os.path.exists(caminho_windows):
                subprocess.Popen([caminho_windows], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print("❌ Erro: Não foi possível encontrar o Docker Desktop no caminho padrão do Windows.")
                return False
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", "-a", "Docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # Linux
            print("ℹ️ Em Linux, por favor inicie o serviço com: sudo systemctl start docker")
            return False
    except Exception as e:
        print(f"❌ Erro ao tentar lançar a aplicação Docker Desktop: {e}")
        return False

    # 2. Loop de espera (Polling) para o motor ficar "Ready"
    tentativas_maximas = 15
    print("⏳ A aguardar que o motor do Docker inicialize completamente", end="", flush=True)
    
    for _ in range(tentativas_maximas):
        time.sleep(3)
        print(".", end="", flush=True)
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("\n🚀 [Docker] Motor totalmente ativo e pronto a receber comandos!")
            return True
        except subprocess.CalledProcessError:
            continue

    print("\n❌ Erro: O Docker Desktop foi aberto, mas demorou demasiado tempo a inicializar.")
    return False


def correr_modulo_geoespacial_via_docker():
    """Orquestra a construção e execução do Docker focado na pasta geoespaciais."""
    print("\n🌍 [DOCKER] A iniciar automação do módulo Geoespacial...")
    
    if not abrir_e_esperar_docker():
        print("⚠️ O módulo Geoespacial foi saltado porque o Docker Desktop não está disponível/ativo.")
        return False
        
    # RESOLUÇÃO DE CAMINHO DINÂMICA:
    # __file__ está em: PFACD/__pipeline__/main.py
    # 1º dirname -> PFACD/__pipeline__
    # 2º dirname -> PFACD (Raiz do projeto)
    pasta_raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_geo = os.path.join(pasta_raiz_projeto, "geoespaciais")
    
    if not os.path.exists(pasta_geo):
        print(f"❌ Erro: Pasta geoespaciais não encontrada em: {pasta_geo}")
        return False

    try:
        # 1. Fazer o Docker Build apontando para a pasta geoespaciais
        print(f"🐳 [Docker] A construir a imagem 'pfacd-geoespacial' a partir de: {pasta_geo}")
        subprocess.run(
            ["docker", "build", "-t", "pfacd-geoespacial", "."], 
            cwd=pasta_geo, 
            check=True
        )
        
        # 2. Fazer o Docker Run ligando o volume físico dos ficheiros geoespaciais
        print("🐳 [Docker] A iniciar o contentor e a processar os dados geoespaciais...")
        comando_run = [
            "docker", "run", "--rm",
            "-v", f"{pasta_geo}:/app",  # Garante que os mapas/ficheiros finais são salvos na tua pasta real
            "-w", "/app",
            "pfacd-geoespacial"
        ]
        
        subprocess.run(comando_run, check=True)
        print("🐳 [Docker] Contentor geoespacial finalizado e limpo (--rm) com sucesso!")
        return True

    except FileNotFoundError:
        print("❌ Erro: O executável do 'docker' não foi encontrado no PATH do sistema.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a execução dos comandos Docker: {e}")
        return False


def main():
    """Executa o pipeline completo de ponta a ponta."""
    print("\n==================================================")
    print("📂 Executando os Módulos do Pipeline")
    print("==================================================")

    print("\n--- 1. A gerar dados meteorológicos ---")
    metereology()
    print("Geração de dados meteorológicos terminada.")

    print("\n--- 2. A gerar dados demográficos ---")
    demography()
    print("Geração de dados demográficos terminada.")

    print("\n--- 3. A gerar dados económicos ---")
    economy()
    print("Geração de dados económicos terminada.")

    print("\n--- 4. A gerar dados geoespaciais (Isolamento Docker) ---")
    sucesso_geo = correr_modulo_geoespacial_via_docker()
    
    if sucesso_geo:
        print("Geração de dados geoespaciais terminada com sucesso!")
    else:
        print("Aviso: A componente geoespacial foi ignorada ou falhou.")


if __name__ == "__main__":
    main()