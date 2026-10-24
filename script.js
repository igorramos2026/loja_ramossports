// =====================================================================
// RAMOS SPORTS - CATÁLOGO (script.js)
//
// Correções aplicadas:
//  1) Modelo (Casa/Visitante/Terceiro) agora é identificado a partir do
//     nome do arquivo da imagem, não só do campo "versao" — evita exibir
//     modelo errado em fotos duplicadas (ex: "Toulouse_III_1.jpeg").
//  2) Cards e itens do carrinho agora são montados via DOM (createElement
//     + textContent), não mais com innerHTML concatenando strings — isso
//     elimina o bug de escaping (ex: times com apóstrofo no nome) e
//     deixa o código mais seguro de um jeito geral.
//  3) Imagens com loading="lazy" + decoding="async" (catálogo tem 400+
//     produtos, isso evita carregar tudo de uma vez).
//  4) Busca com debounce (não refaz o grid inteiro a cada tecla digitada).
//  5) Carrinho agora é salvo no localStorage (sobrevive a F5 / fechar aba).
//
// Melhorias extras:
//  - Filtro por Modelo (Casa / Visitante / Terceiro Uniforme).
//  - Contador de resultados acima da vitrine.
//  - Modais fecham com Esc, e o do carrinho também fecha clicando fora.
//  - Feedback visual rápido no botão ao adicionar ao carrinho.
// =====================================================================

const SEU_NUMERO_WHATSAPP = "5544997339870";

// ⚠️ ATENÇÃO: o camisas.json tem "preco": "R$ 150,00" em todos os itens,
// mas o site sempre mostrou R$ 140,00. Mantive 140 aqui (igual já estava
// no ar) — confirme qual é o valor certo e ajuste essa constante se precisar.
const PRECO_UNITARIO = 140.00;

const CHAVE_CARRINHO = "ramos_sports_carrinho";

let produtosGlobais = [];
let carrinho = [];

const CLUBES_EUROPA = ["real madrid", "barcelona", "paris saint germain", "psg", "manchester city", "bayern", "liverpool", "arsenal", "juventus", "milan"];
const CLUBES_BRASIL = ["flamengo", "palmeiras", "corinthians", "sao paulo", "santos", "gremio", "internacional", "atletico mineiro", "botafogo", "fluminense", "vasco"];

// ---------------------------------------------------------------------
// UTILITÁRIOS
// ---------------------------------------------------------------------

function getBasePath() {
    const path = window.location.pathname;
    if (path.includes('/') && path.split('/')[1]) {
        const repoName = path.split('/')[1];
        if (repoName && repoName !== 'index.html') {
            return `/${repoName}/`;
        }
    }
    return './';
}

