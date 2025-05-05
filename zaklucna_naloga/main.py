from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query

app = Flask(__name__)

db = TinyDB('zapiski.json')
users = db.table('users')
notes = db.table('notes')  
User = Query()


@app.route('/')
def home():
    if 'username' in session:
        return render_template("domov.html")
    return render_template('domov.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.get(User.username == username)
        if user and user.get("password") == password:
            session['username'] = username
            return render_template('login.html')
        else:
            return render_template("napaka.html")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('domov.html')

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
                return render_template("login.html")
            
            users.insert({
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
            })
            
            session['username'] = username
            return render_template('register.html')
        
        except Exception as e:
            return render_template('napaka.html')
    
    return render_template('register.html')

@app.route('/koledar', methods=['GET', 'POST'])
def koledar():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("koledar.html")


if __name__ == "__main__":
    app.run(debug=True)
