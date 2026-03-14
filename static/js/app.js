/* ============================================
   FutsLab - Frontend Application Logic
   ============================================ */

// ===== CONFIGURATION =====
const API_BASE = window.location.origin + '/api/v1';
const MEDIA_BASE = window.location.origin;

// ===== STATE =====
let state = {
    token: localStorage.getItem('futslab_token') || null,
    user: JSON.parse(localStorage.getItem('futslab_user') || 'null'),
    role: localStorage.getItem('futslab_role') || null,
    currentPage: 'dashboard',
    gameTab: 'upcoming',
};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        loadingScreen.classList.add('fade-out');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            initApp();
        }, 500);
    }, 1500);
});

function initApp() {
    if (state.token) {
        showApp();
    } else {
        showAuth();
    }
    setupForms();
}

// ===== AUTH FUNCTIONS =====
function showAuth() {
    document.getElementById('auth-container').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
    showPage('login-page');
}

function showApp() {
    document.getElementById('auth-container').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    updateUserUI();
    loadDashboard();
}

function showPage(pageId) {
    document.querySelectorAll('.auth-page').forEach(p => p.classList.add('hidden'));
    document.getElementById(pageId).classList.remove('hidden');
}

function showForgotPassword() {
    showPage('forgot-password-page');
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function setupForms() {
    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('login-btn');
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Signing in...';

        try {
            const res = await fetch(`${API_BASE}/accounts/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (res.ok) {
                state.token = data.token;
                state.role = data.role;
                localStorage.setItem('futslab_token', data.token);
                localStorage.setItem('futslab_role', data.role);
                showToast('Welcome back!', 'success');
                await fetchUserProfile();
                showApp();
            } else {
                const errorMsg = typeof data === 'object' ? 
                    (data.non_field_errors ? data.non_field_errors[0] : JSON.stringify(data)) : 
                    data;
                showToast(errorMsg, 'error');
            }
        } catch (err) {
            showToast('Connection error. Please check if the server is running.', 'error');
        }

        btn.disabled = false;
        btn.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('register-btn');
        
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const contact = document.getElementById('reg-contact').value;
        const date_of_birth = document.getElementById('reg-dob').value;
        const favorite_player = document.getElementById('reg-fav-player').value;
        const favorite_team = document.getElementById('reg-fav-team').value;
        const password = document.getElementById('reg-password').value;
        const confirm_password = document.getElementById('reg-confirm').value;

        if (password !== confirm_password) {
            showToast('Passwords do not match!', 'error');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Creating account...';

        try {
            const body = { name, email, password, confirm_password };
            if (contact) body.contact = contact;
            if (date_of_birth) body.date_of_birth = date_of_birth;
            if (favorite_player) body.favorite_player = favorite_player;
            if (favorite_team) body.favorite_team = favorite_team;

            const res = await fetch(`${API_BASE}/accounts/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const data = await res.json();

            if (res.ok) {
                showToast('Account created! Please sign in.', 'success');
                showPage('login-page');
                document.getElementById('register-form').reset();
            } else {
                const errorMsg = extractErrors(data);
                showToast(errorMsg, 'error');
            }
        } catch (err) {
            showToast('Connection error.', 'error');
        }

        btn.disabled = false;
        btn.innerHTML = '<span>Create Account</span><i class="fas fa-arrow-right"></i>';
    });

    // Forgot password form
    document.getElementById('forgot-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('forgot-btn');
        const email = document.getElementById('forgot-email').value;

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Sending...';

        try {
            const res = await fetch(`${API_BASE}/accounts/password/forget/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await res.json();
            if (res.ok) {
                showToast(data.message, 'success');
            } else {
                showToast(data.message || 'Error sending OTP', 'error');
            }
        } catch (err) {
            showToast('Connection error.', 'error');
        }

        btn.disabled = false;
        btn.innerHTML = '<span>Send OTP</span><i class="fas fa-paper-plane"></i>';
    });

    // Edit profile form
    document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData();
        
        const name = document.getElementById('edit-name').value;
        const contact = document.getElementById('edit-contact').value;
        const dob = document.getElementById('edit-dob').value;
        const favPlayer = document.getElementById('edit-fav-player').value;
        const favTeam = document.getElementById('edit-fav-team').value;

        if (name) formData.append('name', name);
        if (contact) formData.append('contact', contact);
        if (dob) formData.append('date_of_birth', dob);
        if (favPlayer) formData.append('favorite_player', favPlayer);
        if (favTeam) formData.append('favorite_team', favTeam);

        try {
            const res = await fetch(`${API_BASE}/accounts/user/edit/`, {
                method: 'PATCH',
                headers: { 'Authorization': `Token ${state.token}` },
                body: formData
            });

            const data = await res.json();
            if (res.ok) {
                showToast('Profile updated!', 'success');
                await fetchUserProfile();
                updateUserUI();
                loadProfile();
            } else {
                showToast(extractErrors(data), 'error');
            }
        } catch (err) {
            showToast('Error updating profile.', 'error');
        }
    });

    // Change password form
    document.getElementById('change-password-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const current = document.getElementById('current-password').value;
        const newPass = document.getElementById('new-password').value;
        const confirm = document.getElementById('confirm-new-password').value;

        if (newPass !== confirm) {
            showToast('New passwords do not match!', 'error');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/accounts/password/change/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${state.token}`
                },
                body: JSON.stringify({
                    current_password: current,
                    new_password: newPass,
                    confirm_password: confirm
                })
            });

            const data = await res.json();
            if (res.ok) {
                showToast('Password changed!', 'success');
                document.getElementById('change-password-form').reset();
            } else {
                showToast(extractErrors(data), 'error');
            }
        } catch (err) {
            showToast('Error changing password.', 'error');
        }
    });

    // Create game form
    document.getElementById('create-game-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const futsal = document.getElementById('game-futsal').value;
        const date = document.getElementById('game-date').value;
        const time = document.getElementById('game-time').value;

        try {
            const res = await fetch(`${API_BASE}/games/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${state.token}`
                },
                body: JSON.stringify({ futsal, date, time: time + ':00' })
            });

            const data = await res.json();
            if (res.ok) {
                showToast(`Game ${data.game} created!`, 'success');
                document.getElementById('create-game-form').reset();
                navigateTo('games');
            } else {
                showToast(extractErrors(data), 'error');
            }
        } catch (err) {
            showToast('Error creating game.', 'error');
        }
    });
}

