import os, sys, subprocess, sqlite3
from threading import Timer
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pdf2docx import Converter 
from db_handler import *

app = Flask(__name__)
app.secret_key = "docubridge_pro_secure_2026"

# Desktop Output Folder: Files yahan save hongi
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "DocuBridge_Files")
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# --- ICON/FAVICON SUPPORT ---
@app.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, 'icon.ico')

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form.get('username'), request.form.get('password')
    user = check_login(u, p)
    if user:
        session['user'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    u, p = request.form.get('username'), request.form.get('password')
    # register_user ab Duplicate username handle karega
    if register_user(u, p):
        session['user'] = u
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    hist = get_user_history(session['user'])
    return render_template('dashboard.html', user=session['user'], history=hist)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' in session:
        file = request.files.get('files')
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join(OUTPUT_FOLDER, file.filename)
            file.save(pdf_path)
            
            docx_name = file.filename.replace('.pdf', '.docx')
            docx_path = os.path.join(OUTPUT_FOLDER, docx_name)
            
            # PDF to DOCX Conversion
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            
            add_to_history(session['user'], docx_name)
            
            # PDF delete (sirf Word file bachegi)
            try: os.remove(pdf_path)
            except: pass
            
            # Desktop par folder kholna
            os.startfile(OUTPUT_FOLDER)
            
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/open-folder')
def open_folder():
    os.startfile(OUTPUT_FOLDER)
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:hid>')
def delete(hid):
    delete_history_item(hid)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def start_app():
    # Chrome ko App Mode mein kholna (Icon tabhi sahi dikhta hai)
    subprocess.Popen(['start', 'chrome', '--app=http://127.0.0.1:5000'], shell=True)

if __name__ == '__main__':
    setup_database() # Tables create karega
    Timer(1.5, start_app).start() # App window launch karega
    app.run(port=5000)