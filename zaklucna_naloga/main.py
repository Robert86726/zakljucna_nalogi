from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query
import os
import json

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"

db = TinyDB('klepet.json')
users = db.table('uporabniki')  
components = db.table('komponente')  
User = Query()  

DB_FILE = "klepet.json"

def preberi_uporabnike():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": []}

def shrani_uporabnike(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        return redirect(url_for('build_your_pc'))
    return render_template('domov.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        data = users.all()
        user = next((u for u in data if u.get("username") == username), None)

        if user:
            if user.get("password") == password:
                session['username'] = username
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Napačno geslo!'})
        else:
            return jsonify({'success': False, 'error': 'Uporabnik ne obstaja!'})

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            
            user = users.get(User.username == username)
            if user:
                return jsonify({'success': False, 'error': 'Uporabnik že obstaja!'})
            
            users.insert({
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
            })
            
            session['username'] = username
            return redirect(url_for('home'))
        
        except Exception as e:
            return jsonify({'success': False, 'error': 'Prišlo je do napake pri registraciji'})
    
    return render_template('register.html')


@app.route('/build')
def build_your_pc():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('build.html')

if __name__ == "__main__":
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
