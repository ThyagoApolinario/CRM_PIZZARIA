"""
Analytics Engine - Motor de Segmentação RFV, Propensão e Processamento de Dados
Responsável por: Limpeza, Validação, RFV, K-Means, Score de Propensão
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import warnings

warnings.filterwarnings('ignore')


class AnalyticsEngine:
    """Motor central de análise de dados de clientes"""

    def __init__(self):
        self.df = None
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.kmeans_model = None
        self.propensity_model = None
        self.cluster_names = {}

    # ==================== LIMPEZA E VALIDAÇÃO ====================

    def load_and_clean_data(self, file_path):
        """
        Carrega arquivo CSV/Excel e aplica limpeza básica
        """
        try:
            # Detectar formato de forma robusta
            if file_path.endswith('.csv'):
                print(f"   📄 Detectado: CSV")
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                print(f"   📊 Detectado: Excel (.xlsx/.xls)")
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                # Tentar CSV primeiro, depois Excel
                print(f"   🔍 Formato desconhecido, tentando CSV...")
                try:
                    df = pd.read_csv(file_path)
                    print(f"   ✅ Carregado como CSV")
                except Exception as csv_error:
                    print(f"   ❌ Falhou CSV, tentando Excel...")
                    try:
                        df = pd.read_excel(file_path, engine='openpyxl')
                        print(f"   ✅ Carregado como Excel")
                    except Exception as excel_error:
                        raise Exception(f"Não consegui carregar o arquivo. CSV: {csv_error}, Excel: {excel_error}")

            # Normalizar nomes de colunas: lowercase + strip
            new_cols = [col.lower().strip() for col in df.columns]
            df.columns = new_cols

            # Remover colunas duplicadas (manter a primeira)
            df = df.loc[:, ~df.columns.duplicated()]

            # Colunas esperadas (fuzzy mapping)
            col_mapping = {
                'criado em': 'data_criacao',
                'nome': 'nome',
                'e-mail': 'email',
                'email': 'email',
                'cpf': 'cpf',
                'ddd': 'ddd',
                'telefone': 'telefone',
                'aniversário': 'aniversario',
                'aniversario': 'aniversario',
                'dtcriacao': 'data_criacao',
                'pedidos': 'pedidos',
                'total': 'valor_total',
                'valor': 'valor_total',
                'último pedido': 'data_ultimo_pedido',
                'ultimo pedido': 'data_ultimo_pedido',
                'dtultimopedido': 'data_ultimo_pedido',
                'horariopedido': 'horario_pedido',
                'ticket': 'ticket_medio',
                'recencia(r)': 'recencia',
                'recencia': 'recencia',
                'frequencia': 'frequencia',
                'valor(v)': 'valor_total',
                'tempocasa': 'tempo_casa',
                'mesaniver': 'mes_aniversario',
                'engajamento': 'engajamento',
                'mediapedido': 'media_dias_pedido',
                'fidelidade': 'fidelidade',
                'unidade': 'unidade',
            }

            # Renomear colunas com segurança
            rename_dict = {}
            existing_cols = set(df.columns)

            for col_old, col_new in col_mapping.items():
                if col_old in existing_cols and col_new not in existing_cols:
                    rename_dict[col_old] = col_new
                    existing_cols.remove(col_old)
                    existing_cols.add(col_new)

            if rename_dict:
                df = df.rename(columns=rename_dict)

            # Conversão de tipos
            date_cols = ['data_criacao', 'data_ultimo_pedido', 'aniversario']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Converter numéricas
            numeric_cols = ['pedidos', 'valor_total', 'ticket_medio', 'ddd', 'tempo_casa']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Remover duplicatas por DDD + Telefone (chave única)
            if 'ddd' in df.columns and 'telefone' in df.columns:
                df['_chave_unica'] = df['ddd'].astype(str) + '-' + df['telefone'].astype(str)
                df = df.drop_duplicates(subset=['_chave_unica'], keep='first')
                df = df.drop(columns=['_chave_unica'])

            print("\n   🔍 Validando integridade dos dados...")

            # Limpar espaços em branco em colunas texto
            text_cols = ['nome', 'email', 'telefone', 'cpf']
            for col in text_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace('', None)
                    df[col] = df[col].replace('nan', None)

            # Preencher Nome vazio usando Email (parte antes do @)
            if 'nome' in df.columns and 'email' in df.columns:
                nome_vazio = df['nome'].isna() | (df['nome'] == '')
                email_valido = df['email'].notna() & (df['email'] != '')
                preenchimento_necessario = nome_vazio & email_valido

                if preenchimento_necessario.sum() > 0:
                    df.loc[preenchimento_necessario, 'nome'] = df.loc[preenchimento_necessario, 'email'].str.split('@').str[0]
                    print(f"   ℹ️  {preenchimento_necessario.sum()} nomes preenchidos com parte do email")

            # Remover linhas onde Nome está vazio (agora remove apenas quem não tem nome E não tem email)
            antes_nome = len(df)
            if 'nome' in df.columns:
                df = df[df['nome'].notna()]
                df = df[df['nome'] != '']
                df = df.reset_index(drop=True)
            removidos_nome = antes_nome - len(df)
            if removidos_nome > 0:
                print(f"   ❌ Removidos {removidos_nome} registros sem Nome e sem Email")

            # Garantir que temos Telefone (obrigatório para pizzaria delivery)
            antes_tel = len(df)
            if 'telefone' in df.columns:
                df = df[df['telefone'].notna()]
                df = df[df['telefone'] != '']
                df = df.reset_index(drop=True)
            removidos_tel = antes_tel - len(df)
            if removidos_tel > 0:
                print(f"   ❌ Removidos {removidos_tel} registros sem Telefone")

            # ===== VALIDAÇÃO DE DADOS FINANCEIROS =====
            print("\n   💰 Validando dados de valor e pedidos...")

            # Remover registros com Pedidos <= 0
            antes_pedidos = len(df)
            if 'pedidos' in df.columns:
                df = df[df['pedidos'] > 0].reset_index(drop=True)
            removidos_pedidos = antes_pedidos - len(df)
            if removidos_pedidos > 0:
                print(f"   ❌ Removidos {removidos_pedidos} registros com Pedidos <= 0")

            # Remover registros com Valor <= 0
            antes_valor = len(df)
            if 'valor_total' in df.columns:
                df = df[df['valor_total'] > 0].reset_index(drop=True)
            removidos_valor = antes_valor - len(df)
            if removidos_valor > 0:
                print(f"   ❌ Removidos {removidos_valor} registros com Valor <= 0")

            # FLAG outliers extremos (em vez de remover)
            if 'valor_total' in df.columns:
                Q1 = df['valor_total'].quantile(0.25)
                Q3 = df['valor_total'].quantile(0.75)
                IQR = Q3 - Q1
                limite_superior = Q3 + (3 * IQR)

                df['flag_vip_valor'] = df['valor_total'] > limite_superior
                vip_count = df['flag_vip_valor'].sum()
                if vip_count > 0:
                    print(f"   👑 {vip_count} clientes VIP identificados (acima de R$ {limite_superior:,.2f})")

            print(f"\n   ✅ Após validação: {len(df)} clientes com dados íntegros")

            self.df = df
            print(f"✅ Base carregada: {len(df)} clientes válidos")

            return df

        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            return None


    # ==================== FEATURE ENGINEERING ====================

    def calculate_rfv(self, df):
        """
        Calcula Recência, Frequência e Valor
        Também calcula variáveis derivadas: tempo_casa, media_dias_pedido, etc
        """
        df = df.copy()
        today = datetime.now()

        # ---- RECÊNCIA ----
        if 'data_ultimo_pedido' in df.columns:
            df['recencia'] = (today - df['data_ultimo_pedido']).dt.days
            # Tratar nulos: usar tempo_casa como fallback
            if 'tempo_casa' not in df.columns:
                df['tempo_casa'] = (today - df['data_criacao']).dt.days if 'data_criacao' in df.columns else 0
            df['recencia'] = df['recencia'].fillna(df['tempo_casa'])

        # ---- FREQUÊNCIA ----
        if 'pedidos' in df.columns:
            df['frequencia'] = df['pedidos'].fillna(0)
        else:
            df['frequencia'] = 0

        # ---- VALOR ----
        if 'valor_total' in df.columns:
            df['valor'] = df['valor_total'].fillna(0)
        elif 'valor' not in df.columns:
            df['valor'] = 0

        # ---- TICKET MÉDIO ----
        if 'ticket_medio' not in df.columns or df['ticket_medio'].isna().sum() > 0:
            df['ticket_medio'] = df['valor'] / (df['frequencia'] + 1)  # +1 para evitar div by zero
        df['ticket_medio'] = df['ticket_medio'].fillna(0)

        # ---- TEMPO DE CASA ----
        if 'tempo_casa' not in df.columns and 'data_criacao' in df.columns:
            df['tempo_casa'] = (today - df['data_criacao']).dt.days
        df['tempo_casa'] = df['tempo_casa'].fillna(0)

        # ---- MEDIA DIAS ENTRE PEDIDOS ----
        if 'media_dias_pedido' not in df.columns:
            # Se tem frequência e tempo_casa, calcular media_dias_pedido
            df['media_dias_pedido'] = np.where(
                df['frequencia'] > 0,
                df['tempo_casa'] / df['frequencia'],
                df['tempo_casa']
            )
        df['media_dias_pedido'] = df['media_dias_pedido'].fillna(0)

        # ---- MÊS ANIVERSÁRIO ----
        if 'aniversario' in df.columns:
            df['mes_aniversario'] = df['aniversario'].dt.month
        else:
            df['mes_aniversario'] = 0

        # ---- VALIDAÇÃO E LIMPEZA ----
        # Outliers: pedidos impossíveis (>365)
        df['flagged_outlier'] = (df['frequencia'] > 365) | (df['recencia'] < 0)

        # Clientes inativos: mais de 180 dias sem comprar E pouca frequência
        df['inativo'] = (df['recencia'] > 180) & (df['frequencia'] < 3)

        return df


    # ==================== SEGMENTAÇÃO RFV ====================

    def segment_customers(self, df, n_clusters=4):
        """
        Aplica K-Means em R, F, V (normalizados) e nomeia clusters automaticamente
        Identifica e marca clientes VIP de alto valor
        """
        df = df.copy()

        # Preparar features para clustering
        features = df[['recencia', 'frequencia', 'valor']].fillna(0)

        # Normalizar (0-1)
        features_scaled = self.minmax_scaler.fit_transform(features)

        # K-Means
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster_id'] = self.kmeans_model.fit_predict(features_scaled)

        # Nomear clusters automaticamente baseado em centróides
        self._name_clusters(df, n_clusters)
        df['cluster_nome'] = df['cluster_id'].map(self.cluster_names)

        # RECLASSIFICAR CLIENTES VIP (alto valor) para cluster especial
        # Se tem flag_vip_valor, reclassifica independente do cluster RFV
        if 'flag_vip_valor' in df.columns:
            vip_mask = df['flag_vip_valor'] == True
            df.loc[vip_mask, 'cluster_nome'] = '👑 VIP Premium'
            vip_count = vip_mask.sum()
            if vip_count > 0:
                print(f"\n   👑 {vip_count} clientes reclassificados como VIP Premium (independente do RFV)")

        # Estatísticas por cluster
        cluster_stats = df.groupby('cluster_nome').agg({
            'recencia': 'mean',
            'frequencia': 'mean',
            'valor': 'mean',
            'nome': 'count'
        }).rename(columns={'nome': 'tamanho'})

        print(f"\n📊 Segmentação RFV ({n_clusters} clusters + VIP):")
        print(cluster_stats)

        return df


    def _name_clusters(self, df, n_clusters):
        """
        Atribui nomes aos clusters baseado em centróides do K-Means
        Heurística: Combina Recência, Frequência e Valor normalizados
        """
        centroids = self.kmeans_model.cluster_centers_

        cluster_characteristics = []
        for i, centroid in enumerate(centroids):
            r_norm, f_norm, v_norm = centroid
            cluster_characteristics.append({
                'id': i,
                'recencia_norm': r_norm,
                'frequencia_norm': f_norm,
                'valor_norm': v_norm,
                'score': (f_norm + (1 - r_norm) + v_norm) / 3  # Score de qualidade
            })

        # Ordenar por score de qualidade
        cluster_characteristics = sorted(cluster_characteristics, key=lambda x: x['score'], reverse=True)

        # Atribui nomes baseado em ranking
        default_names = [
            "Campeões",           # Top: Alta Freq, Baixa Recência, Alto Valor
            "Fiéis Ticket Baixo", # Segundo: Alta Freq, Baixa Recência, Baixo Valor
            "Em Risco",           # Terceiro: Baixa Freq, Alta Recência, Médio/Alto Valor
            "Adormecidos"         # Último: Baixa Freq, Muito Alta Recência
        ]

        self.cluster_names = {}
        for idx, char in enumerate(cluster_characteristics):
            cluster_id = char['id']
            name = default_names[idx] if idx < len(default_names) else f"Cluster {cluster_id}"
            self.cluster_names[cluster_id] = name


    # ==================== SCORE DE PROPENSÃO ====================

    def calculate_propensity(self, df, benchmark_data=None):
        """
        Calcula Score de Propensão (0-100) usando heurística Galunion + ML

        Lógica:
        - Score base: Função de recência + frequência + ticket
        - Benchmark Galunion: Conhecimento do setor
        - Anomalias: Flag para oportunidades e riscos
        """
        df = df.copy()

        if benchmark_data is None:
            benchmark_data = {
                'ticket_esperado_baixo': 60,       # < R$ 60
                'ticket_esperado_medio': 120,      # R$ 60-120
                'freq_esperada_baixo': 12,         # pedidos/mês para ticket baixo
                'freq_esperada_medio': 8,          # pedidos/mês para ticket médio
                'freq_esperada_alto': 4,           # pedidos/mês para ticket alto
                'dias_entre_compras_saudavel': 21, # dias
            }

        # ---- HEURÍSTICA BASE ----
        # Normalizar componentes
        recencia_norm = 1 - np.clip(df['recencia'] / 365, 0, 1)  # Quanto menor recência, melhor
        frequencia_norm = np.clip(df['frequencia'] / 12, 0, 1)   # Normalizar para ~12 pedidos/mês
        valor_norm = np.clip(df['valor'] / 1000, 0, 1)           # Normalizar para ~R$1000 total

        # Score base (média ponderada)
        weights = {'recencia': 0.3, 'frequencia': 0.4, 'valor': 0.3}
        score_base = (
            weights['recencia'] * recencia_norm +
            weights['frequencia'] * frequencia_norm +
            weights['valor'] * valor_norm
        ) * 100

        # ---- KNOWLEDGE INJECTION (Galunion Benchmark) ----

        # Calcular frequência esperada por ticket
        freq_mensal = df['frequencia'] / np.maximum(df['tempo_casa'] / 30, 1)

        freq_ceiling = np.where(
            df['ticket_medio'] < benchmark_data['ticket_esperado_baixo'],
            benchmark_data['freq_esperada_baixo'],
            np.where(
                df['ticket_medio'] < benchmark_data['ticket_esperado_medio'],
                benchmark_data['freq_esperada_medio'],
                benchmark_data['freq_esperada_alto']
            )
        )

        # Ajustar score por anomalias
        anomaly_boost = np.zeros(len(df))

        # Anomalia Positiva: Frequência acima do ceiling (super engajado!)
        above_ceiling = freq_mensal > freq_ceiling
        anomaly_boost[above_ceiling] += 15

        # Oportunidade de Upsell: Alta frequência, baixo ticket
        low_ticket = df['ticket_medio'] < benchmark_data['ticket_esperado_baixo']
        high_freq = freq_mensal > 4
        df['flag_upsell'] = low_ticket & high_freq
        anomaly_boost[df['flag_upsell']] += 10

        # Risco Alto: Cliente de valor que parou
        high_value = df['valor'] > df['valor'].quantile(0.75)
        stopped = df['recencia'] > benchmark_data['dias_entre_compras_saudavel']
        df['flag_risco_alto'] = high_value & stopped
        anomaly_boost[df['flag_risco_alto']] -= 20

        # Score final
        df['score_propensao'] = np.clip(score_base + anomaly_boost, 0, 100)

        print(f"\n📈 Score de Propensão Calculado:")
        print(f"   - Média: {df['score_propensao'].mean():.1f}")
        print(f"   - Mediana: {df['score_propensao'].median():.1f}")
        print(f"   - Clientes c/ Oportunidade Upsell: {df['flag_upsell'].sum()}")
        print(f"   - Clientes em Risco Alto: {df['flag_risco_alto'].sum()}")

        return df


    # ==================== SUGESTÃO DE OFERTA ====================

    def suggest_offer(self, row):
        """
        Sugere a melhor oferta para um cliente baseado em seu perfil RFV
        """
        cluster = row.get('cluster_nome', '')
        recencia = row.get('recencia', 0)
        frequencia = row.get('frequencia', 0)
        valor = row.get('valor', 0)
        ticket_medio = row.get('ticket_medio', 0)
        score_propensao = row.get('score_propensao', 50)

        # Lógica de sugestão
        if cluster == "👑 VIP Premium":
            return "🏆 Programa VIP Exclusivo"

        elif cluster == "Campeões":
            return "VIP Exclusivo"

        elif cluster == "Fiéis Ticket Baixo":
            if row.get('flag_upsell', False):
                return "Combo Premium 20% OFF"
            else:
                return "Frete Grátis"

        elif cluster == "Em Risco":
            # Usar mediana do dataframe em self.df
            valor_medio = self.df['valor'].median() if self.df is not None else 500
            if valor > valor_medio:
                return "Oferta Surprise 15% OFF"
            else:
                return "Brinde na Próxima"

        elif cluster == "Adormecidos":
            return "Volte! Desconto 25% OFF"

        else:
            if score_propensao > 75:
                return "Frete Grátis"
            elif score_propensao > 50:
                return "Desconto 10%"
            else:
                return "Brinde + Frete"


    def apply_offer_suggestions(self, df):
        """
        Aplica sugestão de oferta para cada cliente
        """
        df['oferta_sugerida'] = df.apply(self.suggest_offer, axis=1)
        return df


    # ==================== VALIDAÇÃO E RELATÓRIO ====================

    def get_quality_report(self, df):
        """
        Retorna relatório de qualidade dos dados e cobertura
        """
        total = len(df)

        report = {
            'total_clientes': total,
            'com_telefone': df['telefone'].notna().sum() if 'telefone' in df.columns else 0,
            'com_email': df['email'].notna().sum() if 'email' in df.columns else 0,
            'com_data_ultimo_pedido': df['data_ultimo_pedido'].notna().sum() if 'data_ultimo_pedido' in df.columns else 0,
            'com_ddd': df['ddd'].notna().sum() if 'ddd' in df.columns else 0,
            'outliers_flagged': df['flagged_outlier'].sum() if 'flagged_outlier' in df.columns else 0,
            'inativos': df['inativo'].sum() if 'inativo' in df.columns else 0,
            'cobertura_segmentacao': (total - df['flagged_outlier'].sum()) / total * 100 if 'flagged_outlier' in df.columns else 100,
        }

        print(f"\n📋 Relatório de Qualidade:")
        print(f"   - Total de clientes: {report['total_clientes']}")
        print(f"   - Com DDD + Telefone: {report['com_telefone']} (Chave única)")
        print(f"   - Com e-mail: {report['com_email']}")
        print(f"   - Com data de último pedido: {report['com_data_ultimo_pedido']}")
        print(f"   - Outliers flagged: {report['outliers_flagged']}")
        print(f"   - Inativos (180+ dias): {report['inativos']}")
        print(f"   - Cobertura: {report['cobertura_segmentacao']:.1f}%")

        return report


    # ==================== PROCESSAMENTO COMPLETO ====================

    def process_complete(self, file_path, n_clusters=4):
        """
        Pipeline completo: Load → Clean → RFV → Segment → Propensity → Offers
        """
        print("\n🚀 Iniciando pipeline de processamento...\n")

        print("\n" + "="*60)
        print("🚀 INICIANDO PIPELINE DE PROCESSAMENTO")
        print("="*60)

        # 1. Load e Clean
        print("\n📥 ETAPA 1: Carregando e limpando dados...")
        df = self.load_and_clean_data(file_path)
        if df is None or df.empty:
            print("❌ Falha no carregamento!")
            return None
        print(f"   ✅ {len(df)} registros após limpeza")

        # 2. RFV
        print("\n📊 ETAPA 2: Calculando RFV (Recência, Frequência, Valor)...")
        df = self.calculate_rfv(df)
        print(f"   ✅ Cálculos de RFV concluídos")

        # 3. Segmentação
        print(f"\n🎯 ETAPA 3: Segmentando {len(df)} clientes em clusters...")
        df = self.segment_customers(df, n_clusters=n_clusters)
        print(f"   ✅ Segmentação concluída")

        # 4. Propensão
        print("\n📈 ETAPA 4: Calculando score de propensão...")
        df = self.calculate_propensity(df)
        print(f"   ✅ Propensão calculada")

        # 5. Sugestões
        print("\n💡 ETAPA 5: Aplicando sugestões de oferta...")
        df = self.apply_offer_suggestions(df)
        print(f"   ✅ Sugestões aplicadas")

        # 6. Relatório
        print("\n📋 ETAPA 6: Gerando relatório de qualidade...")
        self.get_quality_report(df)

        print("\n" + "="*60)
        print("✅ PROCESSAMENTO COMPLETO COM SUCESSO!")
        print("="*60)

        self.df = df
        return df
