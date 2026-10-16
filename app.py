import json
import os
import re
import urllib.parse
import streamlit as st

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ramos Sports - Catálogo Oficial",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (Molduras, Tags e Destaques)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fundo escuro unificado */
    .stApp, div[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        color: #f5f5f5 !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: #0e1117 !important;
    }

    h1, h2, h3, h4, label, p, span {
        color: #ffffff !important;
    }

    /* Estilo dos inputs na sidebar */
    div[data-testid="stSidebar"] input, div[data-testid="stSidebar"] select {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }

    /* MOLDURA DO CARD ROBUSTA E EVIDENTE */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22 !important;
        border: 3px solid #f39c12 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 16px rgba(243, 156, 18, 0.25) !important;
    }

    /* Imagem padronizada dentro do card */
    div[data-testid="stVerticalBlockBorderWrapper"] img {
        border-radius: 10px;
        object-fit: cover;
        height: 280px !important;
        width: 100% !important;
        border: 1px solid #30363d;
    }

    /* Nome do Clube (Limpo) */
    .card-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-top: 12px;
        margin-bottom: 8px;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Tag de Modelo (Casa, Visitante, Terceiro, etc.) */
    .tag-modelo {
        background-color: #1f2937;
        color: #f39c12;
        border: 1px solid #f39c12;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }

    /* Tag de Preço */
    .tag-preco {
        background-color: #0d2818;
        color: #2ecc71;
        border: 1px solid #2ecc71;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 800;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 6px;
    }

    /* Tag de Frete Grátis */
    .tag-frete {
        background-color: #1e3a8a;
        color: #60a5fa;
        border: 1px solid #3b82f6;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        text-align: center;
        font-size: 0.8rem;
        margin-bottom: 12px;
        text-transform: uppercase;
    }

    /* Banner promocional de desconto no topo */
    .promo-banner {
        background-color: #1f2937;
        border-left: 5px solid #f39c12;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 25px;
        color: #f1c40f;
        font-weight: 600;
    }

    /* Botão Amarelo */
    .stButton > button {
        background-color: #f39c12;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 10px 16px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #e67e22;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CARREGAMENTO DOS DADOS E ORDENAÇÃO ALTERNADA (EUROPA + BRASIL)
# -------------------------------------------------------------


@st.cache_data
def carregar_dados():
  if os.path.exists("camisas.json"):
    with open("camisas.json", "r", encoding="utf-8") as f:
      return json.load(f)
  return []


produtos = carregar_dados()

CLUBES_EUROPA = [
    "real madrid",
    "barcelona",
    "paris saint germain",
    "psg",
    "manchester city",
    "bayern",
    "liverpool",
    "arsenal",
    "juventus",
    "milan",
]
CLUBES_BRASIL = [
    "flamengo",
    "palmeiras",
    "corinthians",
    "sao paulo",
    "santos",
    "gremio",
    "internacional",
    "atletico mineiro",
    "botafogo",
    "fluminense",
    "vasco",
]

RANKING_INTERCALADO = []
max_len = max(len(CLUBES_EUROPA), len(CLUBES_BRASIL))
for i in range(max_len):
  if i < len(CLUBES_EUROPA):
    RANKING_INTERCALADO.append(CLUBES_EUROPA[i])
  if i < len(CLUBES_BRASIL):
    RANKING_INTERCALADO.append(CLUBES_BRASIL[i])


def prioridade_destaque(camisa):
  nome = camisa.get("nome_limpo", "").lower()
  for index, clube in enumerate(RANKING_INTERCALADO):
    if clube in nome:
      return (0, index, nome)
  return (1, 0, nome)


# Função robusta para traduzir o modelo independentemente do formato no JSON
def traduzir_modelo(versao_original):
  v_str = str(versao_original).strip().upper()
  # Remove termos extras como "MODELO:", "VERSAO:", espaços e pontuações para isolar o identificador
  v_limpo = re.sub(r"[^A-Z0-9]", "", v_str)

  if v_limpo in ["I", "1", "MODELO1", "VERSAO1"]:
    return "Casa"
  elif v_limpo in ["II", "2", "MODELO2", "VERSAO2"]:
    return "Visitante"
  elif v_limpo in ["III", "3", "MODELO3", "VERSAO3"]:
    return "Terceiro Uniforme"
  else:
    return str(versao_original).strip()


# -------------------------------------------------------------
# BARRA LATERAL (LOGO, FILTROS E CARRINHO)
# -------------------------------------------------------------
with st.sidebar:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)

  st.markdown("### 🔍 Filtros de Busca")

  pesquisa = st.text_input(
      "Buscar por time:", placeholder="Ex: Real Madrid, Flamengo..."
  )

  paises_disponiveis = ["Todos"] + sorted(
      list(
          set(
              p["nome_arquivo"].split("/")[0]
              for p in produtos
              if "/" in p["nome_arquivo"]
          )
      )
  )
  pais_selecionado = st.selectbox(
      "Filtrar por País/Liga:", paises_disponiveis
  )

  st.markdown("---")
  st.markdown("### 🛒 Seu Carrinho")

  if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

  if len(st.session_state.carrinho) == 0:
    st.info("Carrinho vazio. Escolha no mínimo **2 peças** para fechar o pedido.")
  else:
    for idx, item in enumerate(st.session_state.carrinho):
      c1, c2 = st.columns([4, 1])
      with c1:
        st.write(f"• {item['time']} ({item['modelo']})")
      with c2:
        if st.button("❌", key=f"del_{idx}"):
          st.session_state.carrinho.pop(idx)
          st.rerun()

    total_pecas = len(st.session_state.carrinho)
    valor_unitario = 140.00
    valor_total = total_pecas * valor_unitario

    st.markdown("---")
    st.markdown(f"**Total de peças:** {total_pecas}")
    st.markdown(f"**Subtotal:** R$ {valor_total:,.2f}".replace(".", ","))

    if total_pecas >= 3:
      st.info(
          "🔥 **Desconto especial aplicado no fechamento via WhatsApp!** (Frete"
          " Grátis)"
      )
    else:
      st.info("📦 **Frete Grátis garantido!**")

    if total_pecas < 2:
      st.warning("⚠️ Adicione **pelo menos 2 peças** para liberar o WhatsApp.")
    else:
      st.success("✅ Pedido liberado!")

      msg = (
          f"Olá, Ramos Sports! Gostaria de fazer um pedido de {total_pecas}"
          " camisas (Frete Grátis):\n\n"
      )
      for item in st.session_state.carrinho:
        msg += f"• {item['time']} ({item['modelo']})\n"
      msg += f"\nTotal: R$ {valor_total:,.2f}"
      if total_pecas >= 3:
        msg += "\n*(Cliente apto ao desconto especial de 3+ peças)*"

      url_wa = f"https://wa.me/5511999999999?text={urllib.parse.quote(msg)}"

      st.markdown(
          f'<a href="{url_wa}" target="_blank">'
          '<button style="background-color: #25D366; color: white; border: none; '
          "padding: 10px; border-radius: 8px; font-weight: bold; width: 100%; "
          'margin-top: 10px;">Finalizar no WhatsApp</button></a>',
          unsafe_allow_html=True,
      )

    if st.button("Limpar Carrinho"):
      st.session_state.carrinho = []
      st.rerun()

# -------------------------------------------------------------
# ÁREA PRINCIPAL (BANNER + GRADE 3 COLUNAS)
# -------------------------------------------------------------

# Banner no topo
if os.path.exists("banner.jpg"):
  st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.png"):
  st.image("banner.png", use_container_width=True)

st.title("⚽ Catálogo Oficial de Camisas")

# Aviso em destaque sobre o pedido mínimo, frete grátis e o desconto
st.markdown(
    """
    <div class="promo-banner">
        📌 <b>Regras da Loja:</b> Pedido mínimo de <b>2 peças</b>.<br>
        📦 <b>Frete Grátis</b> para todo o Brasil em qualquer pedido!<br>
        🎁 <b>Oferta Especial:</b> Na compra de <b>3 ou mais peças</b>, você ganha um <b>desconto especial</b> no fechamento do seu pedido!
    </div>
""",
    unsafe_allow_html=True,
)

# Processamento e filtragem
produtos_filtrados = []
for p in produtos:
  nome_limpo = re.sub(
      r"\b(I{1,3}|IV|V|1|2|3|I{1,3}\s*i{1,3})$",
      "",
      p["time"],
      flags=re.IGNORECASE,
  ).strip()

  if pesquisa and pesquisa.lower() not in nome_limpo.lower():
    continue

  if (
      pais_selecionado != "Todos"
      and not p["nome_arquivo"].startswith(f"{pais_selecionado}/")
  ):
    continue

  p_copia = p.copy()
  p_copia["nome_limpo"] = nome_limpo if nome_limpo else p["time"]
  p_copia["modelo_formatado"] = traduzir_modelo(p.get("versao", ""))
  p_copia["preco_fixo"] = "R$ 140,00"
  produtos_filtrados.append(p_copia)

produtos_filtrados.sort(key=prioridade_destaque)

# Exibição dos cards
if not produtos_filtrados:
  st.warning("Nenhuma camisa encontrada com os filtros selecionados.")
else:
  cols_por_linha = 3
  grid_colunas = st.columns(cols_por_linha)

  for i, camisa in enumerate(produtos_filtrados):
    col_atual = grid_colunas[i % cols_por_linha]

    with col_atual:
      with st.container(border=True):
        if os.path.exists(camisa["nome_arquivo"]):
          st.image(camisa["nome_arquivo"], use_container_width=True)
        else:
          st.info("Imagem indisponível")

        # 1. Nome limpo do clube
        st.markdown(
            f"<div class='card-title'>{camisa['nome_limpo']}</div>",
            unsafe_allow_html=True,
        )

        # 2. Tag de Modelo formatado (Casa, Visitante, Terceiro Uniforme, etc.)
        st.markdown(
            f"<div class='tag-modelo'>Modelo: {camisa['modelo_formatado']}</div>",
            unsafe_allow_html=True,
        )

        # 3. Tag de Preço Fixo (R$ 140,00)
        st.markdown(
            f"<div class='tag-preco'>{camisa['preco_fixo']}</div>",
            unsafe_allow_html=True,
        )

        # 4. Tag de Frete Grátis
        st.markdown(
            "<div class='tag-frete'>🚚 Frete Grátis</div>",
            unsafe_allow_html=True,
        )

        # 5. Botão de Adicionar ao Carrinho
        if st.button("Adicionar ao Carrinho", key=f"btn_{camisa['id']}"):
          st.session_state.carrinho.append({
              "id": camisa["id"],
              "time": camisa["nome_limpo"],
              "modelo": camisa["modelo_formatado"],
              "preco": 140.00,
          })
          st.success("Adicionado!")
          st.rerun()
