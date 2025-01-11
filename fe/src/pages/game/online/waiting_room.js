// import { t } from '/src/modules/locale/localeManager.js';
// import { setCookie } from '/src/modules/cookie/cookieManager.js';

// export function render(app, navigate) {
//     app.innerHTML = `
//         <div class="grid">
//             <div class="grid-item-left" id="you">${t('you', 'You')}</div>
//             <div class="grid-item-right" id="rival">${t('wait_part', 'Waiting for participations...')}</div>
//         </div>
//     `;

//     // document.getElementById('you').addEventListener('click', () => navigate('game/online/2p'));
//     // document.getElementById('rival').addEventListener('click', () => navigate('game/online/4p'));

//     const wss = new WebSocket('wss://localhost:8081/ws/pong');

//     wss.onopen = function(e) {
// 		console.log('Waiting for participations...');
// 	}

// 	wss.onmessage = function(e) {
// 		console.log(e);
// 		const data = JSON.parse(e);
// 		const match_url = data.match_url;
//         setCookie('match_url', match_url);
// 		navigate('game/online/2p/game');
// 	}
// }
