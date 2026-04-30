# 🚀 Melhorias no Módulo de Comunicação

## 📋 Resumo das Melhorias

O módulo de comunicação foi completamente refatorado para ser mais robusto, flexível e fácil de usar. As principais melhorias incluem:

---

## 1️⃣ Sistema de Template Dinâmico Aprimorado

### ✨ Novo método `generate_dynamic_template()`
- **Antes:** Retornava apenas uma string de template
- **Depois:** Retorna um Dict com:
  ```python
  {
      "template": "Template com placeholders",
      "preview": "Template com variáveis substituídas",
      "metadata": {
          "cluster": "Campeões",
          "canal": "whatsapp",
          "tipo_oferta": "desconto",
          "nivel_recencia": "recente",
          "blocos_usados": {
              "saudacao": "Oi {nome}! 👑",
              "gancho": "Que ótimo ter você ativo!",
              "oferta": "Aproveite: {oferta}",
              "cta": "Pede já!",
              "fechamento": "Um beijo,\nEquipe PizzaCRM 🍕"
          }
      }
  }
  ```

### 📊 Composição Transparente
- Visualize exatamente quais blocos foram selecionados
- Entenda como o template foi montado
- Facilita debugging e ajustes

---

## 2️⃣ Validação Robusta de Templates

### ✓ Novo método `validar_template()`
```python
validacao = ce.validar_template("{nome}, aproveite {oferta}!")
# Retorna:
{
    "valido": True,
    "variaveis_encontradas": ["nome", "oferta"],
    "variaveis_faltando": [],
    "comprimento": 40
}
```

**Benefícios:**
- Identifica variáveis faltando antes de enviar
- Valida comprimento da mensagem
- Evita erros de formato

---

## 3️⃣ Aplicação de Variáveis com Fallback

### 🛡️ Novo método `_aplicar_variaveis_ao_template()`
- Aplica variáveis com **tratamento inteligente de erros**
- Se faltar variável, usa placeholder `[variavel_faltando]`
- Nunca quebra a mensagem por falta de dados

**Exemplo:**
```python
template = "Olá {nome}, você faz parte do cluster {cluster}!"
# Se 'cluster' não for fornecido:
# Resultado: "Olá João, você faz parte do cluster [cluster]!"
```

---

## 4️⃣ Detecção Inteligente de Tipo de Oferta

### 🎯 Melhor reconhecimento de ofertas
Antes detectava apenas 4 tipos. Agora detecta:

| Tipo | Keywords Reconhecidas |
|------|----------------------|
| **frete_gratis** | frete, grátis, gratis, shipment |
| **brinde** | brinde, present, surpresa, gift |
| **bundle** | combo, bundle, kit, set |
| **desconto** | desconto, discount, %, off |

Exemplo:
```python
ce._detectar_tipo_oferta("Frete grátis!")  # → "frete_gratis"
ce._detectar_tipo_oferta("Gift card de R$50")  # → "brinde"
```

---

## 5️⃣ Novo Parâmetro `usar_dinamico`

### 🤖 Escolha entre 3 modos de template

#### Modo 1: **Padrão** (usar_dinamico=False, template_custom=None)
- Usa template fixo do cluster
- Rápido e consistente
- Bom para campanhas padrão

#### Modo 2: **Customizado** (template_custom="seu_template")
- Usa seu template personalizado
- Máxima flexibilidade
- Requer validação manual

#### Modo 3: **Dinâmico** (usar_dinamico=True)
- Monta template combinando blocos
- Oferece variação natural
- Determinístico (mesmo cliente = mesmo template)

```python
# Exemplo uso nos 3 modos:
msg1 = ce.format_whatsapp_message(..., usar_dinamico=False)
msg2 = ce.format_whatsapp_message(..., template_custom="Oi {nome}!")
msg3 = ce.format_whatsapp_message(..., usar_dinamico=True)
```

---

## 6️⃣ Novo Método `comparar_templates()`

### 📊 Compare múltiplos templates lado a lado
```python
templates = [
    {
        "nome_template": "Padrão",
        "template": "Oi {nome}...",
        "nome": "João",
        "oferta": "15% desc",
        "dias": 30
    },
    {
        "nome_template": "Dinâmico",
        "dinamico": True,
        "nome": "João",
        "oferta": "15% desc",
        "dias": 30
    }
]

comparacao = ce.comparar_templates(templates)
# Retorna: comprimento, preview, validação para cada um
```

**Útil para:**
- A/B testing de templates
- Escolher melhor versão antes de enviar
- Validar todos os templates de uma vez

---

## 7️⃣ Novo Método `listar_templates_disponiveis()`

### 📚 Visualize todos os templates por cluster
```python
templates = ce.listar_templates_disponiveis()
# Retorna Dict com preview de todos os templates
# Por cluster e por canal (whatsapp/email)
```

---

## 8️⃣ Suporte a Variáveis Customizadas

### 🎨 Passe variáveis adicionais para templates
```python
resultado = ce.generate_dynamic_template(
    nome="João",
    cluster="Campeões",
    dias_sem_comprar=5,
    oferta="15% desc",
    variáveis_custom={
        "endereco": "Rua das Flores",
        "promo_code": "PIZZA20",
        "data_validade": "31/12/2024"
    }
)
```

