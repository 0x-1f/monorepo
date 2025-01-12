import { t } from '/src/modules/locale/localeManager.js';

export function render(app, navigate) {
	app.innerHTML = `
		${t('loading', 'loading')}
	`

	fetch('/api/auth/get_intra_id/', {
		credentials: 'include',
	}).then(response => {
		if (response.ok) {
			return response.json();
		}
		throw new Error('Failed to fetch intra_id');
	}).then(data => {
		const intraId = data.intra_id;
		const apiUrl = `/api/rps/${intraId}/history/`;
		fetch(apiUrl).then(response => {
			if (response.ok) {
				return response.json();
			}
			throw new Error('Failed to fetch history');
		}).then(data => {
			app.innerHTML = '';
			for (let i = 0; i < data.length; i++) {
				const item = data[i];
				// Generate HTML for the current item
				const htmlContent = `
				  <div class="game-result">
					<h3>Game ID: ${item.rps_id}</h3>
					<p>Date: ${item.date}</p>
					<p>Opponent: ${item.opponent || 'None'}</p>
					<p>Result: ${item.result}</p>
					<p>Player 1: ${item.player1_intra_id} (${item.player1_choice})</p>
					<p>Player 2: ${item.player2_intra_id || 'None'} (${item.player2_choice || 'None'})</p>
				  </div>
				`;
				// Append the HTML to the app element
				app.insertAdjacentHTML('beforeend', htmlContent);
			  }
		}).catch(error => {
			console.error('Error fetching history:', error);
		});
	}).catch(error => {
		console.error('eeeeeeeeeppppppyyy ', error);
	});
}