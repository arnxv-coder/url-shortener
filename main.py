from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('shortener.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def init_db():
    conn = sqlite3.connect('shortener.db')
    conn.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, code TEXT, original_url TEXT)')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        code = generate_code()
        conn = get_db_connection()
        conn.execute('INSERT INTO urls (code, original_url) VALUES (?, ?)', (code, original_url))
        conn.commit()
        conn.close()
        return render_template('result.html', short_url=request.host_url + code)
    return render_template('index.html')

@app.route('/<code>')
def redirect_to_url(code):
    conn = get_db_connection()
    result = conn.execute('SELECT original_url FROM urls WHERE code = ?', (code,)).fetchone()
    conn.close()
    if result:
        return redirect(result['original_url'])
    return "URL not found", 404

if __name__ == '__main__':
    init_db()  # Create DB table every time on start
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
