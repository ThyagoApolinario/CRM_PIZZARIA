"""
ROI Calculator - Cálculo de ROI e Análise de Impacto de Campanhas
Compara duas bases em momentos diferentes (T1 e T2) para medir resultado de ações
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


class ROICalculator:
    """Motor de cálculo de ROI e análise de impacto"""

    def __init__(self):
        self.df_t1 = None  # Base em T1 (antes)
        self.df_t2 = None  # Base em T2 (depois)
        self.matched_customers = None

    def load_cohort_data(self, file_t1: str, file_t2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Carrega duas bases de dados para análise de cohort
        """
        try:
            if file_t1.endswith('.csv'):
                df_t1 = pd.read_csv(file_t1)
            else:
                df_t1 = pd.read_excel(file_t1)

            if file_t2.endswith('.csv'):
                df_t2 = pd.read_csv(file_t2)
            else:
                df_t2 = pd.read_excel(file_t2)

            # Normalizar colunas
            df_t1.columns = df_t1.columns.str.lower().str.strip()
            df_t2.columns = df_t2.columns.str.lower().str.strip()

            self.df_t1 = df_t1
            self.df_t2 = df_t2

            print(f"✅ Base T1 carregada: {len(df_t1)} clientes")
            print(f"✅ Base T2 carregada: {len(df_t2)} clientes")

            return df_t1, df_t2

        except Exception as e:
            print(f"❌ Erro ao carregar arquivos: {e}")
            return None, None


    def match_customers(
        self,
        df_t1: pd.DataFrame,
        df_t2: pd.DataFrame,
        match_key: str = 'telefone_ddd'
    ) -> pd.DataFrame:
        """
        Faz match de clientes entre T1 e T2 por DDD+Telefone (chave única)

        Retorna DataFrame com colunas [nome, cluster_t1, cluster_t2, ...]
        """

        # Normalizar colunas de match
        if match_key == 'telefone_ddd' or match_key == 'telefone':
            # Criar chave única DDD+Telefone
            if 'ddd' in df_t1.columns and 'telefone' in df_t1.columns:
                df_t1['_chave_match'] = df_t1['ddd'].astype(str) + '-' + df_t1['telefone'].astype(str)
            if 'ddd' in df_t2.columns and 'telefone' in df_t2.columns:
                df_t2['_chave_match'] = df_t2['ddd'].astype(str) + '-' + df_t2['telefone'].astype(str)
            match_cols = '_chave_match'
        elif match_key == 'email':
            match_cols = 'email'
        else:
            match_cols = ['email', 'telefone']  # Multi-key fallback

        if isinstance(match_cols, str):
            # Merge simples por uma chave
            merged = pd.merge(
                df_t1,
                df_t2,
                on=match_cols,
                how='inner',
                suffixes=('_t1', '_t2')
            )
        else:
            # Merge por múltiplas chaves
            merged = pd.merge(
                df_t1,
                df_t2,
                on=match_cols,
                how='inner',
                suffixes=('_t1', '_t2')
            )

        self.matched_customers = merged

        print(f"\n🔗 Match de clientes:")
        print(f"   - Clientes únicos em T1: {len(df_t1)}")
        print(f"   - Clientes únicos em T2: {len(df_t2)}")
        print(f"   - Clientes matchados: {len(merged)}")
        print(f"   - Taxa de retenção: {len(merged) / len(df_t1) * 100:.1f}%")

        return merged


    def analyze_cluster_movement(self, merged_df: pd.DataFrame) -> Dict:
        """
        Analisa transição de clientes entre clusters

        Exemplo:
            T1: "Em Risco" → T2: "Campeões" = Sucesso!
            T1: "Campeões" → T2: "Em Risco" = Falha
        """

        # Verificar se temos colunas de cluster
        cluster_cols = [col for col in merged_df.columns if 'cluster' in col.lower()]

        if len(cluster_cols) < 2:
            print("⚠️ Colunas de cluster não encontradas. Análise interrompida.")
            return {}

        # Identificar colunas T1 e T2
        cluster_t1_col = next((col for col in cluster_cols if '_t1' in col), None)
        cluster_t2_col = next((col for col in cluster_cols if '_t2' in col), None)

        if not cluster_t1_col or not cluster_t2_col:
            print("⚠️ Colunas de cluster T1 e T2 não identificadas.")
            return {}

        # Criar tabela de transição
        transition_matrix = pd.crosstab(
            merged_df[cluster_t1_col],
            merged_df[cluster_t2_col],
            margins=True
        )

        # Calcular movimentos positivos/negativos
        movements = {
            'positivos': 0,
            'negativos': 0,
            'mantidos': 0,
            'transicoes': []
        }

        # Ranking de qualidade de clusters (exemplo)
        cluster_ranking = {
            "Campeões": 4,
            "Fiéis Ticket Baixo": 3,
            "Em Risco": 2,
            "Adormecidos": 1
        }

        for idx, row in merged_df.iterrows():
            t1 = row[cluster_t1_col]
            t2 = row[cluster_t2_col]

            rank_t1 = cluster_ranking.get(t1, 0)
            rank_t2 = cluster_ranking.get(t2, 0)

            if t1 == t2:
                movements['mantidos'] += 1
            elif rank_t2 > rank_t1:
                movements['positivos'] += 1
                movements['transicoes'].append({
                    'cliente': row.get('nome', 'N/A'),
                    'de': t1,
                    'para': t2,
                    'tipo': 'positivo'
                })
            else:
                movements['negativos'] += 1
                movements['transicoes'].append({
                    'cliente': row.get('nome', 'N/A'),
                    'de': t1,
                    'para': t2,
                    'tipo': 'negativo'
                })

        result = {
            'transition_matrix': transition_matrix.to_dict(),
            'movimentos_positivos': movements['positivos'],
            'movimentos_negativos': movements['negativos'],
            'mantidos': movements['mantidos'],
            'taxa_melhoria': movements['positivos'] / len(merged_df) * 100 if len(merged_df) > 0 else 0,
            'taxa_degradacao': movements['negativos'] / len(merged_df) * 100 if len(merged_df) > 0 else 0,
            'transicoes_exemplo': movements['transicoes'][:5]  # Top 5
        }

        print(f"\n📊 Análise de Movimentos entre Clusters:")
        print(f"   - Positivos (melhoria): {movements['positivos']} ({result['taxa_melhoria']:.1f}%)")
        print(f"   - Negativos (degradação): {movements['negativos']} ({result['taxa_degradacao']:.1f}%)")
        print(f"   - Mantidos no mesmo cluster: {movements['mantidos']}")

        return result


    def calculate_revenue_impact(self, merged_df: pd.DataFrame) -> Dict:
        """
        Calcula impacto de receita entre T1 e T2

        Métricas:
        - Receita total T1 vs T2
        - Crescimento per capita
        - Churn de receita (clientes que reduziram gasto)
        """

        # Identificar colunas de valor
        valor_cols = [col for col in merged_df.columns if any(x in col.lower() for x in ['valor', 'total', 'receita'])]

        valor_t1_col = next((col for col in valor_cols if '_t1' in col), None)
        valor_t2_col = next((col for col in valor_cols if '_t2' in col), None)

        # Fallback
        if not valor_t1_col:
            valor_t1_col = 'valor_t1' if 'valor_t1' in merged_df.columns else 'total_t1'
        if not valor_t2_col:
            valor_t2_col = 'valor_t2' if 'valor_t2' in merged_df.columns else 'total_t2'

        if valor_t1_col not in merged_df.columns or valor_t2_col not in merged_df.columns:
            print(f"⚠️ Colunas de valor não encontradas: {valor_t1_col}, {valor_t2_col}")
            return {}

        # Cálculos
        receita_t1 = merged_df[valor_t1_col].sum()
        receita_t2 = merged_df[valor_t2_col].sum()
        crescimento_absoluto = receita_t2 - receita_t1
        crescimento_pct = (crescimento_absoluto / receita_t1 * 100) if receita_t1 > 0 else 0

        # Per capita
        crescimento_per_capita = merged_df[valor_t2_col].mean() - merged_df[valor_t1_col].mean()

        # Clientes que aumentaram vs diminuíram gasto
        merged_df['delta_valor'] = merged_df[valor_t2_col] - merged_df[valor_t1_col]
        clientes_crescimento = (merged_df['delta_valor'] > 0).sum()
        clientes_reducao = (merged_df['delta_valor'] < 0).sum()

        # Churn de receita (redução > 20%)
        merged_df['churn_receita'] = merged_df['delta_valor'] / merged_df[valor_t1_col].replace(0, 1) < -0.2
        churn_receita_clientes = merged_df['churn_receita'].sum()

        result = {
            'receita_t1': receita_t1,
            'receita_t2': receita_t2,
            'crescimento_absoluto': crescimento_absoluto,
            'crescimento_percentual': crescimento_pct,
            'crescimento_per_capita': crescimento_per_capita,
            'clientes_aumentaram_gasto': clientes_crescimento,
            'clientes_reduziram_gasto': clientes_reducao,
            'taxa_aumento_gasto': clientes_crescimento / len(merged_df) * 100 if len(merged_df) > 0 else 0,
            'churn_receita_clientes': churn_receita_clientes,
        }

        print(f"\n💰 Análise de Impacto de Receita:")
        print(f"   - Receita T1: R$ {receita_t1:,.2f}")
        print(f"   - Receita T2: R$ {receita_t2:,.2f}")
        print(f"   - Crescimento: R$ {crescimento_absoluto:,.2f} ({crescimento_pct:.1f}%)")
        print(f"   - Crescimento per capita: R$ {crescimento_per_capita:.2f}")
        print(f"   - Clientes que aumentaram gasto: {clientes_crescimento} ({result['taxa_aumento_gasto']:.1f}%)")
        print(f"   - Churn de receita (>20% redução): {churn_receita_clientes}")

        return result


    def calculate_frequency_impact(self, merged_df: pd.DataFrame) -> Dict:
        """
        Calcula mudança em frequência de compras
        """

        # Identificar colunas de frequência/pedidos
        freq_cols = [col for col in merged_df.columns if any(x in col.lower() for x in ['pedidos', 'frequencia', 'compras'])]

        freq_t1_col = next((col for col in freq_cols if '_t1' in col), None)
        freq_t2_col = next((col for col in freq_cols if '_t2' in col), None)

        if not freq_t1_col or not freq_t2_col:
            freq_t1_col = 'pedidos_t1' if 'pedidos_t1' in merged_df.columns else None
            freq_t2_col = 'pedidos_t2' if 'pedidos_t2' in merged_df.columns else None

        if not freq_t1_col or not freq_t2_col:
            print("⚠️ Colunas de frequência não encontradas.")
            return {}

        freq_t1 = merged_df[freq_t1_col].mean()
        freq_t2 = merged_df[freq_t2_col].mean()
        delta_freq = freq_t2 - freq_t1

        result = {
            'frequencia_media_t1': freq_t1,
            'frequencia_media_t2': freq_t2,
            'delta_frequencia': delta_freq,
            'delta_pct': (delta_freq / freq_t1 * 100) if freq_t1 > 0 else 0,
        }

        print(f"\n📈 Análise de Impacto em Frequência:")
        print(f"   - Frequência média T1: {freq_t1:.1f} pedidos")
        print(f"   - Frequência média T2: {freq_t2:.1f} pedidos")
        print(f"   - Delta: {delta_freq:.1f} pedidos ({result['delta_pct']:.1f}%)")

        return result


    def calculate_roi(
        self,
        file_t1: str,
        file_t2: str,
        custo_campanha: float = 0.0,
        match_key: str = 'telefone_ddd'
    ) -> Dict:
        """
        Pipeline completo de cálculo de ROI

        Retorna dicionário com todos os indicadores
        """

        print("\n🚀 Iniciando cálculo de ROI...\n")

        # Load
        df_t1, df_t2 = self.load_cohort_data(file_t1, file_t2)
        if df_t1 is None or df_t2 is None:
            return {}

        # Match
        merged = self.match_customers(df_t1, df_t2, match_key)

        # Análises
        cluster_impact = self.analyze_cluster_movement(merged)
        revenue_impact = self.calculate_revenue_impact(merged)
        frequency_impact = self.calculate_frequency_impact(merged)

        # ROI final
        roi = {
            'cluster_impact': cluster_impact,
            'revenue_impact': revenue_impact,
            'frequency_impact': frequency_impact,
            'custo_campanha': custo_campanha,
        }

        # Calcular ROI monetário
        if revenue_impact:
            lucro = revenue_impact.get('crescimento_absoluto', 0) - custo_campanha
            roi['roi_percentual'] = (lucro / custo_campanha * 100) if custo_campanha > 0 else None
            roi['lucro_liquido'] = lucro

            print(f"\n💵 ROI da Campanha:")
            if custo_campanha > 0:
                print(f"   - Custo: R$ {custo_campanha:,.2f}")
                print(f"   - Lucro: R$ {lucro:,.2f}")
                print(f"   - ROI: {roi['roi_percentual']:.1f}%")
            else:
                print(f"   - Receita incremental: R$ {revenue_impact.get('crescimento_absoluto', 0):,.2f}")

        print(f"\n✅ Análise de ROI completa!")

        return roi
