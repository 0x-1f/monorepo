// Function to set a cookie
export function setCookie(name, value, options = {}) {
    let cookieStr = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;

    if (options.expires) {
        if (options.expires instanceof Date) {
            cookieStr += `; expires=${options.expires.toUTCString()}`;
        } else {
            cookieStr += `; expires=${options.expires}`;
        }
    }

    if (options.path) {
        cookieStr += `; path=${options.path}`;
    }

    if (options.domain) {
        cookieStr += `; domain=${options.domain}`;
    }

    if (options.secure) {
        cookieStr += `; secure`;
    }

    if (options.sameSite) {
        cookieStr += `; samesite=${options.sameSite}`;
    }

    document.cookie = cookieStr;
}

// Function to get a cookie by name
export function getCookie(name) {
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
        const [key, value] = cookie.split('=');
        if (key === encodeURIComponent(name)) {
            return decodeURIComponent(value);
        }
    }
    return null; // Cookie not found
}
