#!/usr/bin/env powershell

# ============================================================================
# PizzaCRM Analytics - Setup Automático (Windows PowerShell)
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         🍕 PizzaCRM Analytics - Setup Automático (Windows)    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonCheck = & where.exe python 2>$null
if (-not $pythonCheck) {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "   Instale em: https://www.python.org" -ForegroundColor Yellow
    Write-Host "   ⚠️  Certifique-se de marcar 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = & python --version 2>&1
Write-Host "   ✅ Encontrado: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Criar virtual environment
Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  Ambiente já existe, pulando..." -ForegroundColor Yellow
} else {
    & python -m venv venv
    Write-Host "   ✅ Ambiente criado" -ForegroundColor Green
}
Write-Host ""

# Ativar virtual environment
Write-Host "✅ Ativando ambiente..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Ambiente ativado" -ForegroundColor Green
Write-Host ""

# Atualizar pip
Write-Host "📥 Atualizando pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip 2>&1 | Out-Null
Write-Host "   ✅ pip atualizado" -ForegroundColor Green
Write-Host ""

# Instalar dependências
Write-Host "📥 Instalando dependências (pode levar 2-3 minutos)..." -ForegroundColor Yellow
& pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Resumo final
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   ✅ SETUP CONCLUÍDO!                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Para rodar a aplicação:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   streamlit run main.py" -ForegroundColor White
Write-Host ""
Write-Host "   Acesse: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
