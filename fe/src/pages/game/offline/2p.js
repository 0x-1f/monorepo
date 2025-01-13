let animationFrameId;
let keydownHandler;
let keyupHandler;
let paused = false;

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

  /* Initialize Game Variables */
  const canvas = document.getElementById('pongCanvas');
  const ctx = canvas.getContext('2d');
  const leftScore = document.getElementById('left-score');
  const rightScore = document.getElementById('right-score');

  const paddleWidth = 10, paddleHeight = 100;
  const leftPaddle = { x: 0, y: (canvas.height - paddleHeight) / 2 };
  const rightPaddle = { x: canvas.width - paddleWidth, y: (canvas.height - paddleHeight) / 2 };

  const ballRadius = 10;
  const ball = { x: canvas.width / 2, y: canvas.height / 2 };
  const speed = { paddle: 8, ball: { x: 5, y: 5 } };

  let leftPaddleDirection = null, rightPaddleDirection = null;

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall(ball);
    drawPaddle(leftPaddle);
    drawPaddle(rightPaddle);

    if (!paused) {
      movePaddle(leftPaddleDirection, rightPaddleDirection);
      moveBall();
    }

    animationFrameId = requestAnimationFrame(draw); // Always keep the loop running
  }

  function drawBall(ball) {
    ctx.fillStyle = '#FFF';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ballRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawPaddle(paddle) {
    ctx.fillStyle = '#FFF';
    ctx.fillRect(paddle.x, paddle.y, paddleWidth, paddleHeight);
  }

  function movePaddle(left, right) {
    if (left === 'up' && leftPaddle.y > 0) leftPaddle.y -= speed.paddle;
    if (left === 'down' && leftPaddle.y < canvas.height - paddleHeight) leftPaddle.y += speed.paddle;
    if (right === 'up' && rightPaddle.y > 0) rightPaddle.y -= speed.paddle;
    if (right === 'down' && rightPaddle.y < canvas.height - paddleHeight) rightPaddle.y += speed.paddle;
  }

  function moveBall() {
    ball.x += speed.ball.x;
    ball.y += speed.ball.y;

    // Ball hits the top or bottom wall
    if (ball.y < ballRadius) {
      ball.y = ballRadius; // Correct position
      speed.ball.y = -speed.ball.y; // Reverse direction
    } else if (ball.y > canvas.height - ballRadius) {
      ball.y = canvas.height - ballRadius; // Correct position
      speed.ball.y = -speed.ball.y; // Reverse direction
    }

    // Ball hits the left wall
    if (ball.x - ballRadius <= 0) {
      if (ball.y >= leftPaddle.y && ball.y <= leftPaddle.y + paddleHeight) {
        increaseSpeed();
        reflectBall(ball, leftPaddle, true);
      } else {
        rightScore.textContent = +rightScore.textContent + 1;
        pauseGame(); // Pause the game
        checkWin("Right");
      }
    }

    // Ball hits the right wall
    if (ball.x + ballRadius >= canvas.width) {
      if (ball.y >= rightPaddle.y && ball.y <= rightPaddle.y + paddleHeight) {
        increaseSpeed();
        reflectBall(ball, rightPaddle, false);
      } else {
        leftScore.textContent = +leftScore.textContent + 1;
        pauseGame(); // Pause the game
        checkWin("Left");
      }
    }
  }

  function pauseGame() {
    paused = true; // Set paused state
    window.addEventListener('keydown', resumeGameOnce); // Wait for a keypress to resume
  }

  function resumeGameOnce(e) {
    if (e.key === ' ') {
      paused = false; // Clear paused state
      window.removeEventListener('keydown', resumeGameOnce); // Remove the resume listener
      resetGame(); // Reset the game for the next round
    }
  }

  function reflectBall(ball, paddle, isLeftPaddle) {
    const paddleEdgeX = isLeftPaddle ? paddle.x + paddleWidth : paddle.x;
    const hitPoint = (ball.y - (paddle.y + paddleHeight / 2)) / (paddleHeight / 2);
    const maxBounceAngle = Math.PI / 4; 
    const bounceAngle = hitPoint * maxBounceAngle;
    const speedMagnitude = Math.sqrt(speed.ball.x ** 2 + speed.ball.y ** 2);

    speed.ball.x = speedMagnitude * Math.cos(bounceAngle) * (isLeftPaddle ? 1 : -1);
    speed.ball.y = speedMagnitude * Math.sin(bounceAngle);

    // Adjust ball position to ensure it reflects from the edge
    ball.x = paddleEdgeX + (isLeftPaddle ? ballRadius : -ballRadius);
  }

  function increaseSpeed() {
    const speedIncrement = 1.1;
    speed.ball.x *= speedIncrement;
    speed.ball.y *= speedIncrement;
  }

  function checkWin(winner) {
    if (+leftScore.textContent === 5 || +rightScore.textContent === 5) {
      alert(`${winner} wins!`);
      navigate('main');
      cleanup(); // Stop the game
      location.reload();
    }
  }

  function resetGame() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    leftPaddle.y = (canvas.height - paddleHeight) / 2;
    rightPaddle.y = (canvas.height - paddleHeight) / 2;
    speed.ball.x = Math.random() < 0.5 ? -5 : 5;
    speed.ball.y = Math.random() < 0.5 ? -5 : 5;
  }

  keydownHandler = (e) => {
    switch (e.key) {
      case 'w': leftPaddleDirection = 'up'; break;
      case 's': leftPaddleDirection = 'down'; break;
      case 'ArrowUp': rightPaddleDirection = 'up'; break;
      case 'ArrowDown': rightPaddleDirection = 'down'; break;
    }
  };

  keyupHandler = (e) => {
    switch (e.key) {
      case 'w': leftPaddleDirection = null; break;
      case 's': leftPaddleDirection = null; break;
      case 'ArrowUp': rightPaddleDirection = null; break;
      case 'ArrowDown': rightPaddleDirection = null; break;
    }
  };

  window.addEventListener('keydown', keydownHandler);
  window.addEventListener('keyup', keyupHandler);

  function cleanup() {
    cancelAnimationFrame(animationFrameId); // Stop the game loop
    window.removeEventListener('keydown', keydownHandler);
    window.removeEventListener('keyup', keyupHandler);
  }

  window.onpopstate = () => {
    window.location.reload();
  }

  draw(); // Start the game
}
