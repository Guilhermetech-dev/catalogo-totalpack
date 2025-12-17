import streamlit as st
import pandas as pd
from urllib.parse import quote # Ferramenta para criar o link do WhatsApp

st.set_page_config(page_title="Catálogo de Descartáveis", layout="wide")

# --- CONFIGURAÇÃO DO SEU WHATSAPP ---
# Coloque aqui o seu número com código do país e DDD (sem o +)
# Exemplo: 55 (Brasil) + 21 (Rio) + 999999999
TELEFONE_WHATSAPP = "5521975523288" 

# --- 1. Inicialização da Memória ---
if 'carrinho' not in st.session_state:
    st.session_state['carrinho'] = []

def adicionar_ao_carrinho(produto_id, nome, preco):
    st.session_state['carrinho'].append({
        "id": produto_id,
        "nome": nome,
        "preco": preco
    })
    st.toast(f"{nome} adicionado!", icon="🛒")

# --- 2. Carregar Dados ---
try:
    df = pd.read_csv("produtos.csv")
except FileNotFoundError:
    st.error("Erro: Arquivo 'produtos.csv' não encontrado.")
    st.stop()

# --- 3. Barra Lateral ---
aba_filtros, aba_carrinho = st.sidebar.tabs(["🔍 Filtros", "🛒 Carrinho"])

with aba_filtros:
    opcoes_categorias = ["Todas"] + list(df['categoria'].unique())
    categoria_selecionada = st.selectbox("Categoria:", opcoes_categorias)
    
    preco_min = float(df['preco'].min())
    preco_max = float(df['preco'].max())
    valor_filtro = st.slider("Preço Máximo (R$):", preco_min, preco_max, preco_max)

with aba_carrinho:
    st.write(f"Itens no carrinho: **{len(st.session_state['carrinho'])}**")
    
    if len(st.session_state['carrinho']) > 0:
        total = 0.0
        # Criamos uma lista de texto para o WhatsApp
        texto_pedido = "Olá! Gostaria de fazer o seguinte pedido:\n\n"
        
        for item in st.session_state['carrinho']:
            st.text(f"• {item['nome']}")
            st.caption(f"  R$ {item['preco']:.2f}")
            total += item['preco']
            # Adiciona item ao texto do Zap
            texto_pedido += f"• {item['nome']} - R$ {item['preco']:.2f}\n"
        
        st.markdown("---")
        st.markdown(f"### Total: R$ {total:.2f}")
        texto_pedido += f"\n*Total: R$ {total:.2f}*"
        
        # --- CAMPOS EXTRAS PARA O CLIENTE ---
        # Adicionei um campo para o cliente dizer quem é
        cliente_nome = st.text_input("Seu Nome:", placeholder="Digite seu nome")
        
        if cliente_nome:
            texto_pedido += f"\n\nNome do Cliente: {cliente_nome}"
            
            # Codifica a mensagem para formato de URL (transforma espaços em %20, etc)
            texto_codificado = quote(texto_pedido)
            link_zap = f"https://wa.me/{TELEFONE_WHATSAPP}?text={texto_codificado}"
            
            # Botão Especial de Link
            st.link_button("Enviar Pedido no WhatsApp", link_zap, type="primary")
        else:
            st.warning("Digite seu nome para liberar o botão de envio.")
            
        # Botão limpar
        if st.button("Limpar Carrinho"):
            st.session_state['carrinho'] = []
            st.rerun()
    else:
        st.info("O seu carrinho está vazio.")

# --- 4. Filtros e Vitrine (Igual à aula anterior) ---
df_filtrado = df[df['preco'] <= valor_filtro]
if categoria_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]

st.title("📦 Catálogo de Descartáveis")
st.markdown(f"Exibindo **{len(df_filtrado)}** produtos")
# --- CSS Customizado ---
st.markdown("""
    <style>
    /* 1. Ajusta TODOS os botões normais para ocuparem a largura total */
    .stButton button {
        width: 100%;
    }

    /* 2. Estilização ESPECÍFICA para o botão do WhatsApp */
    /* O código abaixo procura links (a) que começam (^) com 'https://wa.me' */
    a[href^="https://wa.me"] {
        background-color: #25D366 !important; /* Cor Oficial do Zap */
        color: white !important;
        border: none !important;
        text-decoration: none !important;
        display: inline-flex;       /* Garante alinhamento */
        justify-content: center;    /* Centraliza o texto */
        width: 100%;               /* Largura total igual aos outros */
        padding: 0.5rem 1rem;       /* Espaçamento interno */
        border-radius: 0.5rem;      /* Cantos arredondados */
    }

    /* 3. Efeito Hover (Quando passa o mouse em cima) */
    a[href^="https://wa.me"]:hover {
        background-color: #128C7E !important; /* Um verde um pouco mais escuro */
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Sombra suave */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

if df_filtrado.empty:
    st.warning("Nenhum produto encontrado.")
else:
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
                    st.caption(f"{produto['categoria']}")
                    st.markdown(f"### R$ {produto['preco']:.2f}")
                    st.button("Adicionar", key=f"btn_{produto['id']}", on_click=adicionar_ao_carrinho, args=(produto['id'], produto['nome'], produto['preco']))