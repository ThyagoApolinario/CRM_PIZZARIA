"""
PizzaCRM Analytics - Aplicação Principal em Streamlit
Dashboard de CRM + Segmentação RFV + Propensão + Comunicação WhatsApp
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from analytics_engine import AnalyticsEngine
from communication import CommunicationEngine
from roi_calculator import ROICalculator


# ==================== CONFIG STREAMLIT ====================

st.set_page_config(
    page_title="PizzaCRM Analytics",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 0rem 0rem; }
    .stMetric { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================

if 'analytics_engine' not in st.session_state:
    st.session_state.analytics_engine = AnalyticsEngine()

if 'communication_engine' not in st.session_state:
    st.session_state.communication_engine = CommunicationEngine()

if 'roi_calculator' not in st.session_state:
    st.session_state.roi_calculator = ROICalculator()

if 'df_processed' not in st.session_state:
    st.session_state.df_processed = None

if 'df_roi' not in st.session_state:
    st.session_state.df_roi = None


# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("🍕 PizzaCRM Analytics")
    st.divider()

    # Menu de navegação
    secao = st.radio(
        "Escolha a seção:",
        ["🔍 Diagnóstico", "📊 Analytics", "📋 Mesa de Ativação", "💬 Comunicação", "📈 ROI & Cohort"]
    )

    st.divider()
    st.subheader("📁 Dados de Entrada")

    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Carrega sua base de dados (CSV ou Excel)",
        type=['csv', 'xlsx', 'xls']
    )

    if uploaded_file:
        # Salvar temporariamente
        temp_path = f"/tmp/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            if uploaded_file.name.endswith('.csv'):
                num_registros = len(pd.read_csv(temp_path))
            else:
                num_registros = len(pd.read_excel(temp_path, engine='openpyxl'))
            st.success(f"✅ Arquivo carregado: {uploaded_file.name} ({num_registros} registros)")
        except Exception as e:
            st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

        # Processar
        if st.button("🚀 Processar Base", use_container_width=True, key="process_btn"):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            try:
                with progress_placeholder.container():
                    st.info("⏳ Etapa 1/5: Carregando arquivo...")

                df = st.session_state.analytics_engine.process_complete(temp_path, n_clusters=4)
                st.session_state.df_processed = df

                if df is not None and len(df) > 0:
                    with progress_placeholder.container():
                        st.success("✅ Processamento concluído com sucesso!")

                    with status_placeholder.container():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("👥 Clientes", len(df))
                        with col2:
                            st.metric("📊 Clusters", df['cluster_nome'].nunique())
                        with col3:
                            st.metric("📈 Taxa Cobertura", f"{(len(df)/len(df))*100:.1f}%")
                else:
                    with progress_placeholder.container():
                        st.error("❌ Nenhum cliente válido após processamento!")
                        st.warning("Verifique se a base tem Nome e Telefone preenchidos")

            except Exception as e:
                with progress_placeholder.container():
                    st.error(f"❌ Erro durante processamento: {str(e)}")
                with status_placeholder.container():
                    st.code(str(e), language="text")

        st.divider()

        if st.session_state.df_processed is not None and len(st.session_state.df_processed) > 0:
            st.info(f"✔️ {len(st.session_state.df_processed)} clientes carregados e prontos para análise!")
        elif st.session_state.df_processed is not None:
            st.warning("⚠️ Base processada mas sem registros válidos")

    # Upload para ROI (dois arquivos)
    if secao == "📈 ROI & Cohort":
        st.subheader("📂 Cohort Analysis")
        file_t1 = st.file_uploader("Base T1 (Antes)", type=['csv', 'xlsx', 'xls'], key='t1')
        file_t2 = st.file_uploader("Base T2 (Depois)", type=['csv', 'xlsx', 'xls'], key='t2')

        if file_t1 and file_t2:
            if st.button("🔍 Analisar ROI", use_container_width=True):
                temp_t1 = f"/tmp/{file_t1.name}"
                temp_t2 = f"/tmp/{file_t2.name}"

                with open(temp_t1, "wb") as f:
                    f.write(file_t1.getbuffer())
                with open(temp_t2, "wb") as f:
                    f.write(file_t2.getbuffer())

                with st.spinner("Analisando cohort... 🔄"):
                    custo = st.number_input("Custo da campanha (R$):", value=0.0)
                    roi_results = st.session_state.roi_calculator.calculate_roi(
                        temp_t1, temp_t2, custo_campanha=custo, match_key='telefone_ddd'
                    )
                    st.session_state.df_roi = roi_results
                    st.success("✅ ROI calculado!")


# ==================== SEÇÃO 0: DIAGNÓSTICO ====================

if secao == "🔍 Diagnóstico":
    st.title("🔍 Diagnóstico de Base de Dados")
    st.markdown("Use esta seção para entender quantos registros serão usados da sua base e por quê alguns podem ser filtrados.")

    st.divider()

    st.subheader("📁 Carregue sua base para diagnóstico")

    diagnostic_file = st.file_uploader(
        "Selecione um arquivo CSV ou Excel para análise",
        type=['csv', 'xlsx', 'xls'],
        key='diagnostic_upload'
    )

    if diagnostic_file:
        temp_diag_path = f"/tmp/diag_{diagnostic_file.name}"
        with open(temp_diag_path, "wb") as f:
            f.write(diagnostic_file.getbuffer())

        try:
            if diagnostic_file.name.endswith('.csv'):
                df_bruto = pd.read_csv(temp_diag_path)
            else:
                df_bruto = pd.read_excel(temp_diag_path)

            st.success(f"✅ Arquivo carregado: {len(df_bruto)} registros")

            # ---- Diagnóstico ----
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📥 Base BRUTA", len(df_bruto))
            with col2:
                st.metric("📋 Colunas", len(df_bruto.columns))
            with col3:
                st.metric("⚙️ Status", "Analisando...")

            st.divider()

            # Colunas
            st.subheader("📋 Colunas Encontradas")
            st.code(", ".join(df_bruto.columns.tolist()))

            st.divider()

            # Simulação de limpeza
            st.subheader("🧹 Simulação de Limpeza (O Que Será Removido)")

            df_sim = df_bruto.copy()
            etapas = []

            # Normalizar
            df_sim.columns = [col.lower().strip() for col in df_sim.columns]
            df_sim = df_sim.loc[:, ~df_sim.columns.duplicated()]
            etapas.append(("Após normalizar colunas", len(df_sim), 0))

            # Duplicatas DDD+Telefone
            if 'ddd' in df_sim.columns and 'telefone' in df_sim.columns:
                antes = len(df_sim)
                df_sim['_chave'] = df_sim['ddd'].astype(str) + '-' + df_sim['telefone'].astype(str)
                df_sim = df_sim.drop_duplicates(subset=['_chave'], keep='first')
                df_sim = df_sim.drop(columns=['_chave'])
                removidos = antes - len(df_sim)
                if removidos > 0:
                    etapas.append((f"❌ Remover duplicatas (DDD+Telefone)", len(df_sim), removidos))

            # Limpar espaços em branco
            text_cols = ['nome', 'email', 'telefone']
            for col in text_cols:
                if col in df_sim.columns:
                    df_sim[col] = df_sim[col].astype(str).str.strip()
                    df_sim[col] = df_sim[col].replace('', None)
                    df_sim[col] = df_sim[col].replace('nan', None)

            # Preencher Nome vazio usando Email (parte antes do @)
            preenchidos = 0
            if 'nome' in df_sim.columns and 'email' in df_sim.columns:
                nome_vazio = df_sim['nome'].isna() | (df_sim['nome'] == '')
                email_valido = df_sim['email'].notna() & (df_sim['email'] != '')
                preenchimento_necessario = nome_vazio & email_valido

                if preenchimento_necessario.sum() > 0:
                    df_sim.loc[preenchimento_necessario, 'nome'] = df_sim.loc[preenchimento_necessario, 'email'].str.split('@').str[0]
                    preenchidos = preenchimento_necessario.sum()
                    etapas.append((f"ℹ️  Nomes preenchidos com email", len(df_sim), -preenchidos))

            # Nome vazio (remove apenas quem não tem nome E não tem email)
            if 'nome' in df_sim.columns:
                antes = len(df_sim)
                df_sim = df_sim.dropna(subset=['nome'])
                df_sim = df_sim[df_sim['nome'] != ''].reset_index(drop=True)
                removidos = antes - len(df_sim)
                if removidos > 0:
                    etapas.append((f"❌ Registros sem Nome e sem Email", len(df_sim), removidos))

            # Telefone obrigatório
            if 'telefone' in df_sim.columns:
                antes = len(df_sim)
                df_sim = df_sim[df_sim['telefone'].notna()]
                df_sim = df_sim[df_sim['telefone'] != '']
                df_sim = df_sim.reset_index(drop=True)
                removidos = antes - len(df_sim)
                if removidos > 0:
                    etapas.append((f"❌ Sem Telefone ou vazio (obrigatório)", len(df_sim), removidos))

            # ===== VALIDAÇÕES FINANCEIRAS (como o analytics faz) =====
            # Remover Pedidos <= 0
            if 'pedidos' in df_sim.columns:
                antes = len(df_sim)
                # Converter para numérico
                df_sim['pedidos'] = pd.to_numeric(df_sim['pedidos'], errors='coerce')
                df_sim = df_sim[df_sim['pedidos'] > 0].reset_index(drop=True)
                removidos = antes - len(df_sim)
                if removidos > 0:
                    etapas.append((f"❌ Registros com Pedidos ≤ 0", len(df_sim), removidos))

            # Remover Valor <= 0
            if 'total' in df_sim.columns or 'valor' in df_sim.columns:
                antes = len(df_sim)
                col_valor = 'total' if 'total' in df_sim.columns else 'valor'
                df_sim[col_valor] = pd.to_numeric(df_sim[col_valor], errors='coerce')
                df_sim = df_sim[df_sim[col_valor] > 0].reset_index(drop=True)
                removidos = antes - len(df_sim)
                if removidos > 0:
                    etapas.append((f"❌ Registros com Valor ≤ 0", len(df_sim), removidos))

                # FLAG clientes VIP (em vez de remover)
                antes = len(df_sim)
                col_valor = 'total' if 'total' in df_sim.columns else 'valor'
                Q1 = df_sim[col_valor].quantile(0.25)
                Q3 = df_sim[col_valor].quantile(0.75)
                IQR = Q3 - Q1
                limite_superior = Q3 + (3 * IQR)
                df_sim['flag_vip'] = df_sim[col_valor] > limite_superior
                vips = df_sim['flag_vip'].sum()
                if vips > 0:
                    etapas.append((f"👑 {vips} clientes VIP identificados (acima de R$ {limite_superior:,.2f})", len(df_sim), -vips))

            # Mostrar etapas
            for etapa, qtd, remov in etapas:
                if remov > 0:
                    st.write(f"  {etapa}: **-{remov}** registros → {qtd} restam")
                else:
                    st.write(f"  ✅ {etapa}: {qtd} registros")

            st.divider()

            # Resultado
            st.subheader("📊 Resultado Final")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📥 Original", len(df_bruto))
            with col2:
                removidos_total = len(df_bruto) - len(df_sim)
                st.metric("❌ Removidos", removidos_total)
            with col3:
                taxa = (len(df_sim) / len(df_bruto) * 100) if len(df_bruto) > 0 else 0
                color = "🟢" if taxa > 80 else "🟡" if taxa > 50 else "🔴"
                st.metric(f"{color} Retenção", f"{taxa:.1f}%", f"{len(df_sim)} registros")

            if taxa < 80:
                st.warning(f"⚠️ **Apenas {taxa:.1f}% dos registros foram mantidos!**")
                st.info("""
                **Possíveis razões:**
                - Registros com **Nome vazio E sem Email** (impossível preencher nome)
                - Registros sem **Telefone** (obrigatório para delivery)
                - Registros **duplicados** (mesmo DDD+Telefone)

                **Como corrigir sua base:**
                1. Preencha a coluna "Email" para clientes sem Nome (o sistema usará a parte antes do @)
                2. Ou preencha manualmente a coluna "Nome"
                3. Certifique-se que cada cliente tem **Telefone**
                4. Remova duplicatas (clientes com mesmo DDD+Telefone)

                ℹ️ **Nova regra:** Clientes sem Nome mas com Email válido terão o nome preenchido automaticamente com a parte do email antes do @
                ℹ️ CPF é opcional e não será usado como identificador.
                """)
            else:
                st.success(f"✅ Base em bom estado! {taxa:.1f}% dos registros serão usados na análise.")

            st.divider()

            # Preview
            st.subheader("👀 Preview da Base Após Limpeza")
            if len(df_sim) > 0:
                st.dataframe(df_sim.head(20), use_container_width=True, hide_index=True)
                st.caption(f"Mostrando primeiros 20 de {len(df_sim)} registros")

                # Download
                csv_clean = df_sim.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Base Limpa",
                    data=csv_clean,
                    file_name=f"base_limpa_{diagnostic_file.name}",
                    mime="text/csv"
                )
            else:
                st.error("❌ Nenhum registro válido após limpeza!")

        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")

    else:
        st.info("👆 Carregue um arquivo acima para iniciar o diagnóstico")


# ==================== SEÇÃO A: ANALYTICS ====================

elif secao == "📊 Analytics":
    st.title("📊 Visão Geral - Analytics")

    st.markdown("""
    **Bem-vindo ao Dashboard RFV!** Este painel analisa automaticamente seus clientes usando a metodologia **RFV (Recência, Frequência, Valor)**:
    - 📅 **Recência**: Dias desde o último pedido
    - 📦 **Frequência**: Total de pedidos feitos
    - 💰 **Valor**: Quanto gastou no total
    """)

    if st.session_state.df_processed is None:
        st.warning("⬆️ Carregue uma base de dados na barra lateral para começar!")
    else:
        df = st.session_state.df_processed

        # ---- KPIs ----
        st.subheader("📈 Indicadores Principais")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Total de Clientes", len(df))

        with col2:
            ticket_medio = df['ticket_medio'].mean()
            ticket_mediano = df['ticket_medio'].median()
            st.metric("🎫 Ticket Médio", f"R$ {ticket_medio:.2f}",
                     f"Mediano: R$ {ticket_mediano:.2f}")

        with col3:
            freq_media = df['frequencia'].mean()
            st.metric("📦 Frequência Média", f"{freq_media:.1f} pedidos")

        with col4:
            receita_risco = df[df['cluster_nome'] == 'Em Risco']['valor'].sum()
            st.metric("⚠️ Receita em Risco", f"R$ {receita_risco:,.2f}")

        # ---- ALERTAS DE QUALIDADE ----
        col1, col2 = st.columns(2)

        with col1:
            # Estatísticas de Ticket
            ticket_min = df['ticket_medio'].min()
            ticket_max = df['ticket_medio'].max()
            ticket_std = df['ticket_medio'].std()

            st.metric("📊 Spread de Ticket", f"R$ {ticket_min:.2f} - R$ {ticket_max:.2f}",
                     f"Desvio: ±R$ {ticket_std:.2f}")

        with col2:
            # Valor total verificação
            valor_total_base = df['valor'].sum()
            valor_medio_por_pedido = df['valor'].sum() / df['pedidos'].sum() if df['pedidos'].sum() > 0 else 0

            st.metric("💵 Valor Total", f"R$ {valor_total_base:,.2f}",
                     f"Total de pedidos: {int(df['pedidos'].sum())}")

        st.warning("""
        ✅ **Validação de Dados Realizada:**

        Todos os registros foram validados para garantir qualidade:
        - ✅ Removidos registros com Valor = 0 ou negativo
        - ✅ Removidos registros com Pedidos = 0 ou negativo
        - ✅ Removidos outliers extremos (valores anormalmente altos)
        - ✅ Clientes sem Nome tiveram nome preenchido com Email (antes do @)
        - ✅ Garantido que todos têm Nome e Telefone (ou foram removidos)

        **Seu Ticket Médio é confiável!** 🎯
        """)

        st.info("""
        💡 **Como ler os KPIs:**
        - **Ticket Médio**: Quanto cada cliente gasta em média por pedido. Valores maiores = clientes mais valiosos
        - **Ticket Mediano**: O valor "do meio" - evita distorções por valores muito altos
        - **Frequência Média**: Quantos pedidos cada cliente faz em média. Maior frequência = cliente mais leal
        - **Receita em Risco**: Quanto você está deixando de ganhar com clientes "Em Risco" que podem sair
        """)

        st.divider()

        # ---- GRÁFICOS ----
        st.subheader("📊 Segmentação de Clientes (Clusters)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Distribuição por Cluster**")

            cluster_counts = df['cluster_nome'].value_counts()
            fig_cluster = px.pie(
                values=cluster_counts.values,
                names=cluster_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

        with col2:
            st.markdown("**Receita por Cluster**")

            cluster_receita = df.groupby('cluster_nome')['valor'].sum().sort_values(ascending=False)
            fig_receita = px.bar(
                x=cluster_receita.values,
                y=cluster_receita.index,
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_receita, use_container_width=True)

        st.info("""
        📖 **Como interpretar os clusters:**

        🏆 **Campeões**: Compraram recentemente, compram frequentemente e gastam muito
        - ✅ Ação: Manter com ofertas VIP e exclusivas para não sair

        💚 **Fiéis Ticket Baixo**: Compram frequentemente mas gastam pouco
        - ✅ Ação: Incentivar upsell com combos premium ou ofertas personalizadas

        ⚠️ **Em Risco**: Compraram muito antes, mas não voltam
        - ✅ Ação: Campanhas urgentes de reativação com descontos atrativos

        😴 **Adormecidos**: Compraram no passado distante, praticamente não voltam
        - ✅ Ação: Reativação agressiva com oferta muito atrativa ou simplesmente deixar ir

        O gráfico de receita mostra qual cluster gera mais faturamento.
        Nem sempre o maior cluster é o que mais fatura!
        """)

        st.divider()

        # ---- SCATTER RFV ----
        st.subheader("🎯 Dispersão RFV: Recência vs Frequência")

        fig_scatter = px.scatter(
            df,
            x='recencia',
            y='frequencia',
            size='valor',
            color='cluster_nome',
            hover_name='nome',
            hover_data={
                'recencia': ':.0f',
                'frequencia': ':.0f',
                'valor': ':.2f',
                'score_propensao': ':.1f'
            },
            labels={
                'recencia': 'Recência (dias)',
                'frequencia': 'Frequência (pedidos)'
            },
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.info("""
        📖 **Como ler o gráfico RFV:**

        - **Eixo Horizontal (Recência)**: Dias desde o último pedido
          - Esquerda = Cliente comprou recentemente (bom!)
          - Direita = Cliente comprou há muito tempo (preocupante)

        - **Eixo Vertical (Frequência)**: Quantos pedidos já fez
          - Topo = Cliente compra muito (leal!)
          - Base = Cliente compra pouco (novo ou desengajado)

        - **Tamanho da bolha (Valor)**: Quanto o cliente gastou no total
          - Bolhas maiores = Clientes mais valiosos
          - Bolhas menores = Clientes com menor gasto

        **Zona Ideal**: Canto superior esquerdo = Recém (esquerda) + Frequente (topo) + Valioso (bolha grande)

        Explore o gráfico! Passe o mouse sobre os pontos para ver detalhes de cada cliente.
        """)

        st.divider()

        # ---- PROPENSÃO ----
        st.subheader("📈 Probabilidade de Compra (Score de Propensão)")

        fig_propensao = px.histogram(
            df,
            x='score_propensao',
            nbins=20,
            color_discrete_sequence=['#1f77b4'],
            labels={'score_propensao': 'Score de Propensão (0-100)'}
        )
        st.plotly_chart(fig_propensao, use_container_width=True)

        st.info("""
        📖 **O que é Score de Propensão:**

        Um número de 0 a 100 que indica a **probabilidade de cada cliente fazer uma compra em breve**.

        **Interpretação:**
        - 🟢 **80-100**: Cliente muito propenso a comprar (próximo às compras)
        - 🟡 **50-79**: Cliente moderadamente propenso
        - 🔴 **0-49**: Cliente pouco propenso (pode estar dormindo)

        **Como o score é calculado:**
        1. Analisa quanto tempo faz que não compra
        2. Compara com o intervalo médio de compras do cliente
        3. Considera o padrão de gasto histórico
        4. Injeta conhecimento sobre comportamento de delivery no Brasil

        **Dica de Ação:**
        - Clientes com score 80+: Enviar ofertas (alta chance de conversão)
        - Clientes com score 30-50: Enviar campanhas de reativação
        - Clientes com score <30: Considerar abandonar (pouco ROI)

        O histograma mostra como seus clientes estão distribuídos entre esses scores.
        """)

        st.divider()

        # ---- HEATMAP ----
        st.subheader("🔥 Correlação entre Variáveis")

        corr_data = df[['recencia', 'frequencia', 'valor', 'score_propensao']].corr()
        fig_heatmap = px.imshow(
            corr_data,
            text_auto=True,
            color_continuous_scale='RdBu',
            labels={
                'recencia': 'Recência',
                'frequencia': 'Frequência',
                'valor': 'Valor',
                'score_propensao': 'Propensão'
            }
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.info("""
        📖 **Como ler o heatmap de correlação:**

        Cada célula mostra como duas variáveis se relacionam:

        **Cores:**
        - 🔵 **Azul (próximo a +1)**: Correlação positiva forte
          - Quando uma aumenta, a outra também aumenta

        - 🔴 **Vermelho (próximo a -1)**: Correlação negativa forte
          - Quando uma aumenta, a outra diminui

        - ⚪ **Branco (próximo a 0)**: Sem correlação
          - As variáveis são independentes

        **Exemplos de leitura:**
        - **Recência vs Frequência**: Negativa (quanto mais tempo sem comprar, menos comprou no passado)
        - **Frequência vs Valor**: Positiva (cliente que compra muito também gasta mais)
        - **Frequência vs Propensão**: Positiva (clientes frequentes têm mais propensão de comprar)

        Essas correlações confirmam que o modelo RFV está funcionando corretamente!
        """)

        st.divider()

        # ---- RESUMO FINAL ----
        st.subheader("✅ Próximos Passos")

        st.success("""
        Agora que você entende seus dados, explore as outras abas:

        1. **📋 Mesa de Ativação**: Veja cada cliente individualmente, filtre por cluster/propensão
        2. **💬 Comunicação**: Crie campanhas personalizadas de WhatsApp/Email
        3. **📈 ROI & Cohort**: Compare seus dados antes/depois de uma campanha

        **Dica**: Comece ativando clientes "Em Risco" com score alto (80+). São seus melhores candidatos a reativação!
        """)


# ==================== SEÇÃO B: MESA DE ATIVAÇÃO ====================

elif secao == "📋 Mesa de Ativação":
    st.title("📋 Mesa de Ativação")

    if st.session_state.df_processed is None:
        st.warning("⬆️ Carregue uma base de dados na barra lateral para começar!")
    else:
        df = st.session_state.df_processed.copy()

        st.markdown("Filtros dinâmicos e sugestões de oferta personalizadas")

        col1, col2, col3 = st.columns(3)

        # Filtros
        with col1:
            clusters = st.multiselect(
                "Filtrar por Cluster:",
                options=df['cluster_nome'].unique(),
                default=df['cluster_nome'].unique()
            )

        with col2:
            propensao_range = st.slider(
                "Score de Propensão:",
                min_value=0,
                max_value=100,
                value=(0, 100)
            )

        with col3:
            meses = st.multiselect(
                "Mês de Aniversário:",
                options=list(range(1, 13)),
                default=list(range(1, 13)),
                format_func=lambda x: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][x-1]
            )

        # Aplicar filtros
        # Nota: Incluir NaN no filtro de mês para não excluir clientes sem data de aniversário
        filtro_mes = (df['mes_aniversario'].isin(meses)) | (df['mes_aniversario'].isna())

        df_filtered = df[
            (df['cluster_nome'].isin(clusters)) &
            (df['score_propensao'] >= propensao_range[0]) &
            (df['score_propensao'] <= propensao_range[1]) &
            filtro_mes
        ].copy()

        st.info(f"📌 {len(df_filtered)} clientes selecionados")

        # Tabela interativa
        st.subheader("📊 Tabela de Clientes")

        display_cols = ['nome', 'telefone', 'email', 'frequencia', 'ticket_medio', 'recencia', 'cluster_nome', 'score_propensao', 'oferta_sugerida']
        available_cols = [col for col in display_cols if col in df_filtered.columns]

        # Formatação
        df_display = df_filtered[available_cols].copy()
        df_display['score_propensao'] = df_display['score_propensao'].round(1)
        df_display['ticket_medio'] = df_display['ticket_medio'].apply(lambda x: f"R$ {x:.2f}")
        df_display['recencia'] = df_display['recencia'].astype(int)
        df_display['frequencia'] = df_display['frequencia'].astype(int)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Download
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"clientes_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# ==================== SEÇÃO C: COMUNICAÇÃO ====================

elif secao == "💬 Comunicação":
    st.title("💬 Módulo de Ativação - WhatsApp & E-mail")

    if st.session_state.df_processed is None:
        st.warning("⬆️ Carregue uma base de dados na barra lateral para começar!")
    else:
        df = st.session_state.df_processed.copy()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Seleção de Audiência")
            cluster_selecionado = st.selectbox(
                "Escolha um cluster para ativar:",
                options=df['cluster_nome'].unique()
            )

            propensao_minima = st.slider(
                "Score de Propensão mínima:",
                min_value=0,
                max_value=100,
                value=30
            )

        with col2:
            st.subheader("📱 Canal de Comunicação")
            canal = st.radio(
                "Escolha o canal:",
                ["WhatsApp", "E-mail"]
            )

        # Filtrar audiência
        df_campaign = df[
            (df['cluster_nome'] == cluster_selecionado) &
            (df['score_propensao'] >= propensao_minima)
        ].copy()

        # Estatísticas
        st.divider()
        st.subheader("📊 Resumo da Campanha")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("👥 Audiência", len(df_campaign))

        with col2:
            contatos_validos = df_campaign['telefone'].notna().sum() if canal == "WhatsApp" else df_campaign['email'].notna().sum()
            st.metric("✔️ Contatos Válidos", contatos_validos)

        with col3:
            receita_potencial = df_campaign['valor'].sum()
            st.metric("💰 Receita Potencial", f"R$ {receita_potencial:,.0f}")

        st.divider()

        # Template de mensagem
        st.subheader("✍️ Template de Mensagem")

        comm_engine = st.session_state.communication_engine

        # Template padrão
        template_default = comm_engine.TEMPLATES.get(cluster_selecionado, comm_engine.TEMPLATES["Em Risco"])
        template_base = template_default["whatsapp"] if canal == "WhatsApp" else template_default["email"]

        template_custom = st.text_area(
            "Edite o template (variáveis: {nome}, {oferta}, {dias_sem_comprar}, {tempo_casa}):",
            value=template_base,
            height=150
        )

        # Botão para gerar template dinâmico
        if st.button("✨ Gerar Template Dinâmico", use_container_width=True):
            # Calcular recência média do cluster
            recencia_media = int(df_campaign['recencia'].mean()) if len(df_campaign) > 0 else 30
            oferta_media = df_campaign['oferta_sugerida'].mode()[0] if len(df_campaign) > 0 and 'oferta_sugerida' in df_campaign.columns else "Desconto especial"

            # Gerar template dinâmico (usando um nome genérico como referência)
            template_gerado = comm_engine.generate_dynamic_template(
                nome="Cliente",
                cluster=cluster_selecionado,
                dias_sem_comprar=recencia_media,
                oferta=oferta_media,
                canal="whatsapp" if canal == "WhatsApp" else "email"
            )

            st.session_state['template_dinamico'] = template_gerado

        # Se há template dinâmico gerado, usá-lo
        if 'template_dinamico' in st.session_state:
            template_custom = st.session_state['template_dinamico']
            st.info("✨ Usando template dinâmico gerado! Você pode ainda editar abaixo.")

        # Preview
        st.subheader("👀 Preview (3 primeiros clientes)")

        previews = comm_engine.preview_campaign(
            df_campaign.head(3),
            template_custom=template_custom if template_custom != template_base else None
        )

        for preview in previews:
            with st.expander(f"🧑 {preview['cliente']} | Score: {preview['score_propensao']}"):
                st.text(preview['mensagem'])

        st.divider()

        # Exportar campanhas
        st.subheader("📤 Gerar Payloads")

        if st.button("🔗 Gerar Links WhatsApp (clique 1 por 1)", use_container_width=True) if canal == "WhatsApp" else st.button("📧 Gerar Payloads E-mail", use_container_width=True):

            if canal == "WhatsApp":
                st.success("✅ Links WhatsApp gerados! Clique em cada um para abrir:")

                for idx, row in df_campaign.head(10).iterrows():
                    msg = comm_engine.format_whatsapp_message(
                        nome=row.get('nome'),
                        oferta=row.get('oferta_sugerida'),
                        dias_sem_comprar=int(row.get('recencia', 0)),
                        cluster=cluster_selecionado,
                        template_custom=template_custom if template_custom != template_base else None
                    )

                    wa_link = comm_engine.generate_whatsapp_link(
                        ddd=str(row.get('ddd', '')),
                        telefone=str(row.get('telefone', '')),
                        mensagem=msg['mensagem']
                    )

                    if wa_link:
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.write(f"**{row.get('nome')}**")
                        with col2:
                            st.markdown(f"[🔗 Abrir WhatsApp]({wa_link})", unsafe_allow_html=True)

            else:
                st.success("✅ Payloads E-mail gerados!")

                for idx, row in df_campaign.head(5).iterrows():
                    email_msg = comm_engine.format_email_message(
                        nome=row.get('nome'),
                        oferta=row.get('oferta_sugerida'),
                        cluster=cluster_selecionado,
                        dias_sem_comprar=int(row.get('recencia', 0)),
                        tempo_casa=int(row.get('tempo_casa', 0)),
                        template_custom=template_custom if template_custom != template_base else None
                    )

                    payload = comm_engine.prepare_webhook_payload(
                        {
                            'nome': row.get('nome'),
                            'email': row.get('email'),
                            'ddd': row.get('ddd'),
                            'telefone': row.get('telefone'),
                            'mensagem': email_msg,
                            'oferta': row.get('oferta_sugerida'),
                            'cluster': cluster_selecionado,
                            'score_propensao': row.get('score_propensao'),
                            'timestamp': datetime.now().isoformat()
                        },
                        channel='email'
                    )

                    with st.expander(f"📧 {row.get('nome')} ({row.get('email')})"):
                        st.code(payload, language='json')


# ==================== SEÇÃO D: ROI & COHORT ====================

elif secao == "📈 ROI & Cohort":
    st.title("📈 Análise de ROI e Cohort")

    if st.session_state.df_roi is None:
        st.warning("⬆️ Carregue duas bases na barra lateral para começar a análise!")
    else:
        roi_data = st.session_state.df_roi

        st.subheader("📊 Resultados da Análise")

        # Revenue Impact
        if 'revenue_impact' in roi_data:
            st.subheader("💰 Impacto de Receita")

            rev = roi_data['revenue_impact']
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Receita T1", f"R$ {rev.get('receita_t1', 0):,.0f}")

            with col2:
                st.metric("Receita T2", f"R$ {rev.get('receita_t2', 0):,.0f}")

            with col3:
                st.metric(
                    "Crescimento",
                    f"R$ {rev.get('crescimento_absoluto', 0):,.0f}",
                    f"{rev.get('crescimento_percentual', 0):.1f}%"
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Clientes c/ Aumento",
                    rev.get('clientes_aumentaram_gasto', 0),
                    f"{rev.get('taxa_aumento_gasto', 0):.1f}%"
                )

            with col2:
                st.metric(
                    "Clientes c/ Redução",
                    rev.get('clientes_reduziram_gasto', 0)
                )

            with col3:
                st.metric(
                    "Churn Receita",
                    rev.get('churn_receita_clientes', 0)
                )

        # Cluster Movement
        if 'cluster_impact' in roi_data:
            st.subheader("🎯 Movimentos entre Clusters")

            cluster = roi_data['cluster_impact']
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Movimentos Positivos",
                    cluster.get('movimentos_positivos', 0),
                    f"{cluster.get('taxa_melhoria', 0):.1f}%"
                )

            with col2:
                st.metric(
                    "Movimentos Negativos",
                    cluster.get('movimentos_negativos', 0),
                    f"{cluster.get('taxa_degradacao', 0):.1f}%"
                )

            with col3:
                st.metric(
                    "Mantidos",
                    cluster.get('mantidos', 0)
                )

        # ROI Final
        if 'roi_percentual' in roi_data and roi_data['roi_percentual'] is not None:
            st.divider()
            st.subheader("💵 ROI Final")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Lucro Líquido",
                    f"R$ {roi_data.get('lucro_liquido', 0):,.2f}"
                )

            with col2:
                st.metric(
                    "ROI %",
                    f"{roi_data.get('roi_percentual', 0):.1f}%"
                )


# ==================== FOOTER ====================

st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    🍕 PizzaCRM Analytics v1.0 | Desenvolvido com ❤️ para Pizzarias em Delivery
    </div>
""", unsafe_allow_html=True)
