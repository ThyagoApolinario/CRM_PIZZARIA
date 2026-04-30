# 🚀 Guia de Setup Local - PizzaCRM Analytics

## ⚡ Quick Start (3 Passos)

### 1️⃣ Abra o Terminal

**Windows (PowerShell):**
```powershell
# Abra PowerShell como Administrador
cd seu_caminho_para\CRM_PIZZARIA
```

**Mac/Linux:**
```bash
cd ~/CRM_PIZZARIA
# ou aonde você salvou o projeto
```

### 2️⃣ Execute o Setup

**Windows:**
```powershell
# Criar virtual environment
python -m venv venv

# Ativar
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
# Criar virtual environment
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3️⃣ Rodar a Aplicação

**Windows:**
```powershell
streamlit run main.py
```

**Mac/Linux:**
```bash
streamlit run main.py
```

---

## 📱 Resultado

Você verá no terminal:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://seu_ip:8501
```

**Clique em:** http://localhost:8501

---

## 🔧 Troubleshooting

### Erro: "python: command not found"

**Windows:**
- Use `python` ao invés de `python3`
- Certifique-se que Python está instalado: [python.org](https://www.python.org)

**Mac/Linux:**
- Use `python3` (Python 3 é necessário)
- Instale: `brew install python3` (Mac) ou `apt install python3` (Linux)

### Erro: "pip: command not found"

```bash
# Windows
python -m pip install -r requirements.txt

# Mac/Linux
python3 -m pip install -r requirements.txt
```

### Erro: "No module named 'streamlit'"

Certifique-se que o virtual environment está **ativado**:

**Windows:**
```powershell
.\venv\Scripts\activate
# Deve aparecer (venv) no terminal
```

**Mac/Linux:**
```bash
source venv/bin/activate
# Deve aparecer (venv) no terminal
```

### Erro: "Port 8501 already in use"

Streamlit já está rodando em outro lugar. Escolha outra porta:

```bash
streamlit run main.py --server.port 8502
```

---

## 📊 Testando a Aplicação

1. **Abra no navegador:** http://localhost:8501

2. **Na barra lateral:**
   - Clique em "📁 Dados de Entrada"
   - Carregue um arquivo CSV ou Excel
   - Clique em "🚀 Processar Base"

3. **Explore as seções:**
   - 🔍 Diagnóstico - Análise de qualidade dos dados
   - 📊 Analytics - Visualizações e segmentação
   - 📋 Mesa de Ativação - Filtros e campanhas
   - 💬 Comunicação - **NOVA!** Templates avançados
   - 📈 ROI & Cohort - Análise de impacto

---

## 🛑 Parar a Aplicação

**Terminal:**
- Pressione `Ctrl + C`

**Desativar Virtual Environment:**
```bash
deactivate
```

---

## 💾 Dados de Teste

Se quiser testar com dados da pizzaria, use o arquivo em:
```
CRM_PIZZARIA/data/
```

---

## 📝 Estrutura de Pastas

```
CRM_PIZZARIA/
├── main.py                      # Aplicação principal
├── analytics_engine.py          # Motor de análise
├── communication.py             # ✨ Módulo de templates
├── roi_calculator.py            # Cálculo de ROI
├── requirements.txt             # Dependências
├── venv/                        # Virtual environment (criado no step 2)
├── data/                        # Dados e exemplos
├── .streamlit/                  # Configuração do Streamlit
└── SETUP_LOCAL.md              # Este arquivo
```

---

## 🚀 Próximas Etapas (Opcional)

### Adicionar Dados de Verdade

1. Prepare seu arquivo CSV/Excel com colunas:
   - `nome`
   - `email`
   - `telefone` (sem formatação)
   - `ddd` (2 dígitos)
   - `valor_total` (total gasto)
   - `pedidos` (quantidade de pedidos)
   - `data_ultimo_pedido` (YYYY-MM-DD)

2. Carregue na aplicação via sidebar

### Customizar Ofertas

Edite `communication.py`:
```python
TEMPLATES = {
    "Seu Cluster": {
        "whatsapp": "Seu template aqui {nome}, {oferta}",
        "email": "Email template aqui"
    }
}
```

### Integrar com WhatsApp Business

Para enviar automaticamente (não apenas gerar links):
1. Configure API do WhatsApp Business
2. Use o método `generate_whatsapp_link()` 
3. Adicione integração no código

---

## 💬 Ajuda

Se tiver dúvidas:
1. Verifique o arquivo de log: `app.log`
2. Leia a documentação: `MELHORIAS_COMUNICACAO.md`
3. Teste os módulos individualmente no terminal Python

---

**Status:** ✅ Pronto para Uso Local  
**Última Atualização:** 2026-04-30
