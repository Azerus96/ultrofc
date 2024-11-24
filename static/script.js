document.getElementById('start').addEventListener('click', () => {
    fetch('/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                renderGameState(data.state);
            }
        });
});

document.getElementById('end').addEventListener('click', () => {
    fetch('/end', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                showScores(data.scores, data.royalties);
            }
        });
});

function renderGameState(state) {
    const playerBoard = state.player_board;
    const aiBoard = state.ai_board;

    renderBoard(playerBoard, 'player');
    renderBoard(aiBoard, 'ai');
}

function renderBoard(board, playerType) {
    ['bottom', 'middle', 'top'].forEach((line) => {
        const lineElement = document.getElementById(`${playerType}-${line}`);
        lineElement.innerHTML = ''; // Очистить линию
        board[line].forEach((card) => {
            const cardElement = document.createElement('div');
            cardElement.classList.add('card');
            cardElement.innerText = card;
            lineElement.appendChild(cardElement);
        });
    });
}

function showScores(scores, royalties) {
    alert(
        `Игрок: ${scores.player} очков (+${royalties.player.total} бонусов)\n` +
        `ИИ: ${scores.ai} очков (+${royalties.ai.total} бонусов)`
    );

    // Отображение очков на странице
    const playerScoreElement = document.getElementById('player-score');
    const aiScoreElement = document.getElementById('ai-score');
    playerScoreElement.innerText = `Очки игрока: ${scores.player} (+${royalties.player.total} бонусов)`;
    aiScoreElement.innerText = `Очки ИИ: ${scores.ai} (+${royalties.ai.total} бонусов)`;
}

// Drag-and-drop для перемещения карт
document.querySelectorAll('.card').forEach(card => {
    card.draggable = true;

    card.addEventListener('dragstart', (event) => {
        event.dataTransfer.setData('text/plain', event.target.id);
    });
});

document.querySelectorAll('.line').forEach(line => {
    line.addEventListener('dragover', (event) => {
        event.preventDefault();
        line.classList.add('highlight'); // Подсветка допустимого слота
    });

    line.addEventListener('dragleave', () => {
        line.classList.remove('highlight'); // Убираем подсветку
    });

    line.addEventListener('drop', (event) => {
        event.preventDefault();
        const cardId = event.dataTransfer.getData('text/plain');
        const card = document.getElementById(cardId);
        line.appendChild(card);
        line.classList.remove('highlight'); // Убираем подсветку
    });
});

// Поддержка свайпов для мобильных устройств
document.querySelectorAll('.card').forEach(card => {
    const hammer = new Hammer(card);

    hammer.on('pan', (event) => {
        card.style.transform = `translate(${event.deltaX}px, ${event.deltaY}px)`;
    });

    hammer.on('panend', (event) => {
        card.style.transform = 'none';
        const targetSlot = document.elementFromPoint(event.center.x, event.center.y);
        if (targetSlot && targetSlot.classList.contains('line')) {
            targetSlot.appendChild(card);
        }
    });
});
