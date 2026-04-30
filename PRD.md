# PRD - Sistema de CRM e Analytics para Pizzaria em Delivery

## 1. Visão Geral do Produto

**Nome**: PizzaCRM Analytics  
**Objetivo**: Segmentar base de clientes de pizzaria, calcular propensão à compra e ativar campanhas personalizadas via WhatsApp/E-mail.  
**Público-alvo**: Operadores de marketing e gestores de pizzarias (delivery)  
**MVP**: Dashboard de análise + Mesa de Ativação + Gerador de WhatsApp  

---

## 2. Especificação de Dados (Data Schema)

### 2.1 Dados de Entrada Requeridos

A aplicação aceita arquivos CSV ou Excel com as seguintes colunas:

#### Bloco A: Demográficos/Cadastro
- `Unidade` (str): Filial/loja
- `Criado em` (date): Data de criação do cadastro
- `Nome` (str): Nome do cliente
- `E-mail` (str): E-mail (nullable)
- `CPF` (str): CPF (nullable, para segmentação futura)
- `DDD` (str): DDD do telefone
- `Telefone` (str): Número do telefone
- `Aniversário` (date): Data de aniversário (nullable)
- `DtCriacao` (date): Data de criação (duplica `Criado em`, será normalizado)

#### Bloco B: Transacionais
- `Pedidos` (int): Número total de pedidos
- `Total` (float): Valor total gasto
- `Último pedido` (date): Data do último pedido
- `Valor` (float): Valor total (duplica `Total`, será normalizado)
- `DtUltimoPedido` (date): Data do último pedido (duplica `Último pedido`)
- `HorarioPedido` (str): Horário médio do pedido (HH:MM, nullable)

#### Bloco C: Métricas Pré-Calculadas (Opcionais/Validadas)
- `Ticket` (float): Ticket médio (será calculado se não houver: `Total / Pedidos`)
- `Recencia(R)` (int): Dias desde último pedido (será calculado)
- `Frequencia` (int): Pedidos por período (será normalizado)
- `Valor(V)` (float): Valor total/agregado (será validado)
- `TempoCasa` (int): Dias desde `Criado em` (será calculado)
- `MesAniver` (int): Mês do aniversário (será extraído)
- `Engajamento` (float): 0-100 (será calculado ou usado)
- `MediaPedido` (float): Dias médios entre pedidos
- `Fidelidade` (float): Score 0-100

---

## 3. Arquitetura Técnica

```
CRM_PIZZARIA/
├── main.py                    # App Streamlit principal
├── analytics_engine.py        # Motor de segmentação RFV + propensão
├── communication.py           # Gerador de mensagens WhatsApp/Email
├── roi_calculator.py          # Cálculo de ROI entre cohorts
├── requirements.txt           # Dependências
├── data/
│   ├── base_exemplo.csv       # Arquivo CSV exemplo
│   └── base_marzo.csv         # Arquivo para comparação de cohort
└── README.md                  # Instruções
```

### 3.1 Fluxo de Dados

```
Upload CSV/Excel 
    ↓
[Data Cleaning & Validation] → Tratamento de nulos
    ↓
[Feature Engineering] → Cálculo de R, F, V, TempoCasa, MediaPedido
    ↓
[Segmentação RFV] → K-Means com 4-5 clusters
    ↓
[Score de Propensão] → Regressão Logística (Galunion benchmark)
    ↓
[Dashboard Analytics] → Visualizações interativas
    ↓
[Mesa de Ativação] → Tabela com sugestões de oferta
    ↓
[Comunicação] → Gerador WhatsApp/Email personalizado
```

---

## 4. Motor Analítico: Regras de Negócio

### 4.1 Segmentação RFV (K-Means)

**Variáveis de Entrada**:
- `Recencia(R)`: Dias desde último pedido (normalizado 0-1)
- `Frequencia`: Total de pedidos (normalizado 0-1)
- `Valor(V)`: Valor total gasto (normalizado 0-1)

