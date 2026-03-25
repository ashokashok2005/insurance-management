// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            saveToken(data.access_token, data.agent);
            window.location.href = '/dashboard';
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred');
    }
}

// Handle Registration
async function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Registration successful! Please login.');
            window.location.href = '/login';
        } else {
            alert(data.error || 'Registration failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred');
    }
}

// Ensure DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const page = document.body.dataset.page; // We will add this to templates

    // Load saved language
    const savedLang = localStorage.getItem('app_lang') || 'en';
    const switcher = document.getElementById('lang-switcher');
    if (switcher) switcher.value = savedLang;
    changeLanguage(savedLang);

    if (page === 'dashboard') loadDashboard();
    if (page === 'customers') loadCustomers();
    if (page === 'policies') loadPolicies();
    if (page === 'admin_users') loadAdminUsers();
    if (page === 'admin_audit') loadAuditLogs();
});

function changeLanguage(lang) {
    localStorage.setItem('app_lang', lang);
    const t = translations[lang] || translations['en'];

    // Update all static elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) el.innerText = t[key];
    });

    // Update placeholders
    const search = document.getElementById('customer-search');
    if (search && t['search_placeholder']) search.placeholder = t['search_placeholder'];
}

// Helper to get current translation
function getTrans(key) {
    const lang = localStorage.getItem('app_lang') || 'en';
    return (translations[lang] && translations[lang][key]) ? translations[lang][key] : (translations['en'][key] || key);
}

// Dashboard Logic
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
}

function formatCurrency(amount) {
    return '$' + Number(amount).toLocaleString('en-IN');
}

async function loadDashboard() {
    try {
        // Set greeting
        const user = getUser();
        const userName = (user && user.name) ? user.name : '';
        const greetingEl = document.getElementById('greeting-text');
        if (greetingEl) {
            greetingEl.innerText = getGreeting() + (userName ? ', ' + userName + '!' : '!');
        }

        // Set avatar initials
        const avatarEl = document.getElementById('user-avatar');
        if (avatarEl && userName) {
            const parts = userName.split(' ');
            const initials = parts.map(p => p.charAt(0).toUpperCase()).join('').slice(0, 2);
            avatarEl.innerText = initials;
        }

        // Set active nav link
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        const response = await fetchWithAuth('/dashboard/stats');
        if (!response) return;

        if (!response.ok) {
            console.error('Stats API Failed', response.status);
            const err = await response.json();
            throw new Error(err.error || 'Failed to load dashboard stats');
        }

        const stats = await response.json();

        const custEl = document.getElementById('total-customers');
        const polEl = document.getElementById('total-policies');
        const expEl = document.getElementById('expired-policies');

        if (custEl) custEl.innerText = formatCurrency(stats.total_customers * 2900 || 145000);
        if (polEl) polEl.innerText = stats.total_policies || 50;
        if (expEl) expEl.innerText = formatCurrency(stats.expired_policies * 2300 || 115000);

        loadCharts();
    } catch (e) {
        console.error(e);
    }
}

async function loadCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }

    try {
        const canvas = document.getElementById('earningChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const darkData = [35, 85, 45, 65, 115, 95, 75, 55, 90, 50, 60];
        const lightData = [25, 40, 30, 45, 60, 50, 85, 100, 70, 80, 45];

        const isDark = document.body.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)';
        const textColor = isDark ? '#94a3b8' : '#8b8fa3';

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Revenue',
                        data: darkData,
                        backgroundColor: isDark ? '#e2e8f0' : '#1a1a2e',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.7,
                    },
                    {
                        label: 'Expenses',
                        data: lightData,
                        backgroundColor: isDark ? '#475569' : '#d1d5db',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.7,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark ? '#334155' : '#1a1a2e',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        cornerRadius: 10,
                        displayColors: false,
                        callbacks: {
                            title: function (items) {
                                return 'Total Earning';
                            },
                            label: function (item) {
                                const total = darkData[item.dataIndex] + lightData[item.dataIndex];
                                return '$' + (total * 280).toLocaleString('en-US', { minimumFractionDigits: 2 });
                            },
                            afterLabel: function (item) {
                                return '+67%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor, font: { size: 12 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: { size: 11 } },
                        border: { display: false }
                    }
                }
            }
        });
    } catch (e) {
        console.error('Chart error', e);
    }
}

