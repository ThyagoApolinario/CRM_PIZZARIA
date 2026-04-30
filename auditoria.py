"""
Script de Auditoria - Rastreia cada registrato removido
Identifica onde os registros estão sumindo entre Diagnóstico e Mesa de Ativação
"""

import pandas as pd
import sys
from analytics_engine import AnalyticsEngine

# ========== PASSO 1: CARREGAMENTO BRUTO ==========
print("\n" + "="*70)
print("AUDITORIA DE REGISTROS")
print("="*70)

file_path = "/tmp/MilanWabiz_300426.xlsx"
df_bruto = pd.read_excel(file_path)

print(f"\n📥 PASSO 1: CARREGAMENTO BRUTO")
print(f"   ├─ Registros: {len(df_bruto)}")
print(f"   ├─ Colunas: {len(df_bruto.columns)}")
print(f"   └─ Colunas: {list(df_bruto.columns)}")

# ========== PASSO 2: O QUE O DIAGNÓSTICO SIMULA ==========
print(f"\n📊 PASSO 2: SIMULAÇÃO DIAGNÓSTICO (VISUAL)")

df_diag = df_bruto.copy()

# Normalizar
df_diag.columns = [col.lower().strip() for col in df_diag.columns]
df_diag = df_diag.loc[:, ~df_diag.columns.duplicated()]
print(f"   ├─ Após normalizar: {len(df_diag)} registros")

# Duplicatas
if 'ddd' in df_diag.columns and 'telefone' in df_diag.columns:
    antes = len(df_diag)
    df_diag['_chave'] = df_diag['ddd'].astype(str) + '-' + df_diag['telefone'].astype(str)
    df_diag = df_diag.drop_duplicates(subset=['_chave'], keep='first')
    df_diag = df_diag.drop(columns=['_chave'])
    removidos = antes - len(df_diag)
    if removidos > 0:
        print(f"   ├─ Após remover duplicatas DDD+Tel: {len(df_diag)} (-{removidos})")

# Limpar espaços
text_cols = ['nome', 'email', 'telefone']
for col in text_cols:
    if col in df_diag.columns:
        df_diag[col] = df_diag[col].astype(str).str.strip()
        df_diag[col] = df_diag[col].replace('', None)
        df_diag[col] = df_diag[col].replace('nan', None)

# Preencher Nome
preenchidos = 0
if 'nome' in df_diag.columns and 'email' in df_diag.columns:
    nome_vazio = df_diag['nome'].isna() | (df_diag['nome'] == '')
    email_valido = df_diag['email'].notna() & (df_diag['email'] != '')
    preenchimento_necessario = nome_vazio & email_valido
    if preenchimento_necessario.sum() > 0:
        df_diag.loc[preenchimento_necessario, 'nome'] = df_diag.loc[preenchimento_necessario, 'email'].str.split('@').str[0]
        preenchidos = preenchimento_necessario.sum()
        print(f"   ├─ Nomes preenchidos com email: +{preenchidos}")

# Remover sem Nome
if 'nome' in df_diag.columns:
    antes = len(df_diag)
    df_diag = df_diag.dropna(subset=['nome'])
    df_diag = df_diag[df_diag['nome'] != ''].reset_index(drop=True)
    removidos = antes - len(df_diag)
    if removidos > 0:
        print(f"   ├─ Após remover sem Nome: {len(df_diag)} (-{removidos})")

# Remover sem Telefone
if 'telefone' in df_diag.columns:
    antes = len(df_diag)
    df_diag = df_diag[df_diag['telefone'].notna()]
    df_diag = df_diag[df_diag['telefone'] != '']
    df_diag = df_diag.reset_index(drop=True)
    removidos = antes - len(df_diag)
    if removidos > 0:
        print(f"   ├─ Após remover sem Telefone: {len(df_diag)} (-{removidos})")

print(f"   └─ RESULTADO DIAGNÓSTICO: {len(df_diag)} registros válidos")

# ========== PASSO 3: O QUE O ANALYTICS FAZ ==========
print(f"\n🔬 PASSO 3: PROCESSAMENTO ANALYTICS")

