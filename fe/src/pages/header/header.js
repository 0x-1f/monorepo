import { changeLocale } from "../../modules/locale/localeManager";
import { getCookie } from "../../modules/cookie/cookieManager";

export function renderHeader(header) {
    header.innerHTML = `
        <header class="header">
            <h1>PONG</h1>
            <button class="dropbtn" id="dropbtn">Language</button>
            <div class="dropdown-content" id="dropdowncontent">
                <button id="en-US">English</button>
                <button id="ja-JP">日本語</button>
                <button id="ko-KR">한국어</button>
            </div> <!-- .dropdown-content -->
        </header>
    `;

    const jwt = getCookie('jwt');
    if (!jwt && window.location.pathname !== '/login') {
        window.location.href = '/login';
    }

    if (fetch('/api/auth/check_expired', {
        credentials: 'include',
    }).then(response => {
        if (response.status === 400) {
            navigate('2fa');
        }
    }));

    document.getElementById('dropbtn').addEventListener('click', () => {
        const dropdown = document.getElementById('dropdowncontent');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });

    const currentUrl = window.location.href;
    if (currentUrl.includes('/game') || currentUrl.includes('/rps')) {
        document.getElementById('dropbtn').style.display = 'none';
    }

    document.getElementById('en-US').addEventListener('click', () => {
        changeLocale('en-US');
    });
    document.getElementById('ja-JP').addEventListener('click', () => {
        changeLocale('ja-JP');
    });
    document.getElementById('ko-KR').addEventListener('click', () => {
        changeLocale('ko-KR');
    });
}
