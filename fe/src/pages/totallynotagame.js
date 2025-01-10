let intraId = null;
let ws = null;
let matchWs = null;
let choice = "";
let countdownInterval = null;

export function render(app, navigate) {
  // 초기 렌더링
  renderStartPage(app);
  cleanupAllWebSockets();
}

/** 1) 최초 화면: "start matching" 버튼만 있는 화면 */
function renderStartPage(app) {
  app.innerHTML = "";

  // .rps-container 클래스를 가진 div
  const container = document.createElement("div");
  container.className = "rps-container";

  const startBtn = document.createElement("button");
  startBtn.textContent = "start matching";
  
  // Bootstrap 클래스 + rps-btn 클래스(hover 적용)
  startBtn.classList.add("btn", "btn-primary", "rps-btn");

  startBtn.addEventListener("click", () => {
    // intra_id 를 입력 받는다.
    intraId = prompt("Enter your intra_id");
    if (!intraId) {
      alert("intra_id is required!");
      return;
    }
    startMatching(app);
  });

  container.appendChild(startBtn);
  app.appendChild(container);
}

/** 2) 매칭 중인 화면 ("cancel matching" 버튼 + "waiting for opponent...") */
function renderMatchingPage(app) {
  app.innerHTML = "";

  const waitingText = document.createElement("div");
  waitingText.textContent = "waiting for opponent...";
  waitingText.className = "rps-waiting-text";

  const cancelBtn = document.createElement("button");
  cancelBtn.textContent = "cancel matching";
  
  cancelBtn.classList.add("btn", "btn-danger", "rps-btn");

  cancelBtn.addEventListener("click", () => {
    cleanupAllWebSockets();
    renderStartPage(app);
  });

  app.appendChild(waitingText);
  app.appendChild(cancelBtn);
}

/** 매칭 URL이 도착한 뒤, 실제 게임방에 들어가기 전 "대기중" 화면 */
function renderWaitingGamePage(app) {
  app.innerHTML = "";

  const waitingText = document.createElement("div");
  waitingText.textContent = "대기중...";
  waitingText.style.fontSize = "2em"; // 간단한건 그냥 남겨도 되지만, css class로 빼도 됨

  app.appendChild(waitingText);
}

/** 3) 게임 시작 화면 (가위바위보 선택) */
function renderRpsGamePage(app) {
  app.innerHTML = "";

  const counterDiv = document.createElement("div");
  counterDiv.className = "rps-counter";
  counterDiv.textContent = "10"; // 초기값 10

  // 가위바위보 컨테이너
  const gridContainer = document.createElement("div");
  gridContainer.className = "rps-grid-container";

  // rock, paper, scissor
  const items = ["rock", "paper", "scissor"];

  items.forEach(item => {
    const itemDiv = document.createElement("div");
    itemDiv.className = "rps-item";

    const img = document.createElement("img");
    img.src = getImagePath(item);
    // 여기서는 width, height도 CSS로 뺄 수 있음. 지금은 inline 예시로 남김.
    img.className = "rps-img";

    // 선택 표시
    const selectHighlight = document.createElement("div");
    selectHighlight.className = "rps-select-highlight";

    itemDiv.addEventListener("click", () => {
      // 이미 선택된 다른 그리드의 .rps-select-highlight를 모두 숨김
      gridContainer.querySelectorAll(".rps-select-highlight").forEach(div => {
        div.style.display = "none";
      });
      selectHighlight.style.display = "block";
      choice = item;
    });

    itemDiv.appendChild(img);
    itemDiv.appendChild(selectHighlight);
    gridContainer.appendChild(itemDiv);
  });

  app.appendChild(counterDiv);
  app.appendChild(gridContainer);

  // 10초 카운트다운
  let count = 10;
  countdownInterval = setInterval(() => {
    count--;
    counterDiv.textContent = String(count);
    if (count <= 0) {
      clearInterval(countdownInterval);
      countdownInterval = null;
      if (!choice) {
        choice = getRandomChoice();
      }
      sendChoiceToServer(choice);
      renderWaitingResultPage(app);
    }
  }, 1000);
}

/** 4) 응답 대기 화면 */
function renderWaitingResultPage(app) {
  app.innerHTML = "";

  const text = document.createElement("div");
  text.textContent = "응답을 기다리는 중...";
  text.className = "rps-waiting-result";
  app.appendChild(text);
}