Agora você pode usar `{endereco}`, `{promo_code}`, etc. nos templates!

---

## 9️⃣ Retorno Estruturado de Métodos

### 📦 Todos os métodos agora retornam Dicts estruturados

**Antes:**
```python
msg = ce.format_whatsapp_message(...)
# Retornava: {"mensagem": "...", "comprimento": 150}
```

**Depois:**
```python
msg = ce.format_whatsapp_message(..., usar_dinamico=True)
# Retorna:
{
    "mensagem": "...",
    "comprimento": 150,
    "tipo": "dinamico",  # ← novo!
    "metadata": {...}     # ← novo!
}
```

---

## 🔟 Interface Streamlit Aprimorada

### ✨ Novas Funcionalidades na UI

1. **Checkbox para Template Dinâmico**
   - Alterne entre template padrão e dinâmico com 1 clique

2. **Checkbox para Validação**
   - Veja automaticamente se o template é válido
   - Identifique variáveis faltando

3. **Checkbox para Comparação**
   - Compare padrão vs customizado lado a lado
   - Veja comprimento e validação de cada um

4. **Expandir para ver Composição**
   - Veja cada bloco usado na montagem dinâmica
   - Entendar as escolhas do algoritmo

5. **Badges de Tipo de Template**
   - Cada preview mostra se é "padrao", "custom" ou "dinamico"

---

## 🎯 Exemplos de Uso

### Exemplo 1: Gerar Template Dinâmico Simples
```python
from communication import CommunicationEngine

ce = CommunicationEngine()

resultado = ce.generate_dynamic_template(
    nome="Maria Silva",
    cluster="Adormecidos",
    dias_sem_comprar=90,
    oferta="25% de desconto",
    canal="whatsapp"
)

print(resultado["preview"])
# Output: 
# Oi Maria! 👋
#
# Muito tempo sem você por aqui!
#
# Aproveite: 25% de desconto
#
# Corre que não dura!
#
# Um beijo,
# Equipe PizzaCRM 🍕
```

### Exemplo 2: Validar e Comparar Templates
```python
# Validar
validacao = ce.validar_template("{nome}, aproveite {oferta}!")
print(f"Válido: {validacao['valido']}")

# Comparar 3 templates
comparacao = ce.comparar_templates([
    {"nome_template": "T1", "template": "{nome} + {oferta}", ...},
    {"nome_template": "T2", "template": "Oi {nome}...", ...},
    {"nome_template": "T3", "dinamico": True, ...},
])

for tpl in comparacao["templates"]:
    print(f"{tpl['nome']}: {tpl['comprimento']} chars")
```

### Exemplo 3: Usar com Variáveis Customizadas
```python
resultado = ce.format_whatsapp_message(
    nome="Pedro",
    oferta="Combo especial",
    dias_sem_comprar=15,
    cluster="Fiéis Ticket Baixo",
    usar_dinamico=True
)

# Resultado já tem 'mensagem', 'tipo', 'metadata'
print(resultado['tipo'])  # "dinamico"
print(resultado['metadata']['tipo_oferta'])  # "bundle"
```

---

## 📈 Benefícios da Refatoração

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Flexibilidade** | 1 opção | 3 opções (padrão/custom/dinâmico) |
| **Segurança** | Pode quebrar | Nunca quebra (com fallback) |
| **Visibilidade** | Caixa preta | Transparente com metadata |
| **Tipos de Oferta** | 4 | 4+ (com reconhecimento melhor) |
| **Validação** | Nenhuma | Completa |
| **Comparação** | Manual | Automática com `comparar_templates()` |
| **Suporte a Vars** | Fixas | Customizadas |
| **Retorno** | String/Dict simples | Dict estruturado |

---

## 🚀 Próximos Passos Sugeridos

1. **Testes A/B**: Use `comparar_templates()` para testar múltiplos templates
2. **Tracking**: Adicione campo para rastrear qual template foi enviado
3. **Analytics**: Correlacione tipo de template com taxa de conversão
4. **Custom Blocks**: Crie novos blocos de oferta específicos para sua pizzaria
5. **ML**: Implemente seleção automática de blocos baseada em histórico

---

## 📝 Changelog

### v2.0 (Atual)
- ✨ Sistema de template dinâmico aprimorado
- ✅ Validação robusta com fallback
- 🤖 Novo parâmetro `usar_dinamico`
- 📊 Método `comparar_templates()`
- 🎯 Melhor detecção de tipo de oferta
- 🛡️ Tratamento inteligente de erros
- 📦 Retorno estruturado com metadata
- 🎨 Suporte a variáveis customizadas

---

## 💡 Dúvidas Comuns

**P: Qual modo devo usar?**
R: Comece com dinâmico (`usar_dinamico=True`) para variação. Se precisar controle total, use customizado.

**P: O template dinâmico é aleatório?**
R: Não! É determinístico. Mesmo cliente sempre gera mesmo template (baseado em hash do nome).

**P: Posso adicionar meus próprios blocos?**
R: Sim! Edite o dicionário `BLOCOS` na classe `CommunicationEngine`.

**P: E se a variável não existir no template?**
R: Não quebra! O método `_aplicar_variaveis_ao_template()` usa placeholder `[var_faltando]`.

---

**Versão:** 2.0  
**Data:** 2026-04-30  
**Status:** ✅ Pronto para Produção
