import streamlit as st
import json
import os

# Configuração da página para ocupar a largura total e ter um visual profissional de loja
st.set_page_config(page_title="Loja Ramos Sports - Catálogo de Camisas", page_icon="⚽", layout="wide")

# Título Principal da Loja
st.title("⚽ Ramos Sports - Catálogo Exclusivo")
st.markdown("Encontre as melhores camisas de futebol de clubes do mundo inteiro!")

# Função para carregar o arquivo JSON do catálogo
@st.cache_data
def carregar_dados():
    if os.path.exists("camisas.json"):
        with open("camisas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

camisas = carregar_dados()

if not camisas:
    st.warning("⚠️ O arquivo 'camisas.json' não foi encontrado ou está vazio. Certifique-se de que ele foi enviado para o repositório.")
else:
    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header("🔍 Filtrar Catálogo")

    # Filtro por Clube
    clubes_disponiveis = ["Todos"] + sorted(list(set(c["time"] for c in camisas)))
    clube_selecionado = st.sidebar.selectbox("Selecione o Clube", clubes_disponiveis)

    # Filtro por Versão
    versoes_disponiveis = ["Todas"] + sorted(list(set(c["versao"] for c in camisas)))
    versao_selecionada = st.sidebar.selectbox("Selecione a Versão", versoes_disponiveis)

    # Aplicando os filtros dinamicamente
    camisas_filtradas = camisas
    if clube_selecionado != "Todos":
        camisas_filtradas = [c for c in camisas_filtradas if c["time"] == clube_selecionado]
    if versao_selecionada != "Todas":
        camisas_filtradas = [c for c in camisas_filtradas if c["versao"] == versao_selecionada]

    st.markdown(f"### Exibindo {len(camisas_filtradas)} camisas disponíveis")
    st.markdown("---")

    # --- EXIBIÇÃO EM GRADE (4 COLUNAS) ---
    colunas_por_linha = 4
    colunas = st.columns(colunas_por_linha)

    for index, camisa in enumerate(camisas_filtradas):
        coluna_atual = colunas[index % colunas_por_linha]
        
        with coluna_atual:
            # Caminho relativo da imagem (ex: Brasil/Palmeiras_I.jpg)
            caminho_img = camisa.get("nome_arquivo")
            
            # Exibe a imagem se ela existir no repositório
            if caminho_img and os.path.exists(caminho_img):
                st.image(caminho_img, use_container_width=True)
            else:
                # Caso a imagem demore a sincronizar na nuvem, exibe o nome de referência
                st.image("https://via.placeholder.com/300?text=Imagem+Carregando", use_container_width=True)

            st.markdown(f"**{camisa['time']} - Versão {camisa['versao']}**")
            st.markdown(f"💰 **{camisa['preco']}**")
            
            # Botão de Compra customizado com link direto para o WhatsApp
            st.markdown(
                f'<a href="{camisa["link_whatsapp"]}" target="_blank">'
                '<button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">'
                '💬 Comprar via WhatsApp'
                '</button></a>',
                unsafe_allow_html=True
            )
            st.markdown("---")
