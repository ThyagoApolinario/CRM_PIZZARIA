# 🚀 Deploy no Streamlit Cloud

## ✨ O que é Streamlit Cloud?

**Streamlit Cloud** é um serviço gratuito da Streamlit que permite deployar sua aplicação direto do GitHub com um único clique.

**Benefícios:**
- ✅ Gratuito para projetos públicos
- ✅ Deploy automático (sempre que você faz push)
- ✅ URL pública (https://seu-app.streamlit.app)
- ✅ Sem configurar servidor
- ✅ HTTPS automático

---

## 📋 Pré-requisitos

1. **Conta GitHub** (com este repositório)
   - ✅ Já tem: https://github.com/ThyagoApolinario/CRM_PIZZARIA

2. **Conta Streamlit** (gratuita)
   - Criar em: https://share.streamlit.io

3. **Código no GitHub**
   - ✅ Já está!

---

## 🎯 Passo a Passo (5 Minutos)

### 1️⃣ Criar Conta Streamlit

1. Acesse: https://share.streamlit.io
2. Clique em **"Sign in with GitHub"**
3. Autorize a conexão com seu GitHub
4. Pronto! ✅

### 2️⃣ Fazer Deploy

1. Na página inicial do Streamlit Cloud, clique em **"New app"**

2. Preencha os campos:
   ```
   Repository:     ThyagoApolinario/CRM_PIZZARIA
   Branch:         main
   Main file path: main.py
   ```

3. Clique em **"Deploy!"**

4. Aguarde (1-3 minutos) enquanto Streamlit instala as dependências

5. Pronto! Sua app está ao vivo! 🎉

---

## 🔗 URL da Sua Aplicação

Após o deploy, você terá uma URL como:

```
https://pizzacrm.streamlit.app
```

(o nome exato depende de como você configurar)

---

## 🔄 Deploy Automático

A partir de agora, **toda vez que você faz push** no GitHub, o Streamlit Cloud automaticamente:

1. ✅ Detecta as mudanças
2. ✅ Instala as dependências (requirements.txt)
3. ✅ Recarrega a aplicação

**Sem fazer nada!** Só fazer push.

```bash
# Seu workflow:
git add .
git commit -m "sua mensagem"
git push origin main

# Streamlit Cloud automaticamente:
# 1. Detecta o push
# 2. Recarrega a app
# 3. Mostra versão nova em 2-5 minutos
```

---

## 📊 Monitorar Deploy

Na página da app no Streamlit Cloud, você verá:

```
✅ App is live!
↻ Deployed XX seconds ago
👁 X views
```

Se houver erro, você pode ver os logs:
- Clique em **"Logs"** no canto superior direito

---

## ⚙️ Configurações Opcionais

### Adicionar Custom Domain

Se tiver um domínio próprio (ex: pizzacrm.com.br):

1. Vá em **App settings** (⚙️)
2. Clique em **Custom domain**
3. Configure seu domínio
4. Siga as instruções de DNS

### Adicionar Secrets (Senhas/APIs)

Se precisar de variáveis secretas (WhatsApp API, banco de dados, etc):

1. Clique em **Secrets** (🔑)
2. Adicione suas variáveis:
   ```toml
   [secrets]
   whatsapp_api_key = "sua_chave_aqui"
   db_password = "sua_senha"
   ```

3. No código, acesse:
   ```python
   import streamlit as st
   
   api_key = st.secrets["whatsapp_api_key"]
   ```

### Limitar Recursos

Se a app ficar lenta:

1. **Aumentar timeout**: Settings → Timeout (padrão 24h)
2. **Cache de dados**: Use `@st.cache_data` nos dados grandes
3. **Limpar cache**: Botão no topo da app (⚙️ → Clear cache)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

✅ **Solução:** Adicione pacotes faltando no `requirements.txt`

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Atualizar requirements"
git push
```

### "App is not responding"

✅ **Solução:**
1. Verifique se `main.py` está rodando sem erros localmente
2. Verifique os **Logs** na página da app
3. Reinicie a app (App → Reboot)

### "Data not loading"

✅ **Solução:**
1. Se usar arquivo local (data/), certifique-se que está no GitHub
2. Use `st.session_state` para cache
3. Aumente timeout se dados forem grandes

### "Port already in use"

✅ **Não é problema no Streamlit Cloud!**
- Só acontece quando rodando localmente
- No cloud, Streamlit gerencia as portas automaticamente

---

## 📈 Compartilhar com Outros

Sua app está público! Compartilhe o link:

```
https://seu-app.streamlit.app
```

Envie para:
- 📧 Email
- 💬 WhatsApp
- 🔗 Slack
- 📱 Redes sociais

Qualquer pessoa pode acessar (sem instalar nada!)

---

## 🔒 Tornar App Privada

Se quiser restringir acesso:

1. Adicione autenticação (ex: Streamlit Cloud Pro)
2. Ou coloque atrás de um proxy autenticado
3. Ou use `.streamlit/config.toml`:
   ```toml
   [client]
   shareMode = "viewer"  # Desabilita compartilhamento
   ```

---

## 📊 Analisar Performance

No Streamlit Cloud, veja métricas:

1. Clique em **"Logs"**
2. Veja:
   - Tempo de carregamento
   - Erros
   - Performance geral

---

## 🚀 Próximas Integrações

Depois do deploy, você pode integrar:

### WhatsApp Automático
```python
# Enviar mensagens direto pelo SDK do WhatsApp
import requests

def enviar_whatsapp(numero, mensagem):
    # Usar API do WhatsApp Business
    requests.post("https://api.whatsapp.com/...", 
                  json={"numero": numero, "texto": mensagem})
```

### Banco de Dados em Nuvem
```python
import sqlite3
# Ou: PostgreSQL, MySQL, MongoDB no cloud
```

### Email Automático
```python
import smtplib
# Enviar emails automáticos
```

---

## 💡 Dicas

1. **Sempre faça teste local antes de fazer push**
   ```bash
   streamlit run main.py
   ```

2. **Mantenha requirements.txt atualizado**
   ```bash
   pip freeze > requirements.txt
   ```

3. **Use `.gitignore` para não commitar dados sensíveis**
   ```
   venv/
   __pycache__/
   .env
   *.log
   data/*.csv  # Opcional: se dados sensíveis
   ```

4. **Monitore os logs regularmente**
   - Clique em "Logs" para ver erros

5. **Use cache para dados grandes**
   ```python
   @st.cache_data
   def carregar_dados():
       return pd.read_csv("data.csv")
   ```

---

## 📱 Status do Seu Deploy

**Repositório:** https://github.com/ThyagoApolinario/CRM_PIZZARIA
**Branch:** main
**Status:** ✅ Pronto para Deploy

---

## 📚 Documentação Oficial

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [GitHub Integration](https://docs.streamlit.io/streamlit-cloud/deploy-your-app)
- [Security & Secrets](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources)

---

## 🎉 Sucesso!

Quando sua app estiver ao vivo no Streamlit Cloud:

1. ✅ Acesse a URL pública
2. ✅ Carregue um arquivo de dados
3. ✅ Veja a análise funcionando
4. ✅ Compartilhe com clientes

**Parabéns! Você conseguiu fazer deploy! 🚀**

---

**Última Atualização:** 2026-04-30  
**Status:** ✅ Pronto para Deploy
