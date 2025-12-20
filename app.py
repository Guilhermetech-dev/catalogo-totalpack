import streamlit as st
import pandas as pd
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Catálogo Mobile", layout="wide", initial_sidebar_state="collapsed")

# --- SUAS CONFIGURAÇÕES ---
TELEFONE_WHATSAPP = "5521975523288"  # <--- SEU NÚMERO AQUI

# --- 1. Inicialização da Memória ---
if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

def adicionar_ao_carrinho(produto_id, nome, preco_pix, preco_cartao):
    st.session_state['carrinho'].append({
        "id": produto_id,
        "nome": nome,
        "preco_pix": preco_pix,
        "preco_cartao": preco_cartao
    })
    st.toast(f"{nome} adicionado!", icon="✅")

# --- 2. Carregar Dados ---
try:
    # Carrega o CSV novo com as colunas preco_pix e preco_cartao
    df = pd.read_csv("produtos.csv")
except FileNotFoundError:
    st.error("Erro: Arquivo 'produtos.csv' não encontrado.")
    st.stop()

# --- 3. Título e CSS ---
st.title("📦Catálogo TotalPack Embalagens")

st.markdown("""
    <style>
    .stButton button { width: 100%; }
    
    /* Abas maiores */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem; font-weight: bold;
    }
    
    /* Botão Zap Verde */
    a[href^="https://wa.me"] {
        background-color: #25D366 !important; color: white !important; border: none !important;
        text-decoration: none !important; display: inline-flex; justify-content: center;
        width: 100%; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: bold;
    }
    
    /* Preço Destaque (Pix) */
    .preco-pix { font-size: 1.4rem; font-weight: bold; color: #2e7d32; }
    .preco-cartao { font-size: 0.9rem; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AS ABAS ---
qtd_itens = len(st.session_state['carrinho'])
titulo_carrinho = f"🛒 Carrinho ({qtd_itens})"
aba_loja, aba_carrinho = st.tabs(["🛍️ Produtos", titulo_carrinho])

# ================= ABA LOJA =================
with aba_loja:
    with st.expander("🔍 Filtrar Produtos"):
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            opcoes_categorias = ["Todas"] + list(df['categoria'].unique())
            categoria_selecionada = st.selectbox("Categoria:", opcoes_categorias)
        with col_filtro2:
            # Filtra pelo preço Pix (que é o base)
            preco_max = float(df['preco_pix'].max())
            valor_filtro = st.slider("Até R$ (Pix):", 0.0, preco_max, preco_max)

    # Filtragem
    df_filtrado = df[df['preco_pix'] <= valor_filtro]
    if categoria_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]

    st.caption(f"{len(df_filtrado)} produtos encontrados")
    
    if df_filtrado.empty:
        st.warning("Nenhum produto encontrado.")
    else:
        # GRID DE PRODUTOS
        QUANTIDADE_POR_LINHA = 3
        for i in range(0, len(df_filtrado), QUANTIDADE_POR_LINHA):
            grupo = df_filtrado.iloc[i : i + QUANTIDADE_POR_LINHA]
            cols = st.columns(QUANTIDADE_POR_LINHA)
            
            for indice, (id_real, produto) in enumerate(grupo.iterrows()):
                with cols[indice]:
                    with st.container(border=True):
                        try:
                            st.image(produto["img"], use_container_width=True)
                        except:
                            st.text("Sem Imagem")
                        
                        st.subheader(produto["nome"])
                        st.caption(produto['categoria'])
                        
                        # EXIBIÇÃO DUPLA DE PREÇO
                        st.markdown(f"""
                        <div class='preco-pix'>R$ {produto['preco_pix']:.2f} <small>(Pix)</small></div>
                        <div class='preco-cartao'>R$ {produto['preco_cartao']:.2f} (Cartão)</div>
                        """, unsafe_allow_html=True)
                        
                        st.button(
                            "Adicionar", 
                            key=f"btn_{produto['id']}",
                            on_click=adicionar_ao_carrinho,
                            args=(produto['id'], produto['nome'], produto['preco_pix'], produto['preco_cartao'])
                        )

# ================= ABA CARRINHO =================
with aba_carrinho:
    st.header("Seu Pedido")
    
    if len(st.session_state['carrinho']) > 0:
        total_pix = 0.0
        total_cartao = 0.0
        texto_pedido = "Olá! Gostaria de fazer o seguinte pedido:\n\n"
        
        # Lista os itens
        for item in st.session_state['carrinho']:
            colA, colB = st.columns([3, 1])
            with colA:
                st.write(f"• **{item['nome']}**")
            with colB:
                st.write(f"{item['preco_pix']:.2f} / {item['preco_cartao']:.2f}")
            
            total_pix += item['preco_pix']
            total_cartao += item['preco_cartao']
            texto_pedido += f"• {item['nome']}\n"
        
        st.divider()
        # EXIBE OS DOIS TOTAIS
        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total no PIX/Dinheiro", f"R$ {total_pix:.2f}")
        with col_tot2:
            st.metric("Total no Cartão", f"R$ {total_cartao:.2f}")
            
        texto_pedido += f"\n💰 *Total no Pix/Dinheiro: R$ {total_pix:.2f}*"
        texto_pedido += f"\n💳 *Total no Cartão: R$ {total_cartao:.2f}*"
        
        st.write("---")
        st.write("📝 **Dados para entrega:**")
        cliente_nome = st.text_input("Seu Nome:", placeholder="Ex: Maria da Silva")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Limpar"):
                st.session_state['carrinho'] = []
                st.rerun()
        with col_btn2:
            if cliente_nome:
                texto_pedido += f"\n\nNome do Cliente: {cliente_nome}"
                link_zap = f"https://wa.me/{TELEFONE_WHATSAPP}?text={quote(texto_pedido)}"
                st.link_button("Enviar no WhatsApp ➤", link_zap, type="primary")
            else:
                st.warning("Preencha seu nome acima")
    else:
        st.info("Seu carrinho está vazio.")