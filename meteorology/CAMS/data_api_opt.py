import json
import threading
import cdsapi
import logging
import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import sys


# Sobe até a root do projeto
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base_path)

from __configure__.paths import CAMS_FOLDER, IPMA_STATIONS_CSV, CAMS_PROGRESS_FILE


estacoes_concluidas = 0
estacoes_iniciadas = 0
print_lock = Lock() # Lock para proteger a variável de progresso
progresso_lock = Lock() # Lock para proteger a variável de progresso


if not os.path.exists(CAMS_FOLDER):
    os.makedirs(CAMS_FOLDER, exist_ok=True) # Cria a pasta se não existir, sem lançar erro se já existir




# Garante que o logger do cdsapi especificamente está em nível INFO e usa os nossos handlers
logger_cds = logging.getLogger('cdsapi')
logger_cds.setLevel(logging.INFO)
# -----------------------------------------
#########################################################################################################################
############################################################# LOGGING CONFIGURAÇÃO FORÇADA #############################################################
#########################################################################################################################


# Cria uma função de print segura
def safe_print(message):
    with print_lock:
        print(message, flush=True)


# Função para guardar o progresso em um ficheiro JSON
def save_progress(idx, time_step, finish):

    if idx >= finish:
        if os.path.exists(CAMS_PROGRESS_FILE):
            os.remove(CAMS_PROGRESS_FILE) # Remove o ficheiro de progresso se o processo estiver completo
        return
    payload = {
        "idx": idx,
        "time_step": time_step
    }
    with open(CAMS_PROGRESS_FILE, 'w') as f:
        json.dump(payload, f)
        f.close()
    safe_print(f"💾 Progresso guardado: Estação {idx}, Step {time_step}")


# Função para obter os dados da API do CAMS
def api_get(station_id=None, location_name=None, longitude=None, latitude=None, time_step="1month"):

    dataset = "cams-solar-radiation-timeseries"
    request = {
        "sky_type": "observed_cloud",
        "location": {"longitude": longitude, "latitude": latitude}, # Localização da estação
        "altitude": "-999", # Usa o valor por defeito do servidor
        "date": ["2022-01-01/2025-12-31"], # Intervalo de datas (podes ajustar conforme necessário)
        "time_step": time_step, # Dados horários
        "time_reference": "universal_time", # Usa o tempo de referência no final do intervalo
        "data_format": "csv", # Garante que sacas em formato legível para o teu projeto
    }


    # Definir o nome do ficheiro dinamicamente
    time_folder = os.path.join(CAMS_FOLDER, str(time_step)) # Subpasta para o time_step específico
    if not os.path.exists(time_folder):
        os.makedirs(time_folder, exist_ok=True) # Cria a pasta se não existir, sem lançar erro se já existir

    raw_folder = os.path.join(time_folder, "raw_data") # Subpasta para os ficheiros CSV brutos
    if not os.path.exists(raw_folder):
        os.makedirs(raw_folder, exist_ok=True) # Cria a pasta se não existir, sem lançar erro se já existir
    nome_arquivo = f"{raw_folder}/{str(station_id)}.csv"
    try:
        client = cdsapi.Client()
        client.retrieve(dataset, request).download(nome_arquivo)

    except Exception as e:
        safe_print(e)
        return -1


    message = f"Dados obtidos para a estação {station_id} - {location_name} foram salvos em {nome_arquivo}"
    safe_print(message)

    return 0


