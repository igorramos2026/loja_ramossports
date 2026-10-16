import json
import os
import re
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Ramos Sports - Catálogo Oficial", page_icon="⚽", layout="wide"
)

# -------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (Tema Preto e Amarelo / Visual Limpo)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #f39c12;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #d68910;
        color: #ffffff;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #f1c40f;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .card-price {
        font-size: 1rem;
        color: #2ecc71;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CARREGAMENTO DOS DADOS E ATIVOS
# -------------------------------------------------------------


@st.cache_data
def carregar_dados():
  if os.path.exists("camisas.json"):
    with open("camisas.json", "r", encoding="utf-8") as f:
      return json.load(f)
  return []


produtos = carregar_dados()

# Barra Lateral (Logo e Carrinho)
with st.sidebar:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)

  st.title("🛒 Carrinho de Compras")

  # Inicializa o carrinho na sessão
  if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

  # Exibe os itens no carrinho
  if len(st.session_state.carrinho) == 0:
    st.info(
        "Seu carrinho está vazio. Escolha ao menos 2 peças para fechar o"
        " pedido!"
    )
  else:
    for idx, item in enumerate(st.session_state.carrinho):
      col_item1, col_item2 = st.columns([4, 1])
      with col_item1:
        st.write(f"• {item['time']} (Ver. {item['versao']})")
      with col_item2:
        if st.button("❌", key=f"del_{idx}"):
          st.session_state.carrinho.pop(idx)
          st.rerun()

    total_pecas = len(st.session_state.carrinho)
    preco_unitario = 150.00
    valor_total = total_pecas * preco_unitario

    st.markdown("---")
    st.markdown(f"**Total de peças:** {total_pecas}")
    st.markdown(f"**Valor total:** R$ {valor_total:,.2f}".replace(".", ","))

    if total_pecas < 2:
      st.warning(
          "⚠️ Pedido mínimo de **2 peças** para finalizar a compra no"
          " WhatsApp."
      )
    else:
      st.success("✅ Pedido apto para envio!")
      # Monta mensagem do WhatsApp
      mensagem = (
          f"Olá! Gostaria de fazer o pedido de {total_pecas} camisas na Ramos"
          " Sports:\n"
      )
      for item in st.session_state.carrinho:
        mensagem += f"- {item['time']} (Versão {item['versao']})\n"
      mensagem += f"Total: R$ {valor_total:,.2f}"

      import urllib.parse

      whatsapp_url = (
          f"https://wa.me/5511999999999?text={urllib.parse.quote(mensagem)}"
      )
      st.markdown(
          f'<p style="text-align: center;"><a href="{whatsapp_url}"'
          ' target="_blank"><button style="background-color: #25D366; color:'
          ' white; border: none; padding: 10px 20px; border-radius: 8px; font-weight:'
          ' bold; width: 100%;">Finalizar Pedido no'
          " WhatsApp</button></a></p>",
          unsafe_allow_html=True,
      )

    if st.button("Limpar Carrinho"):
      st.session_state.carrinho = []
      st.rerun()

# -------------------------------------------------------------
# CONTEÚDO PRINCIPAL (BANNER E CATÁLOGO)
# -------------------------------------------------------------

# Exibe o Banner no Topo
if os.path.exists("banner.jpg"):
  st.image("banner.jpg", use_container_width=True)
elif os.path.exists("banner.png"):
  st.image("banner.png", use_container_width=True)

st.title("⚽ Ramos Sports - Catálogo Oficial")
st.markdown(
    "Explore nossa coleção exclusiva de camisas de futebol. **Regra da loja:"
    " Mínimo de 2 peças por pedido!**"
)

# Filtros de Pesquisa e País
col_f1, col_f2 = st.columns(2)

with col_f1:
  pesquisa = st.text_input(
      "🔍 Buscar clube:", placeholder="Digite o nome do time..."
  )

# Extrai os países/ligas das pastas dos arquivos
paises_disponíveis = ["Todos"] + sorted(
    list(
        set(
            p["nome_arquivo"].split("/")[0]
            for p in produtos
            if "/" in p["nome_arquivo"]
        )
    )
)

with col_f2:
  pais_selecionado = st.selectbox("🌍 Filtrar por País/Liga:", paises_disponíveis)

# Filtragem dos produtos
produtos_filtrados = []
for p in produtos:
  # Limpeza do nome do clube usando Regex para remover números/sufixos indesejados
  nome_limpo = re.sub(
      r"\b(I{1,3}|IV|V|1|2|3|I{1,3}\s*i{1,3})$",
      "",
      p["time"],
      flags=re.IGNORECASE,
  ).strip()

  # Filtro por texto
  if pesquisa and pesquisa.lower() not in nome_limpo.lower():
    continue

  # Filtro por país
  if (
      pais_selecionado != "Todos"
      and not p["nome_arquivo"].startswith(f"{pais_selecionado}/")
  ):
    continue

  p_copia = p.copy()
  p_copia["nome_limpo"] = nome_limpo if nome_limpo else p["time"]
  produtos_filtrados.append(p_copia)

# Exibição em Grade de 3 Colunas
if not produtos_filtrados:
  st.warning("Nenhuma camisa encontrada com os filtros informados.")
else:
  cols_por_linha = 3
  grid_colunas = st.columns(cols_por_linha)

  for i, camisa in enumerate(produtos_filtrados):
    col_atual = grid_colunas[i % cols_por_linha]

    with col_atual:
      with st.container():
        # Exibe imagem da camisa se existir no repositório
        if os.path.exists(camisa["nome_arquivo"]):
          st.image(camisa["nome_arquivo"], use_container_width=True)
        else:
          st.info(f"Imagem não encontrada: {camisa['nome_arquivo']}")

        st.markdown(
            f"<div class='card-title'>{camisa['nome_limpo']} — Versão"
            f" {camisa['versao']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card-price'>{camisa['preco']}</div>",
            unsafe_allow_html=True,
        )

        if st.button("Adicionar ao Carrinho", key=f"add_{camisa['id']}"):
          st.session_state.carrinho.append({
              "id": camisa["id"],
              "time": camisa["nome_limpo"],
              "versao": camisa["versao"],
              "preco": camisa["preco"],
          })
          st.success(
              f"Adicionado: {camisa['nome_limpo']} (Ver. {camisa['versao']})"
          )
          st.rerun()

        st.markdown("---")
