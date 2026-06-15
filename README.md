# Projeto PFACD: Caracterização do Autoconsumo em Portugal

Este repositório contém o ecossistema de dados desenvolvido para o projeto "Caracterização do Autoconsumo em Portugal", realizado em colaboração com a E-REDES no âmbito da Licenciatura em Ciência de Dados do Iscte - Instituto Universitário de Lisboa. O objetivo central é analisar a transição energética nacional através da caracterização das Unidades de Produção para Autoconsumo (UPAC), focando-se na sua distribuição territorial, evolução temporal e desempenho funcional. Para tal, foi implementada uma infraestrutura robusta em Python que automatiza a recolha de séries temporais da CDS API (CAMS) e dados abertos da E-REDES, utilizando processamento paralelo para otimizar o fluxo de dados. Além da ingestão de dados, o projeto inclui ferramentas avançadas de auditoria geoespacial para validar a precisão das localizações das estações face aos registos oficiais do IPMA, estabelecendo uma base analítica sólida e fiável para futuras modelações preditivas de consumo e produção energética.

---

## Estrutura do Projeto

```
PFACD
├─ demography
│  ├─ main.py
│  ├─ population_density
│  │  ├─ clean_density.py
│  │  ├─ main.py
│  │  ├─ population_density.csv
│  │  └─ __init__.py
│  ├─ population_total
│  │  ├─ data_input
│  │  │  ├─ populacao_total.csv
│  │  │  └─ previsao_oficial_2025.csv
│  │  ├─ data_preparation.py
│  │  ├─ main.py
│  │  ├─ prediction_and_validation.py
│  │  ├─ results_visualization.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ densidade_atualizada.csv
├─ e-redes
│  ├─ data_input
│  │  ├─ 26-centrais.csv
│  │  ├─ 8-unidades-de-producao-para-autoconsumo.csv
│  │  ├─ capitais_distrito.py
│  │  ├─ district_performance.csv
│  │  ├─ distrito_radiation_imputed.csv
│  │  ├─ energia_injectada_upac.csv
│  │  ├─ energia_injetada.py
│  │  ├─ energia_trimestre_escalao.png
│  │  ├─ estimativas_rad_raster.csv
│  │  ├─ injecaoanual.csv
│  │  ├─ injecao_percentual.csv
│  │  ├─ instalacoes_por_trimestre.png
│  │  ├─ instalacoes_trimestre_escalao.png
│  │  ├─ kw_por_trimestre.png
│  │  ├─ mapa_2022_install.png
│  │  ├─ mapa_2022_potency.png
│  │  ├─ mapa_2025_install.png
│  │  ├─ mapa_2025_potency.png
│  │  ├─ pt.json
│  │  ├─ renewable_count.png
│  │  ├─ renewable_type.png
│  │  ├─ summary_table_analise.png
│  │  ├─ upacs_totais.py
│  │  └─ upacs_totais_limpo.csv
│  ├─ energia_injetada.py
│  ├─ upacs_novas.py
│  └─ __init__.py
├─ economy
│  ├─ 15paises_14anos_kW.csv
│  ├─ 15paises_14anos_kWh.csv
│  ├─ 19paises_6anos_kW.csv
│  ├─ IRENA-Datafile-RenPwrGenCosts-in-2023-v2.xlsx
│  ├─ main.py
│  ├─ portugal_2018-2025_kW.csv
│  └─ previsoes_portugal_2024_2025.csv
├─ extract_presentations.py
├─ geoespaciais
│  ├─ .dockerignore
│  ├─ Dockerfile
│  ├─ generateparq.py
│  ├─ geoespacial copy.py
│  ├─ geoespacial.py
│  ├─ geoespacial_w_dbsm.py
│  ├─ main.py
│  ├─ README.md
│  ├─ requirements.txt
│  └─ __init__.py
├─ main.py
├─ main_without_geo.py
├─ meteorology
│  ├─ CAMS
│  │  ├─ aggregation_day.py
│  │  ├─ data_api_manual.py
│  │  ├─ data_api_opt.py
│  │  ├─ data_input
│  │  │  ├─ 1day
│  │  │  │  ├─ processed_data
│  │  │  │  │  └─ 7240919_processed.csv
│  │  │  │  └─ raw_data
│  │  │  │     └─ 7240919.csv
│  │  │  └─ 1month
│  │  │     ├─ processed_data
│  │  │     │  └─ 7240919_processed.csv
│  │  │     └─ raw_data
│  │  │        └─ 7240919.csv
│  │  ├─ main.py
│  │  ├─ process_time_and_concat_api.py
│  │  ├─ teste_same_files.py
│  │  └─ __init__.py
│  ├─ CapitaisDistrito_Valores_dia_Tn_Tx_Prec_RG.xlsx
│  ├─ DadosIPMA_professor
│  │  ├─ Precepitacao.csv
│  │  ├─ RadiacaoGlobal.csv
│  │  ├─ Tmaxima.csv
│  │  └─ Tminima.csv
│  ├─ IPMA
│  │  ├─ create_local_info_IPMA.py
│  │  ├─ main.py
│  │  ├─ merge_oficial_local_info.py
│  │  ├─ read_loc_stations_IPMA.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ METEOSTAT
│  │  ├─ get_api_data.py
│  │  ├─ main.py
│  │  ├─ stations
│  │  │  ├─ data_input
│  │  │  │  └─ stations.db
│  │  │  ├─ get_stations_data.py
│  │  │  └─ main.py
├─ ponto_de_situacao.txt
├─ README.md
├─ requirements.txt
├─ __configure__
│  ├─ dependencies.py
│  ├─ main.py
│  ├─ paths.py
│  └─ __init__.py
├─ __graficos__
│  ├─ clean_princ_test_folder.py
│  ├─ graficos_principais.py
│  ├─ main.py
│  └─ output
└─ __pipeline__
   ├─ main.py
   └─ main_without_geo.py
```

