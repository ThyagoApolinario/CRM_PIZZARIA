"""
Script de Diagnóstico - Analisa bases de dados carregadas
Execute: streamlit run diagnostico.py
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Diagnóstico de Base", page_icon="🔍", layout="wide")

st.title("🔍 Diagnóstico de Base de Dados")
st.markdown("Analise sua base para entender quantos registros serão usados e por quê alguns podem ser filtrados")

st.divider()

# Upload
uploaded_file = st.file_uploader("Carregue sua base (CSV ou Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    # Salvar temporariamente
    temp_path = f"/tmp/{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Carregar base bruta
    try:
        if uploaded_file.name.endswith('.csv'):
            df_bruto = pd.read_csv(temp_path)
        else:
            df_bruto = pd.read_excel(temp_path)

        print(f"✅ Base carregada: {len(df_bruto)} registros")

    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {e}")
        st.stop()

    # ==================== DIAGNÓSTICO ====================

    st.header("📊 Análise Detalhada")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Base BRUTA", len(df_bruto), "registros")
    with col2:
        st.metric("📋 Colunas", len(df_bruto.columns))
    with col3:
        st.metric("✅ Completas", "?", "a verificar")

    st.divider()

    # ---- Colunas ----
    st.subheader("📋 Colunas Encontradas")
    st.write(f"**{len(df_bruto.columns)} colunas:**")
    st.code(", ".join(df_bruto.columns.tolist()))

    st.divider()

    # ---- Análise de Limpeza ----
    st.subheader("🧹 Simulação de Limpeza")

    df = df_bruto.copy()
    historico = []

    # Passo 1: Normalizar colunas
    df.columns = [col.lower().strip() for col in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    historico.append(("Após normalizar", len(df)))

    # Passo 2: Remover duplicatas
    if 'cpf' in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset=['cpf'], keep='first')
        removidos = antes - len(df)
        historico.append((f"Remover duplicatas (CPF): {removidos} removidos", len(df)))

    # Passo 3: Nome vazio
    if 'nome' in df.columns:
        antes = len(df)
        df = df.dropna(subset=['nome'])
        removidos = antes - len(df)
        historico.append((f"Registros sem Nome: {removidos} removidos", len(df)))

    # Passo 4: Telefone E E-mail
    if 'telefone' in df.columns or 'email' in df.columns:
        antes = len(df)

        has_telefone = df['telefone'].notna() if 'telefone' in df.columns else False
        has_email = df['email'].notna() if 'email' in df.columns else False

        if isinstance(has_telefone, bool):
            has_telefone = pd.Series([has_telefone] * len(df))
        if isinstance(has_email, bool):
            has_email = pd.Series([has_email] * len(df))

        df = df[has_telefone | has_email].reset_index(drop=True)
        removidos = antes - len(df)
        historico.append((f"Sem Telefone E sem E-mail: {removidos} removidos", len(df)))

    # Mostrar histórico
    st.markdown("**Passo a passo:**")
    for passo, qtd in historico:
        st.write(f"  ➜ {passo} → **{qtd} registros**")

    st.divider()

    # ---- Resultado Final ----
    st.subheader("✅ Resultado Final")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Base BRUTA", len(df_bruto))
    with col2:
        removidos_total = len(df_bruto) - len(df)
        st.metric("❌ Removidos", removidos_total)
    with col3:
        taxa = (len(df) / len(df_bruto) * 100) if len(df_bruto) > 0 else 0
        st.metric("✅ Retenção", f"{taxa:.1f}%", f"{len(df)} registros")

    if taxa < 80:
        st.warning(f"⚠️ Apenas {taxa:.1f}% dos registros foram mantidos!")
        st.info("""
        **Possíveis razões:**
        1. Muitos registros com **Nome vazio**
        2. Muitos registros sem **Telefone** nem **E-mail**
        3. Muitos registros **duplicados** (mesmo CPF)

        **Como corrigir sua base:**
        - ✅ Preencha a coluna "Nome" para todos os registros
        - ✅ Certifique-se que cada cliente tem Telefone OU E-mail
        - ✅ Remova duplicatas antes de fazer upload
        """)
    else:
        st.success(f"✅ Base em bom estado! {taxa:.1f}% dos registros serão usados")

    st.divider()

    # ---- Preview dos Dados ----
    st.subheader("👀 Preview da Base Após Limpeza")

    if len(df) > 0:
        st.dataframe(df.head(20), use_container_width=True)

        st.write(f"Mostrando os primeiros 20 de {len(df)} registros")

        # Download
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Base Limpa",
            data=csv,
            file_name=f"base_limpa_{uploaded_file.name}",
            mime="text/csv"
        )
    else:
        st.error("❌ Nenhum registro válido na base após limpeza")

else:
    st.info("👆 Carregue um arquivo acima para iniciar o diagnóstico")
