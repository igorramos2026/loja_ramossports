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
# ESTILIZAÇÃO CSS CUSTOMIZADA (Simetria, Cores e Tipografia)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Estilo geral da aplicação */
    .stApp {
        background-color: #0e1117;
        color: #f5f5f5;
    }
    
    /* Titulos e textos com excelente legibilidade */
    h1, h2, h3, h4, label {
        color: #ffffff !important;
    }
    
    /* Container simétrico para o card de produto */
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 480px;
    }

    /* Ajuste para imagens simétricas */
    div[data-testid="column"] img {
        border-radius: 8px;
        object-fit: cover;
        max-height: 280px;
        width: 100%;
    }

    /* Detalhes do Card */
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f39c12;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 4px;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .card-price {
        font-size: 1.1rem;
        color: #2ecc71;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Estilização dos botões principais */
    .stButton > button {
        background-color: #f39c12;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 8px 16px;
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
# CARREGAMENTO DOS DADOS E ORDENAÇÃO POR POPULARIDADE
# -------------------------------------------------------------


@st.cache_data
def carregar_dados():
  if os.path.exists("camisas.json"):
    with open("camisas.json", "r", encoding="utf-8") as f:
      return json.load(f)
  return []


produtos = carregar_dados()

# Lista de clubes de alta demanda/populares
CLUBES_POPULARES = [
    "real madrid",
    "barcelona",
    "paris saint germain",
    "psg",
    "manchester city",
    "manchester united",
    "bayern",
    "liverpool",
    "arsenal",
    "juventus",
    "milan",
    "inter",
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


def prioridade_popularidade(camisa):
  nome = camisa.get("nome_limpo", "").lower()
  for i, clube in enumerate(CLUBES_POPULARES):
    if clube in nome:
      return (0, i, nome)
  return (1, 0, nome)


# -------------------------------------------------------------
# BARRA LATERAL (LOGO, FILTROS E CARRINHO)
# -------------------------------------------------------------
with st.sidebar:
  # Logo da Ramos Sports
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)

  st.markdown("### 🔍 Filtros de Busca")

  pesquisa = st.text_input(
      "Buscar por time:", placeholder="Ex: Real Madrid, Flamengo..."
  )

  # Extração dos países/ligas das pastas
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
        st.write(f"• {item['time']} ({item['versao']})")
      with c2:
        if st.button("❌", key=f"del_{idx}"):
          st.session_state.carrinho.pop(idx)
          st.rerun()

    total_pecas = len(st.session_state.carrinho)
    valor_total = total_pecas * 150.00

    st.markdown("---")
    st.markdown(f"**Total de peças:** {total_pecas}")
    st.markdown(f"**Subtotal:** R$ {valor_total:,.2f}".replace(".", ","))

    if total_pecas < 2:
      st.warning("⚠️ Adicione **pelo menos 2 peças** para liberar o WhatsApp.")
    else:
      st.success("✅ Pedido liberado!")

      # Montagem da mensagem do WhatsApp
      msg = (
          f"Olá, Ramos Sports! Gostaria de fazer um pedido de {total_pecas}"
          " camisas:\n\n"
      )
      for item in st.session_state.carrinho:
        msg += f"• {item['time']} (Versão {item['versao']})\n"
      msg += f"\nTotal: R$ {valor_total:,.2f}"

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

# Exibição do Banner no Topo
if os.path.exists("banner.jpg"):
  st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.png"):
  st.image("banner.png", use_container_width=True)

st.title("⚽ Catálogo Oficial de Camisas")
st.markdown("Selecione suas camisas favoritas. **Pedido mínimo de 2 peças.**")

# Processamento e Filtragem dos Produtos
produtos_filtrados = []
for p in produtos:
  # Limpeza do nome do time via Regex (remove sufixos numéricos/romanos)
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
  produtos_filtrados.append(p_copia)

# Ordenação: Clubes mais populares primeiro
produtos_filtrados.sort(key=prioridade_popularidade)

# Exibição na Grade de 3 Colunas com Linhas Simétricas
if not produtos_filtrados:
  st.warning("Nenhuma camisa encontrada com os filtros selecionados.")
else:
  cols_por_linha = 3
  grid_colunas = st.columns(cols_por_linha)

  for i, camisa in enumerate(produtos_filtrados):
    col_atual = grid_colunas[i % cols_por_linha]

    with col_atual:
      with st.container():
        if os.path.exists(camisa["nome_arquivo"]):
          st.image(camisa["nome_arquivo"], use_container_width=True)
        else:
          st.info("Imagem indisponível")

        st.markdown(
            f"<div class='card-title'>{camisa['nome_limpo']} —"
            f" {camisa['versao']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card-price'>{camisa['preco']}</div>",
            unsafe_allow_html=True,
        )

        if st.button("Adicionar ao Carrinho", key=f"btn_{camisa['id']}"):
          st.session_state.carrinho.append({
              "id": camisa["id"],
              "time": camisa["nome_limpo"],
              "versao": camisa["versao"],
              "preco": camisa["preco"],
          })
          st.success("Adicionado!")
          st.rerun()
