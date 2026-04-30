"""
Análise detalhada dos 56 registros removidos
Por qual motivo cada um foi excluído?
"""

import pandas as pd
import numpy as np

file_path = "/tmp/MilanWabiz_300426.xlsx"

# Carrega bruto
df_bruto = pd.read_excel(file_path)

# Normaliza colunas
df = df_bruto.copy()
df.columns = [col.lower().strip() for col in df.columns]

# Detectar coluna de valor
col_valor = None
if 'total' in df.columns:
    col_valor = 'total'
elif 'valor' in df.columns:
    col_valor = 'valor'

col_pedidos = 'pedidos' if 'pedidos' in df.columns else None

print("\n" + "="*80)
print("ANÁLISE DOS 56 REGISTROS REMOVIDOS (338 → 282)")
print("="*80)

print(f"\n📥 BASE BRUTA: {len(df_bruto)} registros")

# ===== REMOÇÃO 1: PEDIDOS <= 0 =====
print(f"\n1️⃣  VALIDAÇÃO: Pedidos <= 0")
print("-" * 80)

if col_pedidos:
    df[col_pedidos] = pd.to_numeric(df[col_pedidos], errors='coerce')

    # Encontrar removidos
    removidos_pedidos = df[df[col_pedidos].fillna(0) <= 0]
    print(f"   Registros encontrados: {len(removidos_pedidos)}")

    if len(removidos_pedidos) > 0:
        print(f"\n   Distribuição de Pedidos inválidos:")
        print(f"   ├─ Pedidos = 0: {(removidos_pedidos[col_pedidos] == 0).sum()}")
        print(f"   ├─ Pedidos < 0: {(removidos_pedidos[col_pedidos] < 0).sum()}")
        print(f"   └─ Pedidos = NaN: {removidos_pedidos[col_pedidos].isna().sum()}")

        print(f"\n   📋 Exemplos de clientes removidos:")
        for idx, (i, row) in enumerate(removidos_pedidos.head(5).iterrows()):
            nome = row.get('nome', 'N/A')
            pedidos = row.get(col_pedidos, 'NaN')
            valor = row.get(col_valor, 0) if col_valor else 'N/A'
            print(f"      {idx+1}. {nome}")
            print(f"         └─ {pedidos} pedidos, valor: {valor}")

# ===== REMOÇÃO 2: VALOR <= 0 =====
print(f"\n2️⃣  VALIDAÇÃO: Valor Total <= 0")
print("-" * 80)

# Primeiro remove os com pedidos inválidos
df_after_pedidos = df[df[col_pedidos].fillna(0) > 0].copy() if col_pedidos else df.copy()

if col_valor:
    df_after_pedidos[col_valor] = pd.to_numeric(df_after_pedidos[col_valor], errors='coerce')

    removidos_valor = df_after_pedidos[df_after_pedidos[col_valor].fillna(0) <= 0]
    print(f"   Registros encontrados: {len(removidos_valor)}")

    if len(removidos_valor) > 0:
        print(f"\n   Distribuição de Valor inválido:")
        print(f"   ├─ Valor = 0: {(removidos_valor[col_valor] == 0).sum()}")
        print(f"   ├─ Valor < 0: {(removidos_valor[col_valor] < 0).sum()}")
        print(f"   └─ Valor = NaN: {removidos_valor[col_valor].isna().sum()}")

        if len(removidos_valor) > 0:
            print(f"\n   📋 Exemplos de clientes removidos:")
            for idx, (i, row) in enumerate(removidos_valor.head(5).iterrows()):
                nome = row.get('nome', 'N/A')
                pedidos = row.get(col_pedidos, 'N/A') if col_pedidos else 'N/A'
                valor = row.get(col_valor, 'NaN')
                print(f"      {idx+1}. {nome}")
                print(f"         └─ {pedidos} pedidos, valor: {valor}")

# ===== REMOÇÃO 3: OUTLIERS DE VALOR =====
print(f"\n3️⃣  VALIDAÇÃO: Outliers Extremos de Valor")
print("-" * 80)

df_after_valor = df_after_pedidos[df_after_pedidos[col_valor].fillna(0) > 0].copy() if col_valor else df_after_pedidos.copy()

