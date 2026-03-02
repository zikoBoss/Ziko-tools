from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import requests
import base64
import os
import urllib.parse
from functools import wraps
from datetime import datetime, timedelta
from io import BytesIO
import base64 as b64_encode
from dotenv import load_dotenv
import jwt
import secrets

# تحميل المتغيرات من ملف .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ziko_advanced_secret_2026')

# بيانات تسجيل الدخول من متغيرات البيئة
USERNAME = os.getenv('USERNAME', 'ZikoBoss')
PASSWORD = os.getenv('PASSWORD', 'Ziko@2006V1')
TEAM_NAME = "ZIKO-TEAM"

# قنوات المطور
YOUTUBE_URL = "https://youtube.com/@ziko_boss?si=dhuL5-voIabSYdI0"
TELEGRAM_URL = "https://t.me/Ziko_Tim"
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61586247175238"
DEVELOPER = "@ZikoBOSS"

# المفتاح السري للـ JWT (نفسه في الموقع الرئيسي)
JWT_SECRET = os.getenv('JWT_SECRET', 'ziko_advanced_secret_key_2026')

# ==================== دوال المساعدة ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_jwt_token(token):
    """التحقق من صحة التوكن القادم من الموقع الرئيسي"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        # التحقق من المصدر
        if payload.get('source') != 'ziko-main':
            return None
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None  # توكن منتهي الصلاحية
    except:
        return None  # توكن غير صالح

# ==================== قوالب HTML ====================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡️Ziko-Advanced⚡️ - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #001a1a 100%);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-card {
            max-width: 420px;
            width: 100%;
            background: rgba(18, 18, 18, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 150, 255, 0.3);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 20px 40px rgba(0, 100, 255, 0.2);
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .welcome-text {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .welcome-text h1 {
            color: #0099ff;
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: 1px;
            text-shadow: 0 0 15px rgba(0, 150, 255, 0.5);
        }
        
        .welcome-text p {
            color: #66b3ff;
            font-size: 0.95rem;
            font-weight: 400;
            opacity: 0.9;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            color: #66b3ff;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }
        
        .input-group input {
            width: 100%;
            padding: 14px 16px;
            background: rgba(0, 0, 0, 0.3);
            border: 1.5px solid rgba(0, 150, 255, 0.3);
            border-radius: 12px;
            color: #fff;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #0099ff;
            box-shadow: 0 0 0 3px rgba(0, 150, 255, 0.2);
        }
        
        .input-group input::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        
        .login-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #0099ff, #0066cc);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
            letter-spacing: 1px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 150, 255, 0.3);
        }
        
        .error-message {
            background: rgba(0, 150, 255, 0.1);
            border: 1px solid rgba(0, 150, 255, 0.3);
            border-radius: 10px;
            padding: 12px;
            color: #66b3ff;
            font-size: 0.9rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.8rem;
        }
        
        .footer a {
            color: #66b3ff;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="welcome-text">
            <h1>⚡️Ziko-Advanced⚡️</h1>
            <p>{{ team_name }}</p>
        </div>
        
        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="input-group">
                <label>USERNAME</label>
                <input type="text" name="username" placeholder="Enter your username" required>
            </div>
            
            <div class="input-group">
                <label>PASSWORD</label>
                <input type="password" name="password" placeholder="Enter your password" required>
            </div>
            
            <button type="submit" class="login-btn">SIGN IN</button>
        </form>
        
        <div class="footer">
            {{ team_name }} · <a href="https://t.me/Ziko_Tim" target="_blank">{{ developer }}</a>
        </div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>⚡️Ziko-Advanced⚡️ - Pro Tools</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #001a1a 100%);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 80px 20px 40px;
            position: relative;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0099ff;
            margin-bottom: 4px;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 150, 255, 0.3);
        }
        
        .header .team {
            color: #66b3ff;
            font-size: 1rem;
            font-weight: 400;
            opacity: 0.9;
        }
        
        .header .user-badge {
            margin-top: 12px;
            display: inline-block;
            padding: 6px 16px;
            background: rgba(0, 150, 255, 0.1);
            border: 1px solid rgba(0, 150, 255, 0.2);
            border-radius: 30px;
            color: #66b3ff;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            color: #66b3ff;
            border: 2px solid #0099ff;
            padding: 8px 16px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            transition: 0.3s;
        }
        
        .logout-btn:hover {
            background: #0099ff;
            color: black;
            box-shadow: 0 0 15px #0099ff;
        }
        
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .tab-btn {
            background: transparent;
            border: 1.5px solid rgba(0, 150, 255, 0.2);
            color: #66b3ff;
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tab-btn:hover {
            border-color: #0099ff;
            color: #0099ff;
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: #0099ff;
            border-color: #0099ff;
            color: #000;
            font-weight: 600;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: #66b3ff;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-control {
            width: 100%;
            padding: 14px 16px;
            background: rgba(0, 0, 0, 0.3);
            border: 1.5px solid rgba(0, 150, 255, 0.2);
            border-radius: 12px;
            color: #fff;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #0099ff;
            box-shadow: 0 0 0 3px rgba(0, 150, 255, 0.1);
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #0099ff, #0066cc);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 150, 255, 0.3);
        }
        
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: rgba(18, 18, 18, 0.8);
            border: 1px solid rgba(0, 150, 255, 0.2);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        
        .result-box pre {
            font-family: 'Inter', monospace;
            color: #66b3ff;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        
        .image-container {
            margin-top: 15px;
            text-align: center;
        }
        
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            border: 2px solid #0099ff;
        }
        
        .share-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .share-btn {
            padding: 10px 20px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        
        .share-btn.whatsapp {
            background: #25D366;
            color: white;
        }
        
        .share-btn.telegram {
            background: #0088cc;
            color: white;
        }
        
        .share-btn.facebook {
            background: #1877f2;
            color: white;
        }
        
        .share-btn.twitter {
            background: #1DA1F2;
            color: white;
        }
        
        .share-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .error-message {
            background: rgba(0, 150, 255, 0.1);
            border: 1px solid rgba(0, 150, 255, 0.3);
            border-radius: 12px;
            padding: 15px;
            color: #66b3ff;
            font-size: 0.9rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .social-links {
            margin-top: 40px;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        
        .social-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(0, 150, 255, 0.1);
            border: 2px solid #0099ff;
            color: #0099ff;
            font-size: 1.5rem;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .social-link:hover {
            background: #0099ff;
            color: black;
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(0, 150, 255, 0.5);
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }
        
        .footer a {
            color: #66b3ff;
            text-decoration: none;
            font-weight: 500;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 70px 15px 30px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .tab-btn {
                padding: 8px 16px;
                font-size: 0.85rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">LOGOUT</a>
        
        <div class="header">
            <h1>⚡️Ziko-Advanced⚡️</h1>
            <div class="team">{{ team_name }}</div>
            <div class="user-badge">
                <i class="fas fa-user"></i> {{ username }}
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('outfit')"><i class="fas fa-tshirt"></i> OUTFIT CARD</button>
        </div>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <!-- Tab: Outfit Card -->
        <div id="outfit-tab" class="tab-content active">
            <form onsubmit="handleFormSubmit(event, 'get_outfit_card')">
                <div class="form-group">
                    <label><i class="fas fa-fingerprint"></i> UID</label>
                    <input type="text" name="uid" class="form-control" placeholder="Enter UID" required>
                </div>
                
                <button type="submit" class="btn">
                    <i class="fas fa-magic"></i> GENERATE OUTFIT CARD
                </button>
            </form>
        </div>

        <div id="result-container"></div>

        <div class="social-links">
            <a href="{{ youtube_url }}" target="_blank" class="social-link" title="YouTube">
                <i class="fab fa-youtube"></i>
            </a>
            <a href="{{ telegram_url }}" target="_blank" class="social-link" title="Telegram">
                <i class="fab fa-telegram"></i>
            </a>
            <a href="{{ facebook_url }}" target="_blank" class="social-link" title="Facebook">
                <i class="fab fa-facebook-f"></i>
            </a>
        </div>

        <div class="footer">
            {{ team_name }} · <a href="https://t.me/Ziko_Tim" target="_blank">{{ developer }}</a>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        async function handleFormSubmit(event, endpoint) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            
            const resultDiv = document.getElementById('result-container');
            resultDiv.innerHTML = `
                <div class="result-box" style="text-align: center; padding: 30px;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2.5rem; color: #0099ff;"></i>
                    <p style="margin-top: 15px; color: #66b3ff;">Processing your request...</p>
                </div>
            `;
            
            try {
                const response = await fetch(`/${endpoint}`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `<div class="result-box">${data.result}</div>`;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error-message">
                            <i class="fas fa-exclamation-triangle"></i> ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i> Connection Error: ${error.message}
                    </div>
                `;
            }
            
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return false;
        }
        
        function shareResult(platform, uid) {
            const url = window.location.href;
            const text = `Check out this Free Fire outfit card for UID: ${uid} from ⚡️Ziko-Advanced⚡️!`;
            
            let shareUrl = '';
            
            switch(platform) {
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`;
                    break;
                case 'telegram':
                    shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
                    break;
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
                    break;
            }
            
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        const activeTab = urlParams.get('tab');
        if (activeTab) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.getElementById(activeTab + '-tab').classList.add('active');
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick="showTab('${activeTab}')"]`).classList.add('active');
        }
    </script>
</body>
</html>
"""