async function loadRenewals() {
    const response = await fetchWithAuth('/dashboard/renewals?days=30');
    if (!response) return;

    const renewals = await response.json();
    const list = document.getElementById('renewals-list');
    list.innerHTML = '';

    if (renewals.length === 0) {
        list.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No upcoming renewals</td></tr>';
        return;
    }

    renewals.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.customer_name}</td>
            <td>${r.policy_number}</td>
            <td>${r.end_date}</td>
            <td><span class="badge warning">${r.days_left} days</span></td>
            <td>
                <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; width: auto; background: var(--secondary); color: white;" onclick="sendReminder(${r.id})">${getTrans('btn_send')}</button>
            </td>
        `;
        list.appendChild(tr);
    });
}

async function sendReminder(policyId) {
    if (!confirm('Send renewal reminder email to customer?')) return;

    const response = await fetchWithAuth(`/dashboard/send-reminder/${policyId}`, { method: 'POST' });
    if (response) {
        const data = await response.json();
        alert(data.message);
    }
}

// Customers Logic
async function loadCustomers() {
    const list = document.getElementById('customers-list');
    const response = await fetchWithAuth('/customers');
    if (!response) return;

    const customers = await response.json();
    list.innerHTML = '';

    customers.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${c.name}</td>
            <td>${c.mobile}</td>
            <td>${c.email || '-'}</td>
            <td>
                <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; background: var(--danger); color: white;" onclick="deleteCustomer(${c.id})">${getTrans('btn_delete')}</button>
            </td>
        `;
        list.appendChild(tr);
    });
}

async function handleAddCustomer(event) {
    event.preventDefault();
    const name = document.getElementById('cust-name').value;
    const mobile = document.getElementById('cust-mobile').value;
    const email = document.getElementById('cust-email').value;
    const address = document.getElementById('cust-address').value;

    const response = await fetchWithAuth('/customers/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, mobile, email, address })
    });

    if (response) {
        closeCustomerModal();
        loadCustomers(); // Reload list
        event.target.reset();
    }
}

async function deleteCustomer(id) {
    if (!confirm('Are you sure? This will delete all policies linked to this customer.')) return;

    const response = await fetchWithAuth(`/customers/${id}`, { method: 'DELETE' });
    if (response) loadCustomers();
}

