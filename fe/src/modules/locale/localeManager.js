const locales = {};

/**
 * Load a locale JSON file dynamically and cache it.
 * Automatically detects the `locale` value from `localStorage`.
 * @returns {Promise<object>} The loaded locale translations.
 */
export async function loadLocale() {
    const locale = localStorage.getItem('locale'); // Get the current locale from localStorage
    if (!locale) {
        console.warn('No locale set in localStorage.');
        return {};
    }

    if (locales[locale]) return locales[locale]; // Return cached locale if already loaded

    try {
        const translations = await fetch(`/locale/${locale}.json`).then((res) => res.json());
        locales[locale] = translations; // Cache the translations
        console.log(`Locale ${locale} loaded and cached.`);
        return translations;
    } catch (error) {
        console.error(`Failed to load locale: ${locale}`, error);
        return {}; // Return empty object on failure
    }
}

/**
 * Retrieve a translation by key with a fallback.
 * @param {string} key - The key to look up in the locale file.
 * @param {string} fallback - The fallback text if the key doesn't exist.
 * @returns {string} - The localized string or fallback.
 */
export function t(key, fallback) {
    const locale = localStorage.getItem('locale'); // Get the current locale from localStorage
    if (!locale || !locales[locale]) {
        console.warn('Locale not loaded or set.');
        return fallback;
    }
    return locales[locale]?.[key] || fallback;
}

/**
 * Listen for changes in the `locale` key in localStorage and reload the locale dynamically.
 */
export function setupLocaleListener() {
    // Listen for cross-tab locale changes
    window.addEventListener('storage', async (event) => {
        if (event.key === 'locale') {
            console.log(`Locale changed to ${event.newValue} across tabs.`);
            await loadLocale(); // Dynamically reload the locale
        }
    });

    // Listen for same-tab locale changes via a custom event
    window.addEventListener('localStorageChange', async (event) => {
        if (event.detail.key === 'locale') {
            console.log(`Locale changed to ${event.detail.value} in the same tab.`);
            await loadLocale(); // Dynamically reload the locale
        }
    });
}


export const changeLocale = (locale) => {
    localStorage.setItem('locale', locale);
    const event = new CustomEvent('localStorageChange', { detail: { key: 'locale', value: locale } });
    window.dispatchEvent(event);
};