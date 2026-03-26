import os, sqlite3, platform
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pdf2docx import Converter

app = Flask(__name__)
app.secret_key = "docubridge_web_secret_2026"

# --- FOLDER SETUP ---
# Website par files 'uploads' folder mein jayengi
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- DATABASE LOGIC (Single File Mein) ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, username TEXT, filename TEXT)''')
    conn.commit()
    conn.close()

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/signup', methods=['POST'])
def signup():
    u, p = request.form.get('username'), request.form.get('password')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        session['user'] = u
        return redirect(url_for('dashboard'))
    except:
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    user = cursor.fetchone()
    conn.close()
    if user:
        session['user'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename FROM history WHERE username=?", (session['user'],))
    hist = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', user=session['user'], history=hist)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' in session:
        file = request.files.get('files')
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)
            
            docx_name = file.filename.replace('.pdf', '.docx')
            docx_path = os.path.join(UPLOAD_FOLDER, docx_name)
            
            # Conversion Logic
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            
            # History Save
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (username, filename) VALUES (?, ?)", (session['user'], docx_name))
            conn.commit()
            conn.close()
            
            os.remove(pdf_path) # PDF delete kar di
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)