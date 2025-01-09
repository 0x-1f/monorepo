export function render(app, navigate) {
	app.innerHTML = `
		<p>wss connection example</p>
		<button id="lol">lol</button>
		<br>
		<span id="divlol" style="width:10em"></span>
	`;

	const testData = {
		leftPaddle: 3,
		rightPadle: 4,
		ball: {
			x: 3,
			y: 4
		}
	}

	const wss = new WebSocket('wss://echo.websocket.org');

	wss.onopen = function(e) {
		console.log('WebSocket is open now.');
		wss.send('Hello, WebSocket!');
	}

	wss.onmessage = function(e) {
		console.log('Message received:', e.data);
		gameState = JSON.parse(e.data);
		document.getElementById('divlol').innerHTML = JSON.stringify(gameState);
	}

	wss.onerror = function(e) {
		console.error('WebSocket error:', e);
	}

	wss.onclose = function(e) {
		console.log('WebSocket is closed now.');
	}

	document.getElementById('lol').addEventListener('click', function(e) {
		wss.send(testData);
	});
}