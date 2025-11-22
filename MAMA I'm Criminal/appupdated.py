from flask import Flask, request, redirect, make_response
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request
import hashlib
import secrets
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import threading
import time
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# In-memory data storage
users = {
    "admin": {"password": "6e2&JyO3PJ&)", "role": "admin", "info": "Administrator Account"},
}
sessions = {}
FLAG = os.environ.get("FLAG", "FLAG{cr1f_1nj3ct10n_By_Casp3r0x0}")

def visit_url(url):
    """Admin bot visits the provided URL"""
    parsed_url = urlparse(url)
    domain = parsed_url.hostname

    if domain != "127.0.0.1":
        return
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Use Selenium Manager to auto-download correct ChromeDriver
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(10)  # 10 second timeout
        
        # Admin login
        print(f"[Bot] Logging in as admin...")
        driver.get("http://127.0.0.1:5000/")
        time.sleep(1)
        driver.get("http://127.0.0.1:5000/login")
        time.sleep(1)
        
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("6e2&JyO3PJ&)")
        
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(3)
        # Visit the user-provided URL
        print(f"[Bot] Visiting: {url}")
        driver.get(url)
        time.sleep(5)

        #Second login
        driver.get("http://127.0.0.1:5000/")
        time.sleep(1)
        driver.get("http://127.0.0.1:5000/login")
        time.sleep(1)
        
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("6e2&JyO3PJ&)")
        
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(1)
        print(f"[Bot] Visit complete")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def generate_session_token():
    random_data = secrets.token_hex(16)
    return hashlib.md5(random_data.encode()).hexdigest()

def get_session():
    token = request.cookies.get("session")
    if token and token in sessions:
        return sessions[token]
    return None

def create_session(username):
    token = generate_session_token()
    sessions[token] = {"username": username, "authenticated": True}
    return token

