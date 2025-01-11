import rock from '/assets/rock.png';
import paper from '/assets/paper.png';
import scissor from '/assets/scissor.png';

let intraId = null;
let ws = null;
let matchWs = null;
let choice = "";
let countdownInterval = null;

export function render(app, navigate) {
    // 초기 렌더링
    renderStartPage(app);
    cleanupAllWebSockets();
    // renderRpsGamePage(app);
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
  waitingText.textContent = "Waiting for opponent...";
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
  waitingText.textContent = "Game will start soon...";
  waitingText.style.fontSize = "2em"; // 간단한건 그냥 남겨도 되지만, css class로 빼도 됨

  app.appendChild(waitingText);
}
/** 3) 게임 시작 화면 (가위바위보 선택) */
function renderRpsGamePage(app) {
  // 기존 화면 비우기
  app.innerHTML = "";

  // 1) 카운트다운 영역
  const counterDiv = document.createElement("div");
  counterDiv.className = "rps-counter"; 
  counterDiv.textContent = "10";  // 초기 카운트 10

  // 2) 3열 그리드 (가위바위보 선택 영역)
  const gridContainer = document.createElement("div");
  gridContainer.className = "rps-grid-container";

  // 3) 가위바위보 항목
  const items = ["rock", "paper", "scissor"];
  let selectedHighlightDiv = null; // 현재 선택 표시(div) 추적

  items.forEach(item => {
    // 3-1. 각 셀(각 그림용)
    const cellDiv = document.createElement("div");
    cellDiv.className = "rps-item";  
    // .rps-item:hover { background-color: #333; } → CSS에서 호버링 처리

    // 3-2. 이미지
    const img = document.createElement("img");
    img.className = "rps-img";  // 크기 120x120
    img.src = getImagePath(item);

    // 3-3. 선택 표시(하얀색 패)
    const highlightBar = document.createElement("div");
    highlightBar.className = "rps-select-highlight"; 
    // 기본 display: none (CSS에서)

    // 3-4. 클릭 이벤트: 기존 선택 해제 → 새 선택 표시
    cellDiv.addEventListener("click", () => {
      if (selectedHighlightDiv) {
        selectedHighlightDiv.style.display = "none"; // 기존 선택 숨김
      }
      highlightBar.style.display = "block"; // 새 선택 표시
      selectedHighlightDiv = highlightBar;
      choice = item; // 전역 변수 choice 갱신
    });

    // 3-5. 구조 조립
    cellDiv.appendChild(img);
    cellDiv.appendChild(highlightBar);
    gridContainer.appendChild(cellDiv);
  });

  // 4) 10초 미선택 시 랜덤처리 안내 문구
  const warningText = document.createElement("div");
  warningText.className = "rps-warning-text"; 
  warningText.textContent = "If you do not select in 10 seconds, a random selection will be made.";

  // 5) 화면에 요소들 추가
  app.appendChild(counterDiv);
  app.appendChild(gridContainer);
  app.appendChild(warningText);

  // 6) 10초 카운트다운
  let count = 10;
  countdownInterval = setInterval(() => {
    count--;
    counterDiv.textContent = String(count);

    if (count <= 0) {
      clearInterval(countdownInterval);
      countdownInterval = null;

      // 아직 아무것도 클릭 안했다면 랜덤 지정
      if (!choice) {
        choice = getRandomChoice();
      }

      // 서버 전송 후 "응답 대기" 페이지로 이동
      sendChoiceToServer(choice);
      renderWaitingResultPage(app);
    }
  }, 1000);
}

/** 4) 응답 대기 화면 */
function renderWaitingResultPage(app) {
  app.innerHTML = "";

  const text = document.createElement("div");
  text.textContent = "Waiting for result...";
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
  const splitted = matchUrl.split("/");
  const matchName = splitted[splitted.length - 1];
  matchWs = new WebSocket(`ws://localhost:8081/ws/rps/match/${matchName}/${intraId}`);
  matchWs.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === "start") {
      renderRpsGamePage(app);
    }
    if (data.result) {
      const opponentId = getOpponentIdFromMatchName(matchName);
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

function getOpponentIdFromMatchName(matchName) {
  // matchName 예: "sungmiki_junmoon"
  const splitted = matchName.split("_");  // ["sungmiki", "junmoon"]

  // 전역변수 intraId(내 아이디)와 다른 쪽이 상대방 아이디
  // Array.splitted(() =>{}) 는 Array의 요소 중 함수의 조건을 만족하는 첫번째 요소를 반환
  const opponent = splitted.find((id) => id !== intraId);
  return opponent || "UnknownOpponent";
}

function getImagePath(item) {
  switch (item) {
    case "rock": return rock;
    case "paper": return paper;
    case "scissor": return scissor;
    default: return "";
  }
}

function getRandomChoice() {
  const rps = ["rock", "paper", "scissor"];
  const idx = Math.floor(Math.random() * rps.length);
  return rps[idx];
}