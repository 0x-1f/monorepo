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
					<div class="left-tab">
						<p>Date: ${item.date}</p>
						<p>${item.winner_score} by (${item.loser_score})</p>
					</div>
					<div class="right-tab">
						<p>Winner: ${item.winner}</p>
						<p>Loser: ${item.loser}</p>
					</div>
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