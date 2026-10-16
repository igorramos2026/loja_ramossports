const SEU_NUMERO_WHATSAPP = "5544997339870";
let produtosGlobais = [];
let carrinho = [];

const CLUBES_EUROPA = ["real madrid", "barcelona", "paris saint germain", "psg", "manchester city", "bayern", "liverpool", "arsenal", "juventus", "milan"];
const CLUBES_BRASIL = ["flamengo", "palmeiras", "corinthians", "sao paulo", "santos", "gremio", "internacional", "atletico mineiro", "botafogo", "fluminense", "vasco"];

// Obtém o caminho base do repositório para evitar erros de rota no GitHub Pages
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

// Carrega o JSON de forma garantida no GitHub Pages
window.addEventListener("DOMContentLoaded", () => {
    const jsonPath = getBasePath() + "camisas.json";
    
    fetch(jsonPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: Não foi possível carregar ${jsonPath}`);
            }
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
                grid.innerHTML = `<p style="grid-column: 1 / -1; text-align: center; color: #ff4d4d; padding: 20px;">
                    ⚠️ Erro ao carregar os dados (${error.message}). Verifique se o arquivo <b>camisas.json</b> está na raiz do repositório.
                </p>`;
            }
        });
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
    for(let i = 0; i < maxLen; i++) {
        if (i < CLUBES_EUROPA.length) ranking.push(CLUBES_EUROPA[i]);
        if (i < CLUBES_BRASIL.length) ranking.push(CLUBES_BRASIL[i]);
    }

    for(let i = 0; i < ranking.length; i++) {
        if (nomeLower.includes(ranking[i])) return i;
    }
    return 999;
}

function filtrarProdutos() {
    const inputBusca = document.getElementById("input-busca");
    const selectPais = document.getElementById("select-pais");
    
    const termoBusca = inputBusca ? inputBusca.value.toLowerCase() : "";
    const paisSelecionado = selectPais ? selectPais.value : "Todos";

    let filtrados = produtosGlobais.map(p => {
        let nomeOriginal = p.time || p.nome || p.clube || "";
        let nomeLimpo = limparNomeClube(nomeOriginal);
        if (!nomeLimpo) nomeLimpo = nomeOriginal || "Camisa";
        
        return {
            ...p,
            nome_limpo: nomeLimpo,
            modelo_formatado: traduzirModelo(p.versao || p.modelo || "")
        };
    }).filter(p => {
        const matchBusca = p.nome_limpo.toLowerCase().includes(termoBusca);
        let caminhoArquivo = (p.nome_arquivo || p.imagem || p.foto || "").trim();
        if (caminhoArquivo.startsWith('/')) caminhoArquivo = caminhoArquivo.substring(1);
        
        const matchPais = (paisSelecionado === "Todos" || caminhoArquivo.startsWith(paisSelecionado + "/"));
        return matchBusca && matchPais;
    });

    filtrados.sort((a, b) => prioridadeDestaque(a.nome_limpo) - prioridadeDestaque(b.nome_limpo));

    renderizarCatalogo(filtrados);
}

function renderizarCatalogo(produtos) {
    const grid = document.getElementById("catalogo-grid");
    if (!grid) return;
    
    grid.innerHTML = "";

    if (produtos.length === 0) {
        grid.innerHTML = "<p style='grid-column: 1 / -1; text-align: center; color: #888; padding: 40px;'>Nenhuma camisa encontrada.</p>";
        return;
    }

    const basePath = getBasePath();

    produtos.forEach(p => {
        const card = document.createElement("div");
        card.className = "card-produto";
        
        let arqOriginal = p.nome_arquivo || p.imagem || p.foto || "";
        let imgSrc = arqOriginal.trim();
        if (imgSrc.startsWith('/')) {
            imgSrc = imgSrc.substring(1);
        }
        
        // Monta a URL completa do caminho do arquivo no repositório
        const fullImgUrl = basePath + encodeURI(imgSrc);

        card.innerHTML = `
            <img src="${fullImgUrl}" alt="${p.nome_limpo}" onerror="this.onerror=null; this.src='https://via.placeholder.com/250?text=Sem+Imagem';">
            <div class="card-title">${p.nome_limpo}</div>
            <div class="tag-modelo">Modelo: ${p.modelo_formatado}</div>
            <div class="tag-preco">R$ 140,00</div>
            <div class="tag-frete">🚚 Frete Grátis</div>
            <button class="btn-comprar" onclick="adicionarCarrinho('${p.id || p.time}', '${p.nome_limpo.replace(/'/g, "\\'")}', '${p.modelo_formatado.replace(/'/g, "\\'")}')">Adicionar ao Carrinho</button>
        `;
        grid.appendChild(card);
    });
}

function adicionarCarrinho(id, time, modelo) {
    carrinho.push({ id, time, modelo, preco: 140.00 });
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
    const valorTotal = totalPecas * 140.00;

    const cartCount = document.getElementById("cart-count");
    const cartTotal = document.getElementById("cart-total");
    const cartSummary = document.getElementById("cart-summary-text");

    if (cartCount) cartCount.textContent = totalPecas;
    if (cartTotal) cartTotal.textContent = valorTotal.toFixed(2).replace(".", ",");
    if (cartSummary) cartSummary.textContent = `Total de peças: ${totalPecas} (Subtotal: R$ ${valorTotal.toFixed(2).replace(".", ",")})`;

    const container = document.getElementById("cart-items-container");
    if (container) {
        container.innerHTML = "";
        carrinho.forEach((item, index) => {
            const row = document.createElement("div");
            row.className = "cart-item-row";
            row.innerHTML = `
                <span>• ${item.time} (${item.modelo})</span>
                <button onclick="removerCarrinho(${index})"><i class="fa-solid fa-trash"></i></button>
            `;
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
}

function enviarWhatsApp() {
    const totalPecas = carrinho.length;
    const valorTotal = totalPecas * 140.00;

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
