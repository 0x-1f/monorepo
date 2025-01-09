import { changeLocale } from "../../modules/locale/localeManager";

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

    document.getElementById('dropbtn').addEventListener('click', () => {
        const dropdown = document.getElementById('dropdowncontent');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });

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