// MELHORIA: debounce genérico, usado na busca por texto.
function debounce(fn, delay = 250) {
    let timer = null;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// CORREÇÃO (bug de modelo): tenta extrair o modelo (I/II/III/IV/V) direto
// do nome do arquivo, que é mais confiável que o campo "versao" quando
// existem fotos duplicadas do mesmo uniforme (ex: "..._III_1.jpeg",
// "..._III(1).jpeg"). Retorna null se não encontrar nada reconhecível.
function extrairModeloDoArquivo(nomeArquivo) {
    if (!nomeArquivo) return null;

    const nomeBase = nomeArquivo.split("/").pop().replace(/\.[^/.]+$/, ""); // remove pasta e extensão
    const semContadorDuplicata = nomeBase.replace(/\(\d+\)$/, ""); // remove "(1)", "(2)" etc no final
    const partes = semContadorDuplicata.split("_");

    // percorre de trás pra frente: o último token numérico costuma ser
    // só um contador de foto duplicada, não o modelo em si.
    for (let i = partes.length - 1; i >= 0; i--) {
        const token = partes[i].toUpperCase();
        if (["I", "II", "III", "IV", "V"].includes(token)) {
            return token;
        }
    }
    return null;
}

function limparNomeClube(nomeOriginal) {
    if (!nomeOriginal) return "";
    return nomeOriginal.replace(/\b(I{1,3}|IV|V|1|2|3|I{1,3}\s*i{1,3})$/gi, "").trim();
}

function traduzirModelo(versaoOriginal) {
    if (!versaoOriginal) return "Casa";
    const vStr = String(versaoOriginal).trim().toUpperCase();
    const vLimpo = vStr.replace(/[^A-Z0-9]/g, "");

    if (["I", "1", "MODELO1", "VERSAO1"].includes(vLimpo)) return "Casa";
    if (["II", "2", "MODELO2", "VERSAO2"].includes(vLimpo)) return "Visitante";
    if (["III", "3", "MODELO3", "VERSAO3"].includes(vLimpo)) return "Terceiro Uniforme";
    return String(versaoOriginal).trim();
}

function prioridadeDestaque(nomeLimpo) {
    const nomeLower = (nomeLimpo || "").toLowerCase();
    let ranking = [];
    let maxLen = Math.max(CLUBES_EUROPA.length, CLUBES_BRASIL.length);
    for (let i = 0; i < maxLen; i++) {
        if (i < CLUBES_EUROPA.length) ranking.push(CLUBES_EUROPA[i]);
        if (i < CLUBES_BRASIL.length) ranking.push(CLUBES_BRASIL[i]);
    }
    for (let i = 0; i < ranking.length; i++) {
        if (nomeLower.includes(ranking[i])) return i;
    }
    return 999;
}

// ---------------------------------------------------------------------
// INICIALIZAÇÃO
// ---------------------------------------------------------------------

window.addEventListener("DOMContentLoaded", () => {
    carregarCarrinhoSalvo(); // MELHORIA: restaura carrinho salvo (localStorage)

    const jsonPath = getBasePath() + "camisas.json";

    fetch(jsonPath)
        .then(response => {
            if (!response.ok) throw new Error(`Erro ${response.status}`);
            return response.json();
        })
        .then(data => {
            produtosGlobais = data;
            popularFiltroPaises(data);
            filtrarProdutos();
        })
        .catch(error => {
            console.error(error);
            const grid = document.getElementById("catalogo-grid");
            if (grid) {
                grid.innerHTML = `<p class="sem-resultados" style="color:#ff4d4d;">
                    ⚠️ Não foi possível carregar os produtos. Verifique o arquivo <b>camisas.json</b>.
                </p>`;
            }
        });

    // CORREÇÃO/MELHORIA: busca com debounce + listeners dos filtros
    const inputBusca = document.getElementById("input-busca");
    const selectPais = document.getElementById("select-pais");
    const selectModelo = document.getElementById("select-modelo");

    if (inputBusca) inputBusca.addEventListener("input", debounce(filtrarProdutos, 250));
    if (selectPais) selectPais.addEventListener("change", filtrarProdutos);
    if (selectModelo) selectModelo.addEventListener("change", filtrarProdutos);

    // MELHORIA: fechar modais com Esc
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            fecharImagem();
            const cartModal = document.getElementById("cart-modal");
            if (cartModal) cartModal.style.display = "none";
        }
    });

    // MELHORIA: fechar o carrinho clicando fora do conteúdo (no fundo escuro)
    const cartModal = document.getElementById("cart-modal");
    if (cartModal) {
        cartModal.addEventListener("click", (e) => {
            if (e.target === cartModal) toggleCarrinho();
        });
    }
});

function popularFiltroPaises(produtos) {
    const select = document.getElementById("select-pais");
    if (!select) return;

    const paisesSet = new Set();
    produtos.forEach(p => {
        let arq = p.nome_arquivo || p.imagem || p.foto || "";
        if (arq) {
            let caminhoLimpo = arq.trim();
            if (caminhoLimpo.startsWith('/')) caminhoLimpo = caminhoLimpo.substring(1);
            if (caminhoLimpo.includes("/")) {
                const pais = caminhoLimpo.split("/")[0];
                if (pais) paisesSet.add(pais);
            }
        }
    });

    select.innerHTML = '<option value="Todos">🌍 Todos os Países/Ligas</option>';
    Array.from(paisesSet).sort().forEach(pais => {
        const option = document.createElement("option");
        option.value = pais;
        option.textContent = pais;
        select.appendChild(option);
    });
}

// ---------------------------------------------------------------------
// FILTRAGEM E RENDERIZAÇÃO
// ---------------------------------------------------------------------