// ===== API HELPERS =====
function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Token ${state.token}`
    };
}

async function apiFetch(url, options = {}) {
    const headers = options.headers || authHeaders();
    try {
        const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
        if (res.status === 401) {
            logout();
            return null;
        }
        return await res.json();
    } catch (err) {
        console.error('API Error:', err);
        return null;
    }
}

function extractErrors(data) {
    if (typeof data === 'string') return data;
    if (data.message) return data.message;
    if (data.detail) return data.detail;
    
    let errors = [];
    for (const key in data) {
        if (Array.isArray(data[key])) {
            errors.push(...data[key]);
        } else if (typeof data[key] === 'string') {
            errors.push(data[key]);
        } else if (typeof data[key] === 'object') {
            errors.push(extractErrors(data[key]));
        }
    }
    return errors.join(' ') || 'An error occurred.';
}

function getMediaUrl(path) {
    if (!path) return 'https://ui-avatars.com/api/?name=Player&background=6C5CE7&color=fff&size=128';
    if (path.startsWith('http')) return path;
    return `${MEDIA_BASE}/${path.startsWith('/') ? path.slice(1) : path}`;
}

// ===== USER FUNCTIONS =====
async function fetchUserProfile() {
    const data = await apiFetch('/players/info/');
    if (data && data.player) {
        state.user = data.player;
        localStorage.setItem('futslab_user', JSON.stringify(data.player));
    }
}

function updateUserUI() {
    const user = state.user;
    const avatarUrl = user ? getMediaUrl(user.photo) : 'https://ui-avatars.com/api/?name=U&background=6C5CE7&color=fff&size=128';
    const name = user ? user.name : 'User';

    // Sidebar
    document.getElementById('sidebar-avatar').src = avatarUrl;
    document.getElementById('sidebar-username').textContent = name;
    document.getElementById('sidebar-role').textContent = state.role || 'Player';

    // Topbar
    document.getElementById('topbar-avatar').src = avatarUrl;
    document.getElementById('topbar-username').textContent = name;

    // Show/hide manager-only items
    const managerItems = document.querySelectorAll('.manager-only');
    managerItems.forEach(item => {
        if (state.role === 'MANAGER') {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

function logout() {
    // Call logout API
    fetch(`${API_BASE}/accounts/logout/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${state.token}` }
    }).catch(() => {});

    state.token = null;
    state.user = null;
    state.role = null;
    localStorage.removeItem('futslab_token');
    localStorage.removeItem('futslab_user');
    localStorage.removeItem('futslab_role');
    showToast('Logged out!', 'info');
    showAuth();
}

// ===== NAVIGATION =====
function navigateTo(page) {
    state.currentPage = page;

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'games': 'Games',
        'players': 'Players',
        'profile': 'My Profile',
        'create-game': 'Create Game',
        'game-detail': 'Game Details',
        'player-detail': 'Player Details'
    };
    document.getElementById('page-title').textContent = titles[page] || 'FutsLab';

    // Show/hide pages
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    const pageEl = document.getElementById(`${page}-page`);
    if (pageEl) {
        pageEl.classList.remove('hidden');
        pageEl.style.animation = 'none';
        pageEl.offsetHeight; // Trigger reflow
        pageEl.style.animation = null;
    }

    // Load page data
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'games': loadGames(); break;
        case 'players': loadPlayers(); break;
        case 'profile': loadProfile(); break;
        case 'create-game': loadCreateGame(); break;
    }

    // Close mobile sidebar
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('mobile-open');
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ===== SIDEBAR =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('mobile-open');
        // Create/toggle overlay
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.onclick = () => {
                sidebar.classList.remove('mobile-open');
                overlay.classList.remove('active');
            };
            document.body.appendChild(overlay);
        }
        overlay.classList.toggle('active');
    } else {
        sidebar.classList.toggle('collapsed');
    }
}

// ===== DASHBOARD =====
async function loadDashboard() {
    // Load user stats
    if (state.user) {
        animateValue('dash-rating', state.user.rating || 50);
        animateValue('dash-goals', state.user.goals || 0);
        animateValue('dash-assists', state.user.assists || 0);
        animateValue('dash-games', state.user.games_played || 0);
    } else {
        await fetchUserProfile();
        if (state.user) {
            animateValue('dash-rating', state.user.rating || 50);
            animateValue('dash-goals', state.user.goals || 0);
            animateValue('dash-assists', state.user.assists || 0);
            animateValue('dash-games', state.user.games_played || 0);
        }
    }

    // Load upcoming games
    const upcomingGames = await apiFetch('/games/get/?type=upcoming');
    renderDashUpcomingGames(upcomingGames);

    // Load top players
    const players = await apiFetch('/players/');
    renderDashTopPlayers(players);
}

function animateValue(elementId, endValue) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    const duration = 1000;
    const startTime = performance.now();
    const startValue = 0;
    const numericEnd = parseFloat(endValue);

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // cubic ease out

        const current = startValue + (numericEnd - startValue) * eased;
        el.textContent = Number.isInteger(numericEnd) ? Math.round(current) : current.toFixed(1);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function renderDashUpcomingGames(games) {
    const container = document.getElementById('dash-upcoming-games');
    if (!games || !Array.isArray(games) || games.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-xmark"></i>
                <p>No upcoming games</p>
            </div>
        `;
        return;
    }

    const limited = games.slice(0, 3);
    container.innerHTML = limited.map(game => `
        <div class="game-card" onclick="viewGameDetail('${game.game_id}')">
            <div class="game-card-teams">
                <div class="game-team">
                    <div class="game-team-logo">
                        ${game.logoA ? `<img src="${getMediaUrl(game.logoA)}" alt="">` : 'A'}
                    </div>
                    <span class="game-team-name">${game.teamnameA || 'Team A'}</span>
                </div>
                <span class="game-vs">VS</span>
                <div class="game-team">
                    <div class="game-team-logo" style="background: var(--gradient-secondary);">
                        ${game.logoB ? `<img src="${getMediaUrl(game.logoB)}" alt="">` : 'B'}
                    </div>
                    <span class="game-team-name">${game.teamnameB || 'Team B'}</span>
                </div>
            </div>
            <div class="game-card-meta">
                <span class="game-date"><i class="fas fa-calendar"></i> ${formatDate(game.date)}</span>
                <span class="game-venue"><i class="fas fa-clock"></i> ${formatTime(game.time)}</span>
                ${game.futsal ? `<span class="game-venue"><i class="fas fa-location-dot"></i> ${game.futsal.name}</span>` : ''}
            </div>
        </div>
    `).join('');
}

