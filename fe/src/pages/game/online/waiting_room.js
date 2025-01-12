import { t } from '/src/modules/locale/localeManager.js';
import { setCookie } from '/src/modules/cookie/cookieManager.js';

export function render(app, navigate) {
    app.innerHTML = `
        <div class="grid">
            <div class="grid-item-left" id="you">${t('you', 'You')}</div>
            <div class="grid-item-right" id="rival">${t('wait_part', 'Waiting for participations...')}</div>
        </div>
    `;

    // document.getElementById('you').addEventListener('click', () => navigate('game/online/2p'));
    // document.getElementById('rival').addEventListener('click', () => navigate('game/online/4p'));
	let wss;

    //
	fetch('/api/auth/get_intra_id', {
		credentials: 'include',
	}).then(response => {
		response.json().then(data => {
			if (data.intra_id === null) {
				alert('You need to set your intra ID first');
				navigate('main');
			} else {
				wss = new WebSocket(`wss://localhost/ws/pong/join/${data.intra_id}`);
			 	const intra_id = data.intra_id
				console.log(wss)
				console.log('websocket connected')

				wss.onopen = function(e) {
					console.log('Waiting for participations...');
				}

				wss.onmessage = function(e) {
					console.log(e.data);
					const data = JSON.parse(e.data);
					const match_url = data.match_url;
					setCookie('match_url', match_url);
					console.log('setCookie: match_url')
					console.log(match_url)
					//
					setCookie('intraID', intra_id);
					console.log('setCookie: intraID')
					//
					navigate('game/online/2p/game');
				}
			}
		});
	}).catch(error => {
		console.error('Error:', error);
	});
	//

	window.onpopstate = function(event) {
		if (wss.readyState === wss.OPEN) {
			wss.close(); // 필요하면 닫기
		}
	};
}
