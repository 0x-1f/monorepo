import { t } from '/src/modules/locale/localeManager.js';

function waitingRoom(app) {
    app.innerHTML = `
    <div class="grid">
        <div class="grid-item-left" id="you">${t('you', 'You')}</div>
        <div class="grid-item-right" id="rival">${t('wait_part', 'Waiting for participations...')}</div>
    </div>
    `
}

function gameRoom(app, match_url, me) {
    app.innerHTML = `
    <canvas id="pongCanvas" width="800px" height="600px" style="border: 1px solid #FFF">
    Your browser does not support this game.
    </canvas>
    <div class="score-box" style="display: flex; align-items: center; justify-content: center;">
    <h1 id="left-score">0</h1>
    <h1>:</h1>
    <h1 id="right-score">0</h1>
    </div>
    `;

    const wss = new WebSocket(`wss://localhost${match_url}${me}`);
	
    wss.onopen = function(e) {
		console.log('WS Opened');
	}

	wss.onmessage = function(e) {
		const gameState = JSON.parse(e.data);
		drawGameState(gameState);
	}

	function drawGameState(gameState) {
		if (!gameState) return;
		const canvas = document.getElementById('pongCanvas');
  		const ctx = canvas.getContext('2d');
  		const leftScore = document.getElementById('left-score');
  		const rightScore = document.getElementById('right-score');

		ctx.clearRect(0, 0, canvas.width, canvas.height);
		ctx.beginPath();
		ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
		ctx.fillStyle = 'white';
		ctx.fill();
		ctx.closePath();

		ctx.fillStyle = 'white';
		ctx.fillRect(
			10,
			gameState.paddle_positions.player1,
			10,
			100
		);
		ctx.fillRect(
			canvas.width - 20,
			gameState.paddle_positions.player2,
			10,
			100
		);

		ctx.fillStyle = 'white';
		ctx.font = '20px Arial';
		ctx.fillText('Player 1', 20, 30);
		ctx.fillText('Player 2', canvas.width - 120, 30);

		leftScore.innerText = gameState.scores.player1;
		rightScore.innerText = gameState.scores.player2;

		movePaddle();
	}

    document.addEventListener("keydown", function (e) {
        if (!wss) return;
  
        // w -> 위로 이동, s -> 아래로 이동
        if (e.key === "w" || "ArrowUp") {
          // {"move":["up"]} 전송
          wss.send(JSON.stringify({ "move" : "up" }));
        } else if (e.key === "s" || "ArrowDown") {
          // {"move":["down"]} 전송
          wss.send(JSON.stringify({ "move" : "down" }));
        }
    });

    window.onpopstate = function (event) {
        if (wss && wss.readyState === WebSocket.OPEN) {
            wss.close();
        }
    };
}

export function render(app, navigate) {
    waitingRoom(app);

    let wss; // Declare WebSocket at the top for access throughout the function
    let intraId; // To store the fetched intra ID

    // Fetch intra ID from the API
    fetch('https://localhost/api/auth/get_intra_id/', {
        credentials: 'include',
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to fetch intra_id');
        })
        .then(data => {
            intraId = data.intra_id;

            // Dynamically determine the WebSocket protocol based on the current protocol
            const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
            wss = new WebSocket(`${wsProtocol}://localhost/ws/pong/join/${intraId}`);

            // WebSocket event listeners
            wss.onopen = function (e) {
                console.log('Waiting for participations...');
            };

            wss.onmessage = function (e) {
                const data = JSON.parse(e.data);
                const match_url = data.match_url;
                console.log(match_url);

                // Transition to the game room
                gameRoom(app, match_url, intraId);
            };

            wss.onerror = function (e) {
                console.error('WebSocket error:', e);
            };

            wss.onclose = function (e) {
                console.log('WebSocket closed:', e.reason);
            };
        })
        .catch(error => {
            console.error('Error fetching intra ID:', error);
        });

    // Handle back navigation or cleanup
    window.onpopstate = function (event) {
        if (wss && wss.readyState === WebSocket.OPEN) {
            wss.close();
        }
    };
}
