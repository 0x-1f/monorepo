import { getCookie } from '/src/modules/cookie/cookieManager.js';

export function render(app, navigate) {
    app.innerHTML = `
        <h1>PONG</h1>
        <button class="button btn-primary" id="loginButton">Login with 42</button>
    `;
    document.getElementById('loginButton').addEventListener('click', () => {
        window.location.href = 'http://localhost/api/auth/login';
    });

    if (getCookie('jwt')) {
        navigate('main');
    }
}