function renderDashTopPlayers(players) {
    const container = document.getElementById('dash-top-players');
    if (!players || !Array.isArray(players) || players.length === 0) {
        // Try checking for .results property (DRF paginated response)
        if (players && players.results) {
            players = players.results;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-users-slash"></i>
                    <p>No players yet</p>
                </div>
            `;
            return;
        }
    }

    const sorted = [...players].sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 6);
    container.innerHTML = sorted.map((player, index) => `
        <div class="player-mini-card" onclick="viewPlayerDetail('${player.slug}')">
            <div class="player-mini-avatar">
                <img src="${getMediaUrl(player.photo)}" alt="${player.name}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=6C5CE7&color=fff'">
            </div>
            <div class="player-mini-info">
                <span class="player-mini-name">${player.name}</span>
                <span class="player-mini-rating"><i class="fas fa-star"></i> ${player.rating || 50}</span>
            </div>
            <span class="player-mini-rank">#${index + 1}</span>
        </div>
    `).join('');
}

// ===== GAMES =====
async function loadGames() {
    const data = await apiFetch(`/games/get/?type=${state.gameTab}`);
    renderGamesList(data);
}

function switchGameTab(tab) {
    state.gameTab = tab;
    document.getElementById('tab-upcoming').classList.toggle('active', tab === 'upcoming');
    document.getElementById('tab-completed').classList.toggle('active', tab === 'completed');
    loadGames();
}

function renderGamesList(games) {
    const container = document.getElementById('games-list-container');
    
    if (!games || !Array.isArray(games) || games.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <i class="fas fa-gamepad"></i>
                <p>No ${state.gameTab} games found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = games.map(game => `
        <div class="game-grid-card" onclick="viewGameDetail('${game.game_id}')">
            <div class="game-grid-header">
                <span class="game-id">${game.game_id}</span>
                <span class="game-status ${state.gameTab}">${state.gameTab === 'upcoming' ? 'Upcoming' : 'Completed'}</span>
            </div>
            <div class="game-grid-body">
                <div class="game-grid-team">
                    <div class="game-grid-team-logo">
                        ${game.logoA ? `<img src="${getMediaUrl(game.logoA)}" alt="">` : game.teamnameA ? game.teamnameA.charAt(0) : 'A'}
                    </div>
                    <span class="game-grid-team-name">${game.teamnameA || 'Team A'}</span>
                </div>
                <div class="game-grid-score">
                    ${game.goalsA}<span>:</span>${game.goalsB}
                </div>
                <div class="game-grid-team">
                    <div class="game-grid-team-logo team-b">
                        ${game.logoB ? `<img src="${getMediaUrl(game.logoB)}" alt="">` : game.teamnameB ? game.teamnameB.charAt(0) : 'B'}
                    </div>
                    <span class="game-grid-team-name">${game.teamnameB || 'Team B'}</span>
                </div>
            </div>
            <div class="game-grid-footer">
                <div class="game-grid-meta">
                    <span class="game-grid-meta-item">
                        <i class="fas fa-calendar"></i> ${formatDate(game.date)}
                    </span>
                    <span class="game-grid-meta-item">
                        <i class="fas fa-clock"></i> ${formatTime(game.time)}
                    </span>
                </div>
                ${game.futsal ? `
                    <span class="game-grid-meta-item">
                        <i class="fas fa-location-dot"></i> ${game.futsal.name}
                    </span>
                ` : ''}
            </div>
        </div>
    `).join('');
}

async function viewGameDetail(gameId) {
    navigateTo('game-detail');
    const container = document.getElementById('game-detail-content');
    container.innerHTML = '<div class="empty-state"><div class="spinner"></div><p>Loading...</p></div>';

    const game = await apiFetch(`/games/get/${gameId}/`);
    if (!game) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Game not found</p></div>';
        return;
    }

    const isPlayer = state.role === 'PLAYER';
    const isUpcoming = !game.is_complete;

    container.innerHTML = `
        <div class="game-detail-hero">
            <div class="game-detail-teams">
                <div class="game-detail-team">
                    <div class="game-detail-team-logo">
                        ${game.logoA ? `<img src="${getMediaUrl(game.logoA)}" alt="">` : game.teamnameA ? game.teamnameA.charAt(0) : 'A'}
                    </div>
                    <span class="game-detail-team-name">${game.teamnameA || 'Team A'}</span>
                </div>
                <div class="game-detail-score">
                    ${game.goalsA}<span>:</span>${game.goalsB}
                </div>
                <div class="game-detail-team">
                    <div class="game-detail-team-logo team-b">
                        ${game.logoB ? `<img src="${getMediaUrl(game.logoB)}" alt="">` : game.teamnameB ? game.teamnameB.charAt(0) : 'B'}
                    </div>
                    <span class="game-detail-team-name">${game.teamnameB || 'Team B'}</span>
                </div>
            </div>
            <div class="game-detail-info">
                <span class="game-detail-info-item"><i class="fas fa-calendar"></i> ${formatDate(game.date)}</span>
                <span class="game-detail-info-item"><i class="fas fa-clock"></i> ${formatTime(game.time)}</span>
                ${game.futsal ? `<span class="game-detail-info-item"><i class="fas fa-location-dot"></i> ${game.futsal.name}</span>` : ''}
                <span class="game-detail-info-item">
                    <i class="fas fa-${game.is_complete ? 'check-circle' : 'hourglass-half'}"></i>
                    ${game.is_complete ? 'Completed' : 'Upcoming'}
                </span>
            </div>
        </div>

        ${isUpcoming && isPlayer ? `
            <div class="game-register-section">
                <button class="btn btn-success" onclick="registerForGame('${gameId}')" id="register-game-btn">
                    <i class="fas fa-user-plus"></i> Register for this Game
                </button>
            </div>
        ` : ''}

        <div class="game-detail-rosters">
            <div class="roster-card">
                <h4><span style="color: var(--accent-primary);">■</span> ${game.teamnameA || 'Team A'}</h4>
                ${game.teamA && game.teamA.length > 0 ? game.teamA.map(p => `
                    <div class="roster-player" onclick="viewPlayerDetail('${p.slug}')">
                        <div class="roster-player-avatar">
                            <img src="${getMediaUrl(p.photo)}" alt="${p.name}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(p.name)}&background=6C5CE7&color=fff'">
                        </div>
                        <span class="roster-player-name">${p.name}</span>
                        <span class="roster-player-rating"><i class="fas fa-star"></i> ${p.rating}</span>
                    </div>
                `).join('') : '<p style="color: var(--text-muted); font-size: 0.85rem; padding: 0.5rem;">No players assigned yet</p>'}
            </div>
            <div class="roster-card">
                <h4><span style="color: var(--accent-secondary);">■</span> ${game.teamnameB || 'Team B'}</h4>
                ${game.teamB && game.teamB.length > 0 ? game.teamB.map(p => `
                    <div class="roster-player" onclick="viewPlayerDetail('${p.slug}')">
                        <div class="roster-player-avatar">
                            <img src="${getMediaUrl(p.photo)}" alt="${p.name}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(p.name)}&background=00B894&color=fff'">
                        </div>
                        <span class="roster-player-name">${p.name}</span>
                        <span class="roster-player-rating"><i class="fas fa-star"></i> ${p.rating}</span>
                    </div>
                `).join('') : '<p style="color: var(--text-muted); font-size: 0.85rem; padding: 0.5rem;">No players assigned yet</p>'}
            </div>
        </div>
    `;
}

async function registerForGame(gameId) {
    const btn = document.getElementById('register-game-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Registering...';

    try {
        const res = await fetch(`${API_BASE}/games/get/${gameId}/register/`, {
            method: 'POST',
            headers: authHeaders()
        });

        const data = await res.json();
        if (res.ok) {
            showToast(data.message, 'success');
            btn.innerHTML = '<i class="fas fa-check"></i> Registered!';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-secondary');
        } else {
            showToast(data.message || 'Error registering.', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Register for this Game';
        }
    } catch (err) {
        showToast('Error registering.', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-user-plus"></i> Register for this Game';
    }
}

// ===== PLAYERS =====
async function loadPlayers() {
    const data = await apiFetch('/players/');
    let players = data;
    
    // Handle paginated response
    if (data && data.results) {
        players = data.results;
    }

    renderPlayersList(players);
}

function renderPlayersList(players) {
    const container = document.getElementById('players-grid');

    if (!players || !Array.isArray(players) || players.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <i class="fas fa-users"></i>
                <p>No players found</p>
            </div>
        `;
        return;
    }

    const sorted = [...players].sort((a, b) => (b.rating || 0) - (a.rating || 0));
    container.innerHTML = sorted.map(player => `
        <div class="player-card" onclick="viewPlayerDetail('${player.slug}')">
            <div class="player-card-avatar">
                <img src="${getMediaUrl(player.photo)}" alt="${player.name}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=6C5CE7&color=fff&size=128'">
            </div>
            <div class="player-card-name">${player.name}</div>
            <div class="player-card-rating">
                <i class="fas fa-star"></i> ${player.rating || 50}
            </div>
            <div class="player-card-stats">
                <div class="player-card-stat">
                    <span class="player-card-stat-value">${player.age || '--'}</span>
                    <span class="player-card-stat-label">Age</span>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewPlayerDetail(slug) {
    navigateTo('player-detail');
    const container = document.getElementById('player-detail-content');
    container.innerHTML = '<div class="empty-state"><div class="spinner"></div><p>Loading...</p></div>';

    const data = await apiFetch(`/players/info/${slug}/`);
    
    if (!data || !data.player) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Player not found</p></div>';
        return;
    }

    const player = data.player;
    const ratingClass = player.rating >= 70 ? 'high' : player.rating >= 40 ? 'medium' : 'low';

    container.innerHTML = `
        <div class="player-detail-hero">
            <div class="player-detail-avatar">
                <img src="${getMediaUrl(player.photo)}" alt="${player.name}" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=6C5CE7&color=fff&size=150'">
            </div>
            <h2 class="player-detail-name">${player.name}</h2>
            <p class="player-detail-email">${player.email || ''}</p>
            ${player.description ? `<p class="player-detail-description">${player.description}</p>` : ''}
            
            <div class="player-detail-stats">
                <div class="player-detail-stat">
                    <div class="rating-circle ${ratingClass}">${player.rating || 50}</div>
                    <span class="player-detail-stat-label" style="margin-top: 0.5rem;">Rating</span>
                </div>
                <div class="player-detail-stat">
                    <span class="player-detail-stat-value">${player.goals || 0}</span>
                    <span class="player-detail-stat-label">Goals</span>
                </div>
                <div class="player-detail-stat">
                    <span class="player-detail-stat-value">${player.assists || 0}</span>
                    <span class="player-detail-stat-label">Assists</span>
                </div>
                <div class="player-detail-stat">
                    <span class="player-detail-stat-value">${player.games_played || 0}</span>
                    <span class="player-detail-stat-label">Games</span>
                </div>
            </div>
        </div>

        <div class="glass-card" style="padding: 1.5rem; margin-top: 1.5rem;">
            <h3 style="font-family: 'Outfit', sans-serif; margin-bottom: 1rem;">
                <i class="fas fa-info-circle" style="color: var(--accent-primary);"></i> Player Info
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <span style="color: var(--text-muted); font-size: 0.8rem;">Age</span>
                    <p style="font-weight: 600;">${player.age || '--'}</p>
                </div>
                <div>
                    <span style="color: var(--text-muted); font-size: 0.8rem;">Date of Birth</span>
                    <p style="font-weight: 600;">${player.date_of_birth ? formatDate(player.date_of_birth) : '--'}</p>
                </div>
            </div>
        </div>
    `;
}

// ===== PROFILE =====
async function loadProfile() {
    if (!state.user) {
        await fetchUserProfile();
    }

    const user = state.user;
    if (!user) return;

    document.getElementById('profile-avatar').src = getMediaUrl(user.photo);
    document.getElementById('profile-name').textContent = user.name || '--';
    document.getElementById('profile-email').textContent = user.email || '--';
    document.getElementById('profile-role-badge').textContent = state.role || 'PLAYER';

    document.getElementById('profile-rating').textContent = user.rating || '--';
    document.getElementById('profile-goals').textContent = user.goals || 0;
    document.getElementById('profile-assists').textContent = user.assists || 0;
    document.getElementById('profile-games-played').textContent = user.games_played || 0;

    // Populate edit form
    document.getElementById('edit-name').value = user.name || '';
    document.getElementById('edit-dob').value = user.date_of_birth || '';
}

async function handlePhotoUpload(input) {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('photo', file);

    try {
        const res = await fetch(`${API_BASE}/accounts/user/edit/`, {
            method: 'PATCH',
            headers: { 'Authorization': `Token ${state.token}` },
            body: formData
        });

        if (res.ok) {
            showToast('Photo updated!', 'success');
            await fetchUserProfile();
            updateUserUI();
            loadProfile();
        } else {
            showToast('Error uploading photo.', 'error');
        }
    } catch (err) {
        showToast('Error uploading photo.', 'error');
    }
}

// ===== CREATE GAME =====
async function loadCreateGame() {
    const select = document.getElementById('game-futsal');
    
    try {
        const data = await apiFetch('/games/futsals/');
        let futsals = data;
        if (data && data.results) futsals = data.results;

        if (futsals && Array.isArray(futsals)) {
            select.innerHTML = '<option value="">Select a venue</option>' +
                futsals.map(f => `<option value="${f.id}">${f.name} - ${f.location}</option>`).join('');
        }
    } catch (err) {
        console.error('Error loading futsals:', err);
    }
}

// ===== SEARCH =====
function handleSearch(query) {
    // Simple client-side search - navigates to players with a filter
    if (query.length > 2) {
        navigateTo('players');
        // Filter rendered players
        const cards = document.querySelectorAll('.player-card');
        cards.forEach(card => {
            const name = card.querySelector('.player-card-name')?.textContent.toLowerCase() || '';
            card.style.display = name.includes(query.toLowerCase()) ? '' : 'none';
        });
    }
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    toast.innerHTML = `
        <i class="toast-icon ${icons[type] || icons.info}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===== MODAL =====
function openModal(content) {
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== UTILITIES =====
function formatDate(dateStr) {
    if (!dateStr) return '--';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function formatTime(timeStr) {
    if (!timeStr) return '--';
    try {
        const [hours, minutes] = timeStr.split(':');
        const h = parseInt(hours);
        const ampm = h >= 12 ? 'PM' : 'AM';
        const h12 = h % 12 || 12;
        return `${h12}:${minutes} ${ampm}`;
    } catch {
        return timeStr;
    }
}
