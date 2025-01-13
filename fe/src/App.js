import { renderHeader } from './pages/header/header.js';
import { loadLocale, setupLocaleListener } from './modules/locale/localeManager.js';

const app = document.getElementById('app');

setupLocaleListener();

window.addEventListener('localStorageChange', async (event) => {
    if (event.detail.key === 'locale') {
        const currentPath = window.location.pathname.replace('/', '') || 'login'; // Get current path
        await renderPage(currentPath); // Re-render the page dynamically
    }
});

window.addEventListener('storage', async (event) => {
    if (event.key === 'locale') {
        const currentPath = window.location.pathname.replace('/', '') || 'login';
        await renderPage(currentPath);
    }
});


// Routing map for multi-depth routes
const routes = {
    'login': () => import('./pages/login.js').then(module => module.render(app, navigate)),
    '2fa': () => import('./pages/2fa.js').then(module => module.render(app, navigate)),
    'main': () => import('./pages/main.js').then(module => module.render(app, navigate)),
    'game': {
        'offline': {
            'ai': () => import('./pages/game/offline/ai.js').then(module => module.render(app, navigate)),
            '2p': () => import('./pages/game/offline/2p.js').then(module => module.render(app, navigate)),
            '4p': () => import('./pages/game/offline/4p.js').then(module => module.render(app, navigate)),
        },
        'online': {
            '2p': () => import('./pages/game/online/2p.js').then(module => module.render(app, navigate)),
            // '2p': {
            //     'waiting_room': () => import('./pages/game/online/waiting_room.js').then(module => module.render(app, navigate)),
            //     'game': () => import('./pages/game/online/2p.js').then(module => module.render(app, navigate)),
            // },
        },
    },
    'log': {
        'main': () => import('./pages/log/main.js').then(module => module.render(app, navigate)),
        'dual': () => import('./pages/log/dual.js').then(module => module.render(app, navigate)),
        'rps': () => import('./pages/log/rps.js').then(module => module.render(app, navigate)),
    },
    'rps': () => import('./pages/rps.js').then(module => module.render(app, navigate)),
};

// Default error page
const errorPage = () => import('./pages/error.js').then(module => module.render(app, navigate));

function navigate(path) {
    history.pushState({ path }, "", `/${path}`);
    renderPage(path);
}

async function resolveRoute(path) {
    const segments = path.split('/');

    let currentRoute = routes;

    for (let i = 0; i < segments.length; i++) {
        // 현재 segment
        const segment = segments[i];

        // 아직 세그먼트가 남아있는데 currentRoute가 함수라면 => 에러
        if (typeof currentRoute === 'function') {
        return errorPage; 
        }

        // currentRoute가 객체(또는 중첩 라우트)라고 가정 → 해당 키로 접근
        currentRoute = currentRoute[segment];
        // 해당 키가 없으면 즉시 에러
        if (!currentRoute) {
        return errorPage;
        }
    }

    // 모든 segments를 소진한 후:
    // currentRoute가 함수면 정상 라우트, 아니면 에러
    if (typeof currentRoute === 'function') {
        return currentRoute;
    } else {
        return errorPage;
    }
}

async function renderPage(path) {
    await loadLocale();
    renderHeader(document.getElementById('header'), navigate);

    try {
        const renderer = await resolveRoute(path);
        renderer(app, navigate);
    } catch (error) {
        console.error(`Error rendering page for path "${path}":`, error);
    }
}

// Handle popstate for back/forward navigation
window.addEventListener('popstate', (event) => {
    renderPage(event.state ? event.state.path : 'main');
});

// Initial page load
const initialPath = window.location.pathname.replace('/', '') || 'main';
renderPage(initialPath);
