# Projeto PFACD: Caracterização do Autoconsumo em Portugal

Este repositório contém o ecossistema de dados desenvolvido para o projeto "Caracterização do Autoconsumo em Portugal", realizado em colaboração com a E-REDES no âmbito da Licenciatura em Ciência de Dados do Iscte - Instituto Universitário de Lisboa. O objetivo central é analisar a transição energética nacional através da caracterização das Unidades de Produção para Autoconsumo (UPAC), focando-se na sua distribuição territorial, evolução temporal e desempenho funcional. Para tal, foi implementada uma infraestrutura robusta em Python que automatiza a recolha de séries temporais da CDS API (CAMS) e dados abertos da E-REDES, utilizando processamento paralelo para otimizar o fluxo de dados. Além da ingestão de dados, o projeto inclui ferramentas avançadas de auditoria geoespacial para validar a precisão das localizações das estações face aos registos oficiais do IPMA, estabelecendo uma base analítica sólida e fiável para futuras modelações preditivas de consumo e produção energética.

---

## Estrutura do Projeto


```text
{📦PFACD
 ┣ 📂meteorology
 ┃ ┣ 📂CAMS
 ┃ ┃ ┣ 📂1day
 ┃ ┃ ┃ ┣ 📂processed_data
 ┃ ┃ ┃ ┣ 📂raw_data
 ┃ ┃ ┃ ┗ 📜merged.csv
 ┃ ┃ ┣ 📂1month
 ┃ ┃ ┃ ┣ 📂processed_data
 ┃ ┃ ┃ ┣ 📂raw_data
 ┃ ┃ ┃ ┗ 📜merged.csv
 ┃ ┃ ┣ 📂data_final
 ┃ ┃ ┃ ┣ 📜merged_1day_copy_month.csv
 ┃ ┃ ┃ ┣ 📜merged_1day_copy_semester.csv
 ┃ ┃ ┃ ┗ 📜merged_1day_copy_trimester.csv
 ┃ ┃ ┣ 📂data_merged
 ┃ ┃ ┃ ┣ 📜merged_1day.csv
 ┃ ┃ ┃ ┗ 📜merged_1month.csv
 ┃ ┃ ┣ 📜aggregation_day.py
 ┃ ┃ ┣ 📜data_api_manual.py
 ┃ ┃ ┣ 📜data_api_opt.py
 ┃ ┃ ┣ 📜data_api_opt_bot.py
 ┃ ┃ ┣ 📜metadados_cams.txt
 ┃ ┃ ┣ 📜process_time_and_concat_api.py
 ┃ ┃ ┣ 📜progress.json
 ┃ ┃ ┗ 📜teste_same_files.py
 ┃ ┣ 📂IPMA
 ┃ ┃ ┣ 📂data_final
 ┃ ┃ ┣ 📂data_input
 ┃ ┃ ┃ ┣ 📜IPMA_stations.csv
 ┃ ┃ ┃ ┣ 📜IPMA_stations.json
 ┃ ┃ ┃ ┣ 📜IPMA_stations_data_oficial.csv
 ┃ ┃ ┃ ┣ 📜IPMA_stations_data_oficial_corrected.csv
 ┃ ┃ ┃ ┗ 📜IPMA_stations_with_location_info.csv
 ┃ ┃ ┣ 📂data_merged
 ┃ ┃ ┃ ┣ 📜conflict_maps.html
 ┃ ┃ ┃ ┣ 📜IPMA_stations_conflict.csv
 ┃ ┃ ┃ ┣ 📜IPMA_stations_conflict_manual.csv
 ┃ ┃ ┃ ┣ 📜IPMA_stations_dont_match.csv
 ┃ ┃ ┃ ┗ 📜IPMA_stations_merged.csv
 ┃ ┃ ┣ 📜create_local_info_IPMA.py
 ┃ ┃ ┣ 📜merge_oficial_local_info.py
 ┃ ┃ ┗ 📜read_loc_stations_IPMA.py
 ┃ ┗ 📂METEOSTAT
 ┃ ┃ ┗ 📜get_api_data.py
 ┣ 📂population
 ┃ ┣ 📂densidade_populacional
 ┃ ┃ ┗ 📜densidade_populacional.csv
 ┃ ┗ 📂populacao_total
 ┃ ┃ ┣ 📂data
 ┃ ┃ ┃ ┣ 📜ml_data.csv
 ┃ ┃ ┃ ┣ 📜populacao_com_previsao_2025.csv
 ┃ ┃ ┃ ┣ 📜populacao_total.csv
 ┃ ┃ ┃ ┣ 📜populacao_total_nuts2021.csv
 ┃ ┃ ┃ ┣ 📜populacao_total_nuts2024.csv
 ┃ ┃ ┃ ┣ 📜populacao_total_weights.csv
 ┃ ┃ ┃ ┣ 📜prediction.csv
 ┃ ┃ ┃ ┗ 📜previsao_oficial_2025.csv
 ┃ ┃ ┣ 📜data_preparation.py
 ┃ ┃ ┣ 📜pipeline.py
 ┃ ┃ ┣ 📜prediction_and_validation.py
 ┃ ┃ ┗ 📜results_visualization.py
 ┣ 📜bots.py
 ┣ 📜config.py
 ┣ 📜paths.py
 ┣ 📜ponto_de_situacao.txt
 ┣ 📜requirements.txt
 ┗ 📜tree.txt
}
``` 

## Funcionalidades do Projeto
O projeto PFACD estrutura-se em torno de três pilares funcionalidades principais:

### 1. **Módulo Meteorológico (meteorology/)**
Este módulo integra múltiplas fontes de dados meteorológicos e ferramentas de validação geoespacial:

#### **CAMS (Copernicus Atmosphere Monitoring Service)**
- **Recolha Automática de Dados**: Utiliza a CDS API para descarregar séries temporais especializadas e variáveis atmosféricas em diferentes resoluções temporais (1 dia, 1 mês)
- **Processamento Paralelo**: Implementa otimizações de fluxo de dados através do módulo `data_api_opt.py` e `data_api_opt_bot.py`, permitindo a ingestão eficiente de grandes volumes de dados
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
