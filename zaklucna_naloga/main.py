from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "your_secret_key"

db = TinyDB('zapiski.json')
users = db.table('users')
notes = db.table('notes')
subjects = db.table('subjects')
User = Query()

@app.route('/')
def home():
    return render_template("domov.html")  # Vedno prikaži domov z logotipom

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.get(User.username == username)
        if user and user.get("password") == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Napačno uporabniško ime ali geslo.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        user = users.get(User.username == username)
        if user:
            return render_template("login.html", error="Uporabniško ime že obstaja.")
        
        users.insert({
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
        })
        
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    uporabnikovi_predmeti = [
        item['subject']
        for item in subjects.search(User.username == session['username'])
    ]
    return render_template("dashboard.html", username=session['username'], predmeti=uporabnikovi_predmeti)

@app.route('/dodaj_predmet', methods=['POST'])
def dodaj_predmet():
    if 'username' not in session:
        return redirect(url_for('login'))

    predmet = request.form['predmet']
    subjects.insert({'username': session['username'], 'subject': predmet})
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
