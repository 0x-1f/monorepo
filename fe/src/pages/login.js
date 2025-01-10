export function render(app, navigate) {
    app.innerHTML = `
        <h1>PONG</h1>
        <button class="button btn-primary" id="loginButton">Login with 42</button>
    `;
    document.getElementById('loginButton').addEventListener('click', () => {
        // http://localhost:8081로 연결
        window.location.href = 'http://localhost:8081/users/login';
    });
}
