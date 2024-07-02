import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def format_timestamp(created_at):
    if created_at is None:
        return None
    return created_at.date()


def add_new_url(url_name):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO urls (name) VALUES
            ('{url_name}');
            """
        )
        conn.commit()


def add_new_url_check(url_id, status_code, h1, title, description):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO url_checks (
                url_id,
                status_code,
                h1,
                title,
                description
            ) VALUES (
                {url_id},
                {status_code},
                $${h1}$$,
                $${title}$$,
                $${description}$$
            );
            """
        )
        conn.commit()


def get_url_id_by_url_name(url_name):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT urls.id
            FROM urls
            WHERE urls.name = '{url_name}';
            """
        )
        record = cursor.fetchone()
    url_id = record[0] if record else None
    return url_id


def get_url_info_by_url_id(url_id):
    url_info = {}
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT *
            FROM urls
            WHERE urls.id = {url_id};
            """
        )
        record = cursor.fetchone()
    if record:
        url_info['id'] = record[0]
        url_info['name'] = record[1]
        url_info['created_at'] = format_timestamp(record[2])
    return url_info


def get_url_checks_by_url_id(url_id):
    url_checks = []
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
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
    if records:
        for record in records:
            url_checks.append(
                {'id': record[0],
                 'status_code': record[1],
                 'h1': record[2],
                 'title': record[3],
                 'description': record[4],
                 'created_at': format_timestamp(record[5])
                 }
            )
    return url_checks


def get_all_urls():
    urls = []
    with psycopg2.connect(DATABASE_URL) as conn:
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
    if records:
        for record in records:
            urls.append(
                {
                    'id': record[0],
                    'name': record[1],
                    'status_code': record[2],
                    'latest_checked_at': format_timestamp(record[3])
                }
            )
    return urls
