# 🍕 PizzaCRM Analytics

Sistema completo de CRM, Analytics e Ativação para Pizzarias em Delivery.

**Funcionalidades principais:**
- 📊 Segmentação automática de clientes (RFV + K-Means)
- 📈 Cálculo de propensão à compra com knowledge injection Galunion
- 💬 Gerador de mensagens WhatsApp/E-mail personalizadas
- 📋 Mesa de ativação com filtros dinâmicos
- 📈 Análise de ROI e comparação de cohorts

---

## 🚀 Quick Start

### 1. Instalação

```bash
# Clone ou navegue para o diretório
cd CRM_PIZZARIA

# Instale as dependências
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
streamlit run main.py
```

A aplicação abrirá no navegador em `http://localhost:8501`

---

## 📁 Estrutura de Arquivos

```
CRM_PIZZARIA/
├── main.py                    # Aplicação Streamlit (interface)
├── analytics_engine.py        # Motor de segmentação RFV + propensão
├── communication.py           # Gerador de mensagens personalizadas
├── roi_calculator.py          # Cálculo de ROI e análise de cohort
├── requirements.txt           # Dependências Python
├── PRD.md                     # Documento de requisitos
└── README.md                  # Este arquivo
```

---

## 📊 Como Usar

### Seção A: Analytics 📊

1. **Carregue uma base de dados** (CSV ou Excel) na barra lateral
2. Clique em **"Processar Base"**
3. Visualize:
   - KPIs resumidos (clientes, ticket médio, frequência, receita em risco)
   - Distribuição por cluster (gráfico pizza)
   - Scatter plot RFV (Recência vs Frequência vs Valor)
   - Score de Propensão à Compra
   - Heatmap de correlação

**Arquivos de exemplo esperados:**
```
Unidade, Criado em, Nome, E-mail, CPF, DDD, Telefone, Aniversário, DtCriacao,
Pedidos, Total, Último pedido, Valor, DtUltimoPedido, HorarioPedido,
[Opcionais: Ticket, Recencia(R), Frequencia, Valor(V), TempoCasa, MesAniver, Engajamento, MediaPedido, Fidelidade]
```

### Seção B: Mesa de Ativação 📋

1. Selecione a seção **"Mesa de Ativação"**
2. Aplique filtros:
   - **Cluster** (multi-select)
   - **Score de Propensão** (range)
   - **Mês de Aniversário** (multi-select)
3. Visualize a tabela interativa com sugestões de oferta
4. Baixe os dados em CSV

**Sugestões de Oferta Automáticas:**
- **Campeões**: VIP Exclusivo
- **Fiéis Ticket Baixo**: Combo Premium 20% OFF (se flag upsell) ou Frete Grátis
- **Em Risco**: Oferta Surprise 15% OFF (se ticket alto) ou Brinde
- **Adormecidos**: Desconto 25% OFF (reativação agressiva)

### Seção C: Comunicação 💬

1. Selecione a seção **"Comunicação"**
2. Escolha:
   - **Cluster** para ativar
   - **Score de Propensão mínima**
   - **Canal**: WhatsApp ou E-mail
3. Edite o template (variáveis: `{nome}`, `{oferta}`, `{dias_sem_comprar}`, `{tempo_casa}`)
4. Visualize preview das mensagens
5. **Gere links wa.me** para WhatsApp ou **payloads JSON** para E-mail

**Links WhatsApp gerados:**
```
https://wa.me/55[DDD][TELEFONE]?text=[MENSAGEM_URL_ENCODED]
```

**Payloads E-mail** podem ser enviados via Webhook a um serviço de automação.

### Seção D: ROI & Cohort 📈

1. Selecione a seção **"ROI & Cohort"**
2. Carregue **Base T1** (antes da ação) e **Base T2** (depois da ação)
3. Indique o **custo da campanha** (opcional)
4. Clique em **"Analisar ROI"**
5. Visualize:
   - **Impacto de Receita**: Crescimento total, per capita, churn
   - **Movimentos entre Clusters**: Taxa de melhoria/degradação
   - **ROI Final**: Lucro líquido e % de retorno

---

## 🔍 Detalhes Técnicos

### Analytics Engine

**Processamento de dados:**
1. **Limpeza**: Remoção de duplicatas, normalização de tipos, tratamento de nulos
2. **Feature Engineering**: Cálculo de RFV, tempo_casa, media_dias_pedido, etc
3. **Segmentação RFV**: K-Means com 4 clusters (Campeões, Fiéis Ticket Baixo, Em Risco, Adormecidos)
4. **Score de Propensão**: Heurística + ML com knowledge injection Galunion
   - Benchmarks: Ticket esperado, frequência saudável, ceiling por perfil
   - Flags de anomalia: Upsell opportunity, risco alto, super engajado

