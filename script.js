let gamePhrases = [];
let selectedColor = 'red';
let currentPlayer = 1;
let playerScores = { 1: 0, 2: 0 };
let selectedPhrases = [];
let usedIndexes = new Set();

function $(id) {
    return document.getElementById(id);
}

async function loadPhrases() {
    try {
        const response = await fetch('frases.json');
        gamePhrases = await response.json();
        buildShuffled();
        buildGrid();
        buildPalette();
    } catch (error) {
        console.error('Erro ao carregar frases:', error);
        toast('Erro ao carregar frases');
    }
}

function buildShuffled() {
    selectedPhrases = [];
    usedIndexes.clear();
    while (selectedPhrases.length < 6) {
        const i = Math.floor(Math.random() * gamePhrases.length);
        if (!usedIndexes.has(i)) {
            usedIndexes.add(i);
            selectedPhrases.push(gamePhrases[i]);
        }
    }
}

function buildGrid() {
    const grid = $('grid');
    grid.innerHTML = '';
    const palavras = selectedPhrases.flat();
    palavras.sort(() => Math.random() - 0.5);

    palavras.forEach((palavra, i) => {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.textContent = palavra;
        cell.dataset.index = i;
        cell.onclick = () => pintar(cell);
        grid.appendChild(cell);
    });
}

function buildPalette() {
    const p = $('palette');
    p.innerHTML = '';

    const icons = ['🎯', '🎨', '🔥', '🌈', '⭐', '⚡'];

    PALETTE.forEach((col, i) => {
        const s = document.createElement('div');
        s.className = 'swatch';
        s.style.background = col.css;
        s.dataset.id = col.id;
        s.innerHTML = icons[i % icons.length]; // adiciona ícone
        s.onclick = () => selectColor(col.id);
        p.appendChild(s);

        // 👇 Agora o log está dentro do loop, com i definido
        console.log('Ícone inserido:', icons[i % icons.length]);
    });

    refreshPalette();
}

function spawnParticles(x, y, color) {
    for (let i = 0; i < 12; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.background = color;
        p.style.left = `${x}px`;
        p.style.top = `${y}px`;

        const angle = Math.random() * 2 * Math.PI;
        const radius = 40 + Math.random() * 20;
        p.style.setProperty('--x', `${Math.cos(angle) * radius}px`);
        p.style.setProperty('--y', `${Math.sin(angle) * radius}px`);

        p.style.position = 'absolute';
        p.style.width = '8px';
        p.style.height = '8px';
        p.style.borderRadius = '50%';
        p.style.pointerEvents = 'none';
        p.style.animation = 'explode 600ms ease-out forwards';
        p.style.zIndex = '9999';

        document.body.appendChild(p);
        setTimeout(() => p.remove(), 600);
    }
}




function pintar(cell) {
    cell.style.backgroundColor = selectedColor;
    checkSeq(cell.dataset.index);
}

function checkSeq(cid) {
    const grid = Array.from(document.querySelectorAll('.cell'));
    const linhas = [];

    for (let i = 0; i < grid.length; i += 5) {
        const linha = grid.slice(i, i + 5).map(c => c.textContent);
        linhas.push(linha);
    }

    linhas.forEach((linha, i) => {
        selectedPhrases.forEach(frase => {
            if (JSON.stringify(linha) === JSON.stringify(frase)) {
                linha.forEach((_, j) => {
                    grid[i * 5 + j].style.border = '2px solid black';
                });
                playerScores[currentPlayer] += 20;
                $('score1').textContent = playerScores[1];
                $('score2').textContent = playerScores[2];
                toast(`Jogador ${currentPlayer} marcou pontos!`);
                trocarJogador();
            }
        });
    });
}

function trocarJogador() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
    $('turno').textContent = `Vez do Jogador ${currentPlayer}`;
}

function toast(msg) {
    const t = $('toast');
    t.textContent = msg;
    t.style.opacity = 1;
    setTimeout(() => t.style.opacity = 0, 2000);
}

window.onload = () => {
    loadPhrases();
    $('score1').textContent = '0';
    $('score2').textContent = '0';
    $('turno').textContent = 'Vez do Jogador 1';
};
function toast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.opacity = 1;
    setTimeout(() => t.style.opacity = 0, 2000);
}