## Funcionalidades do Projeto
O PFACD é um ecossistema de dados para caracterizar o autoconsumo em Portugal. O projeto combina ingestão, validação e análise de dados meteorológicos, demográficos, económicos e geoespaciais.

### Módulos principais
- **`main.py`**: ponto de entrada principal. Cria/atualiza o ambiente virtual `.venv`, instala dependências e executa o pipeline completo.
- **`__configure__/main.py`**: garante criação de `.venv`, instala `requirements.txt` e cria pastas necessárias.
- **`__pipeline__/main.py`**: orquestra a execução dos módulos de meteorologia, demografia, economia, gráficos e geoespaciais.

### 1. Meteorologia (`meteorology/`)
Este módulo trata a recolha e validação de dados climáticos.
- **`meteorology/main.py`**: executa em sequência `IPMA`, `CAMS` e `METEOSTAT`.
- **`meteorology/IPMA/`**: valida localizações e consolida informações oficiais do IPMA.
- **`meteorology/CAMS/`**: recolhe séries temporais via CDS API, processa dados, agrega por período e valida consistência.
- **`meteorology/METEOSTAT/`**: integra dados históricos complementares para validação e comparação.

### 2. Demografia (`demography/`)
Avalia a evolução populacional e a densidade geográfica.
- **`demography/main.py`**: executa em sequência `population_total` e `population_density`.
- **`demography/population_total/`**: prepara dados, constrói modelos preditivos, valida previsões e gera relatórios.
- **`demography/population_density/`**: limpa e analisa a densidade populacional em território nacional.

### 3. Economia (`economy/`)
Processa informação de produção e custos energéticos.
- **`economy/main.py`**: agrupa análises económicas e dados de custos por país e por ano.
- Dados de entrada incluem ficheiros como `portugal_2018-2025_kW.csv`, `15paises_14anos_kW.csv` e `15paises_14anos_kWh.csv`.

### 4. Geoespaciais (`geoespaciais/`)
Gera análises de potencial energético usando mapas raster e geometria territorial.
- **`geoespaciais/main.py`** e `geoespaciais/Dockerfile` são usados para processamento geoespacial.
- **`geoespaciais/generateparq.py`**: prepara ficheiros de dados espaciais.
- **`geoespaciais/geoespacial.py`**: calcula métricas de produção fotovoltaica e exporta resultados.
- **`geoespaciais/geoespacial_w_dbsm.py`**: executa análise adicional sem depender da ordem de execução dos restantes scripts.

### 5. Gráficos (`__graficos__/`)
Gera visualizações a partir dos dados processados.
- **`__graficos__/main.py`**: coordena a geração de gráficos.
- **`__graficos__/graficos_principais.py`**: contém rotinas de plotagem e exporta imagens finais para `__graficos__/output/`.

### Como executar o projeto (sem processamento geoespacial)
1. Abra a pasta `PFACD` no seu terminal. Não mude para uma subpasta diferente.
2. Execute o ponto de entrada principal:
   - `python main_without_geo.py`
   Isto:
     - cria ou atualiza o ambiente virtual `.venv`
     - instala dependências do `requirements.txt`
     - executa o pipeline completo de meteorologia, demografia, economia, gráficos e geoespaciais
3. Se preferir configurar manualmente:
   - `python __configure__\main.py`
   - depois `python __pipeline__\main.py`
4. Para executar o pipeline completo:
   - [TIAGO COLOCA INSTRUÇÕES AQUI] 
   - Depois de baixar as bases de dados geoespaciais corra `python main.py` no terminal. O script irá automaticamente criar o Docker Image e abrir o Docker backend por si (tem de ter o Docker instalado)
   - Os gráficos resultantes do processamento geoespacial irão ser depositados na pasta [TIAGO METE A PASTA RESULTANTE]

### Execução de módulos independentes
- Meteorologia: `python meteorology\main.py`
- Demografia: `python demography\main.py`
- Economia: `python economy\main.py`
- Gráficos: `python __graficos__\main.py`
- Geoespaciais (Docker recomendado): `python geoespaciais\main.py`

### Geoespaciais com Docker
O módulo geoespacial usa Docker para garantir dependências como GDAL.
1. Abra `geoespaciais/`.
2. Construa a imagem:
   - `docker build -t geoespaciais-app .`
3. Execute um dos scripts:
   - `docker run --rm -v "%cd%:/app" -w /app geoespaciais-app python generateparq.py`
   - `docker run --rm -v "%cd%:/app" -w /app geoespaciais-app python geoespacial.py`
   - `docker run --rm -v "%cd%:/app" -w /app geoespaciais-app python geoespacial_w_dbsm.py`

### Observações práticas
- O `main.py` reinicia automaticamente dentro de `.venv` quando necessário.
- O `requirements.txt` principal prepara o ambiente de execução do projeto.
- O `geoespaciais/requirements.txt` documenta dependências específicas do módulo espacial.
- Se tiver problemas com Docker, use `main_without_geo.py` para correr o pipeline sem a etapa geoespacial.