function filtrarProdutos() {
    const inputBusca = document.getElementById("input-busca");
    const selectPais = document.getElementById("select-pais");
    const selectModelo = document.getElementById("select-modelo");

    const termoBusca = inputBusca ? inputBusca.value.toLowerCase() : "";
    const paisSelecionado = selectPais ? selectPais.value : "Todos";
    const modeloSelecionado = selectModelo ? selectModelo.value : "Todos";

    let filtrados = produtosGlobais.map(p => {
        let nomeOriginal = p.time || p.nome || p.clube || "";
        let nomeLimpo = limparNomeClube(nomeOriginal);
        if (!nomeLimpo) nomeLimpo = nomeOriginal || "Camisa";

        const caminhoImagem = p.nome_arquivo || p.imagem || p.foto || "";

        // CORREÇÃO: prioriza o modelo identificado pelo nome do arquivo;
        // só cai pro campo "versao" se não conseguir identificar pela imagem.
        const modeloDoArquivo = extrairModeloDoArquivo(caminhoImagem);
        const modeloBase = modeloDoArquivo || (p.versao || p.modelo || "");

        return {
            ...p,
            nome_limpo: nomeLimpo,
            modelo_formatado: traduzirModelo(modeloBase),
        };
    }).filter(p => {
        const matchBusca = p.nome_limpo.toLowerCase().includes(termoBusca);

        let caminhoArquivo = (p.nome_arquivo || p.imagem || p.foto || "").trim();
        if (caminhoArquivo.startsWith('/')) caminhoArquivo = caminhoArquivo.substring(1);
        const matchPais = (paisSelecionado === "Todos" || caminhoArquivo.startsWith(paisSelecionado + "/"));

        const matchModelo = (modeloSelecionado === "Todos" || p.modelo_formatado === modeloSelecionado);

        return matchBusca && matchPais && matchModelo;
    });

    filtrados.sort((a, b) => prioridadeDestaque(a.nome_limpo) - prioridadeDestaque(b.nome_limpo));
    renderizarCatalogo(filtrados);
}

function atualizarContadorResultados(qtd) {
    const el = document.getElementById("contador-resultados");
    if (!el) return;
    el.textContent = qtd === 1 ? "1 camisa encontrada" : `${qtd} camisas encontradas`;
}

// CORREÇÃO (bug de escaping): cards agora são montados com createElement +
// textContent + addEventListener, em vez de innerHTML com strings
// concatenadas. Isso elimina o risco de quebrar o HTML (e os cliques)
// quando um nome de time tem aspas, apóstrofo etc.
function renderizarCatalogo(produtos) {
    const grid = document.getElementById("catalogo-grid");
    if (!grid) return;
    grid.innerHTML = "";

    atualizarContadorResultados(produtos.length);

    if (produtos.length === 0) {
        const vazio = document.createElement("p");
        vazio.className = "sem-resultados";
        vazio.textContent = "Nenhuma camisa encontrada.";
        grid.appendChild(vazio);
        return;
    }

    const basePath = getBasePath();
    const fragment = document.createDocumentFragment();

    produtos.forEach(p => {
        let arqOriginal = p.nome_arquivo || p.imagem || p.foto || "";
        let imgSrc = arqOriginal.trim();
        if (imgSrc.startsWith('/')) imgSrc = imgSrc.substring(1);
        const fullImgUrl = basePath + encodeURI(imgSrc);
        const tituloImagem = `${p.nome_limpo} - ${p.modelo_formatado}`;

        const card = document.createElement("div");
        card.className = "card-produto";

        const img = document.createElement("img");
        img.src = fullImgUrl;
        img.alt = p.nome_limpo;
        img.loading = "lazy";      // MELHORIA: lazy loading (performance)
        img.decoding = "async";
        img.addEventListener("click", () => expandirImagem(fullImgUrl, tituloImagem));
        img.addEventListener("error", function onImgError() {
            img.removeEventListener("error", onImgError);
            img.src = "https://via.placeholder.com/250?text=Sem+Imagem";
        });

        const titulo = document.createElement("div");
        titulo.className = "card-title";
        titulo.textContent = p.nome_limpo;

        const tagModelo = document.createElement("div");
        tagModelo.className = "tag-modelo";
        tagModelo.textContent = `Modelo: ${p.modelo_formatado}`;

        const tagPreco = document.createElement("div");
        tagPreco.className = "tag-preco";
        tagPreco.textContent = `R$ ${PRECO_UNITARIO.toFixed(2).replace(".", ",")}`;

        const tagFrete = document.createElement("div");
        tagFrete.className = "tag-frete";
        tagFrete.textContent = "🚚 Frete Grátis";

        const botao = document.createElement("button");
        botao.className = "btn-comprar";
        botao.textContent = "Adicionar ao Carrinho";
        botao.addEventListener("click", () => {
            adicionarCarrinho(p.id || p.time, p.nome_limpo, p.modelo_formatado);

            // MELHORIA: feedback visual rápido no clique
            const textoOriginal = botao.textContent;
            botao.textContent = "✓ Adicionado!";
            botao.disabled = true;
            setTimeout(() => {
                botao.textContent = textoOriginal;
                botao.disabled = false;
            }, 900);
        });

        card.append(img, titulo, tagModelo, tagPreco, tagFrete, botao);
        fragment.appendChild(card);
    });

    grid.appendChild(fragment);
}

