import streamlit as st
import json
import os
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ramos Sports - Catálogo Oficial", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- OTIMIZAÇÃO DE ESTILO E PERFORMANCE (CSS CUSTOMIZADO) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .card-produto {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA SESSÃO DO CARRINHO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- CARREGAMENTO DE DADOS (COM CACHE OTIMIZADO) ---
@st.cache_data(ttl=600)
def carregar_dados():
    if os.path.exists("camisas.json"):
        with open("camisas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

camisas = carregar_dados()

if not camisas:
    st.warning("⚠️ O arquivo 'camisas.json' não foi encontrado ou está vazio. Por favor, adicione o arquivo de dados.")
else:
    # --- BARRA LATERAL: LOGO, CARRINHO E REGRAS ---
    with st.sidebar:
        # Exibição da Logo Otimizada (se o arquivo existir na pasta)
        logo_path = "logo.png"  # Salve sua logo com este nome na mesma pasta
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("## ⚽ RAMOS SPORTS")
        
        st.markdown("---")
        st.markdown("### 🛒 Carrinho de Compras")
        
        # Regras comerciais informadas
        st.info("ℹ️ **Regras:**\n- Pedido mínimo: **2 peças**\n- Pedidos acima de **3 peças**: **Desconto especial!**")

        carrinho = st.session_state.carrinho
        
        if len(carrinho) > 0:
            st.markdown(f"**Itens selecionados ({len(carrinho)}):**")
            
            # Lista os itens no carrinho lateral
            for idx, item in enumerate(carrinho):
                col_i1, col_i2 = st.columns([5, 1])
                col_i1.markdown(f"• {item['time']} ({item['versao']})")
                if col_i2.button("❌", key=f"del_{idx}", help="Remover item"):
                    carrinho.pop(idx)
                    st.rerun()

            st.markdown("---")
            
            # Validação do pedido mínimo (2 peças)
            if len(carrinho) < 2:
                st.warning("⚠️ Adicione pelo menos **2 peças** para fechar o pedido.")
            else:
                st.success("✅ Pedido mínimo atingido!")
                
                if len(carrinho) >= 3:
                    st.markdown("🎉 **Desconto aplicado (acima de 3 peças)!**")

                # Montagem da mensagem dinâmica para o WhatsApp
                texto_pedido = "Olá! Gostaria de encomendar as seguintes camisas na Ramos Sports:\n\n"
                for item in carrinho:
                    texto_pedido += f"• {item['time']} - Versão {item['versao']} ({item['preco']})\n"
                
                if len(carrinho) >= 3:
                    texto_pedido += "\n*(Aplicar desconto para pedido acima de 3 peças)*"
                
                texto_codificado = urllib.parse.quote(texto_pedido)
                # Substitua pelo seu número de WhatsApp real (exemplo: 5511999999999)
                link_wpp_final = f"https://wa.me/5511999999999?text={texto_codificado}"

                st.markdown(
                    f'<a href="{link_wpp_final}" target="_blank" style="text-decoration:none;">'
                    '<button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;">'
                    '💬 Enviar Pedido no WhatsApp'
                    '</button></a>',
                    unsafe_allow_html=True
                )
            
            if st.button("🗑️ Limpar Carrinho", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()
        else:
            st.markdown("_Seu carrinho está vazio._")

        st.markdown("---")
        st.header("🔍 Filtrar Catálogo")

        # Filtros
        clubes_disponiveis = ["Todos"] + sorted(list(set(c["time"] for c in camisas)))
        clube_selecionado = st.selectbox("Selecione o Clube", clubes_disponiveis)

        versoes_disponiveis = ["Todas"] + sorted(list(set(c["versao"] for c in camisas)))
        versao_selecionada = st.selectbox("Selecione a Versão", versoes_disponiveis)

    # --- FILTRAGEM DE DADOS ---
    camisas_filtradas = camisas
    if clube_selecionado != "Todos":
        camisas_filtradas = [c for c in camisas_filtradas if c["time"] == clube_selecionado]
    if versao_selecionada != "Todas":
        camisas_filtradas = [c for c in camisas_filtradas if c["versao"] == versao_selecionada]

    # --- CORPO PRINCIPAL DO SITE ---
    st.title("⚽ Ramos Sports - Catálogo Oficial")
    st.markdown("### 📢 **Aviso:** Pedido mínimo de 2 peças. A partir de 3 peças você ganha desconto especial!")
    st.markdown(f"**Exibindo {len(camisas_filtradas)} camisas disponíveis**")
    st.markdown("---")

    # Grade de produtos (4 colunas)
    colunas_por_linha = 4
    colunas = st.columns(colunas_por_linha)

    for index, camisa in enumerate(camisas_filtradas):
        coluna_atual = colunas[index % colunas_por_linha]
        
        with coluna_atual:
            st.markdown('<div class="card-produto">', unsafe_allow_html=True)
            caminho_img = camisa.get("nome_arquivo")
            
            if caminho_img and os.path.exists(caminho_img):
                st.image(caminho_img, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300?text=Foto+Indisponível", use_container_width=True)

            st.markdown(f"**{camisa['time']} - {camisa['versao']}**")
            st.markdown(f"💰 **{camisa['preco']}**")
            
            # Botão de Adicionar ao Carrinho
            if st.button("➕ Adicionar", key=f"btn_{caminho_img}_{index}", use_container_width=True):
                st.session_state.carrinho.append(camisa)
                st.success(f"{camisa['time']} adicionado!")
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
