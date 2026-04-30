#!/bin/bash

# ============================================================================
# PizzaCRM Analytics - Setup Automático (Mac/Linux)
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       🍕 PizzaCRM Analytics - Setup Automático (Mac/Linux)    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Instale em: https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "   ✅ Encontrado: $PYTHON_VERSION"
echo ""

# Criar virtual environment
echo "📦 Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "   ⚠️  Ambiente já existe, pulando..."
else
    python3 -m venv venv
    echo "   ✅ Ambiente criado"
fi
echo ""

# Ativar virtual environment
echo "✅ Ativando ambiente..."
source venv/bin/activate
echo "   ✅ Ambiente ativado"
echo ""

# Atualizar pip
echo "📥 Atualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ pip atualizado"
echo ""

# Instalar dependências
echo "📥 Instalando dependências (pode levar 2-3 minutos)..."
pip install -r requirements.txt
echo "   ✅ Dependências instaladas"
echo ""

# Resumo final
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SETUP CONCLUÍDO!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Para rodar a aplicação:"
echo ""
echo "   source venv/bin/activate"
echo "   streamlit run main.py"
echo ""
echo "   Acesse: http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
