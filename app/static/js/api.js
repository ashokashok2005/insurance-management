const API_BASE = '/api';

const TOKEN_KEY = 'token';
const USER_KEY = 'user';

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function saveToken(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    if (user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
}

function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

async function fetchWithAuth(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        logout();
        return null;
    }

    return response;
}

function logout() {
    removeToken();
    window.location.href = '/login';
}

function getUser() {
    const u = localStorage.getItem('user');
    try {
        return JSON.parse(u);
    } catch (e) {
        return u;
    }
}

function checkAuth() {
    const token = getToken();
    const path = window.location.pathname;

    if (!token && path !== '/login' && path !== '/register') {
        window.location.href = '/login';
    } else if (token && (path === '/login' || path === '/register')) {
        window.location.href = '/dashboard';
    } else {
        // Show correct UI based on auth state
        if (token) {
            document.getElementById('main-app').classList.remove('hidden');
            if (document.getElementById('auth-app')) {
                document.getElementById('auth-app').classList.add('hidden');
            }

            // Role Based UI
            const user = getUser();
            const adminLinks = document.querySelectorAll('.nav-links-bottom .nav-item');
            const superAdminLinks = document.querySelectorAll('.super-admin-only');

            if (user) {
                // Settings visibility (admin/super_admin)
                const settingsLink = document.querySelector('a[href="/settings"]');
                const isAdvancedUser = ['admin', 'agency_admin', 'super_admin'].includes(user.role);
                if (settingsLink) settingsLink.parentElement.style.display = isAdvancedUser ? 'block' : 'none';

                // Admin/Agency Admin links
                adminLinks.forEach(item => {
                    const link = item.querySelector('a');
                    if (link && (link.getAttribute('href').startsWith('/admin') || link.getAttribute('href').startsWith('/agencies'))) {
                        item.style.display = isAdvancedUser ? 'block' : 'none';
                    }
                });

                // Super Admin specific
                superAdminLinks.forEach(item => {
                    item.style.display = (user.role === 'super_admin') ? 'block' : 'none';
                });
            }
        } else {
            if (document.getElementById('auth-app')) {
                document.getElementById('auth-app').classList.remove('hidden');
            }
            if (document.getElementById('main-app')) {
                document.getElementById('main-app').classList.add('hidden');
            }
        }
    }
}
