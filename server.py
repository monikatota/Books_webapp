from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
import sqlite3

# create app
app = Flask("Flask - Lab")

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'

@app.route('/create_database', methods=['GET'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    conn.execute('CREATE TABLE users (username TEXT, password TEXT, admin TEXT)')
    conn.execute("INSERT INTO users (username,password,admin) VALUES (?,?,?)",("admin","admin","yes"))
    conn.execute("INSERT INTO users (username,password,admin) VALUES (?,?,?)",("monika","monika","no") )
    conn.commit() # konieczne do wpisywania danych do tablicy
    # Zakończenie połączenia z bazą danych
    conn.close()
    return index()

# default route
@app.route("/", methods=['GET']) # pobieranie książek czyli GET
def index(): 
    if 'user' in session:
        conn = sqlite3.connect(DATABASE)
        # retrieve data from table
        cur = conn.cursor()
        cur.execute("select rowid, * from books")
        books = cur.fetchall(); 
        username = session["user"]
        cur.execute("select admin from users where username = '%s'" %username)
        selected_user = cur.fetchall(); 
        print(selected_user)
        print(selected_user[0][0])
        admin_priv = selected_user[0][0]
        return render_template("main.html", session_info=session, books=books, admin_priv=admin_priv)
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
    req_form = request.form.to_dict()
    response_form = request.form
    conn = sqlite3.connect(DATABASE)
    # retrieve user from the database
    cur = conn.cursor()
    cur.execute("select * from users")
    users = cur.fetchall(); 
    for row in users:
        if response_form['login']==row[0] and response_form['password']==row[1]:
            print("User is in the database")
            # Stworzenie sesji dla klienta i dodanie pola user
            session['user']=response_form['login']
            return redirect(url_for('index'))
    # Niepoprawne dane lub użytownika nie ma w bazie - powrót na stronę logowania
    return redirect(url_for('signin'))

@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji 
    if 'user' in session:
        session.pop('user')
    else:
        # Przekierowanie klienta do strony początkowej
        redirect(url_for('index'))
    return redirect(url_for('signin'))

# adding books to database
@app.route('/add', methods=['POST'])
def add():
    author = request.form['author']
    title = request.form['title']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO books (author,title) VALUES (?,?)",(author,title))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/users', methods=['GET'])
def users():
    conn = sqlite3.connect(DATABASE)
    # retrieve user from the database
    cur = conn.cursor()
    cur.execute("select rowid, username, password, admin from users")
    users = cur.fetchall(); 
    return render_template("users.html", session_info=session, users=users)

# adding users to database
@app.route('/addusers', methods=['POST'])
def addusers():
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    if "adminvalue" in request.form:
        admin = "yes"
    else:
        admin = "no"
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO users (username,password,admin) VALUES (?,?,?)",(username,password,admin))
    con.commit()
    con.close()
    return redirect(url_for('users'))

# Endpoint umożliwiający podanie parametru w postaci int'a
@app.route('/users/<int:get_id>')
def user_by_id(get_id):
    conn = sqlite3.connect(DATABASE)
    # retrieve user from the database
    cur = conn.cursor()
    cur.execute("select rowid, username, password, admin from users where rowid=%d" %get_id)
    selected_user = cur.fetchall(); 
    return render_template("user.html", session_info=session, selected_user=selected_user)

# Endpoint umożliwiający podanie parametru w postaci string'a
@app.route('/users/<string:username>')
def user_by_name(username):
    print(username)
    conn = sqlite3.connect(DATABASE)
    # retrieve user from the database
    cur = conn.cursor()
    cur.execute("select rowid, username, password, admin from users where username = '%s'" %username)
    selected_user = cur.fetchall(); 
    return render_template("user.html", session_info=session, selected_user=selected_user)

# Uruchomienie aplikacji w trybie debug
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()

