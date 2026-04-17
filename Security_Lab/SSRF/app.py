import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string, jsonify, Response

app = Flask(__name__)
posts = []

# --- [SỬA BACKEND: THÊM CHẶN IP BẢO VỆ ENDPOINT NỘI BỘ] ---
@app.route('/admin')
def admin_panel():
    # BỨC TƯỜNG LỬA: Chỉ cho phép chính máy chủ (localhost) truy cập
    if request.remote_addr != '127.0.0.1':
        return Response("403 Forbidden: Access Denied. Internal IP required. Khong the truy cap truc tiep tu trinh duyet ngoai!", status=403, mimetype='text/plain')
    
    return Response("Admin Dashboard - Server Metrics: OK. \n\nFLAG{ssrf_internal_admin_access_success}", mimetype='text/plain')

@app.route('/internal-api')
def internal_api():
    # BỨC TƯỜNG LỬA: Chỉ cho phép chính máy chủ (localhost) truy cập
    if request.remote_addr != '127.0.0.1':
        return jsonify({"error": "403 Forbidden - Internal Access Only"}), 403

    return jsonify({
        "status": "ok", 
        "config": "production", 
        "database": "connected",
        "SECRET_KEY": "super_secret_key_123456"
    })
# ---------------------------------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DevSecBlog - Ultimate Link Preview</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .form-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); margin-bottom: 20px; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; margin-bottom: 10px; }
        button { background-color: #0866ff; color: white; border: none; padding: 10px 15px; border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%; }
        .post-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); margin-bottom: 20px; }
        
        .preview-box { border: 1px solid #dddfe2; border-radius: 8px; overflow: hidden; background: #f7f8fa; margin-top: 15px; display: flex; flex-direction: row; text-decoration: none; color: inherit; transition: background 0.2s; }
        .preview-box:hover { background: #e9ebee; cursor: pointer; }
        .preview-img { width: 150px; min-width: 150px; object-fit: cover; border-right: 1px solid #dddfe2; background: #e9eaee; }
        .preview-content { padding: 12px 15px; display: flex; flex-direction: column; justify-content: center; overflow: hidden; }
        .preview-title { font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #1c1e21; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .preview-desc { font-size: 14px; color: #606770; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .preview-url { font-size: 12px; color: #606770; text-transform: uppercase; }
        
        .raw-data-box { border: 1px solid #dddfe2; border-radius: 8px; overflow: hidden; background: #f7f8fa; margin-top: 15px; border-left: 4px solid #28a745; }
        .raw-data { background: #1e1e1e; color: #00ff00; padding: 15px; font-family: monospace; font-size: 14px; overflow-x: auto; border-radius: 4px; margin-top: 10px; white-space: pre-wrap; word-wrap: break-word;}
        .error-text { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align:center;">DevSecBlog</h1>
        <div class="form-card">
            <form method="POST">
                <input type="text" name="title" required placeholder="What's on your mind?">
                <textarea name="content" rows="3" required placeholder="Paste a link here: https://example.com"></textarea>
                <button type="submit">Post</button>
            </form>
        </div>

        {% for post in posts %}
        <div class="post-card">
            <h3>{{ post.title }}</h3>
            <p>{{ post.content }}</p>
            
            {% if post.preview %}
                {% if post.preview.is_error %}
                    <div class="preview-box" style="border-left: 4px solid #dc3545;">
                        <div class="preview-content">
                            <div class="error-text">⚠️ {{ post.preview.message }}</div>
                        </div>
                    </div>
                {% elif post.preview.type == 'html' %}
                    <div class="preview-box">
                        {% if post.preview.image %}
                        <img src="{{ post.preview.image }}" class="preview-img" alt="Thumbnail">
                        {% endif %}
                        <div class="preview-content">
                            <div class="preview-title">{{ post.preview.title }}</div>
                            <div class="preview-desc">{{ post.preview.desc }}</div>
                            <div class="preview-url">{{ post.preview_url_domain }}</div>
                        </div>
                    </div>
                {% else %}
                    <div class="raw-data-box">
                        <div class="preview-content">
                            <div class="preview-url">INTERNAL / RAW DATA RESPONSE</div>
                            <div class="raw-data">{{ post.preview.text }}</div>
                        </div>
                    </div>
                {% endif %}
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        preview = None
        preview_url = None
        preview_url_domain = ""

        url_match = re.search(r'(https?://\S+)', content)
        if url_match:
            preview_url = url_match.group(1)
            preview_url_domain = preview_url.split('/')[2] if len(preview_url.split('/')) > 2 else preview_url
            
            # Lỗ hổng SSRF chặn lỏng lẻo bằng blacklist (vẫn giữ nguyên để khai thác)
            if '127.0.0.1' in preview_url:
                preview = {'is_error': True, 'message': 'Access to 127.0.0.1 is blocked by system policy.'}
            else:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    response = requests.get(preview_url, timeout=5, allow_redirects=True, headers=headers)
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if 'text/html' in content_type:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        og_title = soup.find('meta', property='og:title')
                        p_title = og_title['content'] if og_title and og_title.get('content') else (soup.title.string if soup.title else 'No Title')
                        
                        og_desc = soup.find('meta', property='og:description')
                        if og_desc and og_desc.get('content'):
                            p_desc = og_desc['content']
                        else:
                            meta_desc = soup.find('meta', attrs={'name': 'description'})
                            p_desc = meta_desc['content'] if meta_desc and meta_desc.get('content') else 'No description available.'
                            
                        og_image = soup.find('meta', property='og:image')
                        p_image = og_image['content'] if og_image and og_image.get('content') else None
                        
                        preview = {
                            'is_error': False,
                            'type': 'html',
                            'title': p_title.strip()[:100],
                            'desc': p_desc.strip()[:150],
                            'image': p_image
                        }
                    else:
                        preview = {
                            'is_error': False,
                            'type': 'raw',
                            'text': response.text[:500]
                        }
                except Exception as e:
                    preview = {'is_error': True, 'message': f'Preview failed: {str(e)}'}

        posts.insert(0, {
            'title': title,
            'content': content,
            'preview_url': preview_url,
            'preview_url_domain': preview_url_domain,
            'preview': preview
        })

    return render_template_string(HTML_TEMPLATE, posts=posts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
