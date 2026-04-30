"""
Lista dos 17 clientes VIP identificados
"""

import pandas as pd
from analytics_engine import AnalyticsEngine

file_path = "/tmp/MilanWabiz_300426.xlsx"

engine = AnalyticsEngine()
df = engine.process_complete(file_path, n_clusters=4)

if df is not None and '👑 VIP Premium' in df['cluster_nome'].values:
    vips = df[df['cluster_nome'] == '👑 VIP Premium'].sort_values('valor', ascending=False)

    print("\n" + "="*100)
    print("🏆 SEUS 17 CLIENTES VIP PREMIUM")
    print("="*100)

    print(f"\nTotal gasto: R$ {vips['valor'].sum():,.2f}")
    print(f"Ticket médio: R$ {vips['ticket_medio'].mean():.2f}")
    print(f"Pedidos totais: {int(vips['frequencia'].sum())}")

    print("\n" + "-"*100)
    print(f"{'#':<3} {'Nome':<35} {'Gastou':<15} {'Pedidos':<10} {'Dias s/ Compra':<15} {'Propensão':<12}")
    print("-"*100)

    for idx, (i, row) in enumerate(vips.iterrows(), 1):
        nome = str(row.get('nome', 'N/A'))[:32]
        valor = row.get('valor', 0)
        pedidos = int(row.get('frequencia', 0))
        recencia = int(row.get('recencia', 0))
        propensao = row.get('score_propensao', 0)

        print(f"{idx:<3} {nome:<35} R$ {valor:>10,.2f}   {pedidos:>8}     {recencia:>12} dias  {propensao:>10.1f}%")

    print("-"*100)

    print("\n📊 ANÁLISE VIP:")
    print(f"  • Representam: {len(vips)/len(df)*100:.1f}% dos clientes")
    print(f"  • Geram: R$ {vips['valor'].sum():,.2f} ({vips['valor'].sum()/df['valor'].sum()*100:.1f}% da receita)")
    print(f"  • Média de gasto: R$ {vips['valor'].mean():,.2f}")
    print(f"  • Ofertas sugeridas: {vips['oferta_sugerida'].unique()}")

    print("\n🎯 ESTRATÉGIA RECOMENDADA:")
    print("""
    1. ✅ Mantenha comunicação EXCLUSIVA com esses clientes
    2. ✅ Ofertas personalizadas (não genéricas)
    3. ✅ Atendimento VIP/concierge
    4. ✅ Programas de fidelidade especial
    5. ✅ Eventos exclusivos de clientes
    6. ✅ Aumento de limite de desconto/brindes para retenção
    """)

    print("="*100 + "\n")

else:
    print("❌ Nenhum VIP encontrado ou erro no processamento")
