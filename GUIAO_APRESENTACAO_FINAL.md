# 🎯 GUIÃO PARA APRESENTAÇÃO FINAL
## Projeto: Análise de Autoconsumo em Portugal | Grupo 22

---

## ESTRUTURA SUGERIDA PARA A APRESENTAÇÃO FINAL

### I. INTRODUÇÃO (2-3 slides)
- **Slide 1: Capa**
  - Título do projeto
  - Nomes dos elementos
  - Data

- **Slide 2: Objetivos Gerais**
  - Análise da evolução do autoconsumo em Portugal (2022-2025)
  - Identificação de distritos com melhor/pior desempenho
  - Estimativa de potencial fotovoltaico vs. realidade

- **Slide 3: Cronograma de Trabalho**
  - Mostrar a progressão de 8 semanas
  - Indicar reavaliação no meio do projeto

---

### II. METODOLOGIA (3-4 slides)

- **Slide 4: Fontes de Dados Utilizadas**
  - IPMA: Dados climatológicos (temperatura, precipitação, radiação)
  - Geoespaciais: Mapas vetoriais e rasters
  - DBSM: Estimativas de potência fotovoltaica por telhado
  - Dados de UPACs e produção energética

- **Slide 5: Transformações de Dados - IPMA**
  - Tratamento de valores omissos
  - Windowing temporal (2020-2024)
  - Agregação mensal para reduzir erros aleatórios
  - Antes/Depois: visualização da qualidade dos dados

- **Slide 6: Processamento Geoespacial**
  - Integração de pt.json (mapa vetorial)
  - Processamento de rasters (telhados, radiação solar)
  - Transformação binária → decimal
  - Criação de máscaras por distrito

- **Slide 7: Modelo de Análise**
  - Estimativa de produção distrital baseada em IPMA
  - Cálculo: Potencial Conseguido = Produção Real / Potencial Teórico
  - Limitações: Localização de UPACs, presunções

---

### III. ANÁLISE E RESULTADOS (10-12 slides)

#### A. Análise de Autoconsumo por Distrito (3-4 slides)

- **Slide 8: Destaque - 5 Distritos Principais**
  - Gráfico: Braga, Porto, Lisboa, Viseu e Aveiro = **60% da potência instalada**
  - Implicação: Estes serão o foco principal

- **Slide 9: Distribuição Geográfica**
  - Mapa interativo (se possível) ou gráfico com densidade
  - Correlações: região costeira vs interior; norte vs sul

- **Slide 10: Evolução Temporal (2022-2025)**
  - Crescimento do autoconsumo por ano
  - Tendência de aceleração ou desaceleração
  - Previsão para 2026 (opcional)

- **Slide 11: Comparação Regional**
  - Mapa de calor com desempenho por distrito
  - Identificação de clusters e outliers

#### B. Desempenho vs. Potencial (2-3 slides)

- **Slide 12: Potencial Teórico por Distrito**
  - Usar dados DBSM de radiação solar
  - Mostrar área total disponível de telhados
  - Potência máxima teórica

- **Slide 13: Desempenho Conseguido**
  - **Melhor**: Braga com **4.2%** do potencial
  - **Pior**: Bragança com **1.4%** do potencial
  - Gráfico de ranking dos distritos

- **Slide 14: Gap Analysis**
  - Distância ao potencial por distrito
  - Oportunidade de crescimento identificada
  - Insights sobre barreiras ao crescimento

#### C. Análise Geoespacial (2-3 slides)

- **Slide 15: Mapas de Radiação Solar**
  - Visualização de PVOUT (potência fotovoltaica) por distrito
  - Identificação de áreas com maior potencial

- **Slide 16: Densidade de Telhados**
  - Mapa de construção processado
  - Correlação com áreas urbanas vs rurais

- **Slide 17: Sobreposição de Layers**
  - Cruzamento: Telhados disponíveis + Radiação solar
  - Identificação de zonas de máximo potencial

---

### IV. INSIGHTS E CONCLUSÕES (3-4 slides)

- **Slide 18: Principais Descobertas**
  1. Forte concentração de autoconsumo em 5 distritos
  2. Grande lacuna entre potencial e realidade (95.8% de potencial não aproveitado em Bragança)
  3. Variabilidade regional significativa (4.2% vs 1.4%)
  4. Dados de radiação solar favorecem regiões do interior

- **Slide 19: Fatores Limitantes Identificados**
  - Dados IPMA com valores omissos
  - Desconhecimento de localização exata de UPACs
  - Variações micro-climáticas não capturadas
  - Fatores sócio-económicos não analisados

