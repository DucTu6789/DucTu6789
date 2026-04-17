# app.py
import sqlite3
import uuid
from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

# Lưu trữ Session trên RAM (In-memory storage)
# Cấu trúc: { "session_id": {"id": 1, "username": "admin", "role": "admin"} }
SESSIONS = {}

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Tạo bảng
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Xóa dữ liệu cũ để reset mỗi lần chạy (nếu cần)
    c.execute('DELETE FROM users')
    
    # Dữ liệu mẫu
    users_data = [('admin', 'admin123', 'admin')]
    for i in range(1, 6):
        users_data.append((f'user{i}', '123', 'user'))
        
    # An toàn với SQLi: Sử dụng Parameterized Queries (?)
    c.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users_data)
    conn.commit()
    conn.close()
    print("Database initialized with sample users.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # An toàn với SQLi
    c.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        # Tạo Session ID ngẫu nhiên
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            "id": user[0],
            "username": user[1],
            "role": user[2]
        }
        
        resp = make_response(jsonify({"status": "success", "message": "Login successful"}))
        # LỖ HỔNG: Không set HttpOnly=True -> JavaScript phía client có thể đọc được qua document.cookie
        resp.set_cookie('session_id', session_id, httponly=False)
        return resp
    
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session_id = request.cookies.get('session_id')
    if session_id in SESSIONS:
        del SESSIONS[session_id]
    resp = make_response(jsonify({"status": "success"}))
    resp.set_cookie('session_id', '', expires=0)
    return resp

@app.route('/api/profile')
def profile():
    session_id = request.cookies.get('session_id')
    user = SESSIONS.get(session_id)
    if user:
        return jsonify({"status": "success", "data": user})
    return jsonify({"status": "error", "message": "Not authenticated"}), 401

@app.route('/api/admin')
def admin_panel():
    session_id = request.cookies.get('session_id')
    user = SESSIONS.get(session_id)
    
    if user and user.get('role') == 'admin':
        return jsonify({
            "status": "success", 
            "html": "<h2 style='color:red;'>Admin Dashboard</h2><p>Dữ liệu tuyệt mật của hệ thống...</p>"
        })
    return jsonify({"status": "error", "message": "Access Denied: Admin only"}), 403

if __name__ == '__main__':
    init_db() 
    app.run(port=5000, debug=True)
