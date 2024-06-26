import os
import psycopg2
import requests

from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)

from dotenv import load_dotenv

from page_analyzer.utils import validate_url, normalize_url, format_timestamp
from page_analyzer.html_parser import parse_html

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form.get('url', '', type=str)
    if not validate_url(url):
        flash('Некорректный URL', 'danger')
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
        f"""
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
            INSERT INTO urls (name) VALUES
            ('{url}');
            """
        )
        conn.commit()
        cursor.execute(
            f"""
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
    return redirect(url_for('show_url', url_id=url_id), 302)


@app.get('/urls')
def show_all_urls():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            urls.id,
            urls.name,
            latest_url_checks.status_code,
            latest_url_checks.created_at
        FROM urls
        LEFT JOIN latest_url_checks
            ON urls.id = latest_url_checks.url_id
        ORDER BY urls.id DESC;
        """
    )
    records = cursor.fetchall()
    urls = []
    if records is not None:
        for record in records:
            urls.append(
                {
                    'id': record[0],
                    'name': record[1],
                    'status_code': record[2],
                    'latest_checked_at': format_timestamp(record[3])
                }
            )
    return render_template(
        'show_all_urls.html',
        urls=urls
    )


@app.route('/urls/<int:url_id>')
def show_url(url_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT *
        FROM urls
        WHERE urls.id = {url_id};
        """
    )
    record = cursor.fetchone()
    if not record:
        return render_template('404.html'), 404
    url = {
        'id': record[0],
        'name': record[1],
        'created_at': format_timestamp(record[2])
    }
    cursor.execute(
        f"""
        SELECT
            url_checks.id,
            url_checks.status_code,
            url_checks.h1,
            url_checks.title,
            url_checks.description,
            url_checks.created_at
        FROM url_checks
        WHERE url_checks.url_id = {url_id}
        ORDER BY url_checks.id DESC;
        """
    )
    records = cursor.fetchall()
    url_checks = []
    if records is not None:
        for record in records:
            url_checks.append(
                {
                    'id': record[0],
                    'status_code': record[1],
                    'h1': record[2],
                    'title': record[3],
                    'description': record[4],
                    'created_at': format_timestamp(record[5])
                }
            )
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'show_url.html',
        messages=messages,
        url=url,
        url_checks=url_checks
    )


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT name
        FROM urls
        WHERE urls.id = {url_id};
        """
    )
    record = cursor.fetchone()
    if not record:
        return render_template('404.html'), 404
    try:
        resp = requests.get(record[0])
        resp.raise_for_status()
        h1, title, description = parse_html(resp)
        cursor.execute(
            f"""
            INSERT INTO url_checks (
                url_id,
                status_code,
                h1,
                title,
                description
            ) VALUES (
                '{url_id}',
                {resp.status_code},
                '{h1}',
                '{title}',
                '{description}'
            );
            """
        )
        conn.commit()
        conn.close()
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('show_url', url_id=url_id), 302)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', url_id=url_id))
