import { t } from '/src/modules/locale/localeManager.js';

let animationFrameId;
let keydownHandler;
let keyupHandler;
let paused = false;

/* 플레이어 기본값 (미입력 시 대체) */
let player1 = "player1";
let player2 = "player2";
let player3 = "player3";
let player4 = "player4";

/* 게임 라운드 진행 번호 */
let gameNum = 1;

/* 각 라운드 승자들 */
let winner1 = null;
let winner2 = null;
/* 최종 우승자 */
let WINNER = null;

/* 토너먼트 진행 여부(입력 폼 뒤 게임 시작) */
let tournamentStarted = false;

export function render(app, navigate) {
  /* ------------------------------------------------
     1) 플레이어 이름 입력 폼 보여주기
  ------------------------------------------------ */
  app.innerHTML = `
    <div class="player-input-container" style="text-align:center; color:#fff;">
      <h2>${t('4p-inputName', "ENTER each player's name")}</h2>
      
      <div style="display:flex; justify-content:center; gap:50px; margin:20px;">
        <div style="display:flex; flex-direction:column; gap:10px;">
          <label>Player1</label>
          <input id="player1-input" type="text" placeholder="player1" />
          <label>Player3</label>
          <input id="player3-input" type="text" placeholder="player3" />
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
          <label>Player2</label>
          <input id="player2-input" type="text" placeholder="player2" />
          <label>Player4</label>
          <input id="player4-input" type="text" placeholder="player4" />
        </div>
      </div>
      <button id="start-tournament-btn" style="margin-top:20px;">${t('4p-start', 'START the tournement')}</button>
    </div>
  `;

  const startBtn = document.getElementById('start-tournament-btn');
  startBtn.addEventListener('click', () => {
    /* 입력된 이름이 없으면 기본값을 사용 */
    const blockedChars = /[^a-zA-Z0-9]/g;
    if (blockedChars.test(document.getElementById('player1-input').value) ||
        blockedChars.test(document.getElementById('player2-input').value) ||
        blockedChars.test(document.getElementById('player3-input').value) ||
        blockedChars.test(document.getElementById('player4-input').value)) {
      alert(t('invalid-name', 'Invalid player name'));
      return;
    }
    const p1 = (document.getElementById('player1-input')?.value || "").trim();
    const p2 = (document.getElementById('player2-input')?.value || "").trim();
    const p3 = (document.getElementById('player3-input')?.value || "").trim();
    const p4 = (document.getElementById('player4-input')?.value || "").trim();

    player1 = p1 !== "" ? p1 : "player1";
    player2 = p2 !== "" ? p2 : "player2";
    player3 = p3 !== "" ? p3 : "player3";
    player4 = p4 !== "" ? p4 : "player4";

    console.log("플레이어 입력 완료:", player1, player2, player3, player4);

    tournamentStarted = true;
    startGame(app, navigate);
  });

  window.onpopstate = () => {
    window.location.reload();
  }
}