# ==================== Routes ====================
@app.route('/')
def home():
    # التحقق من وجود توكن من الموقع الرئيسي
    token = request.args.get('token')
    
    if token:
        user_id = verify_jwt_token(token)
        if user_id:
            # توكن صحيح - نسجل دخول المستخدم
            session['logged_in'] = True
            session['username'] = user_id
            return redirect(url_for('index'))
        else:
            # توكن غير صالح
            return render_template_string("""
            <html>
            <head><title>Access Denied</title></head>
            <body style="background: black; color: #0099ff; text-align: center; padding: 50px;">
                <h1>🔒 Access Denied</h1>
                <p>Please access this page through the main site.</p>
                <a href="https://ziko-tools.vercel.app" style="color: #0099ff;">← Back to Ziko TOOLS</a>
            </body>
            </html>
            """)
    
    # إذا كان المستخدم مسجل دخوله بالفعل
    if 'logged_in' in session:
        return redirect(url_for('index'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = "❌ Invalid username or password"
            return render_template_string(LOGIN_TEMPLATE, 
                                        team_name=TEAM_NAME, 
                                        developer=DEVELOPER,
                                        error=error)
    
    return render_template_string(LOGIN_TEMPLATE, 
                                team_name=TEAM_NAME, 
                                developer=DEVELOPER)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/index')
@login_required
def index():
    return render_template_string(MAIN_TEMPLATE, 
                                 team_name=TEAM_NAME,
                                 username=session.get('username', ''),
                                 developer=DEVELOPER,
                                 youtube_url=YOUTUBE_URL,
                                 telegram_url=TELEGRAM_URL,
                                 facebook_url=FACEBOOK_URL)

@app.route('/get_outfit_card', methods=['POST'])
@login_required
def get_outfit_card():
    uid = request.form.get('uid', '').strip()
    
    if not uid:
        return jsonify({"success": False, "error": "Please enter UID"})
    
    try:
        # رابط API الجديد
        api_url = f"https://outfit-by-vaibhav.vercel.app/outfit-card?uid={uid}"
        
        response = requests.get(api_url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Failed to fetch outfit card"})
        
        # تحويل الصورة إلى base64
        image_base64 = b64_encode.b64encode(response.content).decode('utf-8')
        image_data = f"data:image/png;base64,{image_base64}"
        
        result_html = f"""
<div style="text-align: center;">
    <h4 style="color: #0099ff;">🎴 Player Outfit Card</h4>
    <div style="background: #111; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <div style="margin: 8px 0; color: #66b3ff; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
            <span>🆔 UID: <span style="color: white; font-weight: bold;">{uid}</span></span>
        </div>
        <div class="image-container">
            <img src="{image_data}" alt="Outfit Card" style="max-width: 100%; height: auto; border-radius: 10px;">
        </div>
        
        <!-- أزرار المشاركة -->
        <div class="share-buttons">
            <button onclick="shareResult('whatsapp', '{uid}')" class="share-btn whatsapp">
                <i class="fab fa-whatsapp"></i> WhatsApp
            </button>
            <button onclick="shareResult('telegram', '{uid}')" class="share-btn telegram">
                <i class="fab fa-telegram"></i> Telegram
            </button>
            <button onclick="shareResult('facebook', '{uid}')" class="share-btn facebook">
                <i class="fab fa-facebook"></i> Facebook
            </button>
            <button onclick="shareResult('twitter', '{uid}')" class="share-btn twitter">
                <i class="fab fa-twitter"></i> Twitter
            </button>
        </div>
    </div>
    <div style="margin-top: 10px; color: #888; font-size: 0.85rem;">
        💎 ZIKO-TEAM · @ZikoBOSS
    </div>
</div>
"""
        
        return jsonify({"success": True, "result": result_html})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# للتشغيل على Vercel
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)