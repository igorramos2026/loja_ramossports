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

# --- LISTA DE CLUBES POPULARES (PRIORIDADE NO TOPO) ---
CLUBES_POPULARES = [
    # Brasileiros
    "Flamengo", "Corinthians", "Palmeiras", "São Paulo", "Santos", 
    "Vasco", "Grêmio", "Internacional", "Atlético Mineiro", "Cruzeiro", "Botafogo", "Fluminense",
    # Europeus
    "Real Madrid", "Barcelona", "Paris Saint-Germain", "PSG", "Manchester City", 
    "Manchester United", "Liverpool", "Bayern de Munique", "Bayern", "Juventus", "Arsenal", "Chelsea"
]

def obter_prioridade_time(camisa):
    """Retorna a prioridade do time para ordenação (menor valor = aparece primeiro)"""
    time_nome = camisa.get("time", "").strip()
    for index, clube_pop in enumerate(CLUBES_POPULARES):
        if clube_pop.lower() in time_nome.lower():
            return index
    return 999  # Se não for popular, vai para o final da lista

# --- ESTILO E ALINHAMENTO RIGOROSO DOS CARTÕES (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    /* Cartão Flexível com altura fixa perfeita para 3 colunas */
    .card-produto {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px set #e9ecef;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 490px;
    }
    .card-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex-grow: 1;
    }
    /* Controle absoluto da imagem via HTML/CSS para evitar distorções */
    .img-produto {
        width: 100% !important;
        height: 220px !important;
        object-fit: contain !important;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 10px;
    }
    .badge-destaque {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 6px;
        align-self: flex-start;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #0d6efd;
        color: white;
        width: 100%;
        margin-top: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO CARRINHO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- CARREGAMENTO DE DADOS COM CACHE ---
@st.cache_data(ttl=600)
def carregar_dados():
    if os.path.exists("camisas.json"):
        with open("camisas.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            for c in dados:
                if "pais" not in c or not c["pais"]:
                    caminho = c.get("nome_arquivo", "")
                    partes = caminho.replace("\\", "/").split("/")
                    if len(partes) > 1:
                        c["pais"] = partes[0].capitalize()
                    else:
                        c["pais"] = "Geral"
            return dados
    return []

camisas = carregar_dados()

if not camisas:
    st.warning("⚠️ O arquivo 'camisas.json' não foi encontrado ou está vazio. Adicione o arquivo de dados.")
else:
    # --- BARRA LATERAL (LOGO, CARRINHO E FILTROS) ---
    with st.sidebar:
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("## ⚽ RAMOS SPORTS")
        
        st.markdown("---")
        st.markdown("### 🛒 Carrinho de Compras")
        
        # Frase Promocional
        st.info("ℹ️ **Regras:**\n- Pedido mínimo: **2 peças**\n- **Pedidos com 3 ou mais peças você ganha um desconto especial!**")

        carrinho = st.session_state.carrinho
        
        if len(carrinho) > 0:
            st.markdown(f"**Itens selecionados ({len(carrinho)}):**")
            
            for idx, item in enumerate(carrinho):
                col_i1, col_i2 = st.columns([5, 1])
                versao_str = f" ({item['versao']})" if item.get('versao') else ""
                col_i1.markdown(f"• {item['time']}{versao_str}")
                if col_i2.button("❌", key=f"del_{idx}", help="Remover item"):
                    carrinho.pop(idx)
                    st.rerun()

            st.markdown("---")
            
            if len(carrinho) < 2:
                st.warning("⚠️ Adicione pelo menos **2 peças** para fechar o pedido.")
            else:
                st.success("✅ Pedido mínimo atingido!")
                if len(carrinho) >= 3:
                    st.markdown("🎉 **Desconto especial aplicado!**")

                texto_pedido = "Olá! Gostaria de encomendar as seguintes camisas na Ramos Sports:\n\n"
                for item in carrinho:
                    versao_str = f" - Versão {item['versao']}" if item.get('versao') else ""
                    texto_pedido += f"• {item['time']}{versao_str} ({item['preco']})\n"
                
                if len(carrinho) >= 3:
                    texto_pedido += "\n*(Aplicar desconto especial de 3 ou mais peças)*"
                
                texto_codificado = urllib.parse.quote(texto_pedido)
                link_wpp_final = f"https://wa.me/5511999999999?text={texto_codificado}"

                st.markdown(
                    f'<a href="{link_wpp_final}" target="_blank" style="text-decoration:none;">'
                    '<button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer;">'
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
        st.header("🔍 Buscar no Catálogo")

        busca_clube = st.text_input("🔎 Pesquisar Clube", placeholder="Ex: Flamengo, Real Madrid...")
        paises_disponiveis = ["Todos"] + sorted(list(set(c.get("pais", "Geral") for c in camisas)))
        pais_selecionado = st.selectbox("Selecione o País / Liga", paises_disponiveis)

    # --- FILTRAGEM ---
    camisas_filtradas = camisas
    if pais_selecionado != "Todos":
        camisas_filtradas = [c for c in camisas_filtradas if c.get("pais", "Geral") == pais_selecionado]
    if busca_clube.strip():
        camisas_filtradas = [c for c in camisas_filtradas if busca_clube.lower() in c["time"].lower()]

    camisas_ordenadas = sorted(camisas_filtradas, key=obter_prioridade_time)

    # --- CORPO PRINCIPAL DO SITE ---
    st.title("⚽ Ramos Sports - Catálogo Oficial")
    st.markdown("### 📢 **Pedidos com 3 ou mais peças você ganha um desconto especial** *(Mínimo de 2 peças por pedido)*")
    st.markdown(f"**Exibindo {len(camisas_ordenadas)} camisas encontradas**")
    st.markdown("---")

    # --- GRADE DE 3 COLUNAS COM RENDERIZAÇÃO HTML SEGURA ---
    colunas_por_linha = 3
    
    for i in range(0, len(camisas_ordenadas), colunas_por_linha):
        grupo_camisas = camisas_ordenadas[i:i + colunas_por_linha]
        cols = st.columns(colunas_por_linha)
        
        for idx, camisa in enumerate(grupo_camisas):
            with cols[idx]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                st.markdown('<div class="card-content">', unsafe_allow_html=True)
                
                e_popular = obter_prioridade_time(camisa) < 999
                if e_popular:
                    st.markdown('<span class="badge-destaque">🔥 MAIS VENDIDO</span>', unsafe_allow_html=True)

                caminho_img = camisa.get("nome_arquivo")
                
                # Renderiza a imagem usando tag HTML direta para respeitar rigorosamente o CSS de tamanho
                import base64
                if caminho_img and os.path.exists(caminho_img):
                    with open(caminho_img, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                    ext = caminho_img.split('.')[-1].lower()
                    mime = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'webp'] else "image/jpeg"
                    st.markdown(f'<img src="data:{mime};base64,{encoded_string}" class="img-produto">', unsafe_allow_html=True)
                else:
                    st.markdown('<img src="https://via.placeholder.com/300?text=Foto+Indispon%C3%ADvel" class="img-produto">', unsafe_allow_html=True)

                st.markdown(f"**{camisa['time']}**")
                
                if camisa.get("pais"):
                    st.caption(f"📍 {camisa['pais']}")
                
                if camisa.get("versao"):
                    st.markdown(f"Versão: *{camisa['versao']}*")
                    
                st.markdown(f"💰 **{camisa['preco']}**")
                
                st.markdown('</div>', unsafe_allow_html=True) # Fecha card-content
                
                # Botão fixo alinhado na base
                if st.button("➕ Adicionar", key=f"btn_{i}_{idx}_{camisa['time']}_{camisa.get('versao', '')}"):
                    st.session_state.carrinho.append(camisa)
                    st.success(f"{camisa['time']} adicionado!")
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True) # Fecha card-produto
