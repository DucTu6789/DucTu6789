
function doSearch() {
    const q = document.getElementById('searchInput').value;
    window.location.hash = `#search?q=${encodeURIComponent(q)}`;
}

async function router() {
    const appDiv = document.getElementById('app');
    const hash = window.location.hash || '#home';
    const [route, queryString] = hash.split('?');
    const params = new URLSearchParams(queryString || '');

    checkLoginStatus();

    if (route === '#home') {
        appDiv.innerHTML = `
            <div class="card">
                <h2>Welcome to VulnLab</h2>
                <p>This is a modern web application built for security testing. Try logging in or searching!</p>
            </div>
        `;
    } 
    else if (route === '#login') {
        appDiv.innerHTML = `
            <div class="card" style="max-width: 400px; margin: auto;">
                <h2>Login</h2>
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="username" value="user1">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="password" value="123">
                </div>
                <button class="btn" onclick="login()">Login</button>
                <p id="login-msg" style="color: red; margin-top: 10px;"></p>
            </div>
        `;
    }
    else if (route === '#profile') {
        const res = await fetch('/api/profile');
        const json = await res.json();
        
        if (json.status === 'success') {
            appDiv.innerHTML = `
                <div class="card">
                    <h2>User Profile</h2>
                    <p><strong>ID:</strong> ${json.data.id}</p>
                    <p><strong>Username:</strong> ${json.data.username}</p>
                    <p><strong>Role:</strong> ${json.data.role}</p>
                </div>
            `;
        } else {
            appDiv.innerHTML = `<div class="card"><p style="color:red">You must be logged in to view your profile.</p></div>`;
        }
    }
    else if (route === '#admin') {
        const res = await fetch('/api/admin');
        const json = await res.json();
        
        if (json.status === 'success') {
            appDiv.innerHTML = `<div class="card">${json.html}</div>`;
        } else {
            appDiv.innerHTML = `<div class="card"><h2 style="color:red">Access Denied</h2><p>${json.message}</p></div>`;
        }
    }
    // ---------------------------------------------------------
    // VULNERABILITY: DOM-BASED XSS
    // ---------------------------------------------------------
    else if (route === '#search') {
        // SOURCE: Lấy giá trị từ window.location.hash
        // Ở đây chúng ta lấy param 'q' (chưa được làm sạch HTML escape).
        const query = decodeURIComponent(params.get('q') || '');

        // SINK: Đưa trực tiếp biến query vào element bằng innerHTML.
        // Khi attacker chèn mã HTML/JS, trình duyệt sẽ parse và thực thi nó.
        appDiv.innerHTML = `
            <div class="card">
                <h2>Search Results</h2>
                <p>You searched for: <strong style="color: blue;">${query}</strong></p>
                <p>0 items found.</p>
            </div>
        `;
    }
}


async function login() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
    });
    
    const json = await res.json();
    if (json.status === 'success') {
        window.location.hash = '#profile';
    } else {
        document.getElementById('login-msg').innerText = json.message;
    }
}

async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    window.location.hash = '#login';
}

async function checkLoginStatus() {
    const res = await fetch('/api/profile');
    const json = await res.json();
    
    const loginLink = document.getElementById('login-link');
    const logoutLink = document.getElementById('logout-link');
    const greeting = document.getElementById('user-greeting');
    
    if (json.status === 'success') {
        loginLink.style.display = 'none';
        logoutLink.style.display = 'inline';
        greeting.innerText = `Hi, ${json.data.username} | `;
    } else {
        loginLink.style.display = 'inline';
        logoutLink.style.display = 'none';
        greeting.innerText = '';
    }
}
window.addEventListener('hashchange', router);
window.addEventListener('load', router);
