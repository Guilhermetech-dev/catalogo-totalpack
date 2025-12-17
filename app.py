import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(page_title="Catálogo TotalPack", layout="wide", initial_sidebar_state="collapsed")

# --- CONFIGURAÇÃO ---
TELEFONE_WHATSAPP = "5521975523288"  # SEU NÚMERO AQUI

# --- 1. Inicialização da Memória ---
if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

def adicionar_ao_carrinho(produto_id, nome, preco):
    st.session_state['carrinho'].append({
        "id": produto_id,
        "nome": nome,
        "preco": preco
    })
    st.toast(f"{nome} adicionado!", icon="✅")

# --- 2. Carregar Dados ---
try:
    df = pd.read_csv("produtos.csv")
except FileNotFoundError:
    st.error("Erro: Arquivo 'produtos.csv' não encontrado.")
    st.stop()

# --- 3. Título e CSS ---
st.title("📦 Catálogo TotalPack")

# CSS para melhorar o visual no celular
st.markdown("""
    <style>
    /* Botões ocupam largura total */
    .stButton button { width: 100%; }
    
    /* Aumentar o tamanho das abas para facilitar o toque */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Estilo do Botão WhatsApp (Verde) */
    a[href^="https://wa.me"] {
        background-color: #25D366 !important;
        color: white !important;
        border: none !important;
        text-decoration: none !important;
        display: inline-flex;
        justify-content: center;
        width: 100%;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AS ABAS SUPERIORES ---
# Criamos o título da aba do carrinho dinamicamente com a contagem de itens
qtd_itens = len(st.session_state['carrinho'])
titulo_carrinho = f"🛒 Carrinho ({qtd_itens})"

# Criamos as duas grandes abas no topo
aba_loja, aba_carrinho = st.tabs(["🛍️ Produtos", titulo_carrinho])

# ==========================================
# CONTEÚDO DA ABA LOJA
# ==========================================
with aba_loja:
    # FILTROS (Dentro de um expander para economizar espaço no celular)
    with st.expander("🔍 Clique aqui para Filtrar (Preço/Categoria)"):
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            opcoes_categorias = ["Todas"] + list(df['categoria'].unique())
            categoria_selecionada = st.selectbox("Categoria:", opcoes_categorias)
        
        with col_filtro2:
            preco_max = float(df['preco'].max())
            valor_filtro = st.slider("Até R$:", 0.0, preco_max, preco_max)

    # LÓGICA DE FILTRAGEM
    df_filtrado = df[df['preco'] <= valor_filtro]
    if categoria_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]

    # VITRINE
    st.markdown(f"**{len(df_filtrado)}** produtos encontrados")
    
    if df_filtrado.empty:
        st.warning("Nenhum produto encontrado.")
    else:
        # Grid de produtos
        QUANTIDADE_POR_LINHA = 3 # No celular o Streamlit ajusta isso sozinho para 1 por linha
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
                        st.caption(f"{produto['categoria']}")
                        st.markdown(f"### R$ {produto['preco']:.2f}")
                        
                        st.button(
                            "Adicionar", 
                            key=f"btn_{produto['id']}",
                            on_click=adicionar_ao_carrinho,
                            args=(produto['id'], produto['nome'], produto['preco'])
                        )

# ==========================================
# CONTEÚDO DA ABA CARRINHO
# ==========================================
with aba_carrinho:
    st.header("Seu Pedido")
    
    if len(st.session_state['carrinho']) > 0:
        total = 0.0
        texto_pedido = "Olá! Gostaria de fazer o seguinte pedido:\n\n"
        
        # Lista os itens
        for i, item in enumerate(st.session_state['carrinho']):
            colA, colB = st.columns([3, 1])
            with colA:
                st.write(f"• **{item['nome']}**")
            with colB:
                st.write(f"R$ {item['preco']:.2f}")
            
            total += item['preco']
            texto_pedido += f"• {item['nome']} - R$ {item['preco']:.2f}\n"
        
        st.divider()
        st.markdown(f"### Total: R$ {total:.2f}")
        texto_pedido += f"\n*Total: R$ {total:.2f}*"
        
        st.write("---")
        st.write("📝 **Dados para entrega:**")
        cliente_nome = st.text_input("Seu Nome:", placeholder="Ex: Maria da Silva")
        
        # Botões de Ação
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🗑️ Limpar"):
                st.session_state['carrinho'] = []
                st.rerun()
                
        with col_btn2:
            if cliente_nome:
                texto_pedido += f"\n\nNome do Cliente: {cliente_nome}"
                texto_codificado = quote(texto_pedido)
                link_zap = f"https://wa.me/{TELEFONE_WHATSAPP}?text={texto_codificado}"
                st.link_button("Enviar no WhatsApp ➤", link_zap, type="primary")
            else:
                st.warning("Preencha seu nome acima ☝️")
                
    else:
        st.info("Seu carrinho está vazio. Volte para a aba 'Produtos' para comprar!")