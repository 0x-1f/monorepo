import { changeLocale } from "../../modules/locale/localeManager";
import { getCookie, removeCookie } from "../../modules/cookie/cookieManager";

export function renderHeader(header, navigate) {

    const jwt = getCookie('jwt');
    if (!jwt && window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
    
    if (fetch('/api/auth/check_expired', {
        credentials: 'include',
    }).then(response => {
        if (response.status === 400) {
            removeCookie('jwt');
            navigate('2fa');
        }
    }));

    let intraId = '';
    fetch('/api/auth/get_intra_id/', {
        credentials: 'include',
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
    }).then(data => {
        intraId = data.intra_id;
        const uid = `<p>${intraId}</p>`;
        document.querySelector('.dropdown-content').append(uid);
    })

    header.innerHTML = `
        <header class="header">
            <button class="pongbtn"  id="pongbtn">PONG</button>
            <button class="dropbtn" id="dropbtn">Language</button>
            <div class="dropdown-content" id="dropdowncontent">
                <button id="en-US">English</button>
                <button id="ja-JP">日本語</button>
                <button id="ko-KR">한국어</button>
            </div> <!-- .dropdown-content -->
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
