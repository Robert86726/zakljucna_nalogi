from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "1234"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = TinyDB('zapiski.json')
users = db.table('users')
notes = db.table('notes')
subjects = db.table('subjects')
User = Query()

@app.route('/')
def home():
    return render_template("domov.html")  

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

@app.route('/dodaj_zapisek', methods=['POST'])
def dodaj_zapisek():
    if 'username' not in session:
        return redirect(url_for('login'))

    datum = request.form['datum']
    predmet = request.form['predmet']
    file = request.files['zapisek_file']

    if file:
        filename = f"{session['username']}_{datum}.pdf"  
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

    return redirect(url_for('dashboard'))

@app.route('/preveri_zapisek')
def preveri_zapisek():
    datum = request.args.get('datum')
    filename = f"{session['username']}_{datum}.pdf"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return jsonify({'obstaja': os.path.exists(path)})

@app.route("/prenesi_zapisek")
def prenesi_zapisek():
    datum = request.args.get("datum")
    filename = f"{session["username"]}_{datum}.pdf"
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route('/zapiski/<datum>')
def pridobi_zapiske(datum):
    if 'username' not in session:
        return jsonify([])

    zapiski = notes.search((User.username == session['username']) & (User.datum == datum))
    return jsonify(zapiski)


@app.route('/poglej_zapiske')
def poglej_zapiske():
    if 'username' not in session:
        return redirect(url_for('login'))

    datum = request.args.get('datum')
    predmet = request.args.get('predmet')

    if not datum or not predmet:
        return render_template("poglej_zapiske.html", datum=datum, predmet=predmet, datoteka_obstaja=False)

    filename = f"{session['username']}_{datum}.pdf"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    obstaja = os.path.exists(path)

    return render_template("poglej_zapiske.html", datum=datum, predmet=predmet, datoteka_obstaja=obstaja)





if __name__ == "__main__":
    app.run(debug=True)