# Função para processar o ficheiro CSV obtido da API do CAMS
def processar_ficheiro_cams(station_id=None, location_name=None, time_step="1month"):
    if not station_id:
        raise ValueError("O station_id é obrigatório para processar o ficheiro CAMS.")
    
    # Definir o nome do ficheiro dinamicamente
    time_folder = os.path.join(CAMS_FOLDER, str(time_step)) # Subpasta para o time_step específico
    raw_folder = os.path.join(time_folder, "raw_data") # Subpasta para os ficheiros CSV brutos

    nome_ficheiro = f"{raw_folder}/{str(station_id)}.csv"
    # 1. Ler e guardar o cabeçalho (linhas que começam com #)
    cabecalho = []
    with open(nome_ficheiro, 'r', encoding='utf-8') as f:
        for _ in range(42):
            cabecalho.append(f.readline())
    
    # Guardar o cabeçalho num ficheiro à parte para consulta futura
    with open('metadados_cams.txt', 'w', encoding='utf-8') as f:
        f.writelines(cabecalho)
    
    # 2. Ler os dados (a partir da linha 43)
    # O separador deste ficheiro é o ponto e vírgula ';'
    df = pd.read_csv(nome_ficheiro, sep=';', skiprows=42)

    df["Observation period"] = df["# Observation period"] # Renomear a coluna para algo mais simples
    df.drop(columns=["# Observation period"], inplace=True) # Remover a coluna original
    
    # 3. Limpeza básica: Separar o período de observação em datas legíveis
    # O formato é "data_inicio/data_fim"
    df[['inicio', 'fim']] = df['Observation period'].str.split('/', expand=True)
    df['inicio'] = pd.to_datetime(df['inicio'])
    df['fim'] = pd.to_datetime(df['fim'])

    # 4. Adicionar colunas de localização (opcional, mas pode ser útil para análise futura)
    df['station_id'] = station_id if station_id else "Unknown"
    df['location_name'] = location_name if location_name else "Unknown"

    cols = ['station_id', 'location_name', 'inicio', 'fim', 'TOA', 
            'Clear sky GHI', 'Clear sky BHI', 'Clear sky DHI',
            'Clear sky BNI', 'GHI', 'BHI', 'DHI', 'BNI', 'Reliability']
    
    df = df[cols] # Reorganizar as colunas para uma ordem mais lógica

    processed_folder = os.path.join(time_folder, "processed_data") # Subpasta para os ficheiros CSV processados
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder, exist_ok=True) # Cria a pasta se não existir, sem lançar erro se já existir
    # Dataset save
    # Aqui podes salvar o DataFrame ou fazer análises adicionais
    df.to_csv(f"{processed_folder}/{station_id}_processed.csv", index=False, encoding='utf-8', sep=',')
    message = f"Dados processados para a estação {station_id} - {location_name} foram salvos em {processed_folder}/{station_id}_processed.csv"
    safe_print(message)


    return df, cabecalho


# Função para processar cada estação em paralelo com implementação de salvamento de progresso e tratamento de interrupção
def process_station_loop(
        row, 
        finish, idx, time_step="1month"):
    
    global estacoes_concluidas # Variável global para contar estações concluídas
    global estacoes_iniciadas # Variável global para contar estações iniciadas

    station_id = str(row['idEstacao'])
    location_name = str(row['localEstacao'])
    longitude = round(row['longitude'], 4)
    latitude = round(row['latitude'], 4)


    threading.current_thread().name = location_name
    with progresso_lock:
        estacoes_iniciadas += 1
        contagem_iniciada = estacoes_iniciadas


    

    start_time = time.time() # Início do timer para esta estação


    message = f"Processando estação ({contagem_iniciada}/{finish})\n Estação:{station_id} - {location_name}\n(Longitude: {longitude}, Latitude: {latitude})"
    safe_print(f"{message}")


    # Descomenta esta linha para obter os dados diretamente da API (pode demorar)
    status = api_get(
        station_id=station_id, location_name=location_name,
        longitude=longitude, latitude=latitude,
        time_step=time_step
    ) 

    if status == 0:
        # 3. Processar CSV
        processar_ficheiro_cams(station_id, location_name, time_step)

        with progresso_lock:
            estacoes_concluidas += 1
            contagem_concluida = estacoes_concluidas
            save_progress( # Guardar o progresso após cada estação concluída
                idx=idx + 1, 
                time_step=time_step, 
                finish=finish
            ) 
        
        # 4. Calcular tempo e progresso
        end_time = time.time()
        duracao_seg = end_time - start_time
        razao = estacoes_concluidas / finish
        
        # Escolha do ícone de progresso
        if razao <= 0.25: icon = "🔴"
        elif razao <= 0.5: icon = "🟠"
        elif razao <= 0.75: icon = "🟡"
        else: icon = "🟢"

        msg_final = (
            f"{icon} {contagem_concluida/finish:.2%} <b>Estação Finalizada ({contagem_concluida}/{finish})</b>\n"
            f"<code>Estação: {station_id} - {location_name}</code>\n"
            f"<code>Duração: {duracao_seg:.2f}s</code>"
        )
        safe_print(f"✅ [{contagem_concluida}/{finish}] {location_name} concluída em {duracao_seg:.2f}s")
        return 0
    
    else:
        return -1