/** 5) 최종 결과 화면 */
function renderResultPage(app, result, opponentChoice, opponentId) {
  app.innerHTML = "";

  // 결과 문구
  const resultText = document.createElement("div");
  resultText.className = "rps-result-text";
  resultText.textContent = result; // "win" / "lose" / "draw"
  app.appendChild(resultText);

  // 두 명의 선택을 보여줄 그리드
  const resultGrid = document.createElement("div");
  resultGrid.className = "rps-result-grid";

  // 내 쪽
  const mySide = document.createElement("div");
  mySide.classList.add("rps-side", "rps-my-side");

  const myPaddle = document.createElement("div");
  myPaddle.className = "rps-my-paddle";

  const myIdDiv = document.createElement("div");
  myIdDiv.textContent = intraId;

  const myImg = document.createElement("img");
  myImg.className = "rps-img";
  myImg.src = getImagePath(choice);

  mySide.appendChild(myPaddle);
  mySide.appendChild(myIdDiv);
  mySide.appendChild(myImg);

  // 상대방 쪽
  const oppSide = document.createElement("div");
  oppSide.className = "rps-side";

  const oppImg = document.createElement("img");
  oppImg.className = "rps-img";
  oppImg.src = getImagePath(opponentChoice);

  const oppIdDiv = document.createElement("div");
  oppIdDiv.textContent = opponentId;

  const oppPaddle = document.createElement("div");
  oppPaddle.className = "rps-opponent-paddle";

  oppSide.appendChild(oppImg);
  oppSide.appendChild(oppIdDiv);
  oppSide.appendChild(oppPaddle);

  resultGrid.appendChild(mySide);
  resultGrid.appendChild(oppSide);

  app.appendChild(resultGrid);

  // main 버튼
  const mainBtn = document.createElement("button");
  mainBtn.textContent = "main";
  mainBtn.classList.add("btn", "btn-warning", "rps-main-btn");

  mainBtn.addEventListener("click", () => {
    cleanupAllWebSockets();
    navigate("main");
  });

  const btnContainer = document.createElement("div");
  btnContainer.style.display = "flex";
  btnContainer.style.justifyContent = "center";
  btnContainer.appendChild(mainBtn);
  app.appendChild(btnContainer);
}

/** --- 이하 웹소켓 로직 및 유틸 함수는 기존과 동일 --- **/

function startMatching(app) {
  renderMatchingPage(app);
  ws = new WebSocket(`ws://localhost:8081/ws/rps/join/${intraId}`);
  ws.onopen = () => console.log("[Matching WS] Connected");
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.match_url) {
      cleanupWs(ws);
      connectMatchWebSocket(app, data.match_url);
    }
  };
  ws.onerror = (err) => console.error("[Matching WS] Error:", err);
  ws.onclose = () => console.log("[Matching WS] Closed");
}

function connectMatchWebSocket(app, matchUrl) {
  renderWaitingGamePage(app);
  matchWs = new WebSocket(`ws://localhost:8081/ws/rps${matchUrl}${intraId}`);
  matchWs.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === "start") {
      renderRpsGamePage(app);
    }
    if (data.result) {
      const opponentId = getOpponentIdFromUrl(matchUrl);
      renderResultPage(app, data.result, data.opponent_choice, opponentId);
    }
  };
}

function sendChoiceToServer(myChoice) {
  if (matchWs && matchWs.readyState === WebSocket.OPEN) {
    const payload = { choice: myChoice };
    matchWs.send(JSON.stringify(payload));
  }
}

function cleanupAllWebSockets() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  if (ws) {
    cleanupWs(ws);
    ws = null;
  }
  if (matchWs) {
    cleanupWs(matchWs);
    matchWs = null;
  }
  choice = "";
}

function cleanupWs(socket) {
  socket.onopen = null;
  socket.onmessage = null;
  socket.onerror = null;
  socket.onclose = null;
  socket.close();
}

function getOpponentIdFromUrl(url) {
  // url 예: "/ws/rps/sungmiki_junmoon/"
  const tokens = url.split("/").filter(Boolean);
  const lastPart = tokens[tokens.length - 1]; 
  const ids = lastPart.split("_");
  const opponent = ids.find(id => id !== intraId);
  return opponent || "UnknownOpponent";
}

function getImagePath(item) {
  switch (item) {
    case "rock": return "../img/rock.png";
    case "paper": return "../img/paper.png";
    case "scissor": return "../img/scissor.png";
    default: return "";
  }
}

function getRandomChoice() {
  const rps = ["rock", "paper", "scissor"];
  const idx = Math.floor(Math.random() * rps.length);
  return rps[idx];
}