**Número de Clusters**: 4 (ajustável via Elbow Method)

**Nomes de Clusters** (Atribuição automática baseada em centróides):
- **"Campeões"**: Alta Freq + Alto Valor + Baixa Recência (Recent e leal)
- **"Em Risco"**: Baixa Freq + Médio Valor + Alta Recência (Não retorna)
- **"Adormecidos"**: Muito Alta Recência + Baixa Freq (Abandonados)
- **"Fiéis de Ticket Baixo"**: Alta Freq + Baixo Valor + Baixa Recência (Voltam sempre, mas gastam pouco)

### 4.2 Score de Propensão à Compra (0-100)

**Fórmula Heurística + ML**:

```
score_propensao = f(
    recencia,                    # Quanto mais recente, maior score
    media_pedidos,               # Padrão de frequência
    ticket_medio,                # Valor por pedido
    tempo_casa,                  # Tempo de relacionamento
    benchmark_galunion           # Knowledge injection: padrão setor
)
```

**Regra de Conhecimento Embutida (Galunion/ANR)**:

O mercado de delivery brasileiro ("Alimentação Fora do Lar") apresenta:
- **Ticket médio esperado**: R$ 50-100 (pizzarias)
- **Frequência saudável**: 1 pedido a cada 14-21 dias
- **Ceiling de frequência**: Varia com ticket
  - Ticket < R$ 60: Esperado até 12 pedidos/mês
  - Ticket R$ 60-120: Esperado até 8 pedidos/mês
  - Ticket > R$ 120: Esperado até 4 pedidos/mês

**Anomalias Sinalizadas**:
1. **Upsell Opportunity**: `Frequencia Alta + Ticket Baixo` → Cliente pede frequentemente, mas com pouco valor
2. **Risco Alto**: `Frequencia Baixa + Ticket Médio/Alto` → Cliente de valor, mas parou de comprar
3. **Anomalia Positiva**: `Frequencia Acima do Ceiling` → Cliente super engajado (possível afluência)

### 4.3 Motor de Cohort e Delta (A/B Testing)

**Entrada**: Duas bases de dados em momentos diferentes (ex: Janeiro e Março)

**Processamento**:
1. Match de clientes por CPF ou E-mail/Telefone
2. Classificação em momento T1 (Janeiro): Cluster_T1
3. Classificação em momento T2 (Março): Cluster_T2
4. **Delta**: Cluster_T1 → Cluster_T2

**Relatório de Saída**:
- Nº de clientes que saíram de "Em Risco" → "Campeões" (sucesso!)
- Nº de clientes que desceram em clusters (churn)
- Mudança média no Score de Propensão

---

## 5. Interface do Usuário (Dashboard)

### 5.1 Seção A: Visão Geral (Analytics)

**Componentes**:

1. **KPI Cards** (Top do dashboard):
   - Total de clientes
   - Ticket médio
   - Frequência média
   - Receita em risco (soma de Valor de clientes em "Em Risco")

2. **Gráficos Principais**:
   - **Pizza/Donut Chart**: Distribuição de clientes por Cluster
   - **Scatter Plot (RFV)**: Eixo X = Recência, Eixo Y = Frequência, Tamanho = Valor, Cor = Cluster
   - **Bar Chart**: Receita por Cluster
   - **Heatmap**: Correlação entre R, F, V e Score de Propensão

### 5.2 Seção B: Mesa de Ativação (Actionable Table)

**Funcionalidades**:

1. **Tabela Interativa** com colunas:
   - Nome, Telefone, E-mail, Pedidos, Ticket Médio, Dias sem Comprar, Cluster, Score Propensão

2. **Filtros Dinâmicos**:
   - Por Cluster (Multi-select)
   - Por Score de Propensão (Slider: 0-100)
   - Por Mês de Aniversário
   - Por Status (Ativo/Inativo)

