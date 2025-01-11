import { t } from '/src/modules/locale/localeManager.js';

export function render(app, navigate) {
	app.innerHTML = `
	<h1>${t('2fa', '2FA')}</h1>
	<form id="2fa-form">
		<input type="text" id="2fa-input" placeholder="${t('2fa-placeholder', 'Enter 2FA code')}" maxlength="6" required>
		<button type="submit">${t('2fa-submit', 'Submit')}</button>
	</form>
	`;
}