import sqlite3

from flask import Flask, render_template, request
from flask import g

app = Flask(__name__)

DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        db = g._database = conn
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/get_user_info')
def get_user_info():
    return str(request.user_agent), str(request.remote_addr)


@app.route('/add_author', methods=['get', 'post'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        country = request.form.get('country')
        birth = request.form.get('birth')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            insert into author ('name', country, birth)
                values (?, ?, ?)
        """, (name, country, birth))
        conn.commit()

    return render_template('add_author.html')


@app.route('/add_book', methods=['get', 'post'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')

        conn = get_db()
        cursor = conn.cursor()
        resp = cursor.execute("""
            select id
            from author
            where name = ?
        """, (author, ))
        resp = resp.fetchone()
        author_id = resp['id']

        cursor.execute("""
        insert into book (title, author_id, 'year')
            values (?, ?, ?)
        """, (title, author_id, year))
        conn.commit()

    return render_template('add_book.html')


@app.route('/get_books')
def get_books():
    year = request.args.get('year')
    if year is not None:
        connection = get_db()
        cursor = connection.cursor()
        resp = cursor.execute("""
            select book.title, book.year, author.name, author.birth
            from book
            join author on author.id = book.author_id 
            where book.year = ?
        """, (year, ))
        resp = resp.fetchall()
        print(resp)


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    # init_db()
    app.run()