if col_valor and len(df_after_valor) > 0:
    Q1 = df_after_valor[col_valor].quantile(0.25)
    Q3 = df_after_valor[col_valor].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + (3 * IQR)

    print(f"   Quartil 1 (Q1): R$ {Q1:,.2f}")
    print(f"   Quartil 3 (Q3): R$ {Q3:,.2f}")
    print(f"   IQR (Q3-Q1): R$ {IQR:,.2f}")
    print(f"   Limite Superior (Q3 + 3×IQR): R$ {limite_superior:,.2f}")

    removidos_outlier = df_after_valor[df_after_valor[col_valor] > limite_superior]
    print(f"\n   Registros acima do limite: {len(removidos_outlier)}")

    if len(removidos_outlier) > 0:
        print(f"\n   📋 Clientes OUTLIER removidos:")
        for idx, (i, row) in enumerate(removidos_outlier.iterrows()):
            nome = row.get('nome', 'N/A')
            valor = row.get(col_valor, 0)
            pedidos = int(row.get(col_pedidos, 0)) if col_pedidos and pd.notna(row.get(col_pedidos)) else 'N/A'
            percentual_acima = ((valor - limite_superior) / limite_superior * 100)
            print(f"      {idx+1}. {nome}")
            print(f"         └─ R$ {valor:,.2f} ({pedidos} pedidos) | {percentual_acima:+.1f}% acima do limite")
else:
    removidos_outlier = pd.DataFrame()
    limite_superior = 0

# ===== RESUMO FINAL =====
print(f"\n" + "="*80)
print("RESUMO FINAL")
print("="*80)

total_removido = len(removidos_pedidos) + len(removidos_valor) + len(removidos_outlier)

print(f"\n   338 (bruto)")
print(f"   │")
print(f"   ├─ -{len(removidos_pedidos)} (Pedidos ≤ 0) → {len(df) - len(removidos_pedidos)}")
print(f"   │")
print(f"   ├─ -{len(removidos_valor)} (Valor ≤ 0) → {len(df_after_pedidos) - len(removidos_valor)}")
print(f"   │")
print(f"   ├─ -{len(removidos_outlier)} (Outliers extremos)")
print(f"   │")
print(f"   └─ = {len(df_after_valor) - len(removidos_outlier)} registros válidos")

print(f"\n   ✅ TOTAL REMOVIDO: {total_removido} registros ({total_removido/338*100:.1f}%)")

# ===== ANÁLISE: DEVERIA REMOVER MESMO? =====
print(f"\n" + "="*80)
print("ANÁLISE: ESSAS REMOÇÕES FAZEM SENTIDO?")
print("="*80)

print(f"""
❓ PEDIDOS = 0 ({len(removidos_pedidos)} removidos):
   ✅ CORRETO remover!
   Motivo: São contatos cadastrados mas que NUNCA fizeram pedido
   Solução: Melhorar qualidade de cadastro (CRM) para evitar contatos inválidos

❓ VALOR = 0 ({len(removidos_valor)} removidos):
   ✅ CORRETO remover! (se houver)
   Motivo: Pedidos registrados mas sem pagamento = dados incorretos

❓ OUTLIERS EXTREMOS ({len(removidos_outlier)} removidos acima de R$ {limite_superior:,.2f}):
   ⚠️  QUESTIONÁVEL - Depende da sua estratégia!

   Argumentos PARA remover:
   ✓ Evita distorção nas análises RFV
   ✓ Facilita segmentação equilibrada
   ✓ Pode ser erro de digitação/teste

   Argumentos CONTRA remover:
   ✗ Clientes de alto valor SÃO seu negócio principal!
   ✗ Merecem análise e atenção especial
   ✗ Não são erros, são oportunidades

📊 RECOMENDAÇÃO PARA PIZZARIA:
   1. ✅ Manter removição de Pedidos=0 (dados de teste/inválidos)
   2. ✅ Manter removição de Valor=0 (dados inconsistentes)
   3. ⚠️  CONSIDERAR: Não remover outliers - criar cluster "VIP" especial!

   Esses {len(removidos_outlier)} clientes gastaram muito com você.
   Não deveria ignorá-los na análise, deveria celebrá-los!
""")

print("="*80 + "\n")