def loop(time_steps=set(["1month", "1day"]), save_payload=None):

    CORES = {
                "vermelho": "\033[31m",
                "laranja": "\033[38;5;208m",  # Laranja usa código de 256 cores
                "amarelo": "\033[33m",
                "verde": "\033[32m",
                "reset": "\033[0m"           # Necessário para parar de colorir
    }
    
    message = f"🚀 Iniciando o processo de obtenção e processamento dos dados das estações IPMA... {" - Parcial" if save_payload is not None else ""}"
    safe_print(f"{message}")

    time_steps = list(time_steps) # Converter para lista para permitir manipulação de índices

    # Processo de obtenção e processamento dos dados das estações IPMA
    start_main_time = time.time() # Início do timer para o processo completo
    df_stations = pd.read_csv(IPMA_STATIONS_CSV, sep=',', encoding='utf-8', dtype={'idEstacao': str}) # Garante que o ID da estação é lido como string
    finish = len(df_stations)
    idx = 0
    if save_payload is not None:

        global estacoes_concluidas
        global estacoes_iniciadas

        time_step = save_payload.get("time_step", "1month")
        for t_step in time_steps:
            if t_step == time_step:
                break
            time_steps.remove(t_step) # Remove os time_steps anteriores ao que foi salvo, para continuar a partir do ponto correto
        del time_step
        
        idx = save_payload.get("idx", 0)

        estacoes_concluidas = idx
        estacoes_iniciadas = idx
    
    for time_step in time_steps:
        start_time_step = time.time()
        
        # Criar o pool de threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Lista para guardar as tarefas (futures)
            futures = []
            try:
            
                while idx < len(df_stations):
                    row = df_stations.iloc[idx]
                    # Enviamos cada estação para o pool
                    task = executor.submit(process_station_loop, row, finish, idx, time_step)
                    futures.append(task)
                    idx += 1
                
                # (Opcional) Se quiseres esperar e apanhar resultados à medida que chegam:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as e:
                        safe_print(f"Erro numa thread: {e}")
            except KeyboardInterrupt:
                for f in futures:
                    f.cancel() # Tenta cancelar as tarefas pendentes
                raise KeyboardInterrupt() # Relevanta para ser capturado no main

        end_time_step = time.time()
        duracao = end_time_step - start_time_step
        duracao_min = duracao / 60
        duracao_horas = duracao_min / 60

        msg_local = f"✅ Finalizado {time_step} - Duração total: {duracao:.2f} segundos | ({duracao_min:.2f} minutos | {duracao_horas:.2f} horas)"
        safe_print(msg_local)
    
    end_main_time = time.time()
    duracao_total = end_main_time - start_main_time
    duracao_total_min = duracao_total / 60
    duracao_total_horas = duracao_total_min / 60

    safe_print(f"✅ PROCESSO COMPLETO {" - Parcial" if save_payload is not None else ""} - Duração total: {duracao_total:.2f} segundos | ({duracao_total_min:.2f} minutos | {duracao_total_horas:.2f} horas)")


def main():
    
    try:    
        with open(CAMS_PROGRESS_FILE, 'r') as f:
            save_payload = json.load(f)
    except FileNotFoundError:
        save_payload = None
    
    print(save_payload)

    loop(time_steps=set(["1month", "1day"]), 
              save_payload=save_payload)
    return 0


if __name__ == "__main__":
    try:
        main()
    
    except KeyboardInterrupt:
        # 1. Print local imediato (sempre funciona)
        msg_local = "\n⚠️ Script interrompido manualmente pelo utilizador (Ctrl+C)."
        safe_print(msg_local)
            
        os._exit(0) # Força o fecho do processo

    except Exception as e:
        msg_local = f"💥 O script parou devido a um erro crítico: {e}"
        safe_print(msg_local)
        
        os._exit(1)
