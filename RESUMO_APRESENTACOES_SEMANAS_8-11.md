# 📊 RESUMO DAS APRESENTAÇÕES SEMANAIS - SEMANAS 8-11
## Projeto Final em Ciência de Dados | Grupo 22 | 2025/2026

---

## 📋 ÍNDICE
1. [Semana 8 - Apresentação 5](#semana-8)
2. [Semana 9 - Apresentação 6](#semana-9)
3. [Semana 10 - Apresentação 7](#semana-10)
4. [Semana 11 - Apresentação 8](#semana-11)
5. [Progressão do Projeto](#progressão)
6. [Próximas Etapas](#próximas-etapas)

---

## <a id="semana-8"></a>🔹 SEMANA 8 - Apresentação 5
**Responsável**: Francisco Rosa  
**Data**: 2025  
**Total de Slides**: 12

### 📌 Objetivos da Semana
- Procurar mais fontes de dados climatológicos ou definir rumo a seguir
- Fazer previsão demográfica para 2030
- Utilizar modelo de previsão económica para estimar valores de 2024-2025 em Portugal
- Reavaliar objetivos do projeto

### 🎯 Principais Tarefas Realizadas

#### **Tarefa 1: Análise de Dados IPMA (50% Realizada)**
- **Descrição**: Dataset com dados diários (temperatura máx./mín., precipitação, radiação global)
- **Cobertura**: 18 estações meteorológicas (uma por capital de distrito), período 2010-2024
- **Dificuldades Encontradas**:
  - Grande número de valores omissos dependendo do distrito
  - Ex: Viana do Castelo registou radiação global a partir de 2020
  - Viseu sem dados de radiação de 2014-2024
- **Resultados**: Identificados 2 tipos de erros - aleatórios (dias isolados) e sistemáticos (semanas/meses/anos)

#### **Tarefa 2: Transformação e Windowing (90% Realizada)**
- **Estratégia**: Focar em período mais recente (2020-2024) com menos valores omissos
- **Abordagem**: Transformar dados para escala mensal para ignorar erros aleatórios
- **Resultado**: Dataset significativamente reduzido, mas ainda com distritos problemáticos
  - Exemplo: Viseu com 98% de valores omissos

#### **Tarefa 3: Reavaliação dos Objetivos (100% Realizada)**
- **Decisão Importante**: Reorientar projeto para análise da evolução do autoconsumo em Portugal (2022-2025)
- **Justificativa**: Dados adquiridos não contemplam granularidade e completude originalmente idealizada

#### **Tarefa 4: Previsão Demográfica para 2030 (0% Realizada)**
- **Status**: Cancelada após reavaliação dos objetivos

#### **Tarefa 5: Modelo de Previsão Económica (90% Realizada)**
- **Descrição**: Regressão log-linear com efeito por país
- **Objetivo**: Estimar valores para 2024-2025 em Portugal
- **Metodologia**: Aproveitamento de dados de vários países para capturar tendência global
- **Dificuldades**: Limitação no número de anos disponíveis para Portugal
- **Resultados**: 
  - Previsões com erro médio aproximado de 11%
  - Capacidade razoável de generalização

### 🎨 Gráficos/Visualizações Apresentadas
- Resultados de transformações IPMA (gráficos de evolução temporal)
- Planeamento temporal do projeto com estado atual

### 📈 Próximos Objetivos
- Criação e análise de gráficos
- Início da construção do relatório final

---

## <a id="semana-9"></a>🔹 SEMANA 9 - Apresentação 6
**Responsável**: Tiago Woodger  
**Data**: 2025  
**Total de Slides**: 20

### 📌 Objetivos da Semana
- Criação e análise de gráficos
- Início da construção do relatório final
- Explorar dados geoespaciais

### 🎯 Principais Tarefas Realizadas

#### **Tarefa 1: Criação de Gráficos para Análise (40% Realizada)**
- **Descrição**: Múltiplos gráficos para estudo do autoconsumo
- **Quantidade**: ~30 gráficos criados, selecionados os mais interessantes
- **Dificuldades**: Gerar variações significativas de gráficos (não repetir análises anteriores)
- **Achado Importante**: 
  - **Braga, Porto, Lisboa, Viseu e Aveiro representam 60% da potência instalada no país**

#### **Tarefa 2: Dados Geoespaciais - Mapa Vetorial (90% Realizada)**
- **Fonte**: Ficheiro pt.json
- **Conteúdo**: Polígonos dos 18 distritos de Portugal Continental + 2 arquipélagos
- **Status**: Utilizado anteriormente, sem dificuldades
- **Utilidade**: Base para análise espacial

#### **Tarefa 3: Dados Geoespaciais - Mapa Raster Solar (40% Realizada)**
- **Tipo**: Grelha com polígonos de potência fotovoltaica (PVOUT)
- **Resolução**: ~1 quilómetro quadrado
- **Dificuldades**: Dados pouco granulares
- **Resultado**: Pode ser dividido por distritos

#### **Tarefa 4: Dados Geoespaciais - Mapa Raster de Construção (10% Realizada)**
- **Método**: Redes neurais em imagens de satélite
- **Conteúdo**: Identificação de telhados
- **Dificuldades**: 
  - Qualidade incerta
  - Grande volume de dados
  - Necessidade de rasterização
- **Função Planeada**: "Máscara" para identificar área/potencial solar útil por distrito

### 🎨 Gráficos/Visualizações Apresentadas (8 slides com gráficos interessantes)
- Análise de potência instalada por distrito
- Distribuição geográfica do autoconsumo
- Múltiplas perspetivas dos dados regionais

### 📈 Próximos Objetivos
- Continuação da criação e análise de gráficos
- Início construção relatório final
- Criação de máscaras dos mapas
- Obter espaço disponível e PVOUT médios por distrito

---

## <a id="semana-10"></a>🔹 SEMANA 10 - Apresentação 7
**Responsável**: Marcos Mestre  
**Data**: 2025  
**Total de Slides**: 17

### 📌 Objetivos da Semana
- Continuação da criação e análise de gráficos
- Processamento dos dados geoespaciais

### 🎯 Principais Tarefas Realizadas

#### **Tarefa 1: Criação de Gráficos para Análise (60% Realizada)**
- **Continuação** da semana anterior
- **Quantidade**: ~25 gráficos adicionais criados
- **Dificuldades**: Continuar a inovar em visualizações
- **Progresso**: Acumulativo com semana anterior (~55 gráficos totais)

#### **Tarefa 2: Processamento de Dados Geoespaciais (95% Realizada)**
- **Objetivo**: Transformar raster de telhados de binário para decimal
- **Escala**: 0 a 1 em incrementos de 0.05
- **Dificuldades**:
  - Testes computacionalmente dispendiosos e demorados
  - Erro em seleção de coordenadas causou desperdiço de tempo
- **Status**: Transformação completada com sucesso

### 🎨 Gráficos/Visualizações Apresentadas
- 7 slides com gráficos interessantes
- 2 slides com dados geoespaciais processados
- Análise visual dos dados de telhados transformados

### 📈 Próximos Objetivos
- Continuação da criação de gráficos
- Continuação do processamento geoespacial
- Transformação de mais pixeis binários para decimais

---

## <a id="semana-11"></a>🔹 SEMANA 11 - Apresentação 8
**Responsável**: Francisco Rosa  
**Data**: 2025  
**Total de Slides**: 19

### 📌 Objetivos da Semana
- Continuação da criação de gráficos
- Continuação do processamento geoespacial
- Exploração de novas fontes de dados

### 🎯 Principais Tarefas Realizadas

#### **Tarefa 1: Criação de Gráficos para Análise (90% Realizada)**
- **Continuação** das semanas anteriores
- **Quantidade**: ~45 gráficos criados
- **Dificuldades**: Gráficos com muita dispersão de dados, sem padrões de interesse
- **Resultado**: Seleção dos mais interessantes após análise
- **Progresso Cumulativo**: ~100 gráficos totais em 3 semanas

#### **Tarefa 2: Descoberta de Nova Fonte de Dados - DBSM (98% Realizada)**
- **Contexto**: Ao tentar reproduzir resultados de um artigo científico
- **Descoberta Importante**: Dataset DBSM foi atualizado com estimativas de potência fotovoltaica por telhado
- **Impacto**: Era exatamente o que o grupo tentava produzir manualmente!
- **Resultado**: Estimativas mais "fiéis" do potencial fotovoltaico por distrito
- **Vantagem**: Economia de tempo e maior precisão

#### **Tarefa 3: Estimativa Rudimentar da Produção Distrital (98% Realizada)**
- **Objetivo**: Estimar proximidade de Portugal/distritos ao seu "potencial"
- **Metodologia**: Usar dados de estações IPMA de capitais de distrito
- **Dificuldades**:
  - Muitos valores omissos em dados IPMA (imputação necessária)
  - Localização de UPACs desconhecida (não considera variações dentro do distrito)
  - Presunção: Todas as UPACs montadas em telhados
- **Resultado**: Estimativas pouco fiéis mas servem para conservar relação de proximidade ao potencial

#### **Tarefa 4: Estimativa de Potencial Conseguido (98% Realizada)**
- **Cálculo**: Produção de UPACs / Potencial de painéis em telhados
- **Dificuldades**: Impossibilidade de estimativas confiantes da produção de UPACs
- **Resultados Principais**:
  - **Melhor desempenho**: Braga com 4.2% do potencial
  - **Pior desempenho**: Bragança com 1.4% do potencial
  - Dados importantes para comparação regional

### 🎨 Gráficos/Visualizações Apresentadas
- Gráficos retificados vs. gráficos sem interesse
- 1 slide com gráficos interessantes de dados geoespaciais
- Comparação visual de desempenho por distrito

### 📈 Próximos Objetivos
- Consolidação das conclusões
- Início da escrita do Relatório Final
- Passagem de responsabilidade para Tiago Woodger

---

## <a id="progressão"></a>📈 PROGRESSÃO DO PROJETO - SÍNTESE GERAL

### Evolução por Semana

| Aspeto | Semana 8 | Semana 9 | Semana 10 | Semana 11 |
|--------|----------|----------|-----------|-----------|
| **Foco Principal** | Análise IPMA; Reavaliação | Gráficos; Dados Geoespaciais | Processamento Geoespacial | Novas Fontes; Estimativas |
| **Gráficos** | - | ~30 criados | +25 criados | +45 criados |
| **Total Acumulado** | - | 30 | ~55 | ~100 |
| **Estado Geoespacial** | Não iniciado | Exploração (10-90%) | Processamento (95%) | Análise (98%) |
| **Relatório** | Planeado | Iniciado | Continuação | Consolidação |

### Principais Conquistas

1. **Reorientação Estratégica**: De análise climatológica para análise de autoconsumo
2. **Análise Abrangente**: ~100 gráficos criados para visualização de dados
3. **Dados Geoespaciais**: Integração de 3 fontes de dados geoespaciais
4. **Nova Fonte**: Descoberta de DBSM com estimativas pré-calculadas
5. **Métricas Regionais**: Mapeamento de desempenho por distrito (Braga 4.2% vs Bragança 1.4%)
6. **Automatização**: Processamento de rasters para análise espacial

### Desafios Superados

- ❌ Dados IPMA incompletos → ✅ Transformação temporal (2020-2024)
- ❌ Complexidade geoespacial → ✅ Integração múltiplas fontes
- ❌ Estimativas manuais → ✅ Descoberta de DBSM com dados pré-computados
- ❌ Dispersão em gráficos → ✅ Seleção e refinamento visual

---

## <a id="próximas-etapas"></a>🚀 PRÓXIMAS ETAPAS IDENTIFICADAS

### Imediatas (Relatório Final)
1. **Consolidação de Conclusões**
   - Síntese dos 100+ gráficos
   - Integração de análises geoespaciais
   - Métricas de desempenho por distrito

2. **Escrita do Relatório Final**
   - Estrutura: Introdução → Metodologia → Análise → Conclusões
   - Inclusão de visualizações-chave
   - Documentação de decisões e limitações

3. **Apresentação Final**
   - Guião baseado na progressão das 8 semanas
   - Destaque para descobertas principais
   - Comparação do potencial vs. realidade por distrito

### Melhorias Potenciais
- Localização exata de UPACs para estimativas mais precisas
- Imputação mais sofisticada de dados IPMA
- Análise temporal de evolução do autoconsumo
- Projeções futuras com modelos de machine learning

---

## 📝 INFORMAÇÕES DO GRUPO

**Membros**:
- 123418 - Francisco Rosa
- 123385 - Tiago Woodger
- 123436 - Marcos Mestre

**Rotação de Responsáveis**:
- Semana 8: Francisco Rosa
- Semana 9: Tiago Woodger
- Semana 10: Marcos Mestre
- Semana 11: Francisco Rosa
- Próxima: Tiago Woodger

---

**Documento Gerado**: Resumo das Apresentações Semanais (Semanas 8-11)  
**Projeto**: Análise de Autoconsumo em Portugal | Ciência de Dados 2025/2026
