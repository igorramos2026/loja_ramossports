const SEU_NUMERO_WHATSAPP = "5544997339870";
let produtosGlobais = [];
let carrinho = [];

const CLUBES_EUROPA = ["real madrid", "barcelona", "paris saint germain", "psg", "manchester city", "bayern", "liverpool", "arsenal", "juventus", "milan"];
const CLUBES_BRASIL = ["flamengo", "palmeiras", "corinthians", "sao paulo", "santos", "gremio", "internacional", "atletico mineiro", "botafogo", "fluminense", "vasco"];

// Carrega o JSON ao abrir a página de forma robusta
window.addEventListener("DOMContentLoaded", () => {
    fetch("./camisas.json")
        .then(response => {
            if (!response.ok) throw new Error("Erro ao carregar o JSON");
            return response.json();
        })
        .then(data => {
            produtosGlobais = data;
            popularFiltroPaises(data);
            filtrarProdutos();
        })
        .catch(error => console.error("Erro ao carregar camisas.json:", error));
});

function popularFiltroPaises(produtos) {
    const select = document.getElementById("select-pais");
    const paisesSet = new Set();
    
    produtos.forEach(p => {
        if (p.nome_arquivo) {
            let caminhoLimpo = p.nome_arquivo.trim();
            if (caminhoLimpo.startsWith('/')) caminhoLimpo = caminhoLimpo.substring(1);
            if (caminhoLimpo.includes("/")) {
                const pais = caminhoLimpo.split("/")[0];
                if (pais) paisesSet.add(pais);
            }
        }
    });

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
    const termoBusca = (document.getElementById("input-busca").value || "").toLowerCase();
    const paisSelecionado = document.getElementById("select-pais").value;

    let filtrados = produtosGlobais.map(p => {
        let nomeLimpo = limparNomeClube(p.time || p.nome || "");
        if (!nomeLimpo) nomeLimpo = p.time || "Camisa";
        return {
            ...p,
            nome_limpo: nomeLimpo,
            modelo_formatado: traduzirModelo(p.versao || p.modelo || "")
        };
    }).filter(p => {
        const matchBusca = p.nome_limpo.toLowerCase().includes(termoBusca);
        let caminhoArquivo = (p.nome_arquivo || "").trim();
        if (caminhoArquivo.startsWith('/')) caminhoArquivo = caminhoArquivo.substring(1);
        
        const matchPais = (paisSelecionado === "Todos" || caminhoArquivo.startsWith(paisSelecionado + "/"));
        return matchBusca && matchPais;
    });

    filtrados.sort((a, b) => prioridadeDestaque(a.nome_limpo) - prioridadeDestaque(b.nome_limpo));

    renderizarCatalogo(filtrados);
}

function renderizarCatalogo(produtos) {
    const grid = document.getElementById("catalogo-grid");
    grid.innerHTML = "";

    if (produtos.length === 0) {
        grid.innerHTML = "<p style='grid-column: 1 / -1; text-align: center; color: #888; padding: 40px;'>Nenhuma camisa encontrada.</p>";
        return;
    }

    produtos.forEach(p => {
        const card = document.createElement("div");
        card.className = "card-produto";
        
        // Trata o caminho da imagem para o GitHub Pages
        let imgSrc = p.nome_arquivo ? p.nome_arquivo.trim() : '';
        if (imgSrc.startsWith('/')) {
            imgSrc = imgSrc.substring(1);
        }
        imgSrc = encodeURI(imgSrc);

        card.innerHTML = `
            <img src="${imgSrc}" alt="${p.nome_limpo}" onerror="this.onerror=null; this.src='https://via.placeholder.com/250?text=Sem+Imagem';">
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
    modal.style.display = (modal.style.display === "flex") ? "none" : "flex";
}

function atualizarCarrinhoUI() {
    const totalPecas = carrinho.length;
    const valorTotal = totalPecas * 140.00;

    document.getElementById("cart-count").textContent = totalPecas;
    document.getElementById("cart-total").textContent = valorTotal.toFixed(2).replace(".", ",");
    document.getElementById("cart-summary-text").textContent = `Total de peças: ${totalPecas} (Subtotal: R$ ${valorTotal.toFixed(2).replace(".", ",")})`;

    const container = document.getElementById("cart-items-container");
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

    const alertBox = document.getElementById("cart-alert");
    const whatsBtn = document.getElementById("whatsapp-btn");

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