- **Slide 20: Oportunidades Futuras**
  - Expandir análise a outros períodos
  - Incluir dados de radiação mais granulares
  - Integrar informações de custos/incentivos por distrito
  - Machine learning para previsões mais sofisticadas
  - Análise de tendências de investimento

- **Slide 21: Contribuições do Projeto**
  - Identificação de regiões com elevado potencial não aproveitado
  - Framework para análise regional de autoconsumo
  - Integração de dados climatológicos e geoespaciais

---

### V. ENCERRAMENTO (1-2 slides)

- **Slide 22: Referências e Fontes de Dados**
  - IPMA
  - DBSM
  - pt.json (Mapa vetorial de Portugal)
  - Dataset de UPACs

- **Slide 23: Obrigado / Perguntas**
  - Contact info se necessário

---

## RECOMENDAÇÕES DE VISUALIZAÇÕES-CHAVE

### Gráficos Essenciais (do acervo de ~100 gráficos criados)
1. ✅ **Potência instalada por distrito** (Top 5: Braga, Porto, Lisboa, Viseu, Aveiro)
2. ✅ **Distribuição geográfica** (Mapa de Portugal com cores por intensidade)
3. ✅ **Evolução temporal** (Linha com crescimento 2022-2025)
4. ✅ **Desempenho vs Potencial** (Gráfico de barras: % alcançado)
5. ✅ **Ranking de distritos** (Braga 4.2% vs Bragança 1.4%)
6. ✅ **Potencial de Radiação Solar** (Mapa PVOUT)
7. ✅ **Densidade de Telhados** (Mapa de construção)
8. ✅ **Gap Analysis** (Dispersão: distância ao potencial)

### Elementos Visuais Sugeridos
- Mapas interativos (se ferramentas permitirem)
- Gráficos com gradiente de cores por desempenho
- Time-lapse de evolução (se aplicável)
- Comparações lado-a-lado (potencial vs real)

---

## SUGESTÕES PARA APRESENTAÇÃO

### Narrativa Recomendada
1. **Abertura**: "Portugal tem um potencial enorme de autoconsumo solar, mas..."
2. **Desenvolvimento**: Mostrar dados da realidade vs. potencial
3. **Clímax**: Revelar os números de desempenho por distrito
4. **Conclusão**: Chamar atenção para oportunidades de crescimento

### Timing Sugerido (15-20 minutos)
- Introdução: 2 min
- Metodologia: 3 min
- Resultados/Análise: 10 min
- Conclusões: 2 min
- Q&A: 3 min

### Dicas Presentacionais
- ✅ Começar com o contexto: "Portugal quer ser carbono-neutro até 2050"
- ✅ Humanizar os dados: "Em Braga, apenas 4.2% do potencial está sendo aproveitado"
- ✅ Usar o contraste: Braga vs Bragança (3x diferença)
- ✅ Terminar com call-to-action: "Oportunidades de crescimento de 95%+"
- ✅ Antever questões: Preparar respostas sobre limitações de dados

---

## ANOTAÇÕES POR MEMBRO DO GRUPO

### Francisco Rosa (Responsável Semana 8 e 11)
- Trabalhou na reavaliação dos objetivos
- Processou dados económicos e descuberta de DBSM
- Estimativas de produção distrital
- **Ponto forte para apresentação**: Evolução estratégica e descobertas

### Tiago Woodger (Responsável Semana 9)
- Iniciou exploração geoespacial
- Criou base de ~30 gráficos iniciais
- Explorou múltiplas fontes de dados
- **Ponto forte para apresentação**: Amplitude de fontes e criatividade em visualizações

### Marcos Mestre (Responsável Semana 10)
- Processamento técnico de dados geoespaciais
- Transformação de rasters
- Otimizações computacionais
- **Ponto forte para apresentação**: Aspeto técnico e processamento de dados

---

## CHECKLIST PRÉ-APRESENTAÇÃO FINAL

- [ ] Verificar todos os dados e números (especialmente: Braga 4.2%, Bragança 1.4%)
- [ ] Testar funcionamento de todos os gráficos/mapas interativos
- [ ] Preparar versão impressa com melhor resolução
- [ ] Ensaiar transições entre slides
- [ ] Preparar respostas para possíveis perguntas:
  - "Por que Braga tem melhor desempenho?"
  - "Como afetam as limitações de IPMA os resultados?"
  - "Qual é a projeção para 2030?"
  - "Como este estudo pode ser aplicado praticamente?"
- [ ] Sincronizar apresentação entre membros
- [ ] Verificar compatibilidade de ficheiros
- [ ] Ter backup digital e físico

---

**Documento Preparado para**: Apresentação Final do Projeto  
**Grupo**: 22 | **Curso**: Licenciatura em Ciência de Dados 2025/2026  
**Baseado em**: Análise de apresentações das semanas 8-11
