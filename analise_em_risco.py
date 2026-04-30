"""
Script para analisar cluster "Em Risco" e descobrir por que está desaparecendo
"""

import pandas as pd
from analytics_engine import AnalyticsEngine

file_path = "/tmp/MilanWabiz_300426.xlsx"

# Processar
engine = AnalyticsEngine()
df = engine.process_complete(file_path, n_clusters=4)

if df is not None:
    print("\n" + "="*70)
    print("ANÁLISE CLUSTER EM RISCO")
    print("="*70)

    print(f"\n📊 Total de clientes processados: {len(df)}")
    print(f"   Clusters: {df['cluster_nome'].value_counts().to_dict()}")

    # Separar Em Risco
    em_risco = df[df['cluster_nome'] == 'Em Risco']
    outros = df[df['cluster_nome'] != 'Em Risco']

    print(f"\n🔴 CLUSTER EM RISCO:")
    print(f"   ├─ Total: {len(em_risco)}")
    print(f"   ├─ Com mes_aniversario: {em_risco['mes_aniversario'].notna().sum()}")
    print(f"   ├─ Sem mes_aniversario: {em_risco['mes_aniversario'].isna().sum()}")
    print(f"   ├─ mes_aniversario = 0: {(em_risco['mes_aniversario'] == 0).sum()}")
    print(f"   └─ Score propensão: min={em_risco['score_propensao'].min():.1f}, max={em_risco['score_propensao'].max():.1f}")

    print(f"\n🟢 OUTROS CLUSTERS:")
    print(f"   ├─ Total: {len(outros)}")
    print(f"   ├─ Com mes_aniversario: {outros['mes_aniversario'].notna().sum()}")
    print(f"   ├─ Sem mes_aniversario: {outros['mes_aniversario'].isna().sum()}")
    print(f"   ├─ mes_aniversario = 0: {(outros['mes_aniversario'] == 0).sum()}")
    print(f"   └─ Score propensão: min={outros['score_propensao'].min():.1f}, max={outros['score_propensao'].max():.1f}")

    # Simular filtros da mesa
    print(f"\n🎯 SIMULANDO FILTROS DA MESA DE ATIVAÇÃO:")

    clusters_unicos = df['cluster_nome'].unique()
    print(f"   Clusters únicos: {list(clusters_unicos)}")

    propensao_range = (0, 100)
    meses = list(range(1, 13))

    # Filtro 1: clusters
    filtro1 = df['cluster_nome'].isin(clusters_unicos)
    print(f"   ├─ Filtro cluster: {filtro1.sum()} clientes")

    # Filtro 2: propensão
    filtro2 = (df['score_propensao'] >= propensao_range[0]) & (df['score_propensao'] <= propensao_range[1])
    print(f"   ├─ Filtro propensão (0-100): {filtro2.sum()} clientes")

    # Filtro 3: mês
    filtro3 = df['mes_aniversario'].isin(meses)
    print(f"   ├─ Filtro mês (1-12): {filtro3.sum()} clientes")
    print(f"   │  └─ Excludos (não em 1-12): {(~filtro3).sum()}")

    # Combinado
    todos_os_filtros = filtro1 & filtro2 & filtro3
    print(f"   └─ RESULTADO (todos os filtros): {todos_os_filtros.sum()} clientes")

    # Quem foi excluído pelo filtro de mês?
    excluidos_mes = df[~filtro3]
    print(f"\n⚠️  CLIENTES EXCLUÍDOS PELO FILTRO DE MÊS:")
    print(f"   ├─ Total excluído: {len(excluidos_mes)}")
    if len(excluidos_mes) > 0:
        print(f"   ├─ Clusters: {excluidos_mes['cluster_nome'].value_counts().to_dict()}")
        print(f"   └─ Valores de mes_aniversario únicos: {excluidos_mes['mes_aniversario'].unique()}")

    # Investigação: por que Em Risco é 130 e mesa mostra 152?
    print(f"\n🔍 INVESTIGAÇÃO DO DESAPARECIMENTO:")
    print(f"   ├─ Em Risco total: {len(em_risco)}")

    em_risco_filtrado = em_risco[todos_os_filtros[em_risco.index]]
    print(f"   ├─ Em Risco após filtros: {len(em_risco_filtrado)}")

    em_risco_excluido = em_risco[~todos_os_filtros[em_risco.index]]
    print(f"   └─ Em Risco EXCLUÍDO: {len(em_risco_excluido)}")

    if len(em_risco_excluido) > 0:
        print(f"\n   Razões da exclusão:")
        print(f"      ├─ Por mês: {(~em_risco['mes_aniversario'].isin(meses)).sum()}")
        print(f"      ├─ Por propensão: {((em_risco['score_propensao'] < 0) | (em_risco['score_propensao'] > 100)).sum()}")
        print(f"      └─ Por cluster: {(~em_risco['cluster_nome'].isin(clusters_unicos)).sum()}")

print("\n" + "="*70 + "\n")