// ---------------------------------------------------------------------
// ZOOM DE IMAGEM
// ---------------------------------------------------------------------

function expandirImagem(src, titulo) {
    const modal = document.getElementById("image-modal");
    const img = document.getElementById("img-ampliada");
    const caption = document.getElementById("caption-imagem");

    modal.style.display = "flex";
    img.src = src;
    caption.textContent = titulo;
}

function fecharImagem() {
    const modal = document.getElementById("image-modal");
    if (modal) modal.style.display = "none";
}

// ---------------------------------------------------------------------
// CARRINHO
// ---------------------------------------------------------------------

// MELHORIA: persistência do carrinho em localStorage
function salvarCarrinho() {
    try {
        localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(carrinho));
    } catch (e) {
        console.warn("Não foi possível salvar o carrinho:", e);
    }
}

function carregarCarrinhoSalvo() {
    try {
        const salvo = localStorage.getItem(CHAVE_CARRINHO);
        carrinho = salvo ? JSON.parse(salvo) : [];
    } catch (e) {
        console.warn("Não foi possível carregar o carrinho salvo:", e);
        carrinho = [];
    }
    atualizarCarrinhoUI();
}

function adicionarCarrinho(id, time, modelo) {
    carrinho.push({ id, time, modelo, preco: PRECO_UNITARIO });
    atualizarCarrinhoUI();
}

function removerCarrinho(index) {
    carrinho.splice(index, 1);
    atualizarCarrinhoUI();
}

function limparCarrinho() {
    carrinho = [];
    atualizarCarrinhoUI();
}

function toggleCarrinho() {
    const modal = document.getElementById("cart-modal");
    if (modal) {
        modal.style.display = (modal.style.display === "flex") ? "none" : "flex";
    }
}

function atualizarCarrinhoUI() {
    const totalPecas = carrinho.length;
    const valorTotal = totalPecas * PRECO_UNITARIO;

    const cartCount = document.getElementById("cart-count");
    const cartTotal = document.getElementById("cart-total");
    const cartSummary = document.getElementById("cart-summary-text");

    if (cartCount) cartCount.textContent = totalPecas;
    if (cartTotal) cartTotal.textContent = valorTotal.toFixed(2).replace(".", ",");
    if (cartSummary) cartSummary.textContent = `Total de peças: ${totalPecas} (Subtotal: R$ ${valorTotal.toFixed(2).replace(".", ",")})`;

    // CORREÇÃO (bug de escaping): itens do carrinho também via DOM, não innerHTML com string.
    const container = document.getElementById("cart-items-container");
    if (container) {
        container.innerHTML = "";
        carrinho.forEach((item, index) => {
            const row = document.createElement("div");
            row.className = "cart-item-row";

            const texto = document.createElement("span");
            texto.textContent = `• ${item.time} (${item.modelo})`;

            const btnRemover = document.createElement("button");
            btnRemover.innerHTML = '<i class="fa-solid fa-trash"></i>';
            btnRemover.setAttribute("aria-label", "Remover item");
            btnRemover.addEventListener("click", () => removerCarrinho(index));

            row.append(texto, btnRemover);
            container.appendChild(row);
        });
    }

    const alertBox = document.getElementById("cart-alert");
    const whatsBtn = document.getElementById("whatsapp-btn");

    if (alertBox && whatsBtn) {
        if (totalPecas < 2) {
            alertBox.style.display = "block";
            alertBox.textContent = "⚠️ Adicione pelo menos 2 peças para liberar o WhatsApp.";
            whatsBtn.disabled = true;
        } else {
            alertBox.style.display = "block";
            alertBox.textContent = totalPecas >= 3 ? "🔥 Desconto especial aplicado!" : "✅ Pedido liberado com Frete Grátis!";
            whatsBtn.disabled = false;
        }
    }

    salvarCarrinho(); // MELHORIA: toda mudança no carrinho já salva automaticamente
}

function enviarWhatsApp() {
    const totalPecas = carrinho.length;
    const valorTotal = totalPecas * PRECO_UNITARIO;

    let msg = `Olá, Ramos Sports! Gostaria de fazer um pedido de ${totalPecas} camisas (Frete Grátis):\n\n`;
    carrinho.forEach(item => {
        msg += `• ${item.time} (${item.modelo})\n`;
    });
    msg += `\nTotal: R$ ${valorTotal.toFixed(2).replace(".", ",")}`;
    if (totalPecas >= 3) {
        msg += "\n*(Cliente apto ao desconto especial de 3+ peças)*";
    }

    const url = `https://wa.me/${SEU_NUMERO_WHATSAPP}?text=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
}
