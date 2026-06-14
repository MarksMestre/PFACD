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
O projeto PFACD estrutura-se em torno de três pilares funcionalidades principais:

### 1. **Módulo Meteorológico (meteorology/)**
Este módulo integra múltiplas fontes de dados meteorológicos e ferramentas de validação geoespacial:

#### **CAMS (Copernicus Atmosphere Monitoring Service)**
- **Recolha Automática de Dados**: Utiliza a CDS API para descarregar séries temporais especializadas e variáveis atmosféricas em diferentes resoluções temporais (1 dia, 1 mês)
- **Processamento Paralelo**: Implementa otimizações de fluxo de dados através do módulo `data_api_opt.py` e `data_api_manual.py`, permitindo a ingestão eficiente de grandes volumes de dados
- **Agregação Temporal**: O script `aggregation_day.py` consolida dados diários em períodos mais extensos (mensais, trimestrais, semestrais)
- **Gestão de Estado**: Acompanhamento de progresso através de `progress.json` para garantir a recuperação resiliente de transferências interrompidas
- **Validação de Integridade**: Testes comparativos através de `teste_same_files.py` para assegurar consistência dos dados

#### **IPMA (Instituto Português do Mar e da Atmosfera)**
- **Validação Geoespacial**: Auditoria de precisão de localizações de estações meteorológicas contra registos oficiais do IPMA
- **Reconciliação de Dados**: Identificação e resolução de conflitos de localização através de análise comparativa de coordenadas
- **Mapeamento Visual**: Geração de mapas de conflito interativos (`conflict_maps.html`) para inspeção manual de discrepâncias
- **Fusão de Dados**: Consolidação de informações oficiais e informações locais em registos unificados e validados

#### **METEOSTAT**
- **API de Dados Meteorológicos**: Integração de dados climatológicos históricos como fonte complementar de validação

### 2. **Módulo de Análise Populacional (population/)**
Ferramentas avançadas de análise demográfica com capacidades preditivas:

#### **Densidade Populacional**
- **Análise Geoespacial**: Cálculo e visualização da distribuição espacial de população em território português
- **Segmentação Regional**: Análise por unidades administrativas (NUTS) para compreender padrões concentração urbana

#### **População Total com Modelação Preditiva**
- **Pipeline de Processamento**: Orquestração end-to-end de preparação, transformação e validação de dados (`pipeline.py`)
- **Preparação de Dados**: Limpeza, normalização e engenharia de features para modelos machine learning (`data_preparation.py`)
- **Previsão Demográfica**: Modelos preditivos de população para períodos futuros, validados contra previsões oficiais (`prediction_and_validation.py`)
- **Visualização de Resultados**: Geração de gráficos e relatórios interativos para comunicação de insights (`results_visualization.py`)
- **Integração NUTS**: Suporte a múltiplos anos de classificação NUTS (2021, 2024) para análise temporal consistente

### 3. **Sistema de Configuração Centraizado**
Infraestrutura transversal que suporta a execução coordenada do ecossistema:

#### **Configuração Centralizada (config.py)**
- **Parametrização Unificada**: Definição centralizada de credenciais, endpoints de API, parâmetros de processamento
- **Gestão de Ambientes**: Suporte a múltiplos ambientes (desenvolvimento, teste, produção)
- **Validação de Configuração**: Verificação de integridade de parâmetros antes de execução

#### **Gestão de Caminhos (paths.py)**
- **Abstração de Estrutura**: Definição centralizada de caminhos do projeto para portabilidade cross-platform
- **Validação de Diretórios**: Garantia de existência e acessibilidade de diretórios críticos
- **Flexibilidade de Locais**: Suporte a diferentes estruturas de armazenamento local e remoto

### **Fluxo de Integração Transversal**
O projeto implementa um fluxo coordenado onde:
1. Os dados meteorológicos (CAMS, IPMA) são recolhidos, validados e preprocessados
2. A população para 2025 é prevista e os dados demográficos são consolidados para futura integração
3. Os modelos preditivos utilizam dados integrados para gerar previsões de consumo e produção energética

Esta arquitetura modular e eficiente permite análises multi-dimensionais da transição energética portuguesa, focando na caracterização de
Unidades de Produção para Autoconsumo (UPAC) com base em contextos meteorológicos, demográficos e territoriais.


## Fluxo de `script`


1. Abra a pasta "PFACD". NOTA: Não altere a root para outra subpasta, mantenha-se nesta localização
2. Corra o `config.py` com o Python. Isto gerará o ambiente virtual `.venv` e irá instalar as bibliotecas presentes no `requirements.txt`
3. Se o `.venv` ainda não estiver ativado, ative. Se já estiver ativado, pular para passo 4.
4. Corra o `generate_files.py` para gerar todos os ficheiros  



