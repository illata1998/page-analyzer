import os
from flask import (Flask, render_template, request, flash,
                   get_flashed_messages, url_for, redirect)
from dotenv import load_dotenv
import psycopg2
import validators
from datetime import datetime
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


def normalize_url(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    hostname = parsed_url.hostname
    print(hostname)
    return scheme + '://' + hostname


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form.get('url', '', type=str)
    created_at = datetime.now().date()
    if not (validators.url(url) and len(url) <= 255):
        flash('Некорекктный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            messages=messages,
            url=url
        ), 422
    url = normalize_url(url)
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM urls
        WHERE urls.name = '{url}';
        """
    )
    record = cursor.fetchone()
    if not record:
        flash('Страница успешно добавлена', 'success')
        cursor.execute(
            f"""
            INSERT INTO urls (name, created_at) VALUES
            ('{url}', '{created_at}');
            """
        )
        conn.commit()
        cursor.execute(
            """
            SELECT id
            FROM urls
            WHERE urls.name = '{url}';
            """
        )
        url_id = cursor.fetchone()[0]
        conn.close()
    else:
        flash('Страница уже существует', 'info')
        url_id = record[0]
    return redirect(url_for('show_url', url_id=url_id), code=302)


@app.get('/urls')
def show_all_urls():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            urls.id,
            urls.name,
            latest_url_checks.latest_check_at
        FROM urls
        LEFT JOIN (
            SELECT
                url_checks.url_id AS url_id,
                MAX(url_checks.created_at) as latest_check_at
            FROM url_checks
            GROUP BY url_checks.url_id
        ) AS latest_url_checks
            ON latest_url_checks.url_id = urls.id
        ORDER BY urls.id DESC;
        """
    )
    records = cursor.fetchall()
    urls = []
    for record in records:
        urls.append(
            {
                'id': record[0],
                'name': record[1],
                'latest_check_at': record[2]
            }
        )
    return render_template(
        'show_all_urls.html',
        urls=urls
    )


@app.route('/urls/<url_id>')
def show_url(url_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    messages = get_flashed_messages(with_categories=True)
    cursor.execute(
        """
        SELECT *
        FROM urls
        WHERE urls.id = {url_id};
        """
    )
    record = cursor.fetchone()
    if not record:
        return 404
    url = {
        'id': record[0],
        'name': record[1],
    }
    cursor.execute(
        """
        SELECT
            url_checks.id,
            url_checks.created_at
        FROM url_checks
        WHERE url_checks.url_id = {url_id};
        """
    )
    records = cursor.fetchall()
    url_checks = []
    if record is not None:
        for record in records:
            url_checks.append(
                {
                    'id': record[0],
                    'created_at': record[1]
                }
            )
    conn.close()
    return render_template(
        'show_url.html',
        messages=messages,
        url=url,
        url_checks=url_checks
    )


@app.post('/urls/<url_id>/checks')
def check_url(url_id):
    created_at = datetime.now().date()
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM urls
        WHERE urls.id = {url_id};
        """
    )
    record = cursor.fetchone()
    if not record:
        return 404
    cursor.execute(
        f"""
        INSERT INTO url_checks (url_id, created_at) VALUES
        ('{url_id}', '{created_at}');
        """
    )
    conn.commit()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', url_id=url_id), code=302)
