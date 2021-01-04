from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
import sqlite3

# create app
app = Flask("Flask - Lab")

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = 'super secret key'

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    # Zakończenie połączenia z bazą danych
    conn.close()
    return index()

# defalt route
@app.route("/", methods=['GET','POST']) 
def index(): 
    if 'user' in session:
        con = sqlite3.connect(DATABASE)
        # retrieve data from table
        cur = con.cursor()
        cur.execute("select rowid, * from books")
        print(cur)
        books = cur.fetchall(); 
        print(books)
        return render_template("main.html", session_info=session, books=books)
    else:
        # the main view is blocked for not logged in users, redirect to sign-in page
        return redirect(url_for('signin'))

# sign-in page
@app.route("/signin", methods=['GET']) 
def signin(): 
    return render_template("signin.html")

# endpoint after loggin in
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        req_form = request.form.to_dict()
        response_form = request.form
        # Stworzenie sesji dla klienta i dodanie pola user
        session['user']=response_form['login']
        # session['password']=response_form['password']
        return redirect(url_for('index'))
        # return "Sesja została utworzona <br> <a href='/'> Dalej </a> "

@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji 
    if 'user' in session:
        session.pop('user')
    else:
        # Przekierowanie klienta do strony początkowej
        redirect(url_for('index'))
    return redirect(url_for('signin'))

app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)

@app.route('/add', methods=['POST'])
def add():
    author = request.form['author']
    title = request.form['title']
    # Dodanie użytkownika do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO books (author,title) VALUES (?,?)",(author,title) )
    con.commit()
    con.close()

    # return "Dodano użytkownika do bazy danych <br>" + index()

    return redirect(url_for('index'))

# run app in debug mode
app.debug = True
app.run()

