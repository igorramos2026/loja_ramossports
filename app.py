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

# --- OTIMIZAÇÃO DE ESTILO E DESIGN ASSIMÉTRICO (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .card-produto {
        background: white;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .badge-destaque {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #0d6efd;
        color: white;
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
            # Tenta preencher a propriedade 'pais' a partir do caminho do arquivo se não existir no JSON
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
        
        # Frase Promocional Atualizada
        st.info("ℹ️ **Regras:**\n- Pedido mínimo: **2 peças**\n- **Pedidos com 3 ou mais peças você ganha um desconto especial!**")

        carrinho = st.session_state.carrinho
        
        if len(carrinho) > 0:
            st.markdown(f"**Itens selecionados ({len(carrinho)}):**")
            
            for idx, item in enumerate(carrinho):
                col_i1, col_i2 = st.columns([5, 1])
                col_i1.markdown(f"• {item['time']} ({item['versao']})")
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
                    texto_pedido += f"• {item['time']} - Versão {item['versao']} ({item['preco']})\n"
                
                if len(carrinho) >= 3:
                    texto_pedido += "\n*(Aplicar desconto especial de 3 ou mais peças)*"
                
                texto_codificado = urllib.parse.quote(texto_pedido)
                # Altere para o seu WhatsApp real
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
        st.header("🔍 Filtrar Catálogo")

        # 1. Pesquisa Rápida por Nome de Clube
        busca_clube = st.text_input("🔎 Pesquisar Clube", placeholder="Ex: Flamengo, Real Madrid...")

        # 2. Filtro por País/Pasta
        paises_disponiveis = ["Todos"] + sorted(list(set(c.get("pais", "Geral") for c in camisas)))
        pais_selecionado = st.selectbox("Selecione o País / Liga", paises_disponiveis)

        # 3. Filtro por Seleção na Lista de Clubes
        clubes_disponiveis = ["Todos"] + sorted(list(set(c["time"] for c in camisas)))
        clube_selecionado = st.selectbox("Selecione o Clube (Lista)", clubes_disponiveis)

        # 4. Filtro por Versão
        versoes_disponiveis = ["Todas"] + sorted(list(set(c["versao"] for c in camisas)))
        versao_selecionada = st.selectbox("Selecione a Versão", versoes_disponiveis)

    # --- FILTRAGEM MULTICRITÉRIO ---
    camisas_filtradas = camisas
    
    # Filtro por País/Liga
    if pais_selecionado != "Todos":
        camisas_filtradas = [c for c in camisas_filtradas if c.get("pais", "Geral") == pais_selecionado]
    
    # Filtro por Busca Digitada
    if busca_clube.strip():
        camisas_filtradas = [c for c in camisas_filtradas if busca_clube.lower() in c["time"].lower()]
        
    # Filtro por Seleção na Lista
    if clube_selecionado != "Todos":
        camisas_filtradas = [c for c in camisas_filtradas if c["time"] == clube_selecionado]
        
    # Filtro por Versão
    if versao_selecionada != "Todas":
        camisas_filtradas = [c for c in camisas_filtradas if c["versao"] == versao_selecionada]

    # Ordena para colocar os mais populares no topo
    camisas_ordenadas = sorted(camisas_filtradas, key=obter_prioridade_time)

    # --- CORPO PRINCIPAL DO SITE ---
    st.title("⚽ Ramos Sports - Catálogo Oficial")
    st.markdown("### 📢 **Pedidos com 3 ou mais peças você ganha um desconto especial** *(Mínimo de 2 peças por pedido)*")
    st.markdown(f"**Exibindo {len(camisas_ordenadas)} camisas encontradas**")
    st.markdown("---")

    # --- GRADE ASSIMÉTRICA INTUITIVA ---
    itens_por_linha = 3
    
    for i in range(0, len(camisas_ordenadas), itens_por_linha):
        grupo_camisas = camisas_ordenadas[i:i + itens_por_linha]
        
        linha_index = i // itens_por_linha
        if linha_index % 2 == 0:
            proporcoes = [1.3, 1.0, 1.0]
        else:
            proporcoes = [1.0, 1.0, 1.3]

        cols = st.columns(proporcoes[:len(grupo_camisas)])
        
        for idx, camisa in enumerate(grupo_camisas):
            with cols[idx]:
                st.markdown('<div class="card-produto">', unsafe_allow_html=True)
                
                e_popular = obter_prioridade_time(camisa) < 999
                if e_popular:
                    st.markdown('<span class="badge-destaque">🔥 MAIS VENDIDO</span>', unsafe_allow_html=True)

                caminho_img = camisa.get("nome_arquivo")
                if caminho_img and os.path.exists(caminho_img):
                    st.image(caminho_img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300?text=Foto+Indisponível", use_container_width=True)

                st.markdown(f"**{camisa['time']}**")
                if camisa.get("pais"):
                    st.caption(f"📍 {camisa['pais']}")
                st.markdown(f"Versão: *{camisa['versao']}*")
                st.markdown(f"💰 **{camisa['preco']}**")
                
                if st.button("➕ Adicionar", key=f"btn_{i}_{idx}_{camisa['time']}", use_container_width=True):
                    st.session_state.carrinho.append(camisa)
                    st.success(f"{camisa['time']} adicionado!")
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
