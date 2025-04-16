from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tinydb import TinyDB, Query
import requests
import os

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_123"

db = TinyDB('mealmatch.json')
users = db.table('users')
recipes = db.table('recipes')
User = Query()

API_KEY = "fa1b1172374a42b1b8ba88992716df46"

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('search_recipes'))
    return render_template('domov.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.get(User.username == username)
        if user and user.get("password") == password:
            session['username'] = username
            return redirect(url_for('search_recipes'))
        else:
            return jsonify({'success': False, 'error': 'Napačno uporabniško ime ali geslo!'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

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
            return redirect(url_for('search_recipes'))
        
        except Exception as e:
            return jsonify({'success': False, 'error': 'Prišlo je do napake pri registraciji'})
    
    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search_recipes():
    if 'username' not in session:
        return redirect(url_for('home'))

    found_recipes = []
    if request.method == 'POST':
        ingredients = request.form['ingredients']

        url = 'https://api.spoonacular.com/recipes/findByIngredients'
        params = {
            'ingredients': ingredients,
            'number': 10,
            'apiKey': API_KEY
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            found_recipes = response.json()
        else:
            found_recipes = []
    
    return render_template('search.html', recipes=found_recipes)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form['ingredients'].split(', ')  

        recipes.insert({
            'name': name,
            'description': description,
            'ingredients': [ingredient.lower() for ingredient in ingredients]  
        })
        return redirect(url_for('search_recipes'))

    return render_template('add_recipe.html')

if __name__ == "__main__":
    app.run(debug=True)
