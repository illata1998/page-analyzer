import os
from flask import Flask, render_template, request, flash, get_flashed_messages, url_for, redirect
from dotenv import load_dotenv
import psycopg2
import validators
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def index_post():
    url = request.form.get('url', '', type=str)
    created_at = datetime.now().date()
    if validators.url(url) and len(url) <= 255:
        flash('Страница успешно добавлена', 'success')
        cursor.execute(f"INSERT INTO urls (name, created_at) VALUES ('{url}', '{created_at}');")
        cursor.execute(f"SELECT id FROM urls WHERE name = '{url}';")
        id = cursor.fetchone()[0]
        return redirect(url_for('url_get', id=id), code=302)
    flash('Некорекктный URL', 'danger')
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, url=url)


@app.route('/urls/<id>')
def url_get(id):
    messages = get_flashed_messages(with_categories=True)
    cursor.execute(f"SELECT * FROM urls WHERE id = {id}")
    row = cursor.fetchone()
    url = {
        'id': row[0],
        'name': row[1],
        'created_at': row[2]
    }
    return render_template('show.html', messages=messages, url=url)