function filterCustomers() {
    const input = document.getElementById('customer-search');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('customers-list');
    const tr = table.getElementsByTagName('tr');

    for (let i = 0; i < tr.length; i++) {
        // Cells: 0=Name, 1=Mobile
        const tdName = tr[i].getElementsByTagName('td')[0];
        const tdMobile = tr[i].getElementsByTagName('td')[1];

        if (tdName && tdMobile) {
            const txtName = tdName.textContent || tdName.innerText;
            const txtMobile = tdMobile.textContent || tdMobile.innerText;

            if (txtName.toLowerCase().indexOf(filter) > -1 || txtMobile.indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

// Policies Logic
async function loadPolicies() {
    const list = document.getElementById('policies-list');
    const response = await fetchWithAuth('/policies');
    if (!response) return;

    const policies = await response.json();
    list.innerHTML = '';

    if (policies.length === 0) {
        list.innerHTML = '<tr><td colspan="8" class="text-center">No policies found</td></tr>';
        return;
    }

    policies.forEach(p => {
        const tr = document.createElement('tr');

        let payButton = '';
        if (p.status !== 'Active') {
            payButton = `<button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; margin-right: 0.5rem; background: #28a745; color: white;" onclick="initiatePayment(${p.id})">Pay</button>`;
        } else {
            payButton = `<span class="badge success" style="background:var(--secondary); color:white; padding: 2px 8px; border-radius:12px; margin-right: 0.5rem;">Paid</span>`;
        }

        tr.innerHTML = `
            <td>${p.policy_number}</td>
            <td>${p.customer_name}</td>
            <td>${p.insurer}</td>
            <td>${p.type}</td>
            <td>${p.premium}</td>
            <td>${p.frequency}</td>
            <td>${p.end_date}</td>
            <td>${p.status}</td>
            <td>
                <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; margin-right: 0.5rem;" onclick="uploadDocument(${p.id})">${getTrans('btn_upload')}</button>
                <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; margin-right: 0.5rem; background: #6610f2; color: white;" onclick="viewReceipt(${p.id})">${getTrans('btn_receipt')}</button>
                <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; margin-right: 0.5rem; background: #17a2b8; color: white;" onclick="downloadReceipt(${p.id})">PDF</button>
                ${payButton}
                ${p.doc_path ? `<button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; width: auto; background: var(--secondary); color: white;" onclick="viewDocument('${p.doc_path}')">${getTrans('btn_view')}</button>` : ''}
            </td>
        `;
        list.appendChild(tr);
    });
}

async function initiatePayment(policyId) {
    try {
        const response = await fetchWithAuth(`/payments/create-checkout-session/${policyId}`, {
            method: 'POST'
        });

        if (!response) return;

        const data = await response.json();

        if (response.ok && data.url) {
            window.location.href = data.url;
        } else {
            alert(data.error || 'Payment initiation failed');
        }
    } catch (error) {
        console.error('Payment error:', error);
        alert('An error occurred during payment initiation');
    }
}

async function loadCustomerOptions() {
    const response = await fetchWithAuth('/customers');
    if (!response) return;
    const customers = await response.json();
    const select = document.getElementById('pol-customer');
    select.innerHTML = '<option value="">Select Customer</option>';
    customers.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.innerText = `${c.name} (${c.mobile})`;
        select.appendChild(opt);
    });
}




async function handleAddPolicy(event) {
    event.preventDefault();
    const data = {
        customer_id: document.getElementById('pol-customer').value,
        policy_number: document.getElementById('pol-number').value,
        insurer: document.getElementById('pol-insurer').value,
        type: document.getElementById('pol-type').value,
        premium: document.getElementById('pol-premium').value,
        start_date: document.getElementById('pol-start').value,
        end_date: document.getElementById('pol-end').value,
        frequency: document.getElementById('pol-frequency').value
    };

    const response = await fetchWithAuth('/policies/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response) {
        closePolicyModal();
        loadPolicies();
        event.target.reset();
    }
}

async function exportPolicies(event) {
    event.preventDefault();
    try {
        const response = await fetchWithAuth('/reports/export');
        if (!response) return;

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Policies_Export.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error('Export failed:', error);
        alert('Failed to export policies');
    }
}

async function uploadDocument(policyId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf, .jpg, .png, .jpeg';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        const token = getToken();
        // Use standard fetch because we need FormData handling (no Content-Type json)
        const response = await fetch(`${API_BASE}/documents/upload/${policyId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
                // Content-Type undefined to let browser set boundary
            },
            body: formData
        });

        if (response.ok) {
            alert('Document uploaded successfully');
            loadPolicies();
        } else {
            alert('Upload failed');
        }
    };

    input.click();
}

function viewDocument(filename) {
    if (!filename || filename === 'null') {
        alert('No document attached');
        return;
    }
    const token = getToken();
    // For MVP, download endpoint might need to be unprotected or we use a signed URL. 
    // Or we just fetch query param? 
    // The documents endpoint I wrote expects JWT in header which browser window.open doesn't send easy.
    // Workaround: fetch blob and show, or just allow 'download' param with token?
    // Easiest for MVP: just use fetch to get blob and open.

    fetchWithAuth(`/documents/download/${filename}`)
        .then(res => res.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        });
}

function viewReceipt(id) {
    // Open in new tab. Backend handles rendering.
    // In a real secured app, we'd need a short-lived token param here.
    window.open(`/api/policies/receipt/${id}`, '_blank');
}

function downloadReceipt(id) {
    // Open in new tab to trigger download
    window.open(`/api/documents/receipt/${id}/pdf`, '_blank');
}

async function handleSettingsSave(event) {
    event.preventDefault();
    alert('Settings saved! (Mock functionality for MVP)');
}

async function downloadBackup() {
    try {
        const response = await fetchWithAuth('/settings/backup');
        if (!response) return;

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Use content-disposition filename if possible, else default
        // For simplicity in MVP, we trust the backend header or just date it
        const date = new Date().toISOString().slice(0, 10);
        a.download = `insurance_backup_${date}.json`;

        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        alert('Backup downloaded successfully! Please save it in a safe place.');
    } catch (error) {
        console.error('Backup failed:', error);
        alert('Failed to download backup');
    }
}

// Forgot Password Logic
function showForgotPassword(e) {
    if (e) e.preventDefault();
    const modal = document.getElementById('forgot-modal');
    modal.style.display = 'flex';
    modal.classList.remove('hidden');

    // Reset state
    const getOtp = document.getElementById('form-get-otp');
    const resetPass = document.getElementById('form-reset-pass');
    if (getOtp) getOtp.style.display = 'block';
    if (resetPass) resetPass.style.display = 'none';
    const fpTitle = document.getElementById('fp-title');
    const fpDesc = document.getElementById('fp-desc');
    if (fpTitle) fpTitle.innerText = 'Reset Password';
    if (fpDesc) fpDesc.innerText = 'Enter your email to receive an OTP.';
}

function closeForgotModal() {
    const modal = document.getElementById('forgot-modal');
    if (modal) modal.style.display = 'none';
}

let resetEmail = '';

async function handleSendOTP(event) {
    event.preventDefault();
    const email = document.getElementById('fp-email').value;
    resetEmail = email;

    const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });

    const data = await response.json();

    if (response.ok) {
        alert(data.message);
        // Switch to Step 2
        document.getElementById('form-get-otp').style.display = 'none';
        document.getElementById('form-reset-pass').style.display = 'block';
        document.getElementById('fp-title').innerText = 'Enter OTP';
        document.getElementById('fp-desc').innerText = 'Check the server console for the code.';
    } else {
        alert(data.error || 'Failed to send OTP');
    }
}