/* ------------------------------------------------
   2) 퐁 게임 로직 함수
   (기존 코드에 '플레이어 입력 폼' 이후에만
    게임 실행되도록 분리한 버전)
------------------------------------------------ */
function startGame(app, navigate) {
  /* 먼저 게임 화면으로 교체 */
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

  /* 현재 라운드에 따른 출전 선수 반환 함수 */
  function getPlayersForCurrentGame() {
    switch (gameNum) {
      case 1: return [player1, player2];
      case 2: return [player3, player4];
      case 3: return [winner1, winner2];
      default: return ["", ""];
    }
  }

  /* 메인 게임 루프(프레임 단위로 호출) */
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 현재 게임 라운드의 출전 선수 이름을 캔버스 상단 좌우에 표시
    const [leftPlayerName, rightPlayerName] = getPlayersForCurrentGame();
    ctx.fillStyle = '#FFF';
    ctx.font = '20px DOSGothic';
    ctx.fillText(leftPlayerName, 10, 20);
    const rightTextWidth = ctx.measureText(rightPlayerName).width;
    ctx.fillText(rightPlayerName, canvas.width - rightTextWidth - 10, 20);

    drawBall(ball);
    drawPaddle(leftPaddle);
    drawPaddle(rightPaddle);

    if (!paused) {
      movePaddle(leftPaddleDirection, rightPaddleDirection);
      moveBall();
    }

    animationFrameId = requestAnimationFrame(draw); // 게임 루프 지속
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

    // 위/아래 벽 충돌
    if (ball.y < ballRadius) {
      ball.y = ballRadius; 
      speed.ball.y = -speed.ball.y;
    } else if (ball.y > canvas.height - ballRadius) {
      ball.y = canvas.height - ballRadius; 
      speed.ball.y = -speed.ball.y;
    }

    // 왼쪽 벽 충돌
    if (ball.x - ballRadius <= 0) {
      if (ball.y >= leftPaddle.y && ball.y <= leftPaddle.y + paddleHeight) {
        increaseSpeed();
        reflectBall(ball, leftPaddle, true);
      } else {
        rightScore.textContent = +rightScore.textContent + 1;
        pauseGame();
        checkWin("Right");
      }
    }

    // 오른쪽 벽 충돌
    if (ball.x + ballRadius >= canvas.width) {
      if (ball.y >= rightPaddle.y && ball.y <= rightPaddle.y + paddleHeight) {
        increaseSpeed();
        reflectBall(ball, rightPaddle, false);
      } else {
        leftScore.textContent = +leftScore.textContent + 1;
        pauseGame();
        checkWin("Left");
      }
    }
  }

  function pauseGame() {
    paused = true;
    window.addEventListener('keydown', resumeGameOnce);
  }

  function resumeGameOnce(e) {
    if (e.key === ' ') {
      paused = false;
      window.removeEventListener('keydown', resumeGameOnce);
      resetGame();
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

    // 공이 튕겨나갈 위치 조정
    ball.x = paddleEdgeX + (isLeftPaddle ? ballRadius : -ballRadius);
  }

  function increaseSpeed() {
    const speedIncrement = 1.1;
    speed.ball.x *= speedIncrement;
    speed.ball.y *= speedIncrement;
  }

  /* 점수 5점 달성 시 라운드 승자 결정 -> 다음 라운드로 이동 */
  function checkWin(winner) {
    if (+leftScore.textContent === 5 || +rightScore.textContent === 5) {
      alert(`${winner} wins!`);
      leftScore.textContent = 0;
      rightScore.textContent = 0;
      console.log("gameNum: ", gameNum);

      switch(gameNum) {
        case 1:
          winner === "Left" ? winner1 = player1 : winner1 = player2;
          console.log("winner1: ", winner1);
          break;
        case 2:
          winner === "Left" ? winner2 = player3 : winner2 = player4;
          console.log("winner2: ", winner2);
          break;
        case 3:
          // 결승전 승자는 WINNER
          winner === "Left" ? WINNER = winner1 : WINNER = winner2;
          console.log("WINNER: ", WINNER);
          break;
      }
      gameNum++;

      // gameNum이 4가 되면 토너먼트 끝 -> 최종 결과 화면
      if (gameNum === 4) {
        console.log("WINNER: ", WINNER);
        cleanup();
        showFinalResults(app, navigate);
      }
    }
  }

  /* 게임 라운드 리셋 */
  function resetGame() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    leftPaddle.y = (canvas.height - paddleHeight) / 2;
    rightPaddle.y = (canvas.height - paddleHeight) / 2;
    speed.ball.x = Math.random() < 0.5 ? -5 : 5;
    speed.ball.y = Math.random() < 0.5 ? -5 : 5;
  }

  /* 키 이벤트 핸들러들 */
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
      case 'w':
      case 's':
        leftPaddleDirection = null;
        break;
      case 'ArrowUp':
      case 'ArrowDown':
        rightPaddleDirection = null;
        break;
    }
  };

  window.addEventListener('keydown', keydownHandler);
  window.addEventListener('keyup', keyupHandler);

  /* 게임 루프 정리 함수 */
  function cleanup() {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('keydown', keydownHandler);
    window.removeEventListener('keyup', keyupHandler);
  }

  draw();
}

/* ------------------------------------------------
   3) 토너먼트 최종 결과 화면 렌더링
------------------------------------------------ */
function showFinalResults(app, navigate) {
  // WINNER가 우승, winner1과 winner2 중 WINNER가 아닌 쪽이 준우승
  const runnerUp = (winner1 === WINNER) ? winner2 : winner1;

  // 4명 중 winner1, winner2 둘 다 아닌 플레이어가 공동 3등
  const players = [player1, player2, player3, player4];
  const thirdPlace = players.filter(p => p !== winner1 && p !== winner2);

  // 결과 화면 표시
  app.innerHTML = `
    <div style="color: #fff; text-align: center; margin-top: 50px;">
      <h1>${t('4p-result', 'TOURNAMENT result')}</h1>
      <h2>${t('4p-winner', 'WINNER')}: ${WINNER}</h2>
      <h2>${t('4p-2nd', '2ND')}: ${runnerUp}</h2>
      <h2>${t('4p-3rd', '3RD')}: ${thirdPlace[0]}, ${thirdPlace[1]}</h2>
      <button id="go-main-btn" style="margin-top: 30px;">${t('4p-main', "MAIN")}</button>
    </div>
  `;

  // 메인 페이지로 이동 예시
  const goMainBtn = document.getElementById('go-main-btn');
  goMainBtn.addEventListener('click', () => {
    navigate('main');
    cleanup();
    location.reload();
  });
}