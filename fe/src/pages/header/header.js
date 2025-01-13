import { changeLocale } from "../../modules/locale/localeManager";
import { getCookie, removeCookie } from "../../modules/cookie/cookieManager";

export function renderHeader(header, navigate) {

    const jwt = getCookie('jwt');
    if (!jwt) {
        navigate('login');
    }

    if (fetch('/api/auth/check_expired', {
        credentials: 'include',
    }).then(response => {
        if (response.status === 400) {
            removeCookie('jwt');
            navigate('2fa');
        }
    }));

    fetch('/api/auth/get_intra_id/', {
        credentials: 'include',
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
    }).then(data => {
        const divElement = document.querySelector('.uid');
        if (divElement && divElement.querySelector('p')) {
            return;
        }
        const intraId = data.intra_id;
        const uidElement = document.createElement('p');
        uidElement.textContent = intraId;
        document.querySelector('.uid').append(uidElement);
    });

    header.innerHTML = `
        <header class="header">
            <button class="pongbtn" id="pongbtn">PONG</button>
            <button class="dropbtn" id="dropbtn">Language</button>
            <div class="dropdown-content" id="dropdowncontent">
                <button id="en-US">English</button>
                <button id="ja-JP">日本語</button>
                <button id="ko-KR">한국어</button>
            </div> <!-- .dropdown-content -->
            <div class="uid"></div>
        </header>
    `;

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

    document.getElementById('pongbtn').addEventListener('click', () => {
        navigate('main');
    });
}