async function handleResetPassword(event) {
    event.preventDefault();
    const otp = document.getElementById('fp-otp').value;
    const new_password = document.getElementById('fp-new-pass').value;

    const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: resetEmail, otp, new_password })
    });

    const data = await response.json();

    if (response.ok) {
        alert('Password reset successful! Please login with your new password.');
        closeForgotModal();
    } else {
        alert(data.error || 'Reset failed');
    }
}

// Dark Mode Logic
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.innerText = theme === 'dark' ? '☀️' : '🌙';
        icon.nextElementSibling.innerText = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
}

// Initialize Theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
});

// Admin Logic
async function loadAdminUsers() {
    const list = document.getElementById('users-list');
    if (!list) return;

    try {
        const users = await apiFetch('/admin/users');
        list.innerHTML = '';

        // Populate reassignment dropdowns if they exist
        const fromSelect = document.getElementById('reassign-from');
        const toSelect = document.getElementById('reassign-to');
        if (fromSelect) fromSelect.innerHTML = '<option value="">Select Agent</option>';
        if (toSelect) toSelect.innerHTML = '<option value="">Select Agent</option>';

        users.forEach(u => {
            const tr = document.createElement('tr');
            const statusClass = u.is_active ? 'badge-success' : 'badge-danger';
            const roleClass = u.role === 'agency_admin' ? 'badge-primary' : (u.role === 'super_admin' ? 'badge-dark' : 'badge-info');

            tr.innerHTML = `
                <td>
                    <div class="cust-info">
                        <div class="cust-avatar">${u.name ? u.name.substring(0, 1).toUpperCase() : '?'}</div>
                        <div class="cust-details">
                            <div class="name">${u.name || 'No Name'}</div>
                            <div class="date">Joined ${new Date(u.created_at).toLocaleDateString()}</div>
                        </div>
                    </div>
                </td>
                <td>${u.email}</td>
                <td><span class="badge ${roleClass}">${u.role.replace('_', ' ')}</span></td>
                <td><span class="badge ${statusClass}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
                <td style="text-align: right;">
                    <div class="action-buttons-group">
                        <button class="btn-icon" onclick="toggleUser(${u.id})" title="Toggle Status">
                            <span class="material-symbols-outlined">${u.is_active ? 'block' : 'check_circle'}</span>
                        </button>
                        <button class="btn-icon" onclick="showResetPassModal(${u.id}, '${u.email}')" title="Reset Password">
                            <span class="material-symbols-outlined">lock_reset</span>
                        </button>
                    </div>
                </td>
            `;
            list.appendChild(tr);

            // Add to dropdowns if agent
            if (u.role === 'agent' && u.is_active) {
                const opt = `<option value="${u.id}">${u.name} (${u.email})</option>`;
                if (fromSelect) fromSelect.innerHTML += opt;
                if (toSelect) toSelect.innerHTML += opt;
            }
        });

    } catch (err) {
        showStatus('Failed to load team members', 'error');
    }
}

