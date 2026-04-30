#!/bin/bash

# Script de Inicialização Automática - PizzaCRM Analytics
# Tudo que você precisa fazer é executar este arquivo!

echo "🍕 PizzaCRM Analytics - Inicializando..."
echo ""

# Entrar na pasta
cd /root/CRM_PIZZARIA

# Criar virtual environment se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar virtual environment
echo "✅ Ativando ambiente..."
source venv/bin/activate

# Instalar dependências se não foram instaladas
if ! pip show streamlit > /dev/null 2>&1; then
    echo "📥 Instalando dependências (pode levar alguns minutos)..."
    pip install -r requirements.txt
fi

# Parar qualquer Streamlit anterior
echo "🛑 Parando apps anteriores..."
pkill -f streamlit 2>/dev/null

# Esperar um pouco
sleep 2

# Iniciar Streamlit
echo ""
echo "🚀 Iniciando PizzaCRM Analytics..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ APP INICIADO COM SUCESSO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Acesse no navegador:"
echo "   http://seu_ip_vps:8501"
echo ""
echo "📌 Troque 'seu_ip_vps' pelo IP da sua VPS"
echo "   (você encontra no painel Hostinger)"
echo ""
echo "🔄 Para parar a app, feche este terminal ou pressione Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Rodar Streamlit (em foreground para visualizar logs)
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
