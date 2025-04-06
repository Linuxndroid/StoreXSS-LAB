from flask import Flask, request, render_template, redirect, url_for, session
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Insecure for demo purposes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout after 30 minutes
app.permanent_session_lifetime = timedelta(minutes=30)  # Optional, same as above
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=False,  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE='Lax',  # Restrict cookie cross-site usage
)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

messages = []  # Store messages insecurely (for demo purposes)
users = {"user": "user123", "admin": "admin123"}  # Dummy user credentials

# Create default template files if not exist
def create_default_templates():
    templates = {
        "templates/login.html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { width: 300px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
                input { width: 100%; padding: 10px; margin: 5px 0; }
                button { background-color: #28a745; color: white; padding: 10px; width: 100%; border: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Login</h2>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" required><br>
                    <input type="password" name="password" placeholder="Password" required><br>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        """,
        "templates/contact.html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contact</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { width: 400px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
                textarea, input { width: 100%; padding: 10px; margin: 5px 0; }
                button { background-color: #007bff; color: white; padding: 10px; width: 100%; border: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Contact Form</h2>
                <form method="post" enctype="multipart/form-data">
                    <textarea name="message" placeholder="Enter your message"></textarea><br>
                    <input type="file" name="image"><br>
                    <button type="submit">Send</button>
                </form>
                <br>
                <a href="/logout">Logout</a>
            </div>
        </body>
        </html>
        """,
        "templates/admin.html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
                .message { border-bottom: 1px solid #ddd; padding: 10px; }
                img { max-width: 100px; margin-top: 5px; }
                button { background-color: red; color: white; padding: 5px; border: none; cursor: pointer; }
                a { display: block; margin-top: 20px; color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Admin Panel - Messages</h2>
                {% for idx, msg in enumerate(messages) %}
                    <div class="message">
                        <p><b>{{ msg['name'] }}</b>: {{ msg['message']|safe }}</p>
                        {% if msg['image'] %}
                            <img src="/{{ msg['image'] }}" alt="Uploaded Image"><br>
                        {% endif %}
                        <form method="post" action="/delete/{{ idx }}">
                            <button type="submit">Delete</button>
                        </form>
                    </div>
                {% endfor %}
                <a href="/logout">Logout</a>
            </div>
        </body>
        </html>
        """
    }
    for path, content in templates.items():
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)

create_default_templates()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username] == password:
            session['username'] = username
            session.permanent = True  # Make session permanent (it won't expire if inactive)
            return redirect(url_for('admin' if username == 'admin' else 'contact'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'username' not in session or session['username'] == 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = session['username']
        message = request.form.get('message')
        file = request.files.get('image')
        filename = None
        
        if file:
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
        
        messages.append({
            'name': name,
            'message': message,  # User input directly stored (unsafe)
            'image': filename
        })
    
    return render_template('contact.html', messages=messages)

@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    
    return render_template('admin.html', messages=messages)

@app.route('/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    
    if 0 <= msg_id < len(messages):
        del messages[msg_id]
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