engine = AnalyticsEngine()
df_analytics = engine.load_and_clean_data(file_path)

if df_analytics is not None:
    print(f"   ├─ Após load_and_clean: {len(df_analytics)} registros")

    # RFV
    df_rfv = engine.calculate_rfv(df_analytics)
    print(f"   ├─ Após RFV: {len(df_rfv)} registros")

    # Segmentação
    df_seg = engine.segment_customers(df_rfv, n_clusters=4)
    print(f"   ├─ Após segmentação: {len(df_seg)} registros")

    # Propensão
    df_prop = engine.calculate_propensity(df_seg)
    print(f"   ├─ Após propensão: {len(df_prop)} registros")

    # Ofertas
    df_oferta = engine.apply_offer_suggestions(df_prop)
    print(f"   └─ Após ofertas: {len(df_oferta)} registros")

    # Relatório
    print(f"\n📋 PASSO 4: RELATÓRIO DE QUALIDADE")
    report = engine.get_quality_report(df_oferta)

    print(f"\n⚠️  PASSO 5: ANÁLISE DE MARCAÇÕES")
    print(f"   ├─ Flagged Outlier: {df_oferta['flagged_outlier'].sum() if 'flagged_outlier' in df_oferta.columns else 0}")
    print(f"   ├─ Inativos: {df_oferta['inativo'].sum() if 'inativo' in df_oferta.columns else 0}")
    print(f"   └─ Total com flags: {(df_oferta['flagged_outlier'].sum() + df_oferta['inativo'].sum()) if 'flagged_outlier' in df_oferta.columns else 0}")

    # ========== PASSO 6: COMPARAÇÃO FINAL ==========
    print(f"\n📊 PASSO 6: COMPARAÇÃO FINAL")
    print(f"   ├─ Bruto (input): {len(df_bruto)}")
    print(f"   ├─ Diagnóstico simula: {len(df_diag)}")
    print(f"   ├─ Analytics processa: {len(df_oferta)}")
    print(f"   ├─ Mesa de Ativação mostra: 152 (conforme relatado)")

    diferenca_diag = len(df_bruto) - len(df_diag)
    diferenca_analytics = len(df_diag) - len(df_oferta)
    diferenca_mesa = len(df_oferta) - 152

    print(f"\n❓ DISCREPÂNCIAS:")
    print(f"   ├─ Bruto → Diagnóstico: {diferenca_diag} removidos")
    print(f"   ├─ Diagnóstico → Analytics: {diferenca_analytics} removidos AQUI!")
    print(f"   └─ Analytics → Mesa: {diferenca_mesa} desaparecidos AQUI!")

    # ========== PASSO 7: INVESTIGAÇÃO PROFUNDA ==========
    print(f"\n🔍 PASSO 7: INVESTIGAÇÃO PROFUNDA")

    if diferenca_mesa > 0:
        print(f"\n   ⚠️  {diferenca_mesa} registros estão em df_oferta mas não na mesa!")
        print(f"   Checando possíveis causas...\n")

        # Verificar inativos
        inativo_count = df_oferta['inativo'].sum() if 'inativo' in df_oferta.columns else 0
        outlier_count = df_oferta['flagged_outlier'].sum() if 'flagged_outlier' in df_oferta.columns else 0

        print(f"   📌 Clientes marcados como INATIVO: {inativo_count}")
        print(f"   📌 Clientes marcados como OUTLIER: {outlier_count}")
        print(f"   📌 TOTAL com flags: {inativo_count + outlier_count}")

        if (inativo_count + outlier_count) == diferenca_mesa:
            print(f"\n   ✅ DESCOBERTA! A mesa de ativação está FILTRANDO esses registros!")
            print(f"      Há um filtro IMPLÍCITO removendo inativos/outliers")
        else:
            print(f"\n   ❓ Não é inativo/outlier. Investigando...")

            # Ver qual cluster está faltando
            print(f"\n   Clusters em df_oferta: {df_oferta['cluster_nome'].value_counts().to_dict()}")

print("\n" + "="*70)
print("FIM DA AUDITORIA")
print("="*70 + "\n")
