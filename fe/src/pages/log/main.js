import { t } from '/src/modules/locale/localeManager.js';

export function render(app, navigate) {
	app.innerHTML = `
		<div class="grid">
			<div class="grid-item-left" id="result-t">${t('result-t', 'tournament match log')}</div>
			<div class="grid-item-right" id="result-d">${t('result-d', 'dual match log')}</div>
			<div class="grid-item-left" id="result-rps">${t('result-rps', 'RSP match log')}</div>
		</div>
	`;
	document.getElementById('result-t').addEventListener('click', () => navigate('log/tournament'));
	document.getElementById('result-d').addEventListener('click', () => navigate('log/dual'));
	document.getElementById('result-rps').addEventListener('click', () => navigate('log/rps'));
}