3. **Coluna de Sugestão IA** (Melhor Oferta):
   - **"Frete Grátis"**: Se Recência baixa + Ticket médio (recente, quer voltar)
   - **"Desconto 10%"**: Se Frequência alta + Ticket baixo (fiel, precisa incentivo)
   - **"Brinde na Próxima Compra"**: Se Valor alto + Recência alta (caro, parou)
   - **"Oferta Bundle"**: Se Cluster "Adormecido" (precisa reativação)

### 5.3 Seção C: Módulo de Comunicação (WhatsApp/E-mail)

**Fluxo**:

1. **Seleção de Audiência**:
   - Dropdown para escolher Cluster
   - Opcional: Filtro adicional por Score de Propensão

2. **Preview de Mensagem**:
   - Editor de template com variáveis dinâmicas:
     - `{nome}`, `{dias_sem_comprar}`, `{oferta}`, `{ticket_medio}`, `{tempo_casa}`

3. **Template Pré-Preenchido** (baseado no cluster):
   ```
   Oi {nome}! Faz {dias_sem_comprar} dias que não te vejo por aqui 👀
   Prepare seu paladar porque temos uma oferta especial: {oferta}
   Aproveita agora mesmo! 🍕
   ```

4. **Botão de Ação**:
   - **WhatsApp**: Gera link `wa.me/55[DDD][Telefone]?text=[Mensagem_URL_Encoded]`
   - **E-mail**: Exibe payload JSON para envio via Webhook

5. **Tracker de Envios** (Log):
   - Histórico de campanhas disparadas

---

## 6. Requisitos Técnicos

### 6.1 Tratamento de Dados

- [ ] **Valores nulos**: Telefones vazios → Cliente não ativável (marcado)
- [ ] **Datas inválidas**: Se `DtUltimoPedido` > hoje → Usar `Criado em` como fallback
- [ ] **HorarioPedido**: Se vazio → Usar mediana por Unidade
- [ ] **Duplicatas**: Match por CPF/E-mail (fuzzy match com threshold 80%)
- [ ] **Outliers**: Clientes com `Pedidos > 365` (>1 por dia) → Flag para revisão manual

### 6.2 Funções Obrigatórias

1. `load_and_clean_data(file_path)` → DataFrame limpo
2. `calculate_rfv(df)` → DataFrame com R, F, V
3. `segment_customers(df)` → DataFrame com cluster_id
4. `calculate_propensity(df, benchmark_data)` → DataFrame com score_propensao
5. `suggest_offer(cluster, recency, frequency, value)` → str (nome da oferta)
6. `generate_whatsapp_message(customer, offer_template)` → str (URL wa.me)
7. `calculate_roi(df_t1, df_t2)` → dict com métricas de impacto

### 6.3 Validação de Entrada

- [ ] Arquivo não vazio
- [ ] Colunas requeridas presentes (fuzzy match de nomes)
- [ ] Tipos de dados corretos (inferência automática)
- [ ] Nenhum cliente com `Telefone == None` e `E-mail == None`

---

## 7. Métricas de Sucesso

| Métrica | Target | Descrição |
|---------|--------|-----------|
| **Taxa de Cobertura** | >95% | % de clientes com dados suficientes para segmentação |
| **Silhueta (RFV)** | >0.5 | Qualidade da clusterização K-Means |
| **ROI da Ação** | >0% | Comparação de receita antes/depois de ativação |
| **Taxa de Entregabilidade** | >98% | % de WhatsApp/E-mail válidos |

---

## 8. Roadmap Futuro

1. **Integração WhatsApp API**: Disparo automático vs manual
2. **Attribution Model**: Rastrear qual mensagem gerou qual venda
3. **NLP para Sugestão IA**: Gerar templates customizados por cluster
4. **Previsão de Churn**: ML model para prever quem vai sair
5. **Integração CRM**: Sincronização com Pipedrive/HubSpot

---

**Versão**: 1.0  
**Data**: Abril 2026  
**Autor**: Engenharia de Dados & CRM  
