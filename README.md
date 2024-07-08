# Page Analyzer
[![Actions Status](https://github.com/illata1998/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/illata1998/python-project-83/actions)
<a href="https://codeclimate.com/github/illata1998/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/0962810290864cc446ed/maintainability" /></a>

## Description
Page Analyzer is a simple web application that checks the basic page-level elements of websites valuable for on-page SEO.

## Installation
Clone this repository to your local machine.
```bash
git clone git@github.com:illata1998/python-project-83.git
cd python-project-83
```
Install dependencies using [Poetry](https://python-poetry.org/docs/).
```bash
make install
```
Create the new .env file and define SECRET_KEY and DATABASE_URL variables there. For example,
```bash
echo "SECRET_KEY=secret_key" >> .env
echo "DATABASE_URL=postgresql://user:password@host:port/database_name" >> .env
```
Initialize the database manualy or using provided bash script.
```bash
make build
```
Run the app.
```bash
# using Gunicorn
make start
# then open http://0.0.0.0:8000 in your browser


# or using the Flask development server with debug mode
make dev
# then open http://localhost:8000 in your browser
```

## Demo
Check out Page Analyzer by clicking [here](https://python-project-83-2k3w.onrender.com/).