**Validação:**
- Outliers (pedidos > 365/mês)
- Clientes inativos (>180 dias sem comprar)
- Cobertura de dados

### Communication Engine

**Templates dinâmicos** por cluster com variáveis:
- `{nome}`: Nome do cliente
- `{oferta}`: Oferta sugerida
- `{dias_sem_comprar}`: Dias desde último pedido
- `{tempo_casa}`: Dias como cliente

**Canais suportados:**
- WhatsApp (links wa.me)
- E-mail (payloads JSON para webhook)

### ROI Calculator

**Análise de cohort:**
1. **Match de clientes**: CPF ou E-mail entre T1 e T2
2. **Impacto de Receita**: Crescimento total, per capita, churn
3. **Movimentos de Cluster**: Transições positivas/negativas
4. **Frequência**: Mudança em pedidos médios
5. **ROI**: Lucro / Custo da campanha

---

## 🎯 Casos de Uso

### Caso 1: Identificar Clientes em Risco
1. Vá para **Mesa de Ativação**
2. Filtre por Cluster = "Em Risco"
3. Ordene por Score de Propensão (descending)
4. Vá para **Comunicação** e dispare campanha de reativação

### Caso 2: Oportunidade de Upsell
1. Vá para **Analytics**
2. Procure por clientes com `flag_upsell = True` (Alta Freq + Baixo Ticket)
3. Selecione esses clientes e crie oferta de "Combo Premium"

### Caso 3: Medir ROI de Campanha
1. Vá para **ROI & Cohort**
2. Carregue base ANTES da campanha (T1)
3. Carregue base DEPOIS da campanha (T2)
4. Indique custo (opcional)
5. Veja impacto de receita, clusters movidos, ROI %

---

## 📋 Formatos de Arquivo Aceitos

- **CSV** (.csv): Delimiter automático (`,`, `;` ou `\t`)
- **Excel** (.xlsx, .xls): Primeira sheet

**Colunas obrigatórias (fuzzy matching):**
- Nome do cliente
- Pelo menos **Telefone** OU **E-mail**
- Data de último pedido
- Número de pedidos
- Valor total

**Colunas opcionais (detecção automática):**
- CPF, Aniversário, Horário Pedido, DDD
- Métricas pré-calculadas (RFV, Engajamento, etc)

---

## ⚙️ Configurações

### Número de Clusters
No `analytics_engine.process_complete()`, ajuste `n_clusters`:
```python
df = engine.process_complete(file_path, n_clusters=5)  # Default: 4
```

### Benchmarks Galunion
No `analytics_engine.calculate_propensity()`, customize `benchmark_data`:
```python
benchmark_data = {
    'ticket_esperado_baixo': 60,       # R$
    'ticket_esperado_medio': 120,      # R$
    'freq_esperada_baixo': 12,         # pedidos/mês
    'freq_esperada_medio': 8,
    'freq_esperada_alto': 4,
    'dias_entre_compras_saudavel': 21,
}
```

### Templates de Mensagem
Em `communication.py`, customize `TEMPLATES` por cluster:
```python
TEMPLATES = {
    "Campeões": {
        "whatsapp": "Seu template aqui...",
        "email": "Seu template aqui..."
    },
    ...
}
```

---

## 🐛 Troubleshooting

**"Base carregada: 0 clientes válidos"**
- Verifique se o arquivo tem clientes com Nome preenchido
- Garanta que há **Telefone** OU **E-mail** para cada cliente

**"Colunas de cluster não encontradas"**
- A base precisa ter colunas de Cluster em T1 e T2
- Execute `process_complete()` em ambas as bases antes de fazer ROI

**Variáveis não estão sendo substituídas nas mensagens**
- Verifique a ortografia: `{nome}`, `{oferta}`, `{dias_sem_comprar}`, `{tempo_casa}`
- Case-sensitive!

**Links WhatsApp não funcionam**
- Verifique DDD (2 dígitos) e Telefone (8 dígitos)
- Formato esperado: 11987654321 (sem caracteres especiais)

---

## 📞 Suporte

Para dúvidas ou sugestões:
- Abra uma issue no repositório
- Entre em contato: thyagoapo@gmail.com

---

## 📝 Licença

Este projeto é fornecido como-é para fins educacionais e comerciais.

---

**🍕 Desenvolvido com ❤️ para Pizzarias em Delivery**  
*Versão 1.0 | Abril 2026*