async function toggleUser(userId) {
    try {
        const result = await apiFetch(`/admin/users/${userId}/toggle`, { method: 'POST' });
        showStatus(result.message, 'success');
        loadAdminUsers();
    } catch (err) {
        showStatus(err.message, 'error');
    }
}

function showAddUserModal() {
    showModal('addUserModal');
}

function showResetPassModal(id, email) {
    document.getElementById('reset-user-id').value = id;
    document.getElementById('reset-user-email').innerText = email;
    showModal('resetPassModal');
}

async function loadAuditLogs() {
    const response = await fetchWithAuth('/admin/audit-logs');
    if (!response) return;

    if (!response.ok) {
        alert('Failed to load logs');
        return;
    }

    const logs = await response.json();
    const list = document.getElementById('logs-list');
    list.innerHTML = '';

    logs.forEach(l => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(l.timestamp).toLocaleString()}</td>
            <td>${l.agent_name}</td>
            <td><span style="font-weight:bold; color: #4e54c8;">${l.action}</span></td>
            <td>${l.target_id || '-'}</td>
            <td>${l.details || '-'}</td>
            <td>${l.ip_address || '-'}</td>
        `;
        list.appendChild(tr);
    });
}

// --- Idle Timer for Auto Logout (30 minutes) ---
let idleTimer;
const IDLE_TIMEOUT = 30 * 60 * 1000; // 30 minutes

function resetIdleTimer() {
    clearTimeout(idleTimer);
    if (localStorage.getItem('access_token')) {
        idleTimer = setTimeout(logout, IDLE_TIMEOUT);
    }
}

// Event listeners for activity
window.onload = resetIdleTimer;
document.onmousemove = resetIdleTimer;
document.onmousedown = resetIdleTimer;
document.ontouchstart = resetIdleTimer;
document.onclick = resetIdleTimer;
document.onkeydown = resetIdleTimer;
document.addEventListener('scroll', resetIdleTimer, true);

async function handleAuthAction(event, action) {
    event.preventDefault();
    const btn = event.target.querySelector('button[type="submit"]');
    const originalBtnText = btn ? btn.innerText : 'Submit';
    if (btn) btn.innerText = 'Processing...';

    try {
        let endpoint = '';
        let method = 'POST';
        let body = {};
        let successMsg = 'Action completed successfully';

        if (action === 'addUser') {
            endpoint = '/admin/users';
            const role = document.getElementById('add-role').value;
            body = {
                name: document.getElementById('add-name').value,
                email: document.getElementById('add-email').value,
                password: document.getElementById('add-password').value,
                role: role
            };
            successMsg = 'Agent added successfully';
        } else if (action === 'adminResetPassword') {
            const userId = document.getElementById('reset-user-id').value;
            endpoint = `/admin/users/${userId}/reset-password`;
            body = { password: document.getElementById('new-temp-password').value };
            successMsg = 'Password reset successfully';
        } else if (action === 'reassignRecords') {
            endpoint = '/admin/reassign';
            body = {
                from_agent_id: document.getElementById('reassign-from').value,
                to_agent_id: document.getElementById('reassign-to').value
            };
            successMsg = 'Records reassigned successfully';
        }

        const response = await fetchWithAuth(endpoint, {
            method,
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Server error');
        }

        showStatus(successMsg, 'success');

        // Close modal and refresh
        if (action === 'addUser') closeModal('addUserModal');
        if (action === 'adminResetPassword') closeModal('resetPassModal');
        if (action === 'reassignRecords') closeModal('reassignModal');

        loadAdminUsers();
        event.target.reset();

    } catch (err) {
        showStatus(err.message || 'Action failed', 'error');
    } finally {
        if (btn) btn.innerText = originalBtnText;
    }
}

// Global Modal Helpers
function showModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.remove('hidden');
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
}

async function loadAgencies() {
    const list = document.getElementById('agencies-list');
    if (!list) return;

    try {
        const agencies = await apiFetch('/superadmin/agencies');
        list.innerHTML = '';

        agencies.forEach(a => {
            const tr = document.createElement('tr');
            const statusClass = a.status === 'active' ? 'badge-success' : 'badge-danger';

            tr.innerHTML = `
                <td>
                    <div class="cust-info">
                        <div class="cust-avatar" style="background: var(--primary); color: white;">${a.name.substring(0, 1).toUpperCase()}</div>
                        <div class="cust-details">
                            <div class="name">${a.name}</div>
                            <div class="date">ID: #${a.id} • ${new Date(a.created_at).toLocaleDateString()}</div>
                        </div>
                    </div>
                </td>
                <td>${a.contact_details || '-'}</td>
                <td>${a.agent_limit} Agents</td>
                <td><span class="badge ${statusClass}">${a.status}</span></td>
                <td style="text-align: right;">
                    <div class="action-buttons-group">
                        <button class="btn-icon" onclick="toggleAgencyStatus(${a.id}, '${a.status === 'active' ? 'suspended' : 'active'}')" title="Toggle Status">
                            <span class="material-symbols-outlined">${a.status === 'active' ? 'block' : 'check_circle'}</span>
                        </button>
                    </div>
                </td>
            `;
            list.appendChild(tr);
        });
    } catch (err) {
        showStatus('Failed to load agencies', 'error');
    }
}

async function handleSuperAdminAction(event, action) {
    event.preventDefault();
    const btn = event.target.querySelector('button[type="submit"]');
    const originalBtnText = btn ? btn.innerText : 'Submit';
    if (btn) btn.innerText = 'Processing...';

    try {
        let endpoint = '';
        let body = {};
        let successMsg = '';

        if (action === 'createAgency') {
            endpoint = '/superadmin/agencies';
            body = {
                name: document.getElementById('agency-name').value,
                contact_details: document.getElementById('agency-contact').value,
                agent_limit: document.getElementById('agency-limit').value
            };
            successMsg = 'Agency created successfully';
        }

        const response = await fetchWithAuth(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Server error');
        }

        showStatus(successMsg, 'success');
        closeModal('addAgencyModal');
        loadAgencies();
        event.target.reset();
    } catch (err) {
        showStatus(err.message, 'error');
    } finally {
        if (btn) btn.innerText = originalBtnText;
    }
}

async function toggleAgencyStatus(id, newStatus) {
    try {
        const result = await apiFetch(`/superadmin/agencies/${id}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });
        showStatus(result.message, 'success');
        loadAgencies();
    } catch (err) {
        showStatus(err.message, 'error');
    }
}
