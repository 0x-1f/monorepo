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
		const apiUrl = `/api/pong/${intraId}/history/`;
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
					<h3>Game ID: ${item.pong_id}</h3>
					<p>Date: ${item.date}</p>
					<p>Winner: ${item.winner}</p>
					<p>Loser: ${item.loser}</p>
					<p>Score: ${item.winner_score} by (${item.loser_score})</p>
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