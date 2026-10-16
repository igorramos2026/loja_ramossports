import streamlit as st
import json
import os
import urllib.parse
import re

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
    return 999

def limpar_nome_clube(nome):
    """Remove sufixos numéricos ou romanos indesejados (ex: 'Palmeiras lii' -> 'Palmeiras')"""
    nome_limpo = re.sub(r'\b(i{1,3}|iv|v|vi{0,3}|\d+)\b$', '', nome, flags=re.IGNORECASE).strip()
    return nome_limpo if nome_limpo else nome

# --- ESTILO E PADRONIZAÇÃO (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    div[data-testid="stImage"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 5px;
        border: 1px solid #e9ecef;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 220px;
        overflow: hidden;
    }
    div[data-testid="stImage"] img {
        max-height: 210px !important;
        object-fit: contain !important;
        width: auto !important;
    }
    .badge-destaque {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 4px;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #0d6efd;
        color: white;
        width: 100%;
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
    # --- BARRA LATERAL ---
    with st.sidebar:
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("## ⚽ RAMOS SPORTS")
        
        st.markdown("---")
        st.markdown("### 🛒 Carrinho de Compras")
        
        st.info("ℹ️ **Regras:**\n- Pedido mínimo: **2 peças**\n- **Pedidos com 3 ou mais peças você ganha um desconto especial!**")

        carrinho = st.session_state.carrinho
        
        if len(carrinho) > 0:
            st.markdown(f"**Itens selecionados ({len(carrinho)}):**")
            
            for idx, item in enumerate(carrinho):
                col_i1, col_i2 = st.columns([5, 1])
                nome_exibir = limpar_nome_clube(item['time'])
                versao_str = f" ({item['versao']})" if item.get('versao') else ""
                col_i1.markdown(f"• {nome_exibir}{versao_str}")
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
                    nome_exibir = limpar_nome_clube(item['time'])
                    versao_str = f" - Versão {item['versao']}" if item.get('versao') else ""
                    texto_pedido += f"• {nome_exibir}{versao_str} ({item['preco']})\n"
                
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

    # --- GRADE DE 3 COLUNAS ---
    colunas_por_linha = 3
    
    for i in range(0, len(camisas_ordenadas), colunas_por_linha):
        grupo_camisas = camisas_ordenadas[i:i + colunas_por_linha]
        cols = st.columns(colunas_por_linha)
        
        for idx, camisa in enumerate(grupo_camisas):
            with cols[idx]:
                e_popular = obter_prioridade_time(camisa) < 999
                if e_popular:
                    st.markdown('<span class="badge-destaque">🔥 MAIS VENDIDO</span>', unsafe_allow_html=True)

                caminho_img = camisa.get("nome_arquivo")
                if caminho_img and os.path.exists(caminho_img):
                    st.image(caminho_img)
                    
                    # Codifica a imagem em base64 para abrir em tela cheia/nova aba com tamanho grande ao clicar
                    import base64
                    with open(caminho_img, "rb") as f_img:
                        b64_data = base64.b64encode(f_img.read()).decode()
                    ext_img = caminho_img.split('.')[-1].lower()
                    mime_tipo = f"image/{ext_img}" if ext_img in ['jpg', 'jpeg', 'png', 'webp'] else "image/jpeg"
                    
                    st.markdown(
                        f'<div style="text-align: center; margin-bottom: 8px;">'
                        f'<a href="data:{mime_tipo};base64,{b64_data}" target="_blank" style="font-size: 13px; color: #0d6efd; text-decoration: none; font-weight: 600;">'
                        f'🔍 Ver foto em tamanho real'
                        f'</a></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.image("https://via.placeholder.com/300?text=Foto+Indisponível")

                # Nome limpo do clube (sem sufixos numéricos/romanos)
                nome_limpo = limpar_nome_clube(camisa['time'])
                st.markdown(f"**{nome_limpo}**")
                
                if camisa.get("pais"):
                    st.caption(f"📍 {camisa['pais']}")
                
                if camisa.get("versao"):
                    st.markdown(f"Versão: *{camisa['versao']}*")
                    
                st.markdown(f"💰 **{camisa['preco']}**")
                
                if st.button("➕ Adicionar", key=f"btn_{i}_{idx}_{camisa['time']}_{camisa.get('versao', '')}"):
                    st.session_state.carrinho.append(camisa)
                    st.success(f"{nome_limpo} adicionado!")
                    st.rerun()
                
                st.markdown("---")
