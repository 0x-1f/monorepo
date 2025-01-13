import { t } from '/src/modules/locale/localeManager.js';

export function render(app, navigate) {
	app.innerHTML = `
		<div class="grid">
			<div class="grid-item-left" id="result-d">${t('result-d', '1:1 match log')}</div>
			<div class="grid-item-right" id="result-rps">${t('result-rps', 'RSP match log')}</div>
		</div>
	`;
	document.getElementById('result-d').addEventListener('click', () => navigate('log/dual'));
	document.getElementById('result-rps').addEventListener('click', () => navigate('log/rps'));
}
