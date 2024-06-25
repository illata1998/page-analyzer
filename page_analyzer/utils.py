import validators
from urllib.parse import urlparse, urlunparse


def validate_url(url):
    if validators.url(url) and len(url) <= 255:
        return True
    return False


def normalize_url(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.hostname, '', '', '', ''))


def format_timestamp(created_at):
    if created_at is None:
        return None
    return created_at.date()
