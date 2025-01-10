import { t } from '/src/modules/locale/localeManager.js';
import { getCookie } from '/src/modules/cookie/cookieManager.js';

export function render(app, navigate) {
	app.innerHTML = `
		<canvas id="pongCanvas" width="800px" height="400px" style="border: 1px solid #FFF">
		Your browser does not support this game.
		</canvas>
		<div class="score-box" style="display: flex; align-items: center; justify-content: center;">
		<h1 id="left-score">0</h1>
		<h1>:</h1>
		<h1 id="right-score">0</h1>
		</div>
	`;

	const wsurl = getCookie('match_url');
	if (wsurl === null) {
		console.log('No match url found');
		navigate('/404');
	}

	const wss = new WebSocket(`wss://localhost:8081${wsurl}`);

	wss.onopen = function(e) {
		console.log('WS Opened');
	}

	wss.onmessage = function(e) {
		const gameState = JSON.parse(e.data);
		drawGameState(gameState);
	}

	wss.onclose = function(e) {
		console.log('WS Closed');
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

	// let leftPaddleDirection = null, rightPaddleDirection = null;

	// window.addEventListener('keydown', keydownHandler);
	// window.addEventListener('keyup', keyupHandler);

	// function keydownHandler(e) {
	// 	if (e.key === 'w') leftPaddleDirection = 'up';
	// 	if (e.key === 's') leftPaddleDirection = 'down';
	// 	if (e.key === 'ArrowUp') rightPaddleDirection = 'up';
	// 	if (e.key === 'ArrowDown') rightPaddleDirection = 'down';
	// }

	// function keyupHandler(e) {
	// 	if (e.key === 'w' || e.key === 's') leftPaddleDirection = null;
	// 	if (e.key === 'ArrowUp' || e.key === 'ArrowDown') rightPaddleDirection = null;
	// }

    //임시 키보드 이벤트 감지 코드
    document.addEventListener("keydown", function (e) {
        if (!wss) return;
  
        // w -> 위로 이동, s -> 아래로 이동
        if (e.key === "w") {
          // {"move":["up"]} 전송
          wss.send(JSON.stringify({ "move" : "up" }));
        } else if (e.key === "s") {
          // {"move":["down"]} 전송
          wss.send(JSON.stringify({ "move" : "down" }));
        }
      });
}