# HTML Templates as strings
def render_page(title, content):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ddd; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        form {{ margin: 20px 0; }}
        label {{ display: block; margin: 10px 0 5px; font-weight: bold; }}
        input {{ width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; box-sizing: border-box; }}
        button {{ background: #333; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
        button:hover {{ background: #555; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ margin-right: 15px; color: #333; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        .message {{ padding: 10px; background: #e8f4f8; border: 1px solid #b8d4e8; margin: 10px 0; }}
        .error {{ background: #f8d7da; border-color: #f5c6cb; }}
        .info {{ background: #d4edda; border-color: #c3e6cb; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

def nav_links(authenticated=False):
    if authenticated:
        return '<div class="nav"><a href="/">Home</a><a href="/profile">Profile</a><a href="/logout">Logout</a></div>'
    return '<div class="nav"><a href="/">Home</a><a href="/login">Login</a><a href="/register">Register</a></div>'

@app.route("/")
def index():
    session = get_session()
    
    # Create unauthenticated session token on first visit
    if not request.cookies.get("session"):
        token = generate_session_token()
        sessions[token] = {"username": None, "authenticated": False}
        response = make_response(redirect("/"))
        response.set_cookie("session", token)
        return response
    
    if session and session.get("authenticated"):
        username = session.get("username")
        content = f"""
        {nav_links(True)}
        <h1>Welcome</h1>
        <p>Hello, {username}</p>
        <p>You are logged in.</p>
        <p><a href="/contact">Contact Us</a></p>
        """
    else:
        content = f"""
        {nav_links(False)}
        <h1>Welcome</h1>
        <p>Please login or register to continue.</p>
        <p><a href="/contact">Contact Us</a></p>
        """
    
    return render_page("Home", content)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    session = get_session()
    authenticated = session and session.get("authenticated")
    
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        
        if not url:
            content = f"""
            {nav_links(authenticated)}
            <h1>Contact Us</h1>
            <div class="message error">Please provide a URL.</div>
            <form method="post">
                <label>URL for Admin to Visit:</label>
                <input type="text" name="url" placeholder="http://example.com" required>
                <button type="submit">Submit</button>
            </form>
            """
            return render_page("Contact Us", content)
        
        if not url.startswith("http://") and not url.startswith("https://"):
            content = f"""
            {nav_links(authenticated)}
            <h1>Contact Us</h1>
            <div class="message error">URL must start with http:// or https://</div>
            <form method="post">
                <label>URL for Admin to Visit:</label>
                <input type="text" name="url" placeholder="http://example.com" required>
                <button type="submit">Submit</button>
            </form>
            """
            return render_page("Contact Us", content)
        
        # Start bot in background thread
        thread = threading.Thread(target=visit_url, args=(url,))
        thread.daemon = True
        thread.start()
        
        content = f"""
        {nav_links(authenticated)}
        <h1>Contact Us</h1>
        <div class="message info">Thank you! An admin will visit your URL shortly. from 127.0.0.1</div>
        <p><a href="/">Back to Home</a></p>
        """
        return render_page("Contact Us", content)
    
    content = f"""
    {nav_links(authenticated)}
    <h1>Contact Us</h1>
    <p>Submit a URL and our admin will review it.</p>
    <form method="post">
        <label>URL for Admin to Visit:</label>
        <input type="text" name="url" placeholder="http://example.com" required>
        <button type="submit">Submit</button>
    </form>
    """
    return render_page("Contact Us", content)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        info = request.form.get("info", "").strip()
        
        if not username or not password:
            content = f"""
            {nav_links(False)}
            <h1>Register</h1>
            <div class="message error">Username and password are required.</div>
            <form method="post">
                <label>Username:</label>
                <input type="text" name="username" required>
                <label>Password:</label>
                <input type="password" name="password" required>
                <label>Additional Info:</label>
                <input type="text" name="info">
                <button type="submit">Register</button>
            </form>
            """
            return render_page("Register", content)
        
        if username in users:
            content = f"""
            {nav_links(False)}
            <h1>Register</h1>
            <div class="message error">Username already exists.</div>
            <form method="post">
                <label>Username:</label>
                <input type="text" name="username" required>
                <label>Password:</label>
                <input type="password" name="password" required>
                <label>Additional Info:</label>
                <input type="text" name="info">
                <button type="submit">Register</button>
            </form>
            """
            return render_page("Register", content)
        
        users[username] = {"password": password, "role": "user", "info": info or "No additional info"}
        
        content = f"""
        {nav_links(False)}
        <h1>Register</h1>
        <div class="message info">Registration successful! Please login.</div>
        <p><a href="/login">Go to Login</a></p>
        """
        return render_page("Register", content)
    
    content = f"""
    {nav_links(False)}
    <h1>Register</h1>
    <form method="post">
        <label>Username:</label>
        <input type="text" name="username" required>
        <label>Password:</label>
        <input type="password" name="password" required>
        <label>Additional Info:</label>
        <input type="text" name="info">
        <button type="submit">Register</button>
    </form>
    """
    return render_page("Register", content)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username in users and users[username]["password"] == password:
            # Reuse existing session token but mark as authenticated
            token = request.cookies.get("session")
            if token and token in sessions:
                sessions[token]["username"] = username
                sessions[token]["authenticated"] = True
                response = make_response(redirect("/"))
                return response
            else:
                # This shouldn't happen, but create a session if cookie is missing
                token = create_session(username)
            
            response = make_response(redirect("/"))
            response.set_cookie("session", token)
            return response
        
        content = f"""
        {nav_links(False)}
        <h1>Login</h1>
        <div class="message error">Invalid credentials.</div>
        <form method="post">
            <label>Username:</label>
            <input type="text" name="username" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
        """
        return render_page("Login", content)
    
    content = f"""
    {nav_links(False)}
    <h1>Login</h1>
    <form method="post">
        <label>Username:</label>
        <input type="text" name="username" required>
        <label>Password:</label>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    """
    return render_page("Login", content)

@app.route("/logout")
def logout():
    token = request.cookies.get("session")
    if token and token in sessions:
        sessions[token]["authenticated"] = False
        sessions[token]["username"] = None
    
    response = make_response(redirect("/"))
    return response

@app.route("/profile")
def profile():
    session = get_session()
    
    if not session or not session.get("authenticated"):
        return redirect("/login")
    
    username = session.get("username")
    user_data = users.get(username, {})
    role = user_data.get("role", "user")
    info = user_data.get("info", "")
    
    flag_section = ""
    if role == "admin":
        flag_section = f'<div class="message info"><strong>FLAG:</strong> {FLAG}</div>'
    
    content = f"""
    {nav_links(True)}
    <h1>Profile</h1>
    <p><strong>Username:</strong> {username}</p>
    <p><strong>Role:</strong> {role}</p>
    <p><strong>Info:</strong> {info}</p>
    {flag_section}
    <p><a href="/download?file=userinfo.txt">Download My Info</a></p>
    """
    return render_page("Profile", content)

# Vulnerable endpoint (raw WSGI handling)
def vuln_app(environ, start_response):
    req = Request(environ)
    
    # Check session authentication
    cookies = req.cookies
    token = cookies.get("session")
    
    if not token or token not in sessions or not sessions[token].get("authenticated"):
        start_response("403 Forbidden", [("Content-Type", "text/plain")])
        return [b"Unauthorized"]
    
    username = sessions[token].get("username")
    user_data = users.get(username, {})
    
    filename = req.args.get("file", "userinfo.txt")
    
    # CRLF injection vulnerability
    headers = [
        ("Content-Type", "text/plain"),
        ("X-Filename", filename)   # CRLF injection point
    ]
    
    user_info = f"Username: {username}\nRole: {user_data.get('role')}\nInfo: {user_data.get('info')}\n"
    
    start_response("200 OK", headers)
    return [user_info.encode()]

# Override default dispatch to route /download to raw WSGI handler
def wsgi_dispatch(environ, start_response):
    if environ.get("PATH_INFO") == "/download":
        return vuln_app(environ, start_response)
    return app.wsgi_app(environ, start_response)

if __name__ == "__main__":
    print("Server starting on http://0.0.0.0:5000")
    run_simple("0.0.0.0", 5000, wsgi_dispatch, threaded=True, use_reloader=True, use_debugger=False)
