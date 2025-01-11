import { getCookie } from '/src/modules/cookie/cookieManager.js';
import { t } from '/src/modules/locale/localeManager.js';

export function render(app, navigate) {
	app.innerHTML = `
	<h1>${t('2fa', '2FA')}</h1>
	<form id="2fa-form">
		<input type="text" id="2fa-input" placeholder="${t('2fa-placeholder', 'Enter 2FA code')}" maxlength="6" required>
		<button type="submit" id="submit">${t('2fa-submit', 'Submit')}</button>
	</form>
	`;

	document.getElementById('2fa-form').addEventListener('submit', async (e) => {
		e.preventDefault();
		const code = document.getElementById('2fa-input').value;
		if (code.length !== 6) {
			alert(t('2fa-invalid', 'Invalid 2FA code'));
			return;
		}
		fetch('/api/auth/verify/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
					'code': code,
					'jwt': getCookie('jwt'),
				}),
		}).then(response => {
			if (response.ok) {
				navigate('main');
			} else {
				alert(t('2fa-invalid', 'Invalid 2FA code'));
			}
		});
	});

}